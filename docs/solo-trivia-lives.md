# Solo Trivia lives

New solo games start with 3 lives and continue until all are lost. A wrong answer or a question timeout costs one life and clears the correct-answer streak. Five consecutive correct answers restore one life, up to five. Each group of five resets the streak even at the cap. A final answer is revealed before the results screen.

The first ten questions retain the category difficulty ramp from 60/30/10 to 30/50/20. Later draws hold the latter mix. Selected categories still apply; absent difficulty buckets renormalize. Questions do not repeat until the eligible pool is exhausted, then a fresh cycle begins. Only ten question texts are queued at a time; seen IDs and global progress persist across reloads.

Multiplayer/party Trivia and Millionaire retain their rules. Existing saves without the new life state remain legacy; start a new solo game for these rules.

Validation: node --test game-rules/*.test.mjs (13 passed); node browser-site/run-tv-qa.mjs (functional flow and 15,054 questions in each layout, zero clipping). Not yet packaged or deployed.
