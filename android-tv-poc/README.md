# TriviTV Android TV proof of concept

Version `0.2.1-poc2` (versionCode 2), app ID `dev.trivitv.poc`, display name **TriviTV POC**. Installs as an update to POC1 using the same signing key. Universal APK with no native ABI-specific libraries; minimum Android 8.0/API 26. Standard Android TV/Google TV manifest, landscape, TV launcher icon/banner, no touchscreen requirement, no Xiaomi-specific APIs. Needs a sufficiently current Android System WebView for the existing JavaScript module app.

Adapted from the original TriviTV Kotlin/WebView launcher in `source-audit/android/`. The game itself is reused unchanged from `browser-site/dist/`, including exactly 916 Ukrainian EU questions, all 20 categories, Trivia/Millionaire, attribution and CC BY-SA 4.0 license.

Launch opens https://trivitv-ua-europe-test.jauntysloth128.chatgpt.site/?language=uk. Online changes arrive at the same URL; use Back/Menu → Reload to refresh. On a main-page connection failure or 12-second loading timeout, the app switches to the bundled version, served through intercepted HTTPS requests at appassets.androidplatform.net. No PC server is required in either mode. The bundled copy does not change when the live site is updated.

POC2 replaces the tall scrolling setup with fixed-height mode cards and one-click Start, separate paged category settings/credits, and a game view fitting question, four answers and actions on screen. Arrows/D-pad now call the web app's explicit row/column focus map through `window.TriviTVRemote`; native WebView spatial navigation is consumed. OK selects; Back closes web settings/credits/dialogs first, otherwise opens native Continue/Reload/Live/Bundled/Exit controls. Play/Pause maps to Trivia pause. Held OK is ignored. The single-choice Ukrainian language control and non-interactive logo are not focus stops. Touch/pointer interactions remain available. Saved progress/settings are independent for live and bundled origins.

Installation: copy the APK to the TV using a USB drive or an existing trusted file-transfer method; open it using the TV's file manager and allow that installer to install unknown apps if prompted. Launch TriviTV POC from TV apps. This is a signed debug build for sideload testing, not a Play Store release. It can coexist with earlier TriviTV apps because its package ID is different. Actual installation/remote testing remains to be performed on a TV.

Build in this workspace using the local JDK 21, SDK platform 36/build-tools 35.0.0 under `.tools/android-build`, and `gradlew.bat --no-daemon assembleDebug`. `local.properties` points to the local SDK and is not committed. The existing Gradle wrapper verifies its distribution checksum. Keep the debug signing key for compatible APK updates; do not distribute its private key.

Validation: compilation, Android lint, APK signature/manifest and bundled asset/count checks are recorded with the delivered artifact. No physical TV or Android emulator testing is claimed.
