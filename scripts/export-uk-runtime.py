"""Export the current Ukrainian potential pool without backend editorial tags."""
import hashlib
import json
import argparse
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pool',choices=['expanded','fun'],default='expanded')
args=parser.parse_args()
archive=ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data'
source=json.loads((archive/'opentriviaqa/questions.json').read_text(encoding='utf8'))
translations={q['id']:q for q in json.loads((archive/'translations/uk.json').read_text(encoding='utf8'))['questions']}
master=json.loads((ROOT/'question-bank/questions.json').read_text(encoding='utf8'))
byid={q['id']:q for q in master}
blocked={}
if args.pool=='fun':
    selected=[q for q in master if 'custom:fun-bank:candidate' in q['tags'] and q['id'] in translations]
    ids=set()
    edits=json.loads((ROOT/'question-bank/editorial-overrides.json').read_text(encoding='utf8'))['records'] if (ROOT/'question-bank/editorial-overrides.json').exists() else {}
    for q in selected:
        reasons=[tag for tag in q['tags'] if tag.startswith('reason:eu:uk:uk-') or tag=='reason:eu:uk:unit-localization']
        if edits.get(q['id'],{}).get('status',{}).get('uk') in ('hold','exclude'):reasons.append('manual-uk-hold-or-exclude')
        t=translations[q['id']]
        if len(t['text'])>500 or len(set(c.strip().casefold() for c in t['choices']))!=4:reasons.append('unusable-translation-structure')
        if reasons:blocked[q['id']]=reasons
        else:ids.add(q['id'])
else:
    ids={q['id'] for q in master if 'EU:uk' in q['tags'] or 'pool:eu-uk:potential-unassessed' in q['tags']}
scores={r['id']:r for r in json.loads((ROOT/'question-bank/quality-full-v1/assessment.json').read_text(encoding='utf8'))['records']} if args.pool=='fun' else {}
runtime=[]
for q in source:
    if q['id'] not in ids:continue
    t=translations[q['id']]
    h=hashlib.sha256(json.dumps([q['text'],q['choices']],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    assert t['sourceHash']==h and len(t['choices'])==4 and 0<=q['correct']<4
    extra={}
    if args.pool=='fun':
        rating=scores[q['id']]
        canonical={k:byid[q['id']][k] for k in ['id','text','choices','correct']}
        digest=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert rating['sourceFingerprint']==digest(canonical) and rating['translationFingerprint']==digest(t)
        extra={'difficultyStars':rating['difficultyStars']}
    runtime.append({**q,**extra,'category':byid[q['id']]['category'],'text':t['text'],'choices':t['choices'],'language':'uk','translationStatus':t['status']})
assert len(runtime)==len(ids) and len({q['id'] for q in runtime})==len(ids)
assert all(len(q['text'])<=500 for q in runtime)
assert not any(q['category']=='Religion & Faith' for q in runtime)
dist=ROOT/'browser-site/dist'
data=(json.dumps(runtime,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
(dist/'questions.json').write_bytes(data)
categories=sorted({q['category'] for q in runtime})
(dist/'questions.js').write_text("export const questions = await fetch('./questions.json').then(r=>{if(!r.ok)throw Error('Question data unavailable');return r.json()});\nexport const categories = "+json.dumps(categories)+";\nexport function questionPool(language,region){return language==='uk'&&region==='Europe'?questions:[];}\n",encoding='utf8')
report={'pool':args.pool,'count':len(runtime),'categories':dict(sorted(Counter(q['category'] for q in runtime).items())),'runtimeBytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'status':'strict-fun-semantic-and-localization-screened-drafts' if args.pool=='fun' else 'filtered-translated-drafts-including-unassessed','source':'OpenTriviaQA contributors','license':'CC-BY-SA-4.0','translationHolds':len(blocked),'translationHoldReasonsOverlapping':dict(Counter(r for reasons in blocked.values() for r in reasons)),'notes':'Strict Fun v2 holds all tagged translation risks and unverified movie/book titles; machine screening is not factual certification. No backend tags included.' if args.pool=='fun' else 'Current filters applied; semantic review and translated-title verification incomplete. No backend tags included.'}
(dist/'bank-info.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if args.pool=='fun':
    (ROOT/'question-bank/fun-bank/uk-build-holds.json').write_text(json.dumps(blocked,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
