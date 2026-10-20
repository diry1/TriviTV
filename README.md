# TriviTV

Current delivery is the browser-only Ukrainian/Europe solo prototype in [`browser-site/dist/`](browser-site/dist/), with the TV launcher in [`android-tv-poc/`](android-tv-poc/). It preserves the supplied 916-question pool, original IDs/answer keys, attribution and gameplay rules. Start with [`PROJECT-HANDOVER.md`](PROJECT-HANDOVER.md).

- Live browser prototype: https://trivitv-ua-europe-test.jauntysloth128.chatgpt.site
- Browser source and validation instructions: [`browser-site/README.md`](browser-site/README.md).
- Sideloadable TV build and instructions: [`artifacts/TriviTV-TV-POC2/`](artifacts/TriviTV-TV-POC2/).
- Preserved authoritative question/editorial source: [`provided-916/`](provided-916/).
- Eight selected trivia masters: [`sounds/SELECTED-TRACKS.md`](sounds/SELECTED-TRACKS.md) and [`sounds/selection.json`](sounds/selection.json).
- Navigation/notification audition, revision 2: [`sounds/sfx-v1/`](sounds/sfx-v1/). Serve the repository locally and open `sounds/sfx-v1/index.html`, or open that file directly in a browser.

Music and sound effects are review assets; they have not yet been integrated into the game. UI sound source is Kenney CC0 with original synthesized result cues; provenance/license are included. Music sample provenance is recorded in each track folder. Raw Samples from Mars files, intermediate stems, rejected draft WAVs, local credentials, build caches and private conversation archives are excluded from this GitHub snapshot. They remain preserved in the original local workspace. Audio scripts retain local authoring paths and require the corresponding sample pack and numpy/scipy/soundfile; the committed WAV masters and audition page need no authoring dependencies.

## Run and validate

Serve `browser-site/dist/` with any static HTTP server. No application backend or accounts are required. For the browser QA suite, install Node.js, Microsoft Edge, then run `npm ci` and `npm test` inside `browser-site/`. The root Node server and original `android/` are historical; their instructions are retained in [`docs/legacy-server-README.md`](docs/legacy-server-README.md).

Question data retain OpenTriviaQA attribution and CC BY-SA 4.0 licensing. Preserve the selected bank and editorial decisions when making updates. No translation jobs or paid API requests are part of this prototype.
