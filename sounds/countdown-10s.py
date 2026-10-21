from pathlib import Path
import numpy as np
import soundfile as sf
import json
P=Path(__file__).resolve().parent;sr=48000
y=np.zeros(sr*10);times=[]
# Smooth acceleration: 90 to 240 clicks/minute over ten seconds.
# Integrated rate is 1.5t + .125t²; solve at each integer pulse.
for pulse in range(28):
    t=(-1.5+np.sqrt(2.25+.5*pulse))/.25
    if t>=9.97:break
    times.append(float(t));u=np.arange(int(.045*sr))/sr
    z=(np.sin(2*np.pi*1550*u)+.25*np.sin(2*np.pi*2400*u))*np.exp(-u*115)*np.minimum(u/.0015,1)
    z*=np.minimum((.045-u)/.008,1)*.13
    a=round(t*sr);n=min(len(z),len(y)-a);y[a:a+n]+=z[:n]
y=np.column_stack([y,y]);out=P/'TriviTV-Countdown-Metronome-10s-v1.wav'
sf.write(out,y,sr,subtype='PCM_16')
from scipy.signal import resample_poly
# The cue is mono and contains only low-kHz tones; 24kHz mono avoids redundant
# stereo/high-rate PCM in the APK while preserving duration and click timing.
sf.write(P.parent/'browser-site/dist/audio/countdown-10s.wav',resample_poly(y[:,0],1,2),24000,subtype='PCM_16')
(P/'countdown-10s.json').write_text(json.dumps({'duration':10,'bpm_start':90,'bpm_end':240,'click_times':times,'peak_dbfs':float(20*np.log10(abs(y).max())),'source':'Original synthesized soft metronome; no third-party recording'},indent=2))
print(out)
