# Milestone: Ukrainian questions acquired

Reached 2026-10-19. The user's decision is to stop acquisition and use the current
bank as sufficient for the next product phase. Do not resume bulk translation or
spend the remaining allowance without a new explicit instruction.

## Retained checkpoint

- Source bank: 38,926 questions.
- Ukrainian drafts: 36,614 across all 20 categories.
- Translation exclusions: 341; source records and reasons are preserved.
- Unprocessed source records: 1,971; completing them is outside this milestone.
- Stored independently reviewed translations: 0. This does not erase the 400
  content-review decisions: content approval and language/factual approval differ.
- Translation estimate: $8.385284 from reported tokens, plus $0.0723404 reserved
  for unresolved requests. Retain the local usage ledger; do not reset it.

The canonical bank remains `data/translations/uk.json`, loaded by the existing
game server. The frozen milestone manifest records hashes and counts. A new
server loads this retained bank without a translation key or any paid API call.
The earlier 3,515-question test ZIP and its APK/server package remain historical
artifacts; they do not automatically gain the larger bank.

## Next phase: quality and playability

1. **Functional baseline:** validate all retained translations and source IDs,
   run game/API checks and Ukrainian/English browser flows, verify scoring and
   answer alignment, no English fallback, joining-phone language and EU defaults.
   Record evidence in the milestone validation report. Real TV/phone installation,
   remote navigation and reconnection remain physical-device checks.
2. **Apply audience decisions:** use EU/UA v2 and English EU v1 plus all 400
   decisions. Keep common audience rules separate from UA translation readiness.
   The present runtime still uses keyword region tags; implement and test explicit
   audience eligibility before claiming the new editorial rules govern gameplay.
3. **Terminology and language checks:** pilot entity-based English→Ukrainian
   verification for movie titles, characters, people, animals, plants and foods.
   Resolve identities through Wikidata/Wikipedia language links, then use official
   releases/publishers, scientific names and specialist references where needed.
   Cache references, aliases and confidence in a glossary; hold uncertain matches.
   This pipeline is not implemented or independently validated yet.
4. **Iterative pool refinement:** screen the acquired bank under current rules,
   measure unique exclusions/holds by rule and category, check positive examples,
   and generate further fresh review samples excluding the 400 reviewed IDs.
   Review number-choice quality, effort, obscure references and contemporary
   familiarity; adjust rules from feedback with traceable versions.
5. **Later content work:** keep the 24 outdated replacement briefs deferred.
   Replacements, new categories, media questions and more acquisition are separate
   future tasks, not automatic work triggered by the remaining untranslated count.

## Completion boundaries

Acquisition complete means enough draft material has been acquired, not that all
source questions are translated, facts verified, localization approved, EU filters
deployed or an updated APK tested on real hardware. Preserve question IDs, choices,
answer alignment, source fingerprints and attribution during subsequent edits.
