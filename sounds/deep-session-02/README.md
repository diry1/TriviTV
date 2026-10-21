# Deep Session 02 — Amber Rooms

Second of three new session drafts; listening review pending. Third track is not created yet.

Master: ../TriviTV-Deep-Session-02-Amber-Rooms-130s-v1.wav — 2:10.1695, stereo48kHz24bit, steady118BPM, Bminor. Small arrangement changes at32.54/65.08/97.63seconds. No ending speed-up, countdown or dramatic drop. Simple warm Bminor/A/G triads, syncopated bass, mellow snare, organic percussion and sparse sampled guitar accents.

Seven different source samples from all three available libraries (Vinyl SP, Perkons,808 Loops), listed in arrangement.json. Different drums/hat loop, harmony, bass rhythm and tonal accent from Low Tide. Chords and bass synthesized. 808hat source is slowed120→118BPM with a tiny drum-pitch change.

compose.py prepares processed voices and872 editable native clips on7tracks in Amber Rooms.tracktionedit. Prepared in the background, then loaded/exported through Waveform14FREE's native Render to File,48kHz24bit, normalization off. Raw native mix retained at Exported/Amber Rooms Export 1.wav.

master.py applies final low-end EQ, gain and fades after the native export:78Hz high-pass, gentle-8dB low shelf around150Hz. This fixes a bass-heavy kick detected in the first render. The native project contains the premaster; rerenders should be run through master.py to reproduce the delivered balance/level. Final RMS-25dBFS, peak-6.78dBFS, zero clipped samples;40–80Hz energy1.77%, below40Hz effectively0%. Original scripts/provenance and validation.json retained.

This new draft is not in the game playlist pending review. Low Tide's user Export2 is separately approved and already staged for the next build.
