"""Finish quality assessment of 7,104 Fun Ukrainian questions; preserve pilot and bank."""
import importlib.util,json,collections,concurrent.futures,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PILOT=HERE.parent/'quality-pilot-v1'
spec=importlib.util.spec_from_file_location('pilot',PILOT/'pilot.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.HERE=HERE;c=p.c;c.HERE=HERE;c.LIMIT=5.0

def prepare():
    bank=c.load(ROOT/'question-bank/fun-bank/questions.en.json');uk={q['id']:q for q in c.load(ROOT/'question-bank/fun-bank/translations.uk.json')['questions']};pilot={q['id']:q for q in c.load(PILOT/'selection.json')}
    rows=[dict(id=q['id'],category=q['category'],text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian=uk[q['id']],sourceFingerprint=c.digest({k:q[k] for k in ['id','text','choices','correct']}),translationFingerprint=c.digest(uk[q['id']])) for q in bank if q['id'] in uk]
    assert len(rows)==7104 and set(pilot)<=set(q['id'] for q in rows)
    for q in rows:
        if q['id'] in pilot:assert q==pilot[q['id']]
    remaining=sorted([q for q in rows if q['id'] not in pilot],key=lambda q:c.digest('quality-full-v1|'+q['id']))
    manifest=dict(perCategory=dict(collections.Counter(q['category'] for q in rows)),sourcePool=7104,reusedPilot=200,newQuestions=6904,model=c.MODEL,additionalSafetyCeilingUsd=5,authorization='User: proceed with all 7104, API limits are up',bankSha256=c.digest(c.load(ROOT/'question-bank/questions.json')),runtimeSha256=hashlib.sha256((ROOT/'browser-site/dist/questions.json').read_bytes()).hexdigest(),instructionsSha256=c.digest((HERE/'instructions.txt').read_text(encoding='utf-8')),pilotAuditSha256=c.digest(c.load(PILOT/'assessment.json')))
    for name,value in [('selection.json',rows),('new-selection.json',remaining),('manifest.json',manifest)]:
        if (HERE/name).exists():assert c.load(HERE/name)==value
        else:c.write(HERE/name,value)
    (HERE/'responses').mkdir(exist_ok=True)
    if not (HERE/'ledger.json').exists():c.write(HERE/'ledger.json',dict(limitUsd=5,model=c.MODEL,rates=c.RATES,requests={}))
    return remaining

def parse(raw):
    assert raw['status']=='completed',('Incomplete response',raw.get('incomplete_details'))
    return json.loads(''.join(t['text'] for item in raw['output'] for t in item.get('content',[]) if t['type']=='output_text'))['records']

def work(pair):
    name,chunk=pair;path=HERE/'responses'/f'{name}.validated.json'
    if path.exists():return len(c.load(path))
    raw=c.request(name,chunk);output=parse(raw);wanted={q['id']:q for q in chunk};counts=collections.Counter(r['id'] for r in output);good={r['id']:r for r in output if r['id'] in wanted and counts[r['id']]==1};origins={qid:raw['id'] for qid in good}
    for attempt in range(2):
        missing=[q for q in chunk if q['id'] not in good]
        if not missing:break
        repaired=c.request(name+f'-repair-{attempt}',missing);rr=parse(repaired);freq=collections.Counter(r['id'] for r in rr)
        for r in rr:
            if r['id'] in wanted and r['id'] not in good and freq[r['id']]==1:good[r['id']]=r;origins[r['id']]=repaired['id']
    assert set(good)==set(wanted),'Missing IDs: '+name
    result=[]
    for q in chunk:
        r=good[q['id']];valid=[];withheld=[]
        for ent in r['entities']:
            e=q['text'] if ent['role']=='prompt' else q['choices'][int(ent['role'][-1])];u=q['ukrainian']['text'] if ent['role']=='prompt' else q['ukrainian']['choices'][int(ent['role'][-1])]
            if ent['english'] and ent['ukrainian'] and ent['english'] in e and ent['ukrainian'] in u:valid.append(ent)
            else:withheld.append(ent)
        r['entities']=valid;r['withheldEntities']=withheld
        if withheld and r['translationStatus']=='pass':r['translationStatus']='needs-source-verification';r['translationReason']+=' Validator withheld non-exact entity pairs; review needed.'
        r.update(sourceFingerprint=q['sourceFingerprint'],translationFingerprint=q['translationFingerprint'],responseId=origins[r['id']],externallyVerified=False);result.append(r)
    c.write(path,result);return len(result)

def run():
    rows=prepare();jobs=[(f'full-{i//10:04}',rows[i:i+10]) for i in range(0,len(rows),10)];jobs=[pair for pair in jobs if not (HERE/'responses'/f'{pair[0]}.validated.json').exists()]
    for i in range(0,len(jobs),48):
        with concurrent.futures.ThreadPoolExecutor(max_workers=48) as pool:
            futures=[pool.submit(work,pair) for pair in jobs[i:i+48]];errors=[]
            for future in concurrent.futures.as_completed(futures):
                try:future.result()
                except Exception as error:errors.append(str(error))
        count=sum(len(c.load(f)) for f in (HERE/'responses').glob('*.validated.json'));ledger=c.load(HERE/'ledger.json');status=dict(newCompleted=count,totalCompleted=count+200,remaining=6904-count,additionalCommittedUsd=c.charge_total(ledger),errors=errors);c.write(HERE/'run-status.json',status);print(json.dumps(status),flush=True)
        if errors:raise RuntimeError('; '.join(errors))
    print('ALL 7104 COMPLETE',flush=True)
if __name__=='__main__':run()
