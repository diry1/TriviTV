# Stricter sample-feedback comparison

This comparison scans the full 38,926-record master with additional patterns derived from the 400 human-reviewed samples. It is **rule-based/heuristic extrapolation**, not a completed semantic review and not independent factual or title verification. It cannot reliably decide general familiarity or obscurity for every entity. A surviving question is not approved merely because it did not match these patterns.

Baseline Ukrainian potential pool: **24,931** (24,932 originally; one demonstrably corrupted repetitive translation was separately blocked). New provisional holds: **1,409 (5.65%)**. Remaining potential pool if those holds are applied: **23,522**.

| Additional flag | Questions (overlapping) |
| --- | ---: |
| Fan/biography detail | 592 |
| Album/song detail | 382 |
| Similar multiword options | 198 |
| US-specific subjects/entities | 84 |
| Numeric/spelled-out-number choices | 70 |
| Precise dates/records | 56 |
| Specialist terminology/details | 39 |
| US state/local detail | 14 |
| Missing media/context | 14 |

All 214 original human Keep decisions are preserved. There are 16 matches against Keep examples across the full master; these are recorded separately as conflicts, not silently overridden. Narrowing incidental birth-date and media-description matches reduced obvious false positives before this result was recorded. Other false positives/negatives remain possible.

`new-holds.csv` contains every newly flagged Ukrainian candidate, source prompt, reasons and exact matched evidence. `decisions.json` covers all 5,701 full-master pattern matches; `remaining-ids.json` is the proposed Ukrainian survivor list; `keep-conflicts.json` exposes positive calibration conflicts.

Tags were propagated to the full English master through `question-bank/tag-sources/sample-feedback.json`: `custom:sample-feedback:hold`, `custom:sample-feedback:preserved-human-keep`, and `custom:sample-reason:*`. These are comparison/review tags. They do not yet remove EU membership or silently modify the 0.8.0 APK's 24,931-question bank. UA-only corruption flags do not disqualify English questions.

Reproduce: `python scripts/screen-sample-feedback.py`. Then regenerate the custom source from the decisions and rebuild master tags if updating the tag snapshot. All source text/IDs/answers and original editorial decisions are retained.
