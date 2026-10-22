# TriviTV

Ukrainian TV trivia and phone multiplayer, live at https://iggro.com. Browser TV interface: https://iggro.com/tv/.

Current version: **0.11.0 Ukrainian question difficulty build**. Main menu: Trivia (1–8), Millionaire (1), Imposter (3–8 phones), Turf War (2, TV remote + phone or two phones). Music, sound effects and accelerating final-ten-second countdown included.

- [Latest TV APK and install instructions](artifacts/TriviTV-TV-Difficulty-UK/)
- [Multiplayer source, deployment and rules](multiplayer/README.md)
- [Project continuity and validation](PROJECT-HANDOVER.md)
- [Browser source](browser-site/), [Android launcher](android-tv-poc/)
- [Preserved 916-question bank and editorial sources](provided-916/)
- [Sound audition](sounds/sfx-v1/index.html)

Turf War uses a shared 5×5 board. Bid privately before the trivia question. Attacks have 10 seconds. Correct attacks capture unless the owner selected that same tile and also answered correctly. Contested tiles cool down one turn, with the last free tile exempt. Five straight tiles horizontally, vertically or diagonally wins.

For development: Node.js, then `npm ci` in multiplayer; `npm run prepare-assets`; `npm run dev`. With local service running, `npm test` exercises engine and HTTP/WebSocket integration. Deploy to the existing Cloudflare Workers account with `npm run deploy` after authenticating Wrangler. Credentials, local room state and caches are excluded.

Validation: 27 local tests and four public-service integration tests passed; Android build/lint, APK signing/alignment and all 39 bundled files verified. Physical TV testing of this version remains pending. Latest APK is 5,197,524 bytes.

Question attribution: OpenTriviaQA, CC BY-SA 4.0. Preserve IDs, answer keys and editorial decisions. Audio provenance/licenses are included. Commercial raw sample copies, intermediate stems, rejected masters and private conversation history remain local. Existing root server and android/ are historical; see docs/legacy-server-README.md.


### Current question bank and difficulty

The complete English editorial master retains38,926questions. The current Ukrainian Fun build contains7,104questions with individual1–5star assessments, linked by canonical ID. Trivia gradually ramps from easier questions; Millionaire uses strict1★ question1,2★ questions2–5,3★ questions6–10,4★ questions11–14,5★ question15. SoloTrivia starts3lives, earns1 for5consecutivecorrect up to5, and continues untilzero. Start a new game/room after updating.

See [question bank dashboard](question-bank/dashboard/), [Fun policy](question-bank/fun-bank/V3-CHANGE.md), [full quality assessment](question-bank/quality-full-v1/REPORT.md), and [difficulty rules](game-rules/README.md). Machine translation flags and suggested repairs are retained as review metadata; they have not been automatically applied.

Raw model responses are preserved in per-run `responses.tar.gz` archives; large semantic audits in `audit.json.gz`. Run `python scripts/restore-bank-evidence.py` to unpack them locally without API calls. Repeated historical bank exports/review pages are omitted from Git; their local workspace copies remain available. Main CSV/provenance can be rebuilt with `python scripts/build-question-tags.py`. The full current quality review can be built locally with `python question-bank/quality-full-v1/export.py` and `python question-bank/quality-full-v1/finalize.py` after restoring evidence. Manifest source checks must match; these scripts do not submit API calls. Classification runners can spend credits and must not be rerun casually.

Current selector tests: `node --test game-rules/*.test.mjs`. Runtime export: `python scripts/export-uk-runtime.py --pool fun`, then `npm run prepare-assets` in multiplayer. Latest Android project is `android-tv-poc`; historical `android/` remains preserved.
