# Luna balanced classification — completed 2026-10-22

**2,500 unique English master questions, exactly 125 per each of 20 source categories.** Shuffled within each category and interleaved by category round; no top-to-bottom slicing. Ukrainian drafts joined by original ID: **2,432**. All selected records were assessed; **6 retain unresolved topics**, rather than forced guesses.

[Open searchable bilingual review](review.html) · [Bilingual CSV](questions.en.csv) · [Full English JSON](questions.en.json) · [Summary](summary.json) · [Validation](validation.json)

## Scope and spending

User authorized Luna and up to $5. Model: `gpt-6-luna`, Standard Responses processing, low reasoning, structured JSON, no web/API tools, no storage of responses on the API (`store:false`). Raw responses and evidence are kept locally for audit. Requests cap output tokens and reserve a conservative input/output cost before submission; uncertain or rejected requests would retain their reservation rather than silently retry.

The smallest category is Brain Teasers with 125 questions. Strict equal representation across all 20 categories therefore caps this pass at 2,500 unique questions. We stopped there instead of buying duplicate classifications or silently overrepresenting larger categories.

- **Calculated token cost, including calibration: $0.3131.**
- **Unused portion of the $5 allowance: $4.6869.** This is unused authorization, not a statement of the account's current balance.
- **131 API requests:** 125 production requests of 20 questions, plus six calibration requests. All completed and accounted for; no live/background paid jobs remain.
- Published USD rates per million: input $0.10; cached input $0.01; cache writes $0.125; output (including reasoning) $0.50. Cache writes and reasoning tokens are included in ledger.json. Cost is derived from reported token usage and those rates, not an invoice/tax total.
- Compact returned labels and prompt caching made the actual cost much lower than the earlier conservative estimate.

## Classification results

- **10,021 validated high-confidence model tag assignments**; confidence is model judgement, not calibrated truth.
- Medium/low confidence, unsupported evidence, missing entity spans and uncertain eras remain unpublished proposals. **1,358 records have proposals; 468 have model/review notes.**
- **12 selected records already had reviewed pilot tags.** Those tags were retained in preference to model predictions; 11 differences are saved in manual-conflicts.json. They were not silently merged into competing labels.
- A content pass added **14 evidence-backed topic labels** under a separate owned source, preserving machine output as originally received. Six records remain without a definite topic because context or vocabulary is insufficient.
- Main/master still contains religion and US-specific material. Semantic tagging changes metadata only, not eligibility.

The fixed Luna prompt used vocabulary v2. Vocabulary v3 adds three gaps found during review: **radio**, **animation**, and **people** for personal biography/interview questions. Only the separately recorded content-reviewed additions use v3; prior Luna responses are not misrepresented as having used it.

## Standalone exports

| Export | Questions | Meaning |
| --- | ---: | --- |
| questions.en.json | 2,500 | Balanced complete-master selection, all 20 categories, semantic tags and original source attribution |
| translations.uk.json | 2,432 | Linked acquired drafts; original methods, source hashes and statuses retained |
| questions.eu-en.json | 1,714 | Selected IDs that already pass the current EU English policy |
| questions.fun-en.json | 1,150 | Selected IDs already in the English Fun candidate pool |
| questions.fun-uk.json | 1,036 | Selected Fun IDs with Ukrainian drafts, excluding the same known translation holds used for the existing Ukrainian Fun build |

Only the complete-master selection is exactly category-balanced. Filtering removes varying numbers by category, including religion. The CSV contains both languages, original correct indexes, semantic tags and dashboard links. Backend tags remain backend-only; these files have not replaced runtime data or been put into an APK.

## Calibration and limitations

The 50 reviewed examples were classified without their expected answers/tags being supplied. Mean topic-set Jaccard overlap was **90.3%**; mean all-tag overlap was **65.1%**. This is comparison with the same earlier reviewer, not an independent accuracy benchmark. Broad topics were more consistent than narrow translation/audience facets. Luna missed some reviewed title/answer-choice localization risks; no-risk-tag is not translation approval. No outside factual/title reference verification was performed.

The initial calibration exposed bare tag values; the family-prefixed schema was corrected before production. Duplicate same-kind labels are deduplicated while raw output remains available. Non-exact evidence is withheld. Ambiguous cases such as unspecified Junkies/Alfred/Hoops references are not forced into an invented medium/category. See unresolved-topics.json.

## Integrity and repeatability

All 38,926 main records retain identical question text, choices, correct indexes, categories and non-semantic tags. EU English remains 27,948; screened EU Ukrainian remains 799; Fun membership unchanged. Frozen sources, acquired translations, existing human decisions, game/APK and public deployment are unchanged.

Eight classifier checks and six master integrity tests passed; the earlier pilot check passed. Source-owned tag maps exactly match merged semantic tags. Review UI tested for pagination, category/tag/Fun filtering, desktop/mobile overflow and browser errors. Local dashboard was restarted and verified to serve the new tags.

- `manifest.json`, `selection.json`: frozen input selection and context fingerprints.
- `responses/`, `ledger.json`: raw results, token usage and spending reservations. No key or authorization header is stored there.
- `audit.json`, `topic-review.json`, `manual-conflicts.json`: machine evidence, separate content additions and retained human differences.
- Active contributions: semantic-luna-balanced-v1.json and semantic-luna-topic-review-v1.json under question-bank/tag-sources/; pilot contribution preserved.
- `classify.py prepare|calibrate|run|export`: resumable workflow; **calibrate/run can spend money**, prepare/export are local. Do not modify the frozen prompt/selection during a paid run.
- The key is stored only in ignored .env.local and was created with the selected seven-day expiry. No new top-up was made.

Next expansion can use the observed costs and review gaps; this pass has intentionally stopped at the equal-category limit.
