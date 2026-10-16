# TriviTV

A playable trivia prototype for a shared TV screen, TV remotes and phone browsers. The Android TV app is currently a Kotlin/WebView launcher for the shared web interface, not a standalone native game. A session server must be running.

## Play locally

Requires Node.js 24+. No runtime npm dependencies or credentials are needed.

```sh
npm ci
npm start
```

The development server defaults to port 3000 and binds to this computer only. For phones or a physical TV on the same trusted network:

```sh
HOST=0.0.0.0 npm start
```

Open the computer's LAN address on the TV/browser (for example, `http://192.168.1.10:3000`). Choose a game, region and included categories. Other devices open that same address, choose **Join a game**, and enter the six-character room code and their name. The lobby also offers a copyable joining link. QR codes are not implemented yet. Do not use the TV's or phone's own localhost address to reach the computer.

The host starts the game and can use Millionaire lifelines. Answering takes one OK press; answers lock immediately. Local players take turns with the remote, with automatic handoff and focus on the first available answer. Phone players answer individually. Once everyone has answered, the correct answer and scores appear automatically. There are no Reveal or Next buttons, and questions have no answer deadline.

### Automatic pacing and pause

The answer stays on screen for **five seconds**, then the server automatically starts the next question (or final results). A visible countdown and progress bar show the remaining time. **Player 1** can pause and resume with the focused Pause/Resume button using OK/Enter, or the remote’s Play/Pause button. Pausing freezes the answer screen indefinitely; resuming uses the exact remaining time. Other players cannot pause the session. If the single-player seat is handed to a phone, that phone is Player 1 and owns pause controls. A browser reload preserves a paused session while the server is running. Held OK presses are ignored so a held button cannot answer for the next player or repeatedly toggle pause.

Five seconds is an initial product default for reviewing a short answer and the score, not a universal research-backed quiz timing. [W3C Timing Adjustable](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html) supports giving users control over time limits, and [Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) explains why resuming from the paused point helps users read. These were checked through the official [Timing Adjustable source](https://github.com/w3c/wcag/blob/main/understanding/20/timing-adjustable.html) and [Pause, Stop, Hide source](https://github.com/w3c/wcag/blob/main/understanding/20/pause-stop-hide.html). Tune the default after TV playtesting; these guidelines do not prescribe a five-second trivia review.

Transitions run on the server, so backgrounding a phone does not stop the game. All participating players still need to answer; there is no automatic timeout or disconnected-player skip yet.

Host/player access tokens live in the tab's session storage. Reloading the same tab reconnects. Closing the tab loses access; there is no account recovery yet. Rooms and scores are in memory, expire after six inactive hours, and disappear when the server restarts. This is a development prototype, not an Internet deployment.

## Modes

- **Millionaire:** exactly one player, up to 15 progressively harder four-choice questions; points ladder ending at 1,000,000; safe checkpoints after steps 5 and 10; one 50:50 lifeline; walk away before locking an answer. A wrong answer ends the climb at the last checkpoint. All rewards are fictional points. A phone can take the single player seat by joining before the host starts; a second player cannot join.
- **Trivia:** up to 10 questions, 100 points per correct answer and a final leaderboard. Three players are free, including the TV player. Ties are shared by score; ordering is stable, not a tie-break rule. The host is a player in this prototype, not a spectator.

Both modes accept **Europe** or **US** as the regional audience and a category inclusion list. Excluded categories never appear. Regional references are mixed with global questions; selecting Europe is not a claim that every question is about Europe. All text is currently English. The 56 original starter questions span Geography, Entertainment, History, Science, Sport and Arts. A narrow category filter can produce a shorter game/ladder; the lobby shows its actual length. Questions are not repeated within a game, but may repeat between games.

## Party Pass model

The product model is a complete free game plus optional **2-day** and **30-day**, one-time, non-renewing Party Passes. Passes will unlock larger groups and extras such as picture questions. Billing, prices, expiry handling, entitlement persistence, purchase recovery and picture questions are **not implemented**.

To exercise larger groups locally:

```sh
HOST=0.0.0.0 TRIVITV_DEMO_PARTY=1 npm start
```

Select the clearly labelled development Party Mode toggle when creating Trivia. This is a server-authorized test flag, not a paid entitlement. A client cannot enable it when the server flag is off. There is no fixed player-count cap for demo Party Trivia; practical capacity has not been load-tested. Millionaire remains single-player. Do not enable this bypass in a production billing environment.

## Android TV

Open `android/` in Android Studio, or use JDK 21, SDK platform 36 and build-tools 35.0.0:

```sh
cd android
./gradlew --no-daemon assembleDebug
```

Output: `android/app/build/outputs/apk/debug/app-debug.apk` (relative to repository root).

The app appears in the TV launcher. Enter the session server's address in the native toolbar and press **Connect**. The emulator default is `http://10.0.2.2:3000`; a physical TV needs the computer's LAN IP. Menu focuses the address bar. Arrow/D-pad navigation and Enter select game controls; the web interface also supports keyboard and touch. Back returns through web history or focuses server settings. Debug permits HTTP on a trusted local network; release requires HTTPS. No JavaScript-to-native bridge or billing SDK is exposed.

APK compilation has been validated in Linux. Installation, actual Android TV WebView behavior, D-pad input and lifecycle recovery still need physical device/emulator testing. The cloud machine lacks `/dev/kvm`, and adb currently cannot create its sandboxed user configuration directory.

## Validation

```sh
npm run check
npm test
npx playwright install chromium
npm run test:browser
```

With an installed browser, use `CHROMIUM_PATH=/usr/bin/chromium npm run test:browser` instead of downloading one. The browser test advances an injected server clock to avoid waiting through every five-second review, starts and stops its own server, and verifies a full three-player, ten-question session, results, settings, solo lifelines/walk-away, automatic reveal/advance, Player 1 pause/resume across reload, shared-remote handoff, held-button protection and mobile overflow. It saves a home screenshot to `/tmp/trivitv-home.png` (override with `TRIVITV_SCREENSHOT`). Unit/API tests check capacity, filtering, scoring, checkpoints, hidden answers, access roles, countdown boundaries, server timer execution, stale-answer rejection and Party bypass rejection. CI runs web checks and builds the Android APK; the hosted CI workflow itself has not yet run.

In the prepared cloud machine:

```sh
source /workspace/trivitv-setup/activate.sh
npm ci --cache /workspace/.npm-cache
npm test
CHROMIUM_PATH=/usr/bin/chromium npm run test:browser
cd android && ./gradlew --no-daemon assembleDebug
```

## Next milestones

1. Test real TV navigation and phone reconnection; add QR joining and spectator hosting.
2. Expand and editorially review the question bank, with licensed image content and richer difficulty calibration.
3. Add persistent host identities and server-side Party Pass verification/expiry through Google Play one-time purchases.
4. Implement 2-day/30-day pass lifecycle, restoration, refunds and active-game expiry behavior after product decisions are finalized.
5. Load-test party capacity and prepare HTTPS hosting, durable sessions and deployment operations.
