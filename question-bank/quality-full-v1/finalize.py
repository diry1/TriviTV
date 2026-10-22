"""Local export validation, bilingual CSV, deduplicated name verification queue."""
import importlib.util,json,csv,collections,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('qualityrun',HERE/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);c=r.c;ROOT=r.ROOT
rows=c.load(HERE/'selection.json');records=c.load(HERE/'assessment.json')['records'];byid={x['id']:x for x in records};bank={q['id']:q for q in c.load(ROOT/'question-bank/questions.json')};uk={q['id']:q for q in c.load(ROOT/'question-bank/fun-bank/translations.uk.json')['questions']};pilot=c.load(HERE.parent/'quality-pilot-v1/assessment.json')['records'];glossary={}
assert len(rows)==len(records)==len(byid)==7104
for q in rows:
    a=byid[q['id']];assert a['sourceFingerprint']==c.digest({k:bank[q['id']][k] for k in ['id','text','choices','correct']});assert a['translationFingerprint']==c.digest(uk[q['id']]);assert 1<=a['difficultyStars']<=5
    for ent in a['entities']:
        role=ent['role'];e=q['text'] if role=='prompt' else q['choices'][int(role[-1])];u=q['ukrainian']['text'] if role=='prompt' else q['ukrainian']['choices'][int(role[-1])];assert ent['english'] in e and ent['ukrainian'] in u
        key=(ent['english'].casefold(),ent['ukrainian'].casefold(),ent['kind'])
        item=glossary.setdefault(key,dict(english=ent['english'],ukrainian=ent['ukrainian'],kind=ent['kind'],questionIds=[],assessments=set(),externallyVerified=False))
        if q['id'] not in item['questionIds']:item['questionIds'].append(q['id'])
        item['assessments'].add(ent['assessment'])
for a in pilot:assert byid[a['id']]==a,'Pilot evidence/corrections changed'
queue=[]
for item in glossary.values():item['assessments']=sorted(item['assessments']);item['occurrences']=len(item['questionIds']);queue.append(item)
queue.sort(key=lambda x:(not ('suspected-error' in x['assessments']),not ('needs-source-verification' in x['assessments']),-x['occurrences'],x['english']))
c.write(HERE/'name-verification-queue.json',queue)
safe=lambda v:"'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v
with (HERE/'review.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.writer(out);w.writerow(['id','category','question_en','question_uk','choices_en','choices_uk','correct_index','difficultyStars','difficultyConfidence','readingBurden','translationStatus','translationReason','sourceConcerns'])
    for q in rows:
        a=byid[q['id']];w.writerow([safe(v) for v in [q['id'],q['category'],q['text'],q['ukrainian']['text'],json.dumps(q['choices'],ensure_ascii=False),json.dumps(q['ukrainian']['choices'],ensure_ascii=False),q['correct'],a['difficultyStars'],a['difficultyConfidence'],a['readingBurden'],a['translationStatus'],a['translationReason'],json.dumps(a['sourceConcerns'],ensure_ascii=False)]])
with (HERE/'name-verification-queue.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.writer(out);w.writerow(['english','ukrainian','kind','occurrences','assessments','questionIds','externallyVerified'])
    for item in queue:w.writerow([safe(item['english']),safe(item['ukrainian']),item['kind'],item['occurrences'],json.dumps(item['assessments']),json.dumps(item['questionIds']),False])
ledger=c.load(HERE/'ledger.json');assert all(e['status']=='completed' for e in ledger['requests'].values())
summary=c.load(HERE/'summary.json');summary['uniqueEntityPairs']=len(queue);summary['namePairsFlaggedForResearch']=sum(any(t!='plausible-unverified' for t in q['assessments']) for q in queue);summary['difficultyByCategory']={cat:dict(sorted(collections.Counter(byid[q['id']]['difficultyStars'] for q in rows if q['category']==cat).items())) for cat in sorted({q['category'] for q in rows})};c.write(HERE/'summary.json',summary)
c.write(HERE/'validation.json',dict(uniqueQuestions=7104,reusedPilotPreserved=200,newlyAssessed=6904,exactSourceAndTranslationFingerprints=True,exactPublishedEntitySpans=True,allRequestsCompleted=True,masterUnchanged=c.digest(c.load(ROOT/'question-bank/questions.json'))==c.load(HERE/'manifest.json')['bankSha256'],runtimeUnchanged=hashlib.sha256((ROOT/'browser-site/dist/questions.json').read_bytes()).hexdigest()==c.load(HERE/'manifest.json')['runtimeSha256'],uniqueEntityPairs=len(queue),knownAdditionalCostUsd=summary['additionalCostUsd']))
print(c.stable(summary))
