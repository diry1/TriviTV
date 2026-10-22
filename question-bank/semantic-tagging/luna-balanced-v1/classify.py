"""Budgeted, resumable Luna classification. No key or auth headers are logged."""
import argparse, collections, concurrent.futures, hashlib, html, json, os, re, threading, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MODEL='gpt-6-luna'
LIMIT=5.0
RATES={'input':0.10,'cached':0.01,'cache_write':0.125,'output':0.50}
LOCK=threading.Lock()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def stable(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(stable(x).encode()).hexdigest()
def write(p,x):
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,p)
def obj(props):return dict(type='object',properties=props,required=list(props),additionalProperties=False)
def arr(item):return dict(type='array',items=item)
def string():return dict(type='string')
def enum(values):return dict(type='string',enum=values)
VOCAB=load(HERE.parent/'vocabulary-v2.json')
ALLOWED=sorted(f+':'+v for f,vs in VOCAB['families'].items() for v in vs if f+':'+v not in VOCAB.get('deprecatedValues',{}))
def valid_tag(t):return t in ALLOWED or bool(re.fullmatch(r'era:[0-9]{3}0s',t))
SCHEMA=obj({'records':arr(obj({'id':string(),'tags':arr(obj({'tag':enum(ALLOWED+['era:'+str(y).zfill(4)+'s' for y in range(0,2100,10)]),'evidence':string(),'confidence':enum(['high','medium','low'])})),'entities':arr(obj({'surface':string(),'role':enum(['prompt','choice:0','choice:1','choice:2','choice:3']),'kind':enum(VOCAB['families']['entity-kind']+['location']),'confidence':enum(['high','medium','low']),'regions':arr(enum(VOCAB['families']['location-mention']))})),'eras':arr(obj({'value':string(),'confidence':enum(['high','medium','low']),'role':enum(VOCAB['dynamicFamilies']['era']['roles']),'evidence':string()})),'notes':arr(string()),'proposals':arr(obj({'tag':string(),'reason':string()}))}))})
def inputs():
    bank=load(ROOT/'question-bank/questions.json');uk={q['id']:q for q in load(ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data/translations/uk.json')['questions']}
    return bank,uk

def prepare():
    bank,uk=inputs();cats=sorted({q['category'] for q in bank});groups={c:sorted([q for q in bank if q['category']==c],key=lambda q:digest('luna-balanced-v1|'+q['id'])) for c in cats}
    n=min(map(len,groups.values()));assert n==125 and len(cats)==20
    questions=[groups[c][i] for i in range(n) for c in cats]
    rows=[]
    for q in questions:
        u=uk.get(q['id']);rows.append(dict(id=q['id'],category=q['category'],text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian={'text':u['text'],'choices':u['choices']} if u else None,sourceFingerprint=digest({k:q[k] for k in ['id','text','choices','correct']}),translationFingerprint=digest(u) if u else None))
    manifest=dict(model=MODEL,budgetUsd=LIMIT,pricingUsdPerMillion=RATES,processing='standard; explicit token output caps; conservative reservations',seed='luna-balanced-v1',perCategory=n,total=len(rows),categories=cats,selection='Deterministic SHA256 shuffle within each category; interleave one per category per round. All full-master categories, not a change to EU/Fun eligibility.',sourceMasterCount=len(bank),sourceAndNonSemanticTagsSha256=digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank]),instructionsSha256=digest((HERE/'instructions.txt').read_text(encoding='utf-8')),vocabularySha256=digest(VOCAB))
    if (HERE/'selection.json').exists():assert load(HERE/'selection.json')==rows,'Selection/source changed; do not overwrite a paid run'
    if (HERE/'manifest.json').exists():assert load(HERE/'manifest.json')==manifest,'Run context changed'
    write(HERE/'selection.json',rows);write(HERE/'manifest.json',manifest)
    (HERE/'responses').mkdir(exist_ok=True)
    if not (HERE/'ledger.json').exists():write(HERE/'ledger.json',dict(limitUsd=LIMIT,model=MODEL,rates=RATES,requests={}))
    return rows

def api_key():
    key=os.environ.get('OPENAI_API_KEY')
    if not key:
        s=(ROOT/'.env.local').read_text(encoding='utf-8-sig');m=re.search(r'^OPENAI_API_KEY\s*=\s*[\"\']?([^\s\"\']+)',s,re.M);key=m.group(1) if m else None
    if not key or not key.startswith('sk-'):raise RuntimeError('No configured API key')
    return key

def cost(usage):
    inp=usage.get('input_tokens',0);out=usage.get('output_tokens',0);cached=usage.get('input_tokens_details',{}).get('cached_tokens',0)
    written=usage.get('input_tokens_details',{}).get('cache_write_tokens',0)
    return ((inp-cached-written)*RATES['input']+cached*RATES['cached']+written*RATES['cache_write']+out*RATES['output'])/1e6

def reserve_bound(body):
    # UTF-8 bytes upper-bound ordinary text token counts. Include schema and
    # message framing plus generous overhead; output includes reasoning tokens.
    return ((len(stable(body).encode('utf-8'))+8192)*0.125+body['max_output_tokens']*RATES['output'])/1e6

def body_for(rows):
    clean=[{k:v for k,v in r.items() if not k.endswith('Fingerprint')} for r in rows]
    instructions=(HERE/'instructions.txt').read_text(encoding='utf-8')+'\nCONTROLLED VOCABULARY:\n'+stable({'families':VOCAB['families'],'deprecated':VOCAB['deprecatedValues']})
    return dict(model=MODEL,store=False,reasoning={'effort':'low'},max_output_tokens=min(40000,len(rows)*1800+4000),input=[{'role':'developer','content':instructions},{'role':'user','content':stable({'questions':clean})}],text={'format':{'type':'json_schema','name':'semantic_classifications','strict':True,'schema':SCHEMA}})

def charge_total(ledger):return sum(r.get('costUsd',r['reservedUsd']) for r in ledger['requests'].values())
def request(name,rows):
    path=HERE/'responses'/f'{name}.json';body=body_for(rows);bound=reserve_bound(body);key=api_key();hashed=digest(body)
    with LOCK:
        ledger=load(HERE/'ledger.json');old=ledger['requests'].get(name)
        if old:
            assert old['bodySha256']==hashed,'Request changed'
            if old['status']=='completed' and path.exists():return load(path)
            raise RuntimeError(f'Request {name} already has status {old["status"]}; inspect before any resubmission')
        if charge_total(ledger)+bound>LIMIT:raise RuntimeError('Budget ceiling reached; no request submitted')
        ledger['requests'][name]=dict(status='reserved',reservedUsd=bound,bodySha256=hashed,questionIds=[r['id'] for r in rows],createdAt=datetime.now(timezone.utc).isoformat())
        write(HERE/'ledger.json',ledger)
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=240) as response:result=json.load(response)
    except urllib.error.HTTPError as error:
        try:message=json.load(error).get('error',{})
        except Exception:message={}
        with LOCK:
            ledger=load(HERE/'ledger.json');ledger['requests'][name].update(status='http-error',httpStatus=error.code,errorCode=message.get('code'),errorMessage=str(message.get('message',''))[:500].replace(key,'[redacted]'))
            # Known HTTP rejection is not a completed generation. Keep reservation
            # conservatively; no automatic retry/model substitution.
            write(HERE/'ledger.json',ledger)
        raise RuntimeError(f'API rejected {name}: HTTP {error.code}, {message.get("code")}') from None
    except Exception as error:
        with LOCK:
            ledger=load(HERE/'ledger.json');ledger['requests'][name].update(status='uncertain-error',errorType=type(error).__name__);write(HERE/'ledger.json',ledger)
        raise RuntimeError(f'Uncertain request {name}; reservation kept, no automatic retry') from None
    write(path,result)
    usage=result.get('usage',{});spent=cost(usage)
    with LOCK:
        ledger=load(HERE/'ledger.json');ledger['requests'][name].update(status='completed',responseId=result.get('id'),responseStatus=result.get('status'),usage=usage,costUsd=spent)
        write(HERE/'ledger.json',ledger)
        assert spent<=bound,'Conservative reservation invalid: stop'
    print(json.dumps({'request':name,'questions':len(rows),'status':result.get('status'),'costUsd':round(spent,6)}),flush=True)
    return result

def unpack(response,rows):
    assert response['status']=='completed',('Incomplete response',response.get('incomplete_details'))
    texts=[c['text'] for item in response.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text']
    parsed=json.loads(''.join(texts));records=parsed['records'];assert {r['id'] for r in records}=={r['id'] for r in rows} and len(records)==len(rows),'Missing/extra/duplicate IDs'
    sources={r['id']:r for r in rows};clean=[]
    for r in records:
        q=sources[r['id']];strings=[q['text']]+q['choices'];held=[];tags=[]
        for t in r['tags']:
            if not valid_tag(t['tag']) or not t['evidence'] or not any(t['evidence'] in text for text in strings):
                held.append(dict(tag=t['tag'],reason='Validator withheld unknown tag or non-exact evidence',evidence=t['evidence']));continue
            if t['confidence']!='high':held.append(dict(tag=t['tag'],reason='Non-high confidence',evidence=t['evidence']));continue
            tags.append(t)
        valid_entities=[]
        for entity in r['entities']:
            text=q['text'] if entity['role']=='prompt' else q['choices'][int(entity['role'].split(':')[1])]
            if not entity['surface'] or entity['surface'] not in text:
                held.append(dict(tag='entity:'+entity['kind'],reason='Non-exact entity span',evidence=entity['surface']));continue
            assert all(region in VOCAB['families']['location-mention'] for region in entity['regions'])
            valid_entities.append(entity)
        r['entities']=valid_entities
        tags=list({t['tag']:t for t in tags}.values())
        # Entity/era observations are first-class evidence, not optional duplicate tags.
        existing={t['tag'] for t in tags}
        for e in r['entities']:
            if e['confidence']!='high':continue
            derived=(['entity-kind:'+e['kind']] if e['kind']!='location' else [])+['location-mention:'+v for v in e['regions'] if e['kind']=='location']
            for tag in derived:
                if tag not in existing:tags.append(dict(tag=tag,evidence=e['surface'],confidence='high',derivedFrom='entity'));existing.add(tag)
        for e in r['eras']:
            tag='era:'+e['value']
            if e['confidence']=='high' and valid_tag(tag) and tag not in existing and any(e['evidence'] in x for x in strings):tags.append(dict(tag=tag,evidence=e['evidence'],confidence='high',derivedFrom='era'));existing.add(tag)
        for t in tags[:]:
            if t['tag'].startswith('entity-kind:') and not any(e['kind']==t['tag'].split(':',1)[1] and e['confidence']=='high' for e in r['entities']):tags.remove(t);held.append(dict(tag=t['tag'],reason='No matching entity evidence'))
            if t['tag'].startswith('location-mention:') and not any(t['tag'].split(':',1)[1] in e['regions'] and e['kind']=='location' and e['confidence']=='high' for e in r['entities']):tags.remove(t);held.append(dict(tag=t['tag'],reason='No matching location entity evidence'))
            if t['tag'].startswith('era:') and not any(e['value']==t['tag'].split(':',1)[1] and any(e['evidence'] in s for s in strings) for e in r['eras']):tags.remove(t);held.append(dict(tag=t['tag'],reason='No matching era evidence'))
        assert len({t['tag'] for t in tags})==len(tags),'Duplicate tag'
        if not any(t['tag'].startswith('topic:') for t in tags):
            r['notes'].append('No high-confidence in-vocabulary topic; requires topic/vocabulary review, not a forced source-category tag.')
            held.append(dict(tag='topic:unresolved',reason='No high-confidence topic; held for review'))
        clean.append(dict(id=q['id'],category=q['category'],sourceFingerprint=q['sourceFingerprint'],translationFingerprint=q['translationFingerprint'],model=MODEL,vocabularyVersion=2,responseId=response['id'],translationExamined=q['ukrainian'] is not None,assignments=tags,entities=r['entities'],eras=r['eras'],notes=r['notes'],proposals=r['proposals']+held))
    return clean

def calibration():
    bank,uk=inputs();by_id={q['id']:q for q in bank};pilot=load(HERE.parent/'pilot-v1/audit.json')['records']
    rows=[]
    for p in pilot:
        q=by_id[p['id']];u=uk.get(q['id']);rows.append(dict(id=q['id'],category=q['category'],text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian={'text':u['text'],'choices':u['choices']} if u else None,sourceFingerprint=p['sourceFingerprint'],translationFingerprint=p['translationFingerprint']))
    result=[]
    for i in range(0,len(rows),10):result.extend(unpack(request(f'calibration-v2-{i//10:02}',rows[i:i+10]),rows[i:i+10]))
    comparisons=[]
    for a,p in zip(sorted(result,key=lambda x:x['id']),sorted(pilot,key=lambda x:x['id'])):
        expected={x['tag'].removeprefix('custom:semantic:') for x in p['assignments']};actual={x['tag'] for x in a['assignments']}
        comparisons.append(dict(id=a['id'],expected=sorted(expected),actual=sorted(actual),missing=sorted(expected-actual),extra=sorted(actual-expected),jaccard=len(expected&actual)/len(expected|actual)))
    write(HERE/'calibration.json',dict(records=result,comparisons=comparisons,meanTagJaccard=sum(c['jaccard'] for c in comparisons)/len(comparisons),notIndependentAccuracy=True))
    print(json.dumps({'calibration':len(result),'meanTagJaccard':sum(c['jaccard'] for c in comparisons)/len(comparisons)}),flush=True)

def run(workers=4):
    rows=prepare();chunks=[rows[i:i+20] for i in range(0,len(rows),20)];failures=[]
    def work(pair):
        i,chunk=pair;name=f'round-{i:03}';path=HERE/'responses'/f'{name}.validated.json'
        if path.exists():return len(load(path))
        result=unpack(request(name,chunk),chunk);write(path,result);return len(result)
    # Bounded waves: never enqueue the whole run before observing failures.
    for start in range(0,len(chunks),workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures=[pool.submit(work,(i,chunks[i])) for i in range(start,min(start+workers,len(chunks)))]
            for f in futures:
                try:f.result()
                except Exception as e:failures.append(str(e))
        ledger=load(HERE/'ledger.json');print(json.dumps({'roundsCompleted':len(list((HERE/'responses').glob('round-*.validated.json'))),'budgetCommittedUsd':round(charge_total(ledger),6),'errors':failures}),flush=True)
        if failures:raise RuntimeError('; '.join(failures))
    return rows

def export():
    selected=load(HERE/'selection.json');records=[]
    for i in range(125):records.extend(load(HERE/'responses'/f'round-{i:03}.validated.json'))
    assert len(records)==2500 and len({r['id'] for r in records})==2500
    bank,uk=inputs();by_id={q['id']:q for q in bank};manual=load(ROOT/'question-bank/tag-sources/semantic-pilot-v1.json')
    manifest=load(HERE/'manifest.json');assert manifest['sourceAndNonSemanticTagsSha256']==digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank])
    owned={};standalone=[];linked=[];conflicts=[];review_source={}
    topic_reviews=load(HERE/'topic-review.json') if (HERE/'topic-review.json').exists() else []
    review_by_id=collections.defaultdict(list)
    for review in topic_reviews:
        q=by_id[review['id']];assert review['sourceFingerprint']==digest({k:q[k] for k in ['id','text','choices','correct']})
        review_vocab=load(HERE.parent/'vocabulary-v3.json')
        assert review['tag'] in [f+':'+v for f,vs in review_vocab['families'].items() for v in vs] and any(review['evidence'] in text for text in [q['text']]+q['choices'])
        review_by_id[q['id']].append(review)
        review_source.setdefault(q['id'],[]).append('custom:semantic:'+review['tag'])
    for r in records:
        q=by_id[r['id']];assert r['sourceFingerprint']==digest({k:q[k] for k in ['id','text','choices','correct']})
        assert r['translationFingerprint']==(digest(uk[q['id']]) if q['id'] in uk else None)
        predicted=sorted('custom:semantic:'+t['tag'] for t in r['assignments'])
        if q['id'] in manual:
            effective=manual[q['id']]
            if predicted!=effective:conflicts.append(dict(id=q['id'],keptManual=effective,modelProposal=predicted))
        else:owned[q['id']]=predicted;effective=sorted(set(predicted)|set(review_source.get(q['id'],[])))
        r['reviewerAdditions']=review_by_id.get(q['id'],[])
        standalone.append({**q,'tags':sorted(set(q['tags'])|set(effective))})
        if q['id'] in uk:linked.append(uk[q['id']])
    ledger=load(HERE/'ledger.json');committed=charge_total(ledger);assert committed<=LIMIT
    counts=collections.Counter(q['category'] for q in standalone);assert len(counts)==20 and set(counts.values())=={125}
    write(HERE/'audit.json',dict(schemaVersion=1,backendOnly=True,model=MODEL,records=records))
    write(HERE/'questions.en.json',standalone);write(HERE/'questions.eu-en.json',[q for q in standalone if 'EU:en' in q['tags']]);write(HERE/'questions.fun-en.json',[q for q in standalone if 'custom:fun-bank:candidate' in q['tags']]);write(HERE/'translations.uk.json',dict(language='uk',license='CC-BY-SA-4.0',status='linked acquired drafts; not independently approved',questions=linked))
    # Reuse the existing Ukrainian Fun holds without changing any eligibility.
    blocked=set(load(ROOT/'question-bank/fun-bank/uk-build-holds.json'))
    fun_uk=[]
    for q in standalone:
        if 'custom:fun-bank:candidate' not in q['tags'] or q['id'] not in uk or q['id'] in blocked:continue
        t=uk[q['id']]
        assert t['sourceHash']==hashlib.sha256(json.dumps([q['text'],q['choices']],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        fun_uk.append({**q,'text':t['text'],'choices':t['choices'],'language':'uk','translationStatus':t['status']})
    write(HERE/'questions.fun-uk.json',fun_uk)
    write(HERE/'manual-conflicts.json',conflicts)
    write(ROOT/'question-bank/tag-sources/semantic-luna-balanced-v1.json',owned)
    write(ROOT/'question-bank/tag-sources/semantic-luna-topic-review-v1.json',review_source)
    summary=dict(model=MODEL,questions=2500,existingFunUkrainianCandidatesAfterKnownHolds=len(fun_uk),existingEUEnglishCandidates=sum('EU:en' in q['tags'] for q in standalone),existingFunEnglishCandidates=sum('custom:fun-bank:candidate' in q['tags'] for q in standalone),perCategory=dict(sorted(counts.items())),linkedUkrainianDrafts=len(linked),activeLunaIds=len(owned),manualIdsPreserved=2500-len(owned),manualConflicts=len(conflicts),confirmedAssignments=sum(len(r['assignments']) for r in records),recordsWithProposals=sum(bool(r['proposals']) for r in records),recordsWithNotes=sum(bool(r['notes']) for r in records),topicReviewAdditions=len(topic_reviews),recordsWithoutDefiniteTopic=sum(not any(t.startswith('custom:semantic:topic:') for t in q['tags']) for q in standalone),usageCostUsd=sum(r.get('costUsd',0) for r in ledger['requests'].values()),committedCeilingUsd=committed,budgetUsd=LIMIT,remainingBudgetUsd=LIMIT-committed,eligibilityUnchanged=True,classificationIsNotFactualVerification=True)
    write(HERE/'summary.json',summary);print(json.dumps(summary),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','calibrate','run','export']);parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
    if args.action=='prepare':print(json.dumps({'prepared':len(prepare())}))
    elif args.action=='calibrate':prepare();calibration()
    elif args.action=='run':run(args.workers)
    else:export()
if __name__=='__main__':main()
