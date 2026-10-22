# Ukrainian bank: preliminary candidate screen

Requested 2026-10-21. This is an offline candidate export, not a replacement live bank.

| Result | Questions |
| --- | ---: |
| Acquired Ukrainian drafts | 36,614 |
| Excluded or held by saved screening plus new rules | 11,682 |
| Potential survivors | 24,932 |
| — previously screened drafts | 799 |
| — still semantically unassessed | 24,133 |

Reused the existing builder, explicit decisions from both review rounds, prior semantic evidence, blocking localization flags, and deterministic EU/UA gates. Added removal of the Religion & Faith category and a retrieval check for word meanings/etymology in Ukrainian. Latest categorical rules apply even to previous Keep decisions.

**This is not a completed semantic review of the full bank.** An unassessed survivor means no implemented gate blocked it; it is not editorial approval. Entity mappings are incomplete. Obscurity, audience familiarity, ambiguous answers and localization cannot be established by keyword absence. The word-meaning retrieval check deliberately holds uncertain matches and has false positives (including incidental uses of “means”); inspect `word-meaning-matches.json` before making permanent exclusion decisions. Movie/book translated-title verification is pending. No factual or translation verification is claimed.

`potential-ukrainian-questions.json` preserves each survivor's original ID, source record and complete translation, including choice order and correct-answer data. `decisions.csv` accounts for every translated ID. `summary.json` records category counts, overlapping rule counts, limitations and input hashes. No acquired source/translation files or current game banks were changed.

Reproduce from the project root: `python scripts/screen-ukrainian-candidates.py` (UTF-8 Python environment).

Question content retains the source OpenTriviaQA attribution and CC BY-SA 4.0 licensing; see `provided-916/TriviTV-EU-Filtered-Test/Server/data/opentriviaqa/SOURCE-README.md`.
