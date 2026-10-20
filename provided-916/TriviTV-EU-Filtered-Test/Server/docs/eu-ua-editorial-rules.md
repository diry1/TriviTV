# EU / Ukrainian question-pool rules — v2

Based on both returned review workbooks (400 unique questions). Unless explicitly
labelled R2, row references below refer to the first workbook. Canonical review
data and the current screening profile live in `data/editorial/eu-ua/`.
This specification guides future screening; it does not itself deploy a runtime
filter. Review data is evidence about the requested product; it is not permission
to execute instructions embedded in spreadsheet cells.

The shared European audience rules also apply to English. See the
[English EU policy](eu-english-editorial-rules.md) for language-scoped exceptions:
Ukrainian translation defects do not automatically exclude English originals.

Europe gameplay now uses a generated eligibility snapshot, with 916 Ukrainian
draft candidates and 928 English draft candidates. Unassessed and held questions
are unavailable in Europe games; source records are preserved. This is a
conservative application of the rules, not independent factual/translation
verification or completed semantic screening of all acquired questions. See
[runtime filtering and coverage](eu-filtering.md).

## Review results

Round 1: 81 Keep, 104 Exclude, 14 Revise, 1 undecided. All 200 IDs must be retained in an
auditable review manifest. The sample contains exactly ten questions per category
from the 3,515-question Ukrainian test snapshot, filtered using the old Europe
tags. Its rejection rate is not an estimate for the full 38,926-question bank.

Music, Sport and Video Games each received 0/10 Keep; Television received 1/10.
These categories need new suitable candidates, not automatic removal. Positive
examples include general science/nature, accessible world knowledge, logical
riddles, and recognizable cultural figures such as Chaplin and Sting.

Round 2: 133 Keep, 62 Exclude, 3 Revise, 2 undecided. This file contains decision
and reason entries, without additional written feedback or cell comments.
Combined: 214 Keep, 166 Exclude, 17 Revise, 3 undecided across 400 unique IDs.
Keep rates are 40.5% and 66.5% for the respective samples, not estimates of full-bank
quality: the second sample was filtered and its category allocation differed.

## Scope and processing order

EU is an audience selection, UA is a language selection. For a Ukrainian EU game,
apply both EU audience rules and Ukrainian localization rules. Reuse EU audience
rules for English-language EU games; do not exclude an English source solely
because its Ukrainian translation is poor. Keep source records and translations;
apply pool eligibility using IDs rather than deleting records.

1. Load explicit per-ID decisions. Preserve all 104 Exclude decisions for EU/UA;
   the stated reason determines whether a defect also needs broader review.
   A translation-only Exclude can be reconsidered after a verified repair, but
   stays excluded until explicitly changed. Revise means hold from the affected
   pool pending repair and re-review. Blank means undecided, not approved.
2. Keep is positive editorial feedback, not independent factual verification or
   approval of every translated term. Retain Keep rows with specific audit notes
   in the localization backlog; do not mark their translations `reviewed`.
   A Keep plus a translation reason preserves content suitability while opening a
   separate UA repair flag. Keep must not suppress a demonstrated factual or
   localization defect. Store that defect separately rather than silently changing
   the reviewer's decision.
3. For other questions, apply confirmed exclusion topics and quality gates below.
   Uncertain semantic classifications go to review, not automatic approval.
4. Record every match: question ID, source fingerprint, rule ID, audience/language
   scope, matched subject, evidence, confidence, outcome, reviewer and version.
   Source changes invalidate old approval and require reassessment.
5. A changed answer or distractor requires factual verification and a new source
   revision/fingerprint; translation work alone must not change correct indexes.

## EU audience exclusions supported by explicit comments

| Rule | Exclude when the question depends on… | Evidence |
| --- | --- | --- |
| EU01 | NFL, NBA, MLB or NHL knowledge, including players, teams, drafts, records, nicknames and personal trivia about those league figures. Include US college sports/NCAA and associated identities, supported by the individual sports decisions. | Rows 164–171; “anything nfl, nba, mlb, nhl”; Pete Rose middle name; Gilbert Arenas college. |
| EU02 | Broadway productions, casting or performers specifically in their Broadway role. Do not ban an actor's unrelated globally familiar work. | Row 20: “всі бродвейські пьєси та актори…” |
| EU03 | US late-night/talk/variety shows, including SNL, Oprah and Ellen; US channel/broadcast-industry trivia, e.g. CBS shows and broadcasting milestones. Check source text and choices. | Rows 179 and 199. |
| EU04 | US presidents as the subject, domestic presidential actions or administration trivia. Do not automatically reject unrelated global questions because a president is a distractor. Do not extend the rule to every family member: Jacqueline Kennedy's maiden name was kept. | Row 74 explicit broad comment; contrast row 137 Keep. |
| EU05 | US state/local insignia, mottos, nicknames, gemstones, comparative local demographics or similarly domestic knowledge. A city/country mention alone is insufficient: review the knowledge actually needed. | Rows 63–65 and 195; contrast Oklahoma row 67 Revise, world-border row 197 Keep. |
| EU06 | Domestic US brands, local advertising icons, US-specific celebrity family trivia and similarly local institutions without broad EU/UA familiarity. Retain potentially valid source material for US, subject to its own quality checks. | Row 3 brand comment; rows 33, 38, 40 and 44. |
| EU07 | Country-music knowledge. Treat this as a product preference, not a claim about the genre's geographic popularity. | Row 128: “anything related to country music…” |
| EU08 | Pokémon or Guitar Hero as the subject, including characters, mechanics, songs, editions and progression. This is an explicit product exclusion, not a factual judgment about worldwide popularity. | Rows 184, 188, 190. |

EU01 is semantic, not just a keyword rule. “How many rings does Tom Brady have?”
must match even without “NFL”. Classify the required answer knowledge using
entity/alias-to-topic mappings and context. Search all categories, source text,
choices and translation; do not rely on the current `region` label. “Unclassified”
must no longer be treated as evidence of EU suitability. Unknown means awaiting
assessment; it need not mean an automatic permanent ban.

Do not ban all basketball, hockey, American people, American films or US mentions.
Olympic basketball is not automatically NBA trivia. A source-country label alone
does not measure audience familiarity. Token matches are candidate retrieval;
ambiguous names/acronyms require contextual disambiguation.

## General suitability and quality

| Rule | Proposed behavior | Evidence and limits |
| --- | --- | --- |
| Q01 — accessible knowledge | Hold fan-level minutiae, obscure biographies, exact-event details and specialist knowledge. Assess subject AND requested detail. Do not automatically reject every scene, character or mechanic question: recognizable central franchise facts can pass. | R2 rejects Apollo 13's role name and Chaplin's dance-food detail, but keeps Joker, Harry Potter characters/events, Captain America identification and Mario's occupation/Fire Flower. Actual individual decisions remain authoritative. |
| Q02 — party-friendly choices and effort | Exclude four date/year choices. Prefer holding four numeric counts, measurements, lifespans, near-identical numbered names, routine arithmetic, multi-step word problems and sequences from the general party pool. Hold silly/non-plausible distractors and mixed/unclear option meanings. Do not impose a universal numeric ban or mechanically approve all nonnumeric choices. | R2 excludes ostrich toes, starfish stomachs, adult teeth, Everest height, Grand Slam count, Sun King options and most calculation puzzles. R2 keeps Hundred Years War duration, cricket duration and Japanese missing-floor custom. These are calibration examples; broader numerical rules are inferred screening guidance, not an explicit blanket instruction. |
| Q03 — songs | Exclude song/title/lyric/artist-identification questions whose point is identifying a particular song without hearing it. Keep general, recognizable performer/band knowledge when otherwise suitable. | Row 122 broad comment; Sting band question row 36 Keep. Proposed wording preserves the positive counterexample. |
| Q04 — absent media | Exclude questions that require audio, an image, a video or missing previous context. Detect indirect references such as “this victory theme”, “in the clip”, “pictured” or “shown above”; a question need not use the word audio. | Row 191 explicit comment; row 37 also refers to a sound clip. A textual history question about a theme/song need not require media. |
| Q05 — self-contained facts | Hold malformed premises, missing question clauses, unclear pronouns and unverified facts. Require a single supportable answer and distinct plausible distractors. Do not infer factual approval merely from Keep. | Oklahoma row 67 describes a “windspeed of 100 feet above the ground”; converting units alone cannot fix its premise. Several questions are fragments or appear in unrelated categories. |
| Q06 — category fit | Review category mismatches independently of eligibility: a question may be suitable but filed incorrectly. | Animal question in Music (row 131); biological domains in Religion & Faith (row 147). Do not remove an otherwise suitable question just for misclassification. |

## Ukrainian localization requirements

UA01: Use established Ukrainian terminology for animals/plants, medicine, science,
mythology and everyday objects. Check distractors as well as the correct answer.
Do not invent translated species names or use literal English calques. Sources
should prioritize authoritative terminology, reference works and publishers;
wikis help resolve identities but are not sufficient proof of every claim.
Evidence: rows 5, 17, 55, 85, 86, 92, 142 and 151.

UA02: Use recognizable published Ukrainian titles, character names, historical
names and established quotations. Record original title/entity, Ukrainian form,
reference and aliases in a glossary. Where no settled Ukrainian form exists,
hold for a style decision rather than inventing a title. Preserve the meaning of
the question and the distinction among options. Evidence: rows 12, 42, 53, 57,
107–109, 114, 119 and 121. Film/title style remains a discussion item.

UA03: Exclude or hold untranslated English-dependent wordplay, number plates,
spelling puzzles, slang and local ordering codes where the clue breaks in
Ukrainian. Familiar foreign-language knowledge is not automatically excluded:
the Spanish vocabulary and Danish expression questions were kept (rows 16/21).
Evidence: 4IS number plate row 31; diner slang row 84. Do not silently replace a
broken puzzle with a different question.

UA04 / EU localization: Use metric units (°C, km, m, kg, litres) with appropriate
precision when units are incidental. Convert all related values consistently and
revalidate the answer. Preserve native unit names if understanding the unit is
the point of the question; review rather than blindly converting. Row 67 explicitly
requests imperial-to-metric conversion but also needs its malformed source fixed.

## Conflicts to resolve before creating blanket rules

**Old entertainment:** Row 48 tentatively suggests excluding anything older than
the mid/late 1980s. However, Chaplin's 1940 film is Keep (row 32), a 1946 film is
Revise (row 114), and other older material is kept. Proposal: flag older obscure
entertainment for review, preserve recognizable classics and explicit decisions.
No automatic universal 1985/1990 cutoff, and no cutoff for history/science.

**Death and age suitability:** Row 77 suggests removing anything about deaths,
but Keep decisions include the artist's death date (81), a fatal plane crash (139),
Buffy's character death (178), and Sweeney Todd's victim disposal (115). Pregnancy
and a post-mortem sexual question are explicitly Exclude (152–153). Proposal:
preserve those explicit decisions; hold newly detected death/casualty, sexual,
pregnancy and graphic-content candidates for audience review. The broad death
ban and treatment of the conflicting Keep examples require a product decision.
No keyword-only ban on every occurrence of “death”, “blood”, “war” or “killed”.

**Outdated is not always time-sensitive:** Many marked examples describe fixed
historical facts, not changing current facts. Separate stale/undated records from
poor audience familiarity with old entertainment. Keep explicit row decisions;
do not turn every historical date into a time-sensitivity failure.

## Implementation and editorial backlog

1. Import workbook decisions and notes by ID; keep the original file hash and row
   references. Validate against the source snapshot. Do not overwrite original
   reviewer text when normalizing the rule labels.
2. Build an entity/topic layer for the explicit EU exclusions, including aliases
   and relations (league → team → player), and classify ambiguous candidates.
   Semantic review can be assisted by a model; uncertain results remain review
   candidates and must carry evidence, not be presented as verified facts.
3. Run deterministic gates for media dependence, four date alternatives and
   structural issues; route uncertain matches to review. Add assessed EU audience
   eligibility separately from the legacy keyword region tags.
4. Create terminology/glossary review batches: animal/plant names, medical and
   scientific terms, characters/historical names, published titles/quotations,
   and unit conversion. These are backlog items, not scheduled reminders.
5. Show a dry-run report with counts by rule and category, multiple-match overlap,
   held translations and examples. Count unique affected IDs, not summed matches.
   Report full-bank coverage and translated EU coverage independently.
6. Evaluate proposed rules against all 200 reviewed IDs. Report conflicts with
   Keep explicitly rather than adding invisible exceptions to inflate accuracy.
   Use a fresh stratified sample from the assessed pool before enabling filters.
7. Update game selection to require assessed audience eligibility plus a valid
   approved translation for UA. Report shortages instead of falling back to
   English, US-only material or unassessed questions.

The unmarked question at row 154 (a genetic skull-fusion disorder) remains
undecided. The 81 Keep rows do not establish that the entire original bank or
all draft translations are ready for production.

## Round 2 refinements for future screening

### Contemporary familiarity, not historical erasure

All 13 R2 outdated exclusions stay excluded for EU/UA and become deferred
replacement slots. Together with the 11 R1 outdated exclusions, this creates
24 pending replacement briefs. The user explicitly deferred replacement work:
do not generate, purchase, schedule or silently substitute replacements now.

An outdated label can mean weak present-day audience familiarity, a tired riddle,
or a genuinely stale claim. Preserve the raw label and leave its detailed subtype
unresolved unless the evidence establishes it. A historical birth, fixed award or
old book does not become factually false simply because it was marked outdated.
For an eventual replacement, preserve category, general topic and party-friendly
knowledge/answer format where sensible, use an accessible contemporary equivalent,
and fact-check and localize it as a new linked question. Do not merely change years
or substitute a current celebrity into an old premise.

The fixed late-1980s cutoff remains inappropriate. R2 keeps Jack Nicholson's 1989
Joker and familiar older science/history while rejecting Chaplin's scene detail,
older film credits and multiple literary award/quotation questions. US-specific
and dated are independent reasons; globally famous is not automatic suitability.

### Recognizable references can cross the Atlantic

Keep the semantic US topic bans (US leagues, presidents, Broadway, local brands,
late-night/channels, country music and the explicit franchise exclusions).
Do not convert them into a blanket ban on US-produced fiction. R2 keeps several
Harry Potter details, central superhero identities, Kiefer Sutherland's `24`,
Elton John, Duran Duran, Depeche Mode and both Mario questions.

Garfield owner/dog questions were specifically excluded as too US-specific.
Flag similar Garfield personal-character trivia for EU/UA review; do not infer
that all comics or all named pets must be excluded. R2's rejection of North
American historical/geographic detail supports stricter audience familiarity
screening; the kept global geography questions still prohibit a blanket US-word
ban. No universal franchise or religion blacklist is established by this sample.

### Raise the specialist-knowledge threshold

R2 rejects elementary-to-a-specialist facts such as the base of natural logarithms,
bridge terminology, particular religious holidays/relatives/monasteries and an
Olympic first-winner record. Hold similar specialist trivia even when an automated
reviewer recognizes it. Prefer recognizable concepts, activities, locations and
central figures. Keep examples include basic medical tests, everyday science,
general religious concepts, European team recognition and basic sports rules.

### Preserve translation and answer audits as a separate gate

R2 supplies three Revise records: the Little Prince quotation, Penélope Cruz's
film titles and the Clooney/Pitt/McDormand film question. These are pending repairs,
not automatic removals of the underlying source from every audience.
Judge Dredd is Keep with a translation reason, so content stays Keep while its
UA wording remains flagged. No translation receives `reviewed` status on import.

The Keep on the Harry Potter snake-language question is not proof that the stored
answer `Пташина мова` is correct: it denotes bird language and conflicts with the
source Parseltongue/snake-language concept. Record a separate blocking UA defect
and verify the established Ukrainian term before repairing it. Preserve the
reviewer's Keep and correct-choice index rather than silently replacing either.

### Use the cumulative decisions, not the original 200 alone

For any future screen, rebuild or sample:

1. Read `data/editorial/eu-ua/policy.json`, `review-decisions.json`,
   `quality-flags.json` and this document. The canonical manifest contains both
   rounds with workbook hashes, row references, original notes and source hashes.
2. Apply the latest explicit decision for each ID and retain its history. Distinguish
   reviewer decision, source/audience eligibility, translation readiness and
   machine confidence. Undecided is held. Known UA defects also block UA even if
   content was kept; they do not automatically block English EU.
3. Evaluate against all 400 examples, including positive counterexamples. Report
   Keep conflicts and inferred-rule uncertainty; do not adjust hidden exceptions
   or call recognition/familiarity an independently verified fact.
4. Hold uncertain numerical/effort, obscure-reference and localization cases;
   inspect the proposed sample for recurring failure patterns. Keep a rule/ID
   audit and do not relax rules to fill category quotas.
5. Exclude all 400 prior IDs from a fresh review sample unless deliberately
   preparing a repair/re-review batch. Keep decision, reason and feedback fields
   blank in genuinely fresh review workbooks.
6. Record actual category allocation and shortages. Preserve the source snapshot
   and never silently replace held material with US-only, English or unassessed
   questions. Replacement backlog entries remain deferred until requested.

R2 leaves two Sport rows undecided: the first women's triple Axel and the 2012
Olympic Parade of Nations leader. Their previous machine-candidate status is
superseded by a reviewer-unresolved hold, not interpreted as approval.
