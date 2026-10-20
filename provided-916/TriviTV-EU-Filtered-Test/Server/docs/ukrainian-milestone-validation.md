# Ukrainian-acquired milestone validation

Date: 2026-10-19. Checkpoint: 36,614 Ukrainian drafts; 341 translation exclusions;
1,971 unprocessed source questions. The acquired bank spans all 20 categories.

Passed against this checkpoint:

- `npm run check`: server, web application and localization syntax.
- `npm run test:translations`: all retained translation records and metadata.
- `npm test`: 25 tests passed, none failed/skipped. Covers source structure,
  regional filtering, capacity, timing, scoring, hidden answers, roles, Ukrainian
  selection, source fingerprints, choice alignment and malformed-record rejection.
- `CHROMIUM_PATH=/usr/bin/chromium npm run test:browser`: both browser suites
  passed. Covers complete multiplayer gameplay, Millionaire, pause/reconnect,
  timeouts, animations, remote-style keys, mobile layout, Ukrainian setup, Europe
  default, phone language adoption, persistence and switching back to English.
- The staged checkpoint server's `/api/config` reports 36,614 Ukrainian and
  38,926 English questions.
- Dormant bulk-runner guard exits without starting translation when the accepted
  milestone requires a new explicit user instruction to resume.

These checks do not verify factual answers or translation semantics. They do not
independently validate movie/character/species/food terminology. Physical Android
TV installation, actual WebView/remote behavior and real-device network recovery
still require device testing. The APK in the checkpoint package is the existing
test launcher; it has not been rebuilt in this milestone step.

The new editorial policies are saved, but complete EU/UA and English EU eligibility
filtering is not implemented in gameplay. Runtime still uses legacy region tags.
