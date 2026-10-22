"""Local-only publishing and integrity checks; does not submit API calls."""
import collections,csv,importlib.util,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('finish',HERE/'finish.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
c=f.c;ROOT=f.ROOT;OLD=f.OLD
bank,uk=c.inputs();manifest=c.load(HERE/'manifest.json');records=[r for p in sorted((HERE/'responses').glob('*.validated.json')) for r in c.load(p)]
assert len(records)==len({r['id'] for r in records})==1130
assert {r['id'] for r in records}==set(c.load(OLD/'remaining-ids.json'))
byid={q['id']:q for q in bank}
for r in records:
    q=byid[r['id']];assert r['sourceFingerprint']==c.digest({k:q[k] for k in ['id','text','choices','correct']})
    assert r['translationFingerprint']==(c.digest(uk[q['id']]) if q['id'] in uk else None)
owned={r['id']:sorted({'custom:semantic:'+t['tag'] for t in r['assignments']}) for r in records}
c.write(ROOT/'question-bank/tag-sources/semantic-luna-finish-v1.json',owned)
subprocess.run([__import__('sys').executable,'-X','utf8',str(ROOT/'scripts/build-question-tags.py')],cwd=ROOT,check=True)
bank,uk=c.inputs()
assert manifest['sourceNonSemanticSha256']==c.digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank])
allrecords=c.load(OLD/'all-audit.json')['records']+records
assert len(allrecords)==len({r['id'] for r in allrecords})==len(bank)==38926
sources=list((ROOT/'question-bank/tag-sources').glob('semantic-*.json'));union=collections.defaultdict(set)
for p in sources:
    for qid,tags in c.load(p).items():union[qid].update(tags)
for q in bank:assert set(t for t in q['tags'] if t.startswith('custom:semantic:'))==union[q['id']]
ledger=c.load(HERE/'ledger.json');assert all(r['status']=='completed' for r in ledger['requests'].values())
extra=sum(r['costUsd'] for r in ledger['requests'].values());assert extra<=c.charge_total(ledger)<=1
prior=manifest['priorSummary'];holds=set(c.load(ROOT/'question-bank/fun-bank/uk-build-holds.json'))
funuk=[{**q,'text':uk[q['id']]['text'],'choices':uk[q['id']]['choices'],'language':'uk','translationStatus':uk[q['id']]['status']} for q in bank if 'custom:fun-bank:candidate' in q['tags'] and q['id'] in uk and q['id'] not in holds]
summary=dict(model=c.MODEL,newlyClassified=len(records),questions=len(bank),perCategory=dict(sorted(collections.Counter(q['category'] for q in bank).items())),linkedUkrainianDrafts=len(uk),existingEUEnglishCandidates=sum('EU:en' in q['tags'] for q in bank),existingFunEnglishCandidates=sum('custom:fun-bank:candidate' in q['tags'] for q in bank),existingFunUkrainianCandidatesAfterKnownHolds=len(funuk),additionalCostUsd=extra,usageCostUsd=prior['usageCostUsd']+extra,committedCeilingUsd=prior['committedCeilingUsd']+extra,uncertainReservedUsd=prior['uncertainReservedUsd'],unclassifiedMain=0,eligibilityUnchanged=True,combinedRecordsWithoutDefiniteTopic=sum(not any(t.startswith('custom:semantic:topic:') for t in q['tags']) for q in bank))
for name,value in [('summary.json',summary),('audit.json',dict(backendOnly=True,records=records)),('all-audit.json',dict(backendOnly=True,records=allrecords)),('questions.en.json',bank),('questions.eu-en.json',[q for q in bank if 'EU:en' in q['tags']]),('questions.fun-en.json',[q for q in bank if 'custom:fun-bank:candidate' in q['tags']]),('questions.fun-uk.json',funuk),('translations.uk.json',dict(language='uk',license='CC-BY-SA-4.0',status='acquired linked drafts',questions=list(uk.values()))),('remaining-ids.json',[])]:c.write(HERE/name,value)
def safe(v):
    s=v if isinstance(v,str) else c.stable(v)
    return "'"+s if s.startswith(('=','+','-','@','\t','\r')) else s
with (HERE/'questions.en.csv').open('w',encoding='utf-8-sig',newline='') as out:
    writer=csv.writer(out);writer.writerow(['id','category','question_en','choices_en','correct_index','question_uk','choices_uk','semantic_tags','source_attribution','translation_provenance','translation_link'])
    for q in bank:
        u=uk.get(q['id'],{});writer.writerow([safe(v) for v in [q['id'],q['category'],q['text'],q['choices'],q['correct'],u.get('text',''),u.get('choices',[]),[t for t in q['tags'] if t.startswith('custom:semantic:')],q.get('source',q.get('sources',{})),u,'http://127.0.0.1:8791/?question='+q['id']]])
c.write(HERE/'validation.json',dict(uniqueCoverage=38926,newUnique=1130,sourceAndNonSemanticUnchanged=True,fingerprintsVerified=True,semanticSourceUnionVerified=True,allNewRequestsCompleted=True,newCostBelowSafetyCeiling=True))
(HERE/'REPORT.md').write_text(f'''# Full-bank Luna classification completed\n\nAll 38,926 English questions across 20 categories have now been processed. This final cohort contained 1,130 General Knowledge questions, without resubmitting previous cohorts.\n\nAdditional calculated API cost: ${extra:.8f}. Cumulative known cost: ${summary['usageCostUsd']:.8f}. One earlier timed-out request still has an unknown actual cost; its maximum ${summary['uncertainReservedUsd']:.8f} reservation remains preserved. Maximum cumulative committed cost: ${summary['committedCeilingUsd']:.8f}. The user separately authorized finishing beyond the original $5 allowance.\n\nMain content, answer choices, correct indexes, nonsemantic tags and pool membership are unchanged. Source-owned backend tags were merged by canonical ID. Ukrainian drafts are linked by ID, not newly translated or fact-verified. Uncertain proposals remain unpublished; {summary['combinedRecordsWithoutDefiniteTopic']} questions have no definite topic assignment and need review.\n\nExports: {summary['existingEUEnglishCandidates']} EU English; {summary['existingFunEnglishCandidates']} Fun English; {len(funuk)} Fun Ukrainian after existing holds. Raw responses, usage ledger, fingerprints and evidence retained. No runtime/APK/public deployment changes.\n''',encoding='utf-8')
render=(OLD/'render_review.py').read_text(encoding='utf-8').replace('token cost of $5 ceiling','known token cost · final completion separately authorized')
(HERE/'render_review.py').write_text(render,encoding='utf-8')
subprocess.run([__import__('sys').executable,'-X','utf8',str(HERE/'render_review.py')],check=True)
print(c.stable(summary))
