"""Continuation under the SAME cumulative $5 authorization. Resumable; no duplicate IDs."""
import argparse,collections,concurrent.futures,copy,heapq,importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('luna_base',HERE.parent/'luna-balanced-v1/classify.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
PRIOR_LEDGER=HERE.parent/'luna-balanced-v1/ledger.json'
prior=c.load(PRIOR_LEDGER);prior_cost=c.charge_total(prior)
assert all(r['status']=='completed' for r in prior['requests'].values())
c.HERE=HERE;c.LIMIT=5-prior_cost;c.VOCAB=c.load(HERE.parent/'vocabulary-v3.json');c.ALLOWED=sorted(f+':'+v for f,vs in c.VOCAB['families'].items() for v in vs if f+':'+v not in c.VOCAB.get('deprecatedValues',{}))
c.SCHEMA['properties']['records']['items']['properties']['tags']['items']['properties']['tag']['enum']=c.ALLOWED+['era:'+str(y).zfill(4)+'s' for y in range(0,2100,10)]

def prepare():
    bank,uk=c.inputs();old=c.load(HERE.parent/'luna-balanced-v1/selection.json');pilot=c.load(ROOT/'question-bank/tag-sources/semantic-pilot-v1.json');known={q['id'] for q in old}|set(pilot)
    coverage=collections.Counter(q['category'] for q in bank if q['id'] in known)
    groups={cat:collections.deque(sorted([q for q in bank if q['category']==cat and q['id'] not in known],key=lambda q:c.digest('luna-expand-v1|'+q['id']))) for cat in sorted({q['category'] for q in bank})}
    heap=[(coverage[cat],cat) for cat,g in groups.items() if g];heapq.heapify(heap);ordered=[]
    while heap:
        count,cat=heapq.heappop(heap);q=groups[cat].popleft();u=uk.get(q['id']);ordered.append(dict(id=q['id'],category=cat,text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian={'text':u['text'],'choices':u['choices']} if u else None,sourceFingerprint=c.digest({k:q[k] for k in ['id','text','choices','correct']}),translationFingerprint=c.digest(u) if u else None))
        if groups[cat]:heapq.heappush(heap,(count+1,cat))
    manifest=dict(model=c.MODEL,priorCostUsd=prior_cost,cumulativeBudgetUsd=5,remainingAuthorizationUsd=c.LIMIT,totalUnclassified=len(ordered),alreadyClassified=len(known),initialCoverage=dict(coverage),selection='SHA256 shuffle within category; prioritize lowest cumulative coverage among categories with records left; never repeat IDs.',sourceNonSemanticSha256=c.digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank]),instructionsSha256=c.digest((HERE/'instructions.txt').read_text(encoding='utf-8')),vocabularySha256=c.digest(c.VOCAB),priorLedgerSha256=c.digest(prior))
    if (HERE/'selection.json').exists():assert c.load(HERE/'selection.json')==ordered
    if (HERE/'manifest.json').exists():assert c.load(HERE/'manifest.json')==manifest
    c.write(HERE/'selection.json',ordered);c.write(HERE/'manifest.json',manifest);(HERE/'responses').mkdir(exist_ok=True)
    if not (HERE/'ledger.json').exists():c.write(HERE/'ledger.json',dict(limitUsd=c.LIMIT,priorCostUsd=prior_cost,cumulativeLimitUsd=5,model=c.MODEL,rates=c.RATES,requests={}))
    return ordered

def classified_chunk(name,chunk):
    response=c.request(name,chunk)
    def parse(raw):
        assert raw['status']=='completed',('Incomplete response',raw.get('incomplete_details'))
        return json.loads(''.join(x['text'] for item in raw.get('output',[]) for x in item.get('content',[]) if x.get('type')=='output_text'))['records']
    output=parse(response);wanted={r['id']:r for r in chunk};counts=collections.Counter(r['id'] for r in output)
    good={r['id']:r for r in output if r['id'] in wanted and counts[r['id']]==1};origins={qid:response['id'] for qid in good}
    for attempt in range(3):
        missing=[q for q in chunk if q['id'] not in good]
        if not missing:break
        repaired=c.request(name+f'-repair-{attempt}',missing);fixed=parse(repaired);freq=collections.Counter(r['id'] for r in fixed)
        for r in fixed:
            if r['id'] in wanted and r['id'] not in good and freq[r['id']]==1:good[r['id']]=r;origins[r['id']]=repaired['id']
    assert set(good)==set(wanted),'IDs still incomplete after targeted repairs'
    combined={**response,'output':[{'content':[{'type':'output_text','text':json.dumps({'records':[good[q['id']] for q in chunk]},ensure_ascii=False)}]}]}
    result=c.unpack(combined,chunk)
    for r in result:r['responseId']=origins[r['id']];r['vocabularyVersion']=3
    return result

def next_number(requests):return max((int(name.split('-')[1]) for name in requests),default=-1)+1
def budget_exhausted(size,before,after):return size==1 and before==after

def run(workers):
    rows=prepare();completed=set();files=sorted((HERE/'responses').glob('*.validated.json'))
    for p in files:completed.update(r['id'] for r in c.load(p))
    # Recover completed paid requests before considering new calls, including a
    # validation interruption. Never blindly resubmit a paid or uncertain call.
    ledger=c.load(HERE/'ledger.json');by_id={q['id']:q for q in rows}
    for name,entry in ledger['requests'].items():
        if entry['status']!='completed':
            recoveries=c.load(HERE/'request-recoveries.json') if (HERE/'request-recoveries.json').exists() else {}
            if entry['status']=='uncertain-error' and name in recoveries:
                path=HERE/'responses'/f'{name}.validated.json'
                if not path.exists():
                    chunk=[by_id[qid] for qid in entry['questionIds']];result=classified_chunk(recoveries[name]['replacement'],chunk);c.write(path,result);completed.update(r['id'] for r in result)
                continue
            raise RuntimeError('Inspect unresolved request '+name)
        if '-repair-' in name:continue
        path=HERE/'responses'/f'{name}.validated.json'
        if not path.exists():
            chunk=[by_id[qid] for qid in entry['questionIds']];result=classified_chunk(name,chunk)
            for r in result:r['vocabularyVersion']=3
            c.write(path,result);completed.update(r['id'] for r in result)
    remaining=[q for q in rows if q['id'] not in completed];counter=next_number(ledger['requests']);stop='bank-complete'
    while remaining:
        before_count=len(completed)
        workers_now=min(workers,len(remaining));chunks=[]
        # Near the ceiling, use smaller requests rather than overspend.
        available=c.LIMIT-c.charge_total(c.load(HERE/'ledger.json'))
        size=20 if available>.1 else 5 if available>.025 else 1
        for _ in range(workers_now):
            if not remaining:break
            chunk=remaining[:size];remaining=remaining[size:];name=f'continue-{counter:04}';counter+=1;chunks.append((name,chunk))
        def work(pair):
            name,chunk=pair;result=classified_chunk(name,chunk)
            for r in result:r['vocabularyVersion']=3
            c.write(HERE/'responses'/f'{name}.validated.json',result);return chunk
        errors=[];budget_blocked=False
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers_now) as pool:
            for f in [pool.submit(work,pair) for pair in chunks]:
                try:
                    for q in f.result():completed.add(q['id'])
                except RuntimeError as e:
                    if 'Budget ceiling reached' in str(e):budget_blocked=True
                    else:errors.append(str(e))
                except Exception as e:errors.append(str(e))
        ledger=c.load(HERE/'ledger.json');print(json.dumps({'classifiedNew':len(completed),'classifiedTotal':len(completed)+c.load(HERE/'manifest.json')['alreadyClassified'],'cumulativeCommittedUsd':round(prior_cost+c.charge_total(ledger),6),'errors':errors}),flush=True)
        if errors:raise RuntimeError('; '.join(errors))
        if budget_blocked:
            # No budget-rejected call was submitted, and all in-flight work has
            # joined. Rebuild the remaining queue and retry with single records.
            remaining=[q for q in rows if q['id'] not in completed]
            if budget_exhausted(size,before_count,len(completed)):stop='budget-ceiling';break
    c.write(HERE/'run-status.json',dict(reason=stop,classifiedNew=len(completed),remaining=len(rows)-len(completed),cumulativeCostUsd=prior_cost+c.charge_total(c.load(HERE/'ledger.json'))))

def export():
    bank,uk=c.inputs();by_id={q['id']:q for q in bank};manifest=c.load(HERE/'manifest.json');assert manifest['sourceNonSemanticSha256']==c.digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank])
    records=[r for p in sorted((HERE/'responses').glob('*.validated.json')) for r in c.load(p)];assert len(records)==len({r['id'] for r in records})
    owned={}
    for r in records:
        q=by_id[r['id']];assert r['sourceFingerprint']==c.digest({k:q[k] for k in ['id','text','choices','correct']});assert r['translationFingerprint']==(c.digest(uk[q['id']]) if q['id'] in uk else None)
        owned[q['id']]=sorted(set('custom:semantic:'+t['tag'] for t in r['assignments']))
    prior_audit=c.load(HERE.parent/'luna-balanced-v1/audit.json')['records'];c.write(HERE/'audit.json',dict(model=c.MODEL,vocabularyVersion=3,backendOnly=True,records=records))
    c.write(ROOT/'question-bank/tag-sources/semantic-luna-expand-v1.json',owned)
    all_ids=set(owned)|{r['id'] for r in prior_audit}|set(c.load(ROOT/'question-bank/tag-sources/semantic-pilot-v1.json'));combined=[]
    for q in bank:
        if q['id'] in all_ids:combined.append({**q,'tags':sorted(set(q['tags'])|set(owned.get(q['id'],[])))})
    combined_audit={r['id']:r for r in prior_audit}
    for r in c.load(HERE.parent/'pilot-v1/audit.json')['records']:
        combined_audit.setdefault(r['id'],{**r,'notes':r['issues']})
    combined_audit.update({r['id']:r for r in records})
    c.write(HERE/'all-audit.json',dict(backendOnly=True,records=list(combined_audit.values())))
    c.write(HERE/'questions.en.json',combined);c.write(HERE/'questions.eu-en.json',[q for q in combined if 'EU:en' in q['tags']]);c.write(HERE/'questions.fun-en.json',[q for q in combined if 'custom:fun-bank:candidate' in q['tags']]);c.write(HERE/'translations.uk.json',dict(language='uk',license='CC-BY-SA-4.0',status='acquired linked drafts',questions=[uk[q['id']] for q in combined if q['id'] in uk]))
    blocked=set(c.load(ROOT/'question-bank/fun-bank/uk-build-holds.json'));funuk=[]
    for q in combined:
        if 'custom:fun-bank:candidate' in q['tags'] and q['id'] in uk and q['id'] not in blocked:
            t=uk[q['id']];funuk.append({**q,'text':t['text'],'choices':t['choices'],'language':'uk','translationStatus':t['status']})
    c.write(HERE/'questions.fun-uk.json',funuk)
    ledger=c.load(HERE/'ledger.json');cost=prior_cost+c.charge_total(ledger)
    summary=dict(model=c.MODEL,newlyClassified=len(records),questions=len(combined),perCategory=dict(sorted(collections.Counter(q['category'] for q in combined).items())),existingEUEnglishCandidates=sum('EU:en' in q['tags'] for q in combined),existingFunEnglishCandidates=sum('custom:fun-bank:candidate' in q['tags'] for q in combined),existingFunUkrainianCandidatesAfterKnownHolds=len(funuk),linkedUkrainianDrafts=sum(q['id'] in uk for q in combined),usageCostUsd=prior_cost+sum(r.get('costUsd',0) for r in ledger['requests'].values()),committedCeilingUsd=cost,uncertainReservedUsd=sum(r['reservedUsd'] for r in ledger['requests'].values() if r['status']!='completed'),continuationCostUsd=sum(r.get('costUsd',0) for r in ledger['requests'].values()),remainingBudgetUsd=5-cost,budgetUsd=5,unclassifiedMain=len(bank)-len(combined),newAssignments=sum(len(r['assignments']) for r in records),newRecordsWithoutDefiniteTopic=sum(not any(t['tag'].startswith('topic:') for t in r['assignments']) for r in records),combinedRecordsWithoutDefiniteTopic=sum(not any(t.startswith('custom:semantic:topic:') for t in q['tags']) for q in combined),recordsWithProposals=sum(bool(r['proposals']) for r in records),recordsWithNotes=sum(bool(r['notes']) for r in records),eligibilityUnchanged=True)
    c.write(HERE/'summary.json',summary);print(json.dumps(summary),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','export']);p.add_argument('--workers',type=int,default=32);args=p.parse_args()
    if args.action=='prepare':print(json.dumps({'prepared':len(prepare()),'remainingBudgetUsd':c.LIMIT}))
    elif args.action=='run':run(args.workers)
    else:export()
if __name__=='__main__':main()
