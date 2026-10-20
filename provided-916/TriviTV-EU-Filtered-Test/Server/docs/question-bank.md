# OpenTriviaQA question bank

TriviTV now uses **only OpenTriviaQA**. The 56 original starter questions were removed from the runtime bank. No questions or images from Wikidata, Commons, OpenTDB or paid APIs are included.

## Snapshot and license

- Source: [OpenTriviaQA by its contributors](https://github.com/uberspot/OpenTriviaQA).
- Pinned revision: `dcc1cdf36c2985ed5c849d1f2265c5041ffcdfb9`.
- Snapshot date: 2026-10-16.
- Source records: **49,716**.
- Adapted four-choice questions: **38,926**.
- Exact duplicate records merged: 21.
- Excluded records: 10,769.
- Source and adapted question data: **CC BY-SA 4.0**, with attribution and applicable share-alike obligations. The full license and upstream README are retained in `data/opentriviaqa/`. The app links its Credits page in the footer, including source, changes, license and downloadable data.

This is structurally validated community content, **not an individually fact-checked or calibrated bank**. Source answers, older references and editorial quality still need review.

## Source-based categories

Twenty topic groups are available in both modes. The category panel is collapsed by default for quicker TV setup. Its labels map directly to the source filenames through `data/opentriviaqa/config.json`.

| Category             | Questions |
| -------------------- | --------: |
| Animals              |       802 |
| Arts & Humanities    |       871 |
| Brain Teasers        |       125 |
| Celebrities          |     2,461 |
| Entertainment        |       211 |
| General Knowledge    |     6,838 |
| Geography            |       710 |
| History              |     1,323 |
| Hobbies              |       976 |
| Kids Trivia          |       545 |
| Literature           |     1,038 |
| Movies               |     3,465 |
| Music                |     4,346 |
| People               |     2,221 |
| Religion & Faith     |       483 |
| Science & Technology |     1,888 |
| Sport                |     2,299 |
| Television           |     4,143 |
| Video Games          |       418 |
| World                |     3,763 |

The `newest` and `rated` files are treated as collections rather than extra subjects. Their questions map to General Knowledge unless an exact duplicate in a topic file supplies a better category. All original source category references are preserved; `rated` is not interpreted as a difficulty rating.

## Regional targeting and difficulty

OpenTriviaQA supplies **neither Europe/US audience labels nor difficulty ratings**.

Prompt keyword rules currently identify 2,818 Europe-cued and 2,944 US-cued questions. The remaining 33,164 questions are explicitly **Unclassified**, not falsely called globally relevant. Selecting a region excludes explicit opposite-region cues and shares unclassified content between both audiences. These automatic cues can be imperfect; they are not reviewed cultural targeting. Choice distractors are not used for classification. Language references such as “English” and ambiguous mixed-region prompts are not enough by themselves.

All questions have `difficulty: null`. Millionaire retains its fifteen-step points ladder, lifelines and checkpoints, but **cannot promise increasing difficulty** until editorial ratings exist. The selection engine supports source ratings in the future and currently draws from the unrated pool.

## Import and reproducibility

Play uses the committed `data/opentriviaqa/questions.json` snapshot, not a live external API. No extra runtime npm dependencies, API key or Internet connection are required. Correct answers stay server-side until their reveal stage.

```sh
npm run bank:import
npm run test:bank
```

Maintenance requires Python 3.10+ (the cloud uses 3.12). The importer reads the retained original files from `data/opentriviaqa/source/`, checks their pinned SHA-256 hashes and the source license, and deterministically builds questions, manifest and rejection ledger. `--check` verifies the retained outputs without rewriting them. Raw bytes are preserved across Git checkouts using `.gitattributes`.

Records retain a stable ID, original source categories, source filename/record/line, upstream revision, license, normalization review status and regional method. Normalization decodes HTML entities, strips markup, normalizes whitespace, keeps the source's correct answer and three of its supplied distractors, and never invents answers. Exact normalized prompt duplicates merge their provenance; conflicting answer keys are excluded.

### Exclusions

| Reason                      | Records |
| --------------------------- | ------: |
| conflicting-correct-answers |      10 |
| duplicate-choices           |      29 |
| fewer-than-four-choices     |   6,617 |
| invalid-source-encoding     |      31 |
| missing-media               |      20 |
| position-dependent-options  |   2,248 |
| time-sensitive              |     191 |
| tv-length                   |     377 |
| unparsed-lines              |   1,246 |

These checks reject fewer-than-four choices (including true/false), ambiguous position-dependent options such as “all of the above”, corrupt encodings, prompts requiring unavailable media, obvious changing-time references, overly long TV text and malformed/conflicting records. They cannot establish factual accuracy. Separate importer tests cover those cases, source tampering, Unicode, deduplication, correct-answer preservation and repeatability.

## Next editorial work

Europe games now enforce the [generated eligibility snapshot](eu-filtering.md).
Semantic assessment is not complete across the full bank: unassessed records are
held. Raw source and translation inventories above count acquired material,
not the smaller currently playable Europe pools.

For EU audience selection and Ukrainian localization, use the current
[EU/UA editorial rules](eu-ua-editorial-rules.md) and cumulative review data in
`data/editorial/eu-ua/`. Read these before future filtering or review sampling.
For the same European audience playing in English, use the
[English EU policy](eu-english-editorial-rules.md) and its scoped projections in
`data/editorial/eu-en/`; Ukrainian translation-only issues do not block English.
Individual review decisions and translation-quality flags are separate; outdated
exclusions have deferred replacement briefs rather than generated substitutes.

Review a representative sample per category, correct factual errors with cited references, add audience tags and calibrate easy/medium/hard ratings through playtesting. Corrections to this adapted question content keep the bank's CC BY-SA notices. There are no licensed picture rounds in this text-only source import.
