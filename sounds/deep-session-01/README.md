# Deep Session 01 — Low Tide

First of three requested new session tracks. Listening review pending; tracks 2 and 3 have not been created, following the user's one-at-a-time instruction.

- Master: `../TriviTV-Deep-Session-01-Low-Tide-128s-v1.wav`, 2:08, stereo 48 kHz / 24 bit.
- Constant 120 BPM, D minor / F major, no late tempo ramp or built-in countdown.
- Small changes every 16 bars / 32 seconds: core ninth-chord groove; shaker/rim variation; spacious dub phrase with lighter bass/clap; return to core pattern. No big drops or ending build.
- Seven actual sources across all three libraries present in the supplied folder: Perkons, 808 Loops, Vinyl SP. 4,224 WAV paths inventoried, including duplicates in preset folders; not 4,224 unique sounds. Inventory in sample-inventory.json, selected provenance in arrangement.json.
- Original synthesized mid-bass complements sampled instruments. Processed voices in voices/, with 864 editable audio clips on seven tracks in the native Waveform edit.

## Workflow

compose.py prepares EQ/pitch/gain-processed voices and native clip placement. The edit was opened and played in Waveform 14 FREE using the EDIFIER output, and exported through Waveform Render to File at 48 kHz / 24 bit without normalization. Export retained in Exported/. master.py applies conservative final gain, 50ms start fade and 1s end fade to that actual Waveform export; it does not synthesize or repeat the mix.

Final RMS -25 dBFS, peak -8.80 dBFS, zero clipping. Below-40Hz energy 0.28%; 40–80Hz 9.37%. Measurements do not replace a speaker listening check. The native project renders quieter than the gain-adjusted delivered master.

Reproduce: run compose.py with numpy/scipy/soundfile, open tracktionedit through Waveform Projects > Open Project chooser, render 48kHz/24bit without normalization to the retained export filename, then run master.py. Close the edit before regenerating voices because Waveform locks source files.

New music is not in the game playlist pending review. Separate timer cue: ../TriviTV-Countdown-Metronome-10s-v1.wav. It is connected to the timed Trivia question clock.
