"""Finish the explicitly authorized remaining cohort; separate $1 safety ceiling, no prior resubmissions."""
import importlib.util,concurrent.futures,collections,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('expansion',HERE.parent/'luna-expand-v1/expand.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
c=e.c;c.HERE=HERE;c.LIMIT=1.0
ROOT=c.ROOT;OLD=HERE.parent/'luna-expand-v1'

def prepare():
    bank,uk=c.inputs();ids=set(c.load(OLD/'remaining-ids.json'));oldids={r['id'] for r in c.load(OLD/'all-audit.json')['records']}
    assert len(ids)==1130 and not ids&oldids and ids|oldids=={q['id'] for q in bank}
    rows=[]
    for q in bank:
        if q['id'] not in ids:continue
        u=uk.get(q['id']);rows.append(dict(id=q['id'],category=q['category'],text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian={'text':u['text'],'choices':u['choices']} if u else None,sourceFingerprint=c.digest({k:q[k] for k in ['id','text','choices','correct']}),translationFingerprint=c.digest(u) if u else None))
    manifest=dict(authorization='User: finish remaining, API limits should be enough; additional to previous $5',newRunSafetyCeilingUsd=1,sourceNonSemanticSha256=c.digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank]),priorSummary=c.load(OLD/'summary.json'),questions=len(rows),model=c.MODEL,vocabularySha256=c.digest(c.VOCAB))
    for name,value in [('selection.json',rows),('manifest.json',manifest)]:
        if (HERE/name).exists():assert c.load(HERE/name)==value
        else:c.write(HERE/name,value)
    (HERE/'responses').mkdir(exist_ok=True)
    if not (HERE/'ledger.json').exists():c.write(HERE/'ledger.json',dict(limitUsd=1,model=c.MODEL,rates=c.RATES,requests={}))
    return rows

def run():
    rows=prepare();done=set();ledger=c.load(HERE/'ledger.json');byid={q['id']:q for q in rows}
    for name,entry in ledger['requests'].items():
        assert entry['status']=='completed', 'Unresolved request: '+name
        if '-repair-' in name:continue
        path=HERE/'responses'/f'{name}.validated.json'
        if not path.exists():c.write(path,e.classified_chunk(name,[byid[qid] for qid in entry['questionIds']]))
    for p in (HERE/'responses').glob('*.validated.json'):done.update(r['id'] for r in c.load(p))
    remaining=[q for q in rows if q['id'] not in done];counter=e.next_number(ledger['requests'])
    def work(pair):
        name,chunk=pair;result=e.classified_chunk(name,chunk);c.write(HERE/'responses'/f'{name}.validated.json',result);return len(result)
    while remaining:
        jobs=[]
        for _ in range(12):
            if not remaining:break
            jobs.append((f'finish-{counter:04}',remaining[:20]));remaining=remaining[20:];counter+=1
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(work,jobs))
        print({'completedThisWave':sum(results),'remaining':len(remaining),'additionalCommittedUsd':c.charge_total(c.load(HERE/'ledger.json'))},flush=True)
    print('FINISHED',flush=True)

if __name__=='__main__':run()
