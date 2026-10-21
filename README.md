# TriviTV

Ukrainian TV trivia and phone multiplayer, live at https://iggro.com. Browser TV interface: https://iggro.com/tv/.

Current version: **0.6.0 Turf War**. Main menu: Trivia (1–8), Millionaire (1), Imposter (3–8 phones), Turf War (2, TV remote + phone or two phones). Music, sound effects and accelerating final-ten-second countdown included.

- [TV APK and install instructions](artifacts/TriviTV-TV-Turf-War/)
- [Multiplayer source, deployment and rules](multiplayer/README.md)
- [Project continuity and validation](PROJECT-HANDOVER.md)
- [Browser source](browser-site/), [Android launcher](android-tv-poc/)
- [Preserved 916-question bank and editorial sources](provided-916/)
- [Sound audition](sounds/sfx-v1/index.html)

Turf War uses a shared 5×5 board. Bid privately before the trivia question. Attacks have 10 seconds. Correct attacks capture unless the owner selected that same tile and also answered correctly. Contested tiles cool down one turn, with the last free tile exempt. Five straight tiles horizontally, vertically or diagonally wins.

For development: Node.js, then `npm ci` in multiplayer; `npm run prepare-assets`; `npm run dev`. With local service running, `npm test` exercises engine and HTTP/WebSocket integration. Deploy to the existing Cloudflare Workers account with `npm run deploy` after authenticating Wrangler. Credentials, local room state and caches are excluded.

Validation: 27 local tests and four public-service integration tests passed; Android build/lint, APK signing/alignment and all 39 bundled files verified. Physical TV testing of this version remains pending. Latest APK is 5,197,524 bytes.

Question attribution: OpenTriviaQA, CC BY-SA 4.0. Preserve IDs, answer keys and editorial decisions. Audio provenance/licenses are included. Commercial raw sample copies, intermediate stems, rejected masters and private conversation history remain local. Existing root server and android/ are historical; see docs/legacy-server-README.md.
