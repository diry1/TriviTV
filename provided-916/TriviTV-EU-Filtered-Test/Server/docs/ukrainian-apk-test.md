# Ukrainian Android TV test build

Build with `cd android && ./gradlew assembleUkrainianTest` using the Android SDK
and JDK described in the main README. The debug-signed APK is written to
`android/app/build/outputs/apk/ukrainianTest/app-ukrainianTest.apk`.
It installs separately as `dev.trivitv.app.uktest` and is labelled
**TriviTV — Українська (тест)**.

This APK is a TV WebView launcher and requires the accompanying session server;
questions are served by that server, rather than bundled inside the APK.

1. Extract the accompanying server ZIP on a computer with Node.js 24 or newer.
2. Run `node start-uk-test.js` in the extracted folder. No npm installation or API
   key is required. Keep the computer and server running during play.
3. Install the APK on an Android TV running Android 8.0 or newer.
4. Connect the TV and computer to the same trusted network. Enter the computer's
   LAN address, such as `http://192.168.1.10:3000`, and press **Підключитися**.
5. The game opens in Ukrainian with Europe selected. Selecting Ukrainian also
   resets the region to Europe. The region selector remains available.
   Ukrainian games use only the translated snapshot
   in the server package, with no English fallback. Joining phones adopt the room
   language. Category/region combinations can have fewer questions.

The test build permits HTTP for local testing. Translations are unreviewed drafts;
the server ZIP records the exact count and snapshot time in `TEST-BUILD.txt`.
The ongoing bulk translation job is separate from this frozen snapshot.

Compilation and browser flow checks do not replace testing installation, remote
navigation, and WebView behavior on a physical TV.
