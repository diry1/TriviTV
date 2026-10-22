# Backend editorial question bank

`questions.json` is the complete English editorial master: all 38,926 adapted questions, with a `tags` array on every record. `questions.csv` exposes the same tags as a JSON array in a **tags column**, alongside ID, category, prompt, four choices and zero-based correct index. All original question fields, order, IDs and answers are preserved.

The frozen supplied import stays under `provided-916/`. This enriched master is the place to filter and export future question groups. It is backend/editorial data: do not copy tags or provenance into player payloads or UI. No current website, APK or game bank is changed by rebuilding this master.

## Tag conventions

- `EU`: eligible for at least one editorial EU draft pool. Use `EU:en` or `EU:uk` when selecting a language. English EU is the full English bank minus audience/content filters, including unassessed survivors; Ukrainian EU membership still identifies screened drafts. Neither implies factual verification. They describe the latest editorial pool, not the unchanged deployed game.
- `pool:eu-uk:potential-unassessed`: survived the preliminary filter but has not passed semantic screening; deliberately has no `EU:uk` tag.
- `screen:eu:uk:hold`, `screen:eu:en:exclude`, etc.: scoped outcome. A hold is not a confirmed rejection.
- `rule:eu:uk:Q02`, etc.: exact saved screening-rule IDs.
- `reason:eu:uk:numeric-choices-or-calculation`, `reason:eu:en:us-sports`, etc.: human-readable filtering reasons. Reasons describe recorded flags, not independently established defects. Heuristic word-meaning matches remain review candidates.
- `review:eu:uk:keep`, `exclude`, `revise`, `unreviewed`: original human-review decision, separate from current eligibility.
- Additional useful metadata: `category:movies`, `source:opentriviaqa`, `translation:uk:draft`, `translation:uk:missing`, `difficulty:unrated`, `verification:not-fact-checked`.

Religion has no EU membership in either language. Ukrainian-only vocabulary/translation issues do not remove English membership. Movie/book title verification is still pending; no tag claims a title or translation has been verified.

## Multiple tag sources and removal

Rebuild with `python scripts/build-question-tags.py` from the project root. Validate with the same command plus `--check`. The builder refreshes the preliminary Ukrainian screening and reads the canonical per-language decisions; English membership follows a subtractive policy: lack of a filter match allows inclusion, but does not imply semantic approval. Ukrainian screened membership remains conservative. Generated tags are rebuilt from current inputs, so removing an ID from an eligible pool removes its language EU tag; `EU` disappears when neither language remains eligible. Stale output can be detected with `--check`.

Additional groups/tools can each maintain a JSON file in `tag-sources/`, shaped as `{ "question-id": ["custom:topic:space", "custom:collection:party"] }`. Use real IDs. Unknown IDs and reserved/generated tag names are rejected. All source contributions merge into the main record by ID. Remove a tag from its source file to withdraw that contribution; a tag supported by another source remains. Generated membership tags cannot be added manually. Future automated sources should be integrated in the builder with their own source ownership and evidence.

`tag-provenance.json` retains source ownership, prior decision evidence and preliminary filtering status per ID. `tag-summary.json` contains tag counts and the frozen source hash. Generated output must not be manually edited. Dashboard edits persist separately in `editorial-overrides.json`; `editorial.py` applies category/status/personal-tag overrides after source contributions merge. Category edits update category/difficulty-default tags; manual holds/exclusions remove the affected language's EU membership and potential-pool tags. General EU membership remains if the other language is still included. Religion remains excluded from EU by policy; original imported records are preserved. Each override retains before/after history. Rebuilding the master preserves these edits.

Content remains OpenTriviaQA contributor content under CC BY-SA 4.0. Original source revision, license and per-question attribution are preserved in every JSON record. Original license and attribution: `../provided-916/TriviTV-EU-Filtered-Test/Server/data/opentriviaqa/`.
