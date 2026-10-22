# Semantic tagging — vocabulary and pilot

Drafted 2026-10-22. Step 2 completed: [50-question pilot report](pilot-v1/REPORT.md) and [bilingual review](pilot-v1/review.html). Applied 296 semantic assignments to those 50 master IDs only. Vocabulary v1 is preserved; vocabulary-v2.json records pilot refinements. No API run or bulk classification has started. Semantic metadata is separate from existing regex/filter tags.

## What gets tagged

| Family | Purpose | Examples |
| --- | --- | --- |
| Topic | What knowledge is actually tested; multiple topics permitted | movies, actors, animals, geography |
| Subject | More specific reusable concept | Oscars, film awards, habitats, polar regions |
| Form/style | How the question works | humor, wordplay, negative question, number recall |
| Era | Relevant era of the knowledge being asked | 1990s, with award-year/work-release role in the audit |
| Audience | Required regional or specialist familiarity | US-specific, specialist knowledge |
| Ukrainian translation risk | What needs localization attention | wordplay, localized title, scientific terminology |

`vocabulary-v1.json` is the initial controlled list. Proposed new subtopics go into a vocabulary-expansion queue with example IDs; do not create thousands of one-off tags. Named entities can be stored separately in the audit without each becoming a tag. There is no obligation to assign a risk or audience tag to every question.

## Examples supplied by the user — illustrations, not bank records

1. Tomato / “catch up” joke: **food, humor, wordplay**, plus **Ukrainian translation risk: wordplay**. Translating the words literally may not preserve the joke. No replacement joke or answer should be invented during tagging.
2. Best Actress Oscar in 1999: **movies, actors, film awards, Oscars, 1990s, award-winner recall** (represented initially as event-detail). Record that the era refers to the award/event, not the actor's birth or all films they made. Ceremony year and film eligibility year may differ; ambiguity needs a note rather than an invented resolution.
3. Animal not living in the Arctic: **animals, geography, habitats, polar regions, negative question**. Check the full prompt and all alternatives before proposing an ambiguity flag. The mention of a dingo does not by itself require a translation-risk tag or factual correction.

## Classification boundaries

- Read the full prompt, all four choices and canonical answer index. Tag the knowledge required to answer, not every incidental word or distractor. Use linked Ukrainian text where available to identify localization concerns.
- Do not blindly copy the source category as semantic truth. Preserve it independently; a source Music question about an animal can receive animal tags.
- Keep core topical tags on the English master by stable ID. Ukrainian risk tags are language-scoped, and never automatically disqualify the English question.
- Era tags require relevant evidence. An actor born in 1960 can be the subject of a question about a 2015 film. Missing dates do not imply modernity. Outside knowledge that is uncertain or unsupported belongs in review.
- A title-localization risk says an established Ukrainian title may need checking; it does not assert that the current title is wrong. Scientific terminology is not inherently a mistranslation.
- Absence of translation-risk tags is not proof that the translation is correct. Fact-checking, translated-title verification, readability and difficulty remain separate tasks.
- Avoid low-value generic tags like “question”, “trivia”, “fun” or “general knowledge” on every record. Most records should need only a handful of tags; do not fill tag quotas.
- Metadata changes do not alter question text, answer order, correct indexes, review decisions or pool membership. Any later exclusion rule should explicitly consume selected tags.

## Audit and persistence

Each classification will retain question ID, source fingerprint, translation fingerprint when examined, vocabulary version, tag source, evidence excerpt, ordinal confidence (high/medium/low), and unresolved issues. Confidence is a judgement, not a calibrated probability. Preserve uncertain proposals separately from definite tags. New source/translation content invalidates stale matching assessments.

Use source-owned `custom:semantic:*` tags, compatible with the existing tag merger. Rebuilding a semantic source removes withdrawn assignments without deleting manual or other-source tags. Do not place example tags in the active `tag-sources/` directory during this vocabulary step.

## Next bounded step

Classify 50 actual questions: cover all 20 original categories plus targeted examples of puns, dates, negative questions, US-specific entities and localized titles. Include known Keep/Exclude counterexamples to expose conflicts, without treating that calibration set as a fresh accuracy benchmark. Report sample tags, evidence, uncertainty and vocabulary gaps before running the full 38,926-record bank. API/provider selection and any paid run remain a later decision.


## Added entity and location tags — 2026-10-22

- **Entity kinds:** movie titles, book titles, brand names and historical-figure names. Store the actual detected surface text and its role (prompt/correct option/distractor) in the audit; a kind tag does not mean the Ukrainian rendering is verified or wrong. Brand names are not automatically US-specific.
- **Location mentions:** USA, Europe, Asia, Africa, plus North America, South America, Oceania and Antarctica so the vocabulary covers the remaining regions. Match places in the prompt and every option, including distractors. Examples: Michigan → USA and North America; Lake Victoria → Africa. This is a mention tag, not an automatic audience exclusion.
- Resolve ambiguous places by context, rather than guessing: Georgia may be the country or US state, Washington a person/place, and Victoria a person/lake/city. Keep unresolved entities in the audit. Do not assign a location just because an incidental person/brand is associated with that region.
- Separate Europe/Asia and transcontinental cases explicitly; multiple location tags may be appropriate. Detailed geographic disambiguation can be added incrementally after the pilot.


## Completed pilot — 2026-10-22

40 deterministic category-stratified questions (2 per each of 20 categories), plus 10 targeted cases; 48 linked Ukrainian drafts. 296 assignments / 84 distinct tags, with unpublished proposals on 16 records. Source-owned contribution: `question-bank/tag-sources/semantic-pilot-v1.json`; full evidence and fingerprints in `pilot-v1/audit.json`. No eligibility or answer changes. Vocabulary v2 adds philosophy/comics/business, missing-word, TV/game/song title kinds, proverb risk and consistent screen-characters. See the report for boundaries and remaining gaps; this sample is calibration, not an independent accuracy estimate.


## Luna balanced pass completed — 2026-10-22

See [run report](luna-balanced-v1/REPORT.md) and [searchable bilingual review](luna-balanced-v1/review.html). 2,500uniqueEnglishquestions,125per20categories;2,432linkedUA drafts. CalculatedAPI token cost $0.3131 of$5ceiling, allcalls complete. Modelusedv2; current vocabulary-v3.json adds people/radio/animation for separately reviewed cases. Humanpilot tags preserved, noeligibility changes. Independent content/title verification remains separate;6unresolvedtopics held for review.


## Latest continuation — 2026-10-22

[Searchable review](luna-expand-v1/review.html) · [Run report](luna-expand-v1/REPORT.md). 37,796of38,926questions assessed/tagged;19categoriescomplete,1,130GeneralKnowledge IDsremain. CumulativeknownAPI token cost$4.9700 plus$0.0244uncertain-callreserve, maximumcommitted$4.9944 under same$5authorization; paidrun stopped. CombinedEnglish/EU/Fun/UAexports retainexistingpolicies and acquired translationprovenance. Source-owned semantic-luna-expand-v1 mergedintomaster;no eligibility orruntimechange.
