# Luna continuation — 2026-10-22

**35,258 additional questions classified; 37,796 total including the previous balanced pass and reviewed pilot.** 1,130 main-bank questions remain unclassified. Stop reason: **budget-ceiling**.

[Searchable bilingual review](review.html) · [Bilingual CSV](questions.en.csv) · [English JSON](questions.en.json) · [EU English](questions.eu-en.json) · [Fun English](questions.fun-en.json) · [Fun Ukrainian](questions.fun-uk.json) · [Validation](validation.json)

## Spending

- Same cumulative **$5 ceiling**, including the earlier $0.313091635 pass, not a new $5.
- Continuation calculated token cost: **$4.6569**.
- Cumulative calculated token cost: **$4.9700**.
- Uncertain call reservation retained: **$0.0244**; known usage plus reservation **$4.9944**.
- Unused authorization: **$0.0056**. This is not a claim about the account balance or taxes.
- Model gpt-6-luna, low reasoning, Standard Responses, frozen vocabulary v3. Raw responses and token usage retained locally; no tools/web lookup or API response storage.
- Spending reservations include bounded output/hidden reasoning and conservative input/cache-write costs. No blind resubmission of completed/uncertain calls. Missing/duplicate IDs repaired by requesting only unresolved IDs, retaining original successful records.
- No local paid runner remains after this report; the original timed-out request has unknown server outcome/cost, conservatively reserved in full. If the bank finishes under $5, stop rather than buy duplicate labels simply to consume credit.

## Selection and tags

The previous 2,500 balanced IDs and all 50 manually reviewed pilot IDs were excluded from new calls. Questions were hash-shuffled within category, then selected from the lowest cumulative coverage among categories with unseen questions remaining. Exhausted categories keep their completed coverage; larger categories continue. This is a useful broad selection rather than top-to-bottom slicing; exact equal shares are impossible after category exhaustion.

Semantic labels remain backend-only. High-confidence labels require exact source evidence, supported entity spans and era roles. Low/medium confidence and failed evidence stay in proposals. Model confidence is not factual approval. Vocabulary v3 includes personal biography, radio and animation; previous reviewed sources remain separately owned and preserved. 153,496 validated assignments added in this continuation; 21,609 records have unpublished proposals and 8,148 have review notes.

231 selected records still have no definite high-confidence topic; they remain flagged for review, not force-filled.

No question wording, choices, canonical correct indexes, category, existing editorial decisions or EU/Fun eligibility changed. Classification did not perform outside title/fact verification. The earlier calibration showed stronger broad topics than subtle translation-risk detection; absence of a risk tag is not approval.

## Combined exports

| Pool | Count |
| --- | ---: |
| Classified English master selection | 37,796 |
| Linked Ukrainian drafts | 35,812 |
| Existing EU English candidates | 27,050 |
| Existing English Fun candidates | 16,593 |
| Existing Ukrainian Fun candidates after known holds | 14,561 |

The full Main retains religion and US-specific material; EU/Fun exports reuse existing filters. Source/translation attribution and source hashes retained. No runtime bank, APK or public deployment changed.

## Files and continuation

manifest.json/selection.json freeze inputs, category order and prior-ledger fingerprint. ledger.json and responses/ retain usage/evidence; audit.json covers only this new pass, all-audit.json includes earlier classified records. Source-owned contribution is question-bank/tag-sources/semantic-luna-expand-v1.json. Removing that source and rebuilding withdraws its tags without touching manual/previous sources.

The paid runner is expand.py run; do not start concurrent runners because its spending lock is process-local. Export/finalize/render are local-only. New calls may need renewed authorization if the existing cumulative ceiling is reached. The remaining unclassified IDs can be reconstructed from the main bank minus prior and current source-owned IDs.


## Final checks

19 source categories are fully covered; all1,130unprocessed IDs are General Knowledge (remaining-ids.json). Sixcontinuation +8classifier +6masterintegrity tests passed, alongwith earlierpilot integrity. Full37,796-questionreview tested for pagination, category/tag/Fun filtering, desktop/mobile overflow and browsererrors;0errors. Dashboard restartedPID30396 and verified to read merged tags. Originalnonsemantic/content digest and allownedsource tags match.

One20-questionrequest timedout after240seconds without a responseID. Its original maximum$0.02439625cost remains reserved; a separately reviewed replacement completed, and both are included under the same$5ceiling. Known cost is$4.97001629; maximum committed is$4.99441254. The original timedout server outcome is unknown; no local paid runner or queued continuation remains. No new request can fit the remaining conservative allowance.
