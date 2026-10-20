# Applied Europe audience filters

Europe games now select only `candidate` IDs from the generated
`data/editorial/eu-eligibility.json` snapshot, separately for English and Ukrainian.
This applies before shuffling questions or choices in both Trivia and Millionaire.
Neither held records nor excluded records are fallback material.

| Language | Playable draft candidates | Excluded | Held |
| --- | ---: | ---: | ---: |
| English | 928 | 7,540 | 30,458 |
| Ukrainian | 916 | 7,234 | 30,776 |

Each row accounts for all 38,926 source IDs. Ukrainian holds include untranslated
records; English does not require any Ukrainian translation. All 36,614 acquired
translations remain in the canonical bank. Filtering changes eligibility rather
than deleting source text, choices, answers or translation records.

## What the counts mean

The historical semantic assessment covered the 3,515-question test snapshot, not
the entire acquired bank. Current output combines that evidence, all 400 human
decisions, English-specific reassessment of suitable translation-exempt questions,
blocking Ukrainian repair flags and conservative deterministic checks across the
full source bank. Many holds mean **not yet assessed**, not a proven defect.
The versioned evidence and per-language reasons are retained for every ID.

The deterministic screen catches explicit US league/entity, presidential,
Broadway, channel, country-music and franchise subjects; date/quantity/effort
issues; missing-media cues and unit/wordplay concerns. It cannot enumerate every
player, title, idiom or factual error. Absence of a match is never enough to admit
an unassessed record. Historical model screening remains fallible; admitted
candidates are drafts for further user review, not independently verified facts.

Explicit human Keep decisions remain the policy's positive calibration examples.
Separate known Ukrainian repair flags still block Ukrainian use, even for content
marked Keep. Shared negative decisions carry across languages; Ukrainian-only
defects do not block English, but reopened questions require an English audience
assessment before admission.

Small categories can produce short games. Current Ukrainian examples: Television
1, Video Games 2, Music 3. The setup reports available questions for the selected
language, region and categories. Do not fill shortages using held or excluded
material. US gameplay keeps its existing audience-tag behavior; the new policy is
specific to Europe.

## Rebuild and validate

```sh
python3 scripts/build_eu_eligibility.py
python3 scripts/build_eu_eligibility.py --check
python3 scripts/build_eu_eligibility.py --report-dir /tmp/eu-filter-report
npm run check
npm test
CHROMIUM_PATH=/usr/bin/chromium npm run test:browser
```

This builder is local and deterministic, uses no API key, makes no network calls
and never resumes bulk translation. Reports distinguish exclusions and holds and
include both languages, source fingerprints, evidence, rule IDs and origins.
Update semantic evidence or review decisions before rebuilding if you want more
questions admitted; do not simply turn unassessed holds into candidates.

Startup verifies source, translation, policy, review, evidence and rule-document
hashes. Missing, stale or incomplete eligibility fails closed with a rebuild
message; it never silently restores the old permissive Europe filter. Translation
changes also require rebuilding eligibility, preserving answer/choice alignment.

The Ukrainian-acquired milestone ZIP remains the unfiltered historical checkpoint.
Use the separately packaged **EU-filtered** server for the applied behavior. The
existing Android test APK remains compatible; it obtains its bank from the server.
The 24 outdated replacement briefs remain deferred.
