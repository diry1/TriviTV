# TriviTV menu draft v1

30 seconds, 16 bars, 128 BPM, stereo 48 kHz / 24-bit WAV.

Original light electronic menu composition: bouncy bass, soft chord stabs, plucked hook and restrained Perkons drums. Fall Guys was a broad mood reference; no soundtrack audio was used.

- `TriviTV-Menu-30s-v1.wav`: loop master.
- `TriviTV-Menu-Loop-Test-60s.wav`: two repetitions for judging the join.
- `TriviTV Menu.tracktionedit`: Waveform edit with four separate rendered stems. Absolute paths refer to this folder.
- `compose.py`: reproducible original synthesis / sample sequencing and native edit preparation. Close Waveform before rerendering because it locks open WAVs.
- `validation.json`: format, levels and sample provenance.
- `samples/`: the four selected local Perkons samples.

Waveform 14 successfully imported and saved a Perkons kick test. The composed four-stem edit was opened and playback meters verified in Waveform, with unity faders corrected to Waveform's native 0.637628 parameter value. Composition and master rendering were scripted, not exported through Waveform. Subjective listening review remains for the user. No game integration or publication performed.

The open Waveform project is `C:\Users\User\Documents\trivitv`, edit `Menu`. Its stems reference this workspace folder. The preserved sample-import test edit's relative kick.wav is available in that Documents project.
