# Fun Bank v1

A separate English pool derived from the complete 38,926-question master. Ukrainian translations are linked by stable question ID; they are not independently approved by inclusion here. Main, US, EU, UA and the live game/APK are retained.

First pass, 2026-10-22:

- **17,315 English candidates**, with **15,873 linked Ukrainian drafts**.
- **8,617 exclusions** under the requested gates.
- **12,994 review holds**, mostly culture references with unverified eras. Holds are not permanent rejections.

## Requested gates

1. Remove the Religion & Faith category.
2. Remove date/year answer questions. Numeric quantities are not automatically dates; numeric-looking titles and ambiguous alternatives can be held.
3. Remove US-specific league/player/team, presidential, state/local and related audience subjects using saved EU flags and explicit entity/context rules. Ambiguous place names such as Georgia are held unless context resolves them.
4. Remove cultural references explicitly dated **1950–1989**. This applies to cultural works/eras, not general historical events. Birth dates alone do not establish a work's era. Undated culture references are held for entity/era verification instead of admitted by absence of a year. This does not invent a ban on all pre-1990 history or all pre-1950 classics.

These are conservative rules and retrieval patterns, **not exhaustive semantic classification**. US-specific entities and cultural references without recognizable cues can still escape detection; candidates are not fact-checked. Culture categories are sparse because unverified-era questions are not included. Newer titles, years and answers also require factual review before final acceptance.

## Files and tags

- `questions.en.json` / `questions.en.csv`: candidates only; source IDs, choices, answer indexes and provenance retained.
- `translations.uk.json`: matching acquired Ukrainian translations, joined by ID.
- `decisions.json`: all source IDs with outcomes, matched rules and evidence.
- `summary.json`: counts, categories and overlapping rule matches.

Full-master tags use `custom:fun-bank:candidate`, `custom:fun-bank:exclude`, `custom:fun-bank:hold`, plus `custom:fun-reason:*`. Membership and reasons are isolated to this collection; excluding a Fun question does not remove its EU tag or delete it from the master. Rebuilding the source-owned tag contribution withdraws stale Fun membership automatically.

Rebuild: `python scripts/build-fun-bank.py`, then `python scripts/build-question-tags.py` to propagate tags into the master/dashboard. Restart the local dashboard after rebuilding. The Fun tab shows English candidates; linked Ukrainian text is visible in question details.

Content: OpenTriviaQA contributors, pinned revision `dcc1cdf36c2985ed5c849d1f2265c5041ffcdfb9`, CC BY-SA 4.0. Retain source and translation attribution/license on export.

## Suggested extra filters — not applied yet

- **Fan/biographical minutiae:** episode titles, supporting-character relatives, celebrity family trivia and minor credits.
- **Numeric guessing:** exact heights, populations, distances and records when alternatives differ only slightly.
- **Long reading burden:** long prompts or sentence-length options; tag separately and consider reduced frequency rather than blanket deletion.
- **Missing media and wordplay:** questions requiring an absent clip/image; language-dependent spelling/puns for translated variants.
- **Weak distractors:** near-identical, overlapping, implausible or non-parallel choices; ensure exactly one supportable answer.
- **Specialist terminology:** Latin species names, niche chemical formulas, advanced rules and technical trivia.
- **Song/album identification without playback:** consider replacing these with broadly recognizable artist/band knowledge.

These are proposals, not extra silently applied gates. A short stem and familiar subject do not by themselves prove that a question is fun.
