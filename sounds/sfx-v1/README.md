# TriviTV navigation and notification draft pack

Open `index.html` in a browser. It works offline beside the existing sounds folder. Nothing plays automatically. Each of 12 events has A/B candidates; compare over the original selected deep house track, test arrow-key navigation, and export choices as JSON. The defaults are placeholders, not accepted user decisions.

Events: highlight, press, back, unavailable, question appears, answer locked, choices revealed, correct, incorrect, final-seconds tick, expired, round complete. The warning asset is a single tick for runtime scheduling, not a five-second recording. Choices revealed means the options appear, separate from correct-answer feedback.

`audio/` holds 24 mono 48kHz/16-bit PCM WAVs. Navigation is intentionally quieter than notifications. `manifest.json` maps every cue to its source and records duration/levels. `TriviTV-SFX-Audition-A.wav` plays the A candidates in the numbered page order, separated by 0.8 seconds; see reel-order.json for times.

Kenney Interface Sounds 1.0, downloaded from https://kenney.nl/assets/interface-sounds ; original archive and license preserved in source/. Kenney source sounds are CC0. Modified navigation cues are trimmed, gently filtered, faded and gain-balanced. Custom result/timeout/round cues are original synthesis dedicated to CC0. No external account or payment used.

Rebuild with the bundled Python runtime and `build.py` (numpy, scipy, soundfile). `validation.json` validates all 24 output files and preserves source ZIP SHA256. Browser QA in `qa.cjs` and `browser-validation.json` checks file loading, cue/music playback, stop, arrow navigation, choice export, and mobile width in headless Edge. Automated checks establish playback functionality, not subjective audio quality; listening review remains pending.

No game integration or publication performed. Millionaire-specific lifeline, suspense, checkpoint, walk-away and jackpot cues remain outside this first 12-event draft.

## Revision 2 — user feedback
Button pressed now uses former unavailable 4.B (switch_002) at the exact same processed level; one confirmed option. Both choices-revealed candidates replaced by new soft layered tones. Time-expired options are 2.1 seconds, sustained descending modern tones rather than a wah-wah effect. Warning is now a full three-second countdown recording with pulses at 0/1/2 seconds; trigger once when three seconds remain (do not schedule every second). Manifest contains 23 current cues; old audio preserved in archive-before-revision-2/. An obsolete press-b.wav may remain on disk but is not in the manifest. Prior one-tick warning instructions above are superseded. Browser playback, stop, navigation, export/mobile QA passed again. Subjective review pending.

## Revision 3
User selected Back/Cancel = revision 2's 1.B (select_001 at original -34dBFS RMS), Unavailable Action = revision 2's 3.A (back_001 at original -31dBFS RMS). Both are now single confirmed variants. Exact WAV equality verified against archived originals. Button press selection unchanged. Manifest now contains 21 current candidates; old unused WAVs remain on disk but are excluded from manifest. Browser QA passed again.
