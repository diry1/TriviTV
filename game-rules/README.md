# Weighted game difficulty

`category-difficulty.json` holds the accepted starting 1–5 star category estimates. They are editorial defaults, not calibrated question ratings. `difficulty.mjs` uses an explicit integer `difficultyStars` on an individual question when available, otherwise its category default. The old source `difficulty: null` remains unchanged. Backend master tags include `difficulty:category-default:N` and `difficulty:method:category-estimate`; `difficulty:unrated` still means no individual rating.

For a new game, progress is question index divided by (game length minus one):

| Position | Easy (1–2★) | Medium (3★) | Hard (4–5★) |
| --- | ---: | ---: | ---: |
| Start | 60% | 30% | 10% |
| Middle | 45% | 40% | 15% |
| End | 30% | 50% | 20% |

These are draw probabilities, not guaranteed counts within a short game. The mix changes linearly and permits easier questions late and harder questions early. No category defaults currently use 5★; it is reserved for future per-question expert ratings.

Selection happens after existing language/region/category eligibility. IDs are drawn without replacement. Empty/depleted difficulty buckets have their weights redistributed proportionally across nonempty buckets; source pools and selected categories are never expanded to meet quotas. Answer shuffle and canonical answer alignment are unchanged.

Used by solo Trivia (10), Millionaire (15), multiplayer Trivia (10). Existing saved games/rooms keep their decks. Imposter uses words and Turf War has no fixed game length, so both retain their existing selection behavior.

`multiplayer/prepare.mjs` generates the category module and copies both difficulty modules to browser/public TV assets. Worker code imports the same canonical selector. No star values or backend tags are added to player UI. The master bank is not expanded into the current 916-question runtime.

Checks: `node --test game-rules/*.test.mjs`, plus multiplayer service tests with local Wrangler running. No public deployment or APK rebuild was performed for this change; it is ready for the next game release.


## Question-level build 0.11

`triviaQuestions` uses five-star stages:35/50/15/0/0,20/45/30/5/0,10/35/40/15/0,5/30/40/23/2 for successive5question stages;21onward5/25/40/27/3. Systematic randomized rounding makes five-slot stages unbiased over games; deficit ordering spreads levels. Seed saved in game settings, schedule reproduced across10question queues/reload; late100question cycles exact before sparse-pool substitutions. Eligible questions sampled uniformly inside star, giving proportional category representation; no repeats until selectedpool exhausted. Missing stars fall to nearest available level, lower wins ties.

`millionaireQuestions`:15strict levels1,2,2,2,2,3,3,3,3,3,4,4,4,4,5. Availability requires1/4/5/4/1questions per star; UI warns before start, selector rejects insufficient pool. Legacy weightedQuestions remains only for compatibility/tests. Question scores exported with fingerprint checks from quality-full-v1; translation flags remain unapplied.
