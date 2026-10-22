"""200-question isolated quality pilot. run spends API credits; export is local."""
import importlib.util,json,collections,concurrent.futures,sys,hashlib,html
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('base',ROOT/'question-bank/semantic-tagging/luna-balanced-v1/classify.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.HERE=HERE;c.LIMIT=.5

def prepare():
    bank=c.load(ROOT/'question-bank/fun-bank/questions.en.json');uk={q['id']:q for q in c.load(ROOT/'question-bank/fun-bank/translations.uk.json')['questions']};bank=[q for q in bank if q['id'] in uk];assert len(bank)==7104
    # Half category coverage, half proportional: deterministic without replacement.
    groups={cat:sorted([q for q in bank if q['category']==cat],key=lambda q:c.digest('quality-pilot-v1|'+q['id'])) for cat in sorted({q['category'] for q in bank})};chosen=[];counts=collections.Counter()
    for _ in range(5):
        for cat,g in groups.items():
            if g:chosen.append(g.pop(0));counts[cat]+=1
    rest=sorted([q for g in groups.values() for q in g],key=lambda q:c.digest('quality-pilot-proportional|'+q['id']))
    chosen+=rest[:200-len(chosen)]
    rows=[dict(id=q['id'],category=q['category'],text=q['text'],choices=q['choices'],correct=q['correct'],ukrainian=uk[q['id']],sourceFingerprint=c.digest({k:q[k] for k in ['id','text','choices','correct']}),translationFingerprint=c.digest(uk[q['id']])) for q in chosen]
    for name,value in [('selection.json',rows),('manifest.json',dict(sourcePool=7104,selected=200,seed='quality-pilot-v1',selection='Up to five per category, then deterministic shuffled remainder; oversamples rare categories; not a prevalence estimator.',perCategory=dict(collections.Counter(q['category'] for q in rows)),bankSha256=c.digest(c.load(ROOT/'question-bank/questions.json')),runtimeSha256=hashlib.sha256((ROOT/'browser-site/dist/questions.json').read_bytes()).hexdigest(),model=c.MODEL,safetyCeilingUsd=.5))]:
        if (HERE/name).exists():assert c.load(HERE/name)==value
        else:c.write(HERE/name,value)
    (HERE/'responses').mkdir(exist_ok=True)
    if not (HERE/'ledger.json').exists():c.write(HERE/'ledger.json',dict(limitUsd=.5,model=c.MODEL,rates=c.RATES,requests={}))
    return rows

issue=c.obj({'kind':c.enum(['meaning','names','titles','terminology','answer-choices','grammar','source-quality','audience','other']),'englishEvidence':c.string(),'ukrainianEvidence':c.string(),'explanation':c.string(),'suggestedRepair':c.string()})
entity=c.obj({'english':c.string(),'ukrainian':c.string(),'kind':c.enum(['person','place','brand','title','term','other']),'role':c.enum(['prompt','choice:0','choice:1','choice:2','choice:3']),'assessment':c.enum(['plausible-unverified','needs-source-verification','suspected-error']),'reason':c.string()})
schema=c.obj({'records':c.arr(c.obj({'id':c.string(),'difficultyStars':{'type':'integer','minimum':1,'maximum':5},'difficultyConfidence':c.enum(['high','medium','low']),'difficultyReason':c.string(),'readingBurden':c.enum(['low','medium','high']),'readingReason':c.string(),'translationStatus':c.enum(['pass','needs-repair','needs-source-verification']),'translationReason':c.string(),'issues':c.arr(issue),'entities':c.arr(entity),'sourceConcerns':c.arr(c.string())}))})

def body(rows):
    clean=[{k:v for k,v in q.items() if not k.endswith('Fingerprint')} for q in rows]
    return dict(model=c.MODEL,store=False,reasoning={'effort':'low'},max_output_tokens=20000,input=[dict(role='developer',content=(HERE/'instructions.txt').read_text(encoding='utf-8')),dict(role='user',content=c.stable({'questions':clean}))],text={'format':dict(type='json_schema',name='quality_pilot',strict=True,schema=schema)})
c.body_for=body

def run():
    rows=prepare()
    def work(i):
        chunk=rows[i:i+10];raw=c.request(f'quality-{i//10:03}',chunk);assert raw['status']=='completed'
        parsed=json.loads(''.join(t['text'] for item in raw['output'] for t in item.get('content',[]) if t['type']=='output_text'))['records'];assert len(parsed)==len(chunk) and {r['id'] for r in parsed}=={q['id'] for q in chunk}
        lookup={q['id']:q for q in chunk}
        for r in parsed:
            q=lookup[r['id']]
            valid=[];withheld=[]
            for ent in r['entities']:
                e=q['text'] if ent['role']=='prompt' else q['choices'][int(ent['role'][-1])];u=q['ukrainian']['text'] if ent['role']=='prompt' else q['ukrainian']['choices'][int(ent['role'][-1])]
                if ent['english'] and ent['ukrainian'] and ent['english'] in e and ent['ukrainian'] in u:valid.append(ent)
                else:withheld.append(ent)
            r['entities']=valid;r['withheldEntities']=withheld
            if withheld and r['translationStatus']=='pass':r['translationStatus']='needs-source-verification';r['translationReason']+=' Validator withheld non-exact entity pairs; review needed.'
            r.update(sourceFingerprint=q['sourceFingerprint'],translationFingerprint=q['translationFingerprint'],responseId=raw['id'],externallyVerified=False)
        c.write(HERE/'responses'/f'quality-{i//10:03}.validated.json',parsed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(work,range(0,200,10)))
    print('API pilot complete')

if __name__=='__main__':
    if sys.argv[1]=='prepare':print('Prepared',len(prepare()))
    elif sys.argv[1]=='run':run()
