# English EU question-pool policy — v1

Audience: Europe. Question language: English. This is the English-language
projection of [EU/UA rules v2](eu-ua-editorial-rules.md), using the same 400
reviewed source IDs and the user's instruction to exempt Ukrainian translation
issues. The policy applies to the full English source bank, independently of how
many questions have Ukrainian translations.

## Shared audience rules

Carry over EU01–EU08 and Q01–Q06 from the EU/UA specification, including its Round 2
refinements and positive counterexamples:

- Exclude US-league and US college-sports knowledge by subject, team and player,
  not just acronyms. Keep broadly familiar global sports and European references.
- Exclude Broadway trivia, US talk/late-night and channel trivia, US presidents,
  US domestic brands/state minutiae, country music, Pokémon and Guitar Hero as
  specified. Do not exclude every American person, place, film or cultural work.
- Hold obscure biographies, specialist knowledge and fan-level minutiae; allow
  familiar central facts such as recognizable Harry Potter and Mario references.
- Apply party-friendly choice/effort rules: four dates are excluded; numerical
  guessing, similar names/counts, repetitive choices, calculation-heavy puzzles
  and routine arithmetic are generally held. Preserve reviewed numeric exceptions.
- Exclude song-identification/detail questions dependent on audio and questions
  needing unavailable media. Retain suitable general musician/band knowledge.
- Hold malformed or ambiguous source English, unsupported facts and incorrect
  answers, non-distinct distractors, missing question clauses or category mismatch.
- Preserve the same contemporary-familiarity judgments. Do not treat every old
  fact as false, ban all history, or introduce a universal year cutoff.
- Keep the unresolved age/death-content policy as a review hold for new uncertain
  material, with explicit per-question decisions retained separately.

EU09 — units: retain the European preference for metric units when units are
incidental. This is an audience requirement shared with Ukrainian, not a
translation defect. Preserve named units when understanding the unit is the point
of the question. Verify any conversion and all affected choices. Do not silently
rewrite canonical English text or answer keys.

## Ukrainian-only restrictions that do not transfer

Do not block an English question because of an incorrect Ukrainian animal/plant
or medical term, a mistranslated title, quotation or character name, transliteration,
Ukrainian grammar, or a semantic error introduced by translation. Do not require
a Ukrainian translation, Ukrainian glossary approval or `reviewed` Ukrainian status.
Use recognizable original English titles and correct English names. A title's
Ukrainian distribution name is irrelevant to the English pool.

English wordplay may be eligible if it works in English and is understandable to
the intended European audience. Do not apply UA03's translation-breakage hold
automatically. Local US slang, licence-plate conventions and dialect-dependent
clues still require audience assessment. English EU is not a UK-only audience.

Poor source English, invented names, ambiguous quotations or a false answer are
shared quality problems. A Ukrainian translation can expose an underlying source
defect; exempt only the translation defect, not the source problem.

## Project the existing review decisions by reason and scope

The original reviews are preserved in `data/editorial/eu-ua/review-decisions.json`.
English projections live in `data/editorial/eu-en/review-decisions.json`. They are
derived decisions, not new human approvals of an English review sample.

| Original review | English EU treatment |
| --- | --- |
| Keep | Carry over content suitability. Still subject to factual/source-quality gates. Ignore separate Ukrainian-only repair flags. |
| Exclude for shared audience/content/choice/outdated reasons | Remains Exclude. |
| Revise for a shared reason | Remains Hold pending the shared repair/review. |
| Exclude or Revise only because of translation | Remove the inherited translation block; reopen for English/shared-rule screening. Do not automatically promote to Keep. |
| Mixed translation and local-audience concerns | Remove translation concern, retain a documented audience Hold or Exclude where supported. |
| Blank / undecided | Hold; do not infer approval. |

The Dreamgirls row (R1 row 12) has no dropdown reason but explicitly discusses
translated film titles; treat it as translation-only for projection. The Oklahoma
row (R1 row 67) requests metric units and also has a malformed source premise;
it remains held in English. Ukraine's Christmas-tree custom (R1 row 196) is a
niche-content Revise, so it also remains held.

Examples of exceptions:

- Judge Dredd remains content Keep in English; its Ukrainian tense/wording flag
  does not block English.
- The Little Prince quotation can be reconsidered in its original English form,
  but source quotation accuracy and the requested character knowledge still need
  checking under the shared rules.
- The Harry Potter snake-language question remains content Keep in English;
  the erroneous Ukrainian `Пташина мова` has no effect on English Parseltongue.
- The `4IS` number plate and US diner-order slang remain held for audience fit,
  based on the review's explicit local/UK/UA concerns, despite their translation
  label. Readability in English alone is insufficient.
- A faulty Ukrainian species name does not prove the English distractor is valid:
  use English reference sources when the underlying species identity is uncertain.

## Future screening and review workflow

1. Read `data/editorial/eu-en/policy.json`, the shared EU/UA v2 rules, this document
   and the English projected review manifest. Preserve raw user decisions and their
   workbook/row/source-hash provenance.
2. Screen the complete English source set against shared audience/quality rules.
   Do not restrict it to the 3,515-question translated snapshot or to future UA
   translation coverage. Existing keyword-only `region` tags are insufficient.
3. Reassess translation-exempt questions for remaining shared rules. Record rule,
   matched subject, scope, evidence and confidence per ID. Unknown is held.
4. Require English source quality and EU suitability, not Ukrainian readiness.
   An English Keep is not an independently verified factual answer.
5. Preserve all 24 outdated replacement slots as deferred shared-EU backlog items.
   Later equivalents should serve both language variants when possible; do not
   generate replacements as part of setting up this policy.
6. Exclude the 400 reviewed IDs from a fresh sample unless explicitly preparing
   English re-review of the translation-exempt cases. Clearly label that kind of
   re-review and do not count prior UA content decisions as new English feedback.
7. Keep feedback fields blank in fresh review sheets, include original IDs and
   correct choices, report category shortages and inspect the sample. Do not relax
   filters or claim an unscreened bank is ready merely to reach 200 questions.

Europe gameplay now enforces the generated `data/editorial/eu-eligibility.json`
snapshot. Every source ID has a decision, but semantic evidence still primarily
covers the earlier 3,515-question screening and 400 human reviews. Unassessed IDs
are held rather than admitted on keyword absence. English currently has 928
candidate questions. The full 38,926-question source bank is preserved; US gameplay
retains its prior region filtering. See [runtime filtering](eu-filtering.md).
