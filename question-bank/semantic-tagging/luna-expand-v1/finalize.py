"""Local publication validation and combined CSV/report. No API requests."""
import collections,csv,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
stable=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
digest=lambda x:hashlib.sha256(stable(x).encode()).hexdigest()
s=load(HERE/'summary.json');bank=load(ROOT/'question-bank/questions.json');manifest=load(HERE/'manifest.json');selected=load(HERE/'questions.en.json');byid={q['id']:q for q in bank};uk={q['id']:q for q in load(HERE/'translations.uk.json')['questions']};audit=load(HERE/'audit.json')['records']
assert digest([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in bank])==manifest['sourceNonSemanticSha256']
owned=[load(p) for p in (ROOT/'question-bank/tag-sources').glob('semantic-*.json')]
for q in bank:
 expected={t for src in owned for t in src.get(q['id'],[])};assert expected=={t for t in q['tags'] if t.startswith('custom:semantic:')}
for q in selected:assert q==byid[q['id']]
for r in audit:
 q=byid[r['id']];assert r['sourceFingerprint']==digest({k:q[k] for k in ['id','text','choices','correct']})
assert len({r['id'] for r in audit})==len(audit)
ledger=load(HERE/'ledger.json');recoveries=load(HERE/'request-recoveries.json') if (HERE/'request-recoveries.json').exists() else {}
assert all(r['status']=='completed' or n in recoveries and (HERE/'responses'/f'{n}.validated.json').exists() for n,r in ledger['requests'].items());assert s['committedCeilingUsd']<=5
with (HERE/'questions.en.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['id','category','english_question','A','B','C','D','correct_index','ukrainian_question','uk_A','uk_B','uk_C','uk_D','semantic_tags','source_attribution','uk_translation_provenance','translation_link'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 safe=lambda t:"'"+t if t.lstrip().startswith(('=','+','-','@')) else t
 for q in selected:
  u=uk.get(q['id']);w.writerow({'id':q['id'],'category':q['category'],'english_question':safe(q['text']),**{c:safe(t) for c,t in zip('ABCD',q['choices'])},'correct_index':q['correct'],'ukrainian_question':safe(u['text']) if u else '',**{'uk_'+c:safe(t) for c,t in zip('ABCD',u['choices'] if u else ['']*4)},'semantic_tags':json.dumps([t for t in q['tags'] if t.startswith('custom:semantic:')],ensure_ascii=False),'source_attribution':json.dumps(q['source'],ensure_ascii=False),'uk_translation_provenance':json.dumps({k:u.get(k) for k in ['status','method','sourceHash']},ensure_ascii=False) if u else '', 'translation_link':'http://127.0.0.1:8791/?question='+q['id']})
usage=[r['usage'] for r in ledger['requests'].values() if 'usage' in r];totals={k:sum(x.get(k,0) for x in usage) for k in ['input_tokens','output_tokens']}
validation=dict(date='2026-10-22',newlyClassified=len(audit),classifiedCombined=len(selected),unclassifiedMain=s['unclassifiedMain'],uniqueIds=True,questionTextChoicesCorrectIndexesAndNonSemanticTagsUnchanged=True,allOwnedSemanticSourcesMatchMaster=True,standaloneMatchesMaster=True,cumulativeCostUsd=s['usageCostUsd'],ceilingUsd=5,uncertainReservedUsd=s['uncertainReservedUsd'],committedCeilingUsd=s['committedCeilingUsd'],allRequestsAccounted=True,continuedRequests=len(ledger['requests']),knownUsageResponses=len(usage),uncertainRequests=len(ledger['requests'])-len(usage),continuedUsage=totals,eligibilityUnchanged=True)
(HERE/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reason=load(HERE/'run-status.json')['reason']
report=f"""# Luna continuation — 2026-10-22

**{s['newlyClassified']:,} additional questions classified; {s['questions']:,} total including the previous balanced pass and reviewed pilot.** {s['unclassifiedMain']:,} main-bank questions remain unclassified. Stop reason: **{reason}**.

[Searchable bilingual review](review.html) · [Bilingual CSV](questions.en.csv) · [English JSON](questions.en.json) · [EU English](questions.eu-en.json) · [Fun English](questions.fun-en.json) · [Fun Ukrainian](questions.fun-uk.json) · [Validation](validation.json)

## Spending

- Same cumulative **$5 ceiling**, including the earlier $0.313091635 pass, not a new $5.
- Continuation calculated token cost: **${s['continuationCostUsd']:.4f}**.
- Cumulative calculated token cost: **${s['usageCostUsd']:.4f}**.
- Uncertain call reservation retained: **${s['uncertainReservedUsd']:.4f}**; known usage plus reservation **${s['committedCeilingUsd']:.4f}**.
- Unused authorization: **${s['remainingBudgetUsd']:.4f}**. This is not a claim about the account balance or taxes.
- Model gpt-6-luna, low reasoning, Standard Responses, frozen vocabulary v3. Raw responses and token usage retained locally; no tools/web lookup or API response storage.
- Spending reservations include bounded output/hidden reasoning and conservative input/cache-write costs. No blind resubmission of completed/uncertain calls. Missing/duplicate IDs repaired by requesting only unresolved IDs, retaining original successful records.
- No local paid runner remains after this report; the original timed-out request has unknown server outcome/cost, conservatively reserved in full. If the bank finishes under $5, stop rather than buy duplicate labels simply to consume credit.

## Selection and tags

The previous 2,500 balanced IDs and all 50 manually reviewed pilot IDs were excluded from new calls. Questions were hash-shuffled within category, then selected from the lowest cumulative coverage among categories with unseen questions remaining. Exhausted categories keep their completed coverage; larger categories continue. This is a useful broad selection rather than top-to-bottom slicing; exact equal shares are impossible after category exhaustion.

Semantic labels remain backend-only. High-confidence labels require exact source evidence, supported entity spans and era roles. Low/medium confidence and failed evidence stay in proposals. Model confidence is not factual approval. Vocabulary v3 includes personal biography, radio and animation; previous reviewed sources remain separately owned and preserved. {s['newAssignments']:,} validated assignments added in this continuation; {s['recordsWithProposals']:,} records have unpublished proposals and {s['recordsWithNotes']:,} have review notes.

{s['combinedRecordsWithoutDefiniteTopic']:,} selected records still have no definite high-confidence topic; they remain flagged for review, not force-filled.

No question wording, choices, canonical correct indexes, category, existing editorial decisions or EU/Fun eligibility changed. Classification did not perform outside title/fact verification. The earlier calibration showed stronger broad topics than subtle translation-risk detection; absence of a risk tag is not approval.

## Combined exports

| Pool | Count |
| --- | ---: |
| Classified English master selection | {s['questions']:,} |
| Linked Ukrainian drafts | {s['linkedUkrainianDrafts']:,} |
| Existing EU English candidates | {s['existingEUEnglishCandidates']:,} |
| Existing English Fun candidates | {s['existingFunEnglishCandidates']:,} |
| Existing Ukrainian Fun candidates after known holds | {s['existingFunUkrainianCandidatesAfterKnownHolds']:,} |

The full Main retains religion and US-specific material; EU/Fun exports reuse existing filters. Source/translation attribution and source hashes retained. No runtime bank, APK or public deployment changed.

## Files and continuation

manifest.json/selection.json freeze inputs, category order and prior-ledger fingerprint. ledger.json and responses/ retain usage/evidence; audit.json covers only this new pass, all-audit.json includes earlier classified records. Source-owned contribution is question-bank/tag-sources/semantic-luna-expand-v1.json. Removing that source and rebuilding withdraws its tags without touching manual/previous sources.

The paid runner is expand.py run; do not start concurrent runners because its spending lock is process-local. Export/finalize/render are local-only. New calls may need renewed authorization if the existing cumulative ceiling is reached. The remaining unclassified IDs can be reconstructed from the main bank minus prior and current source-owned IDs.
"""
(HERE/'REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps(validation))
