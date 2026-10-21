"""Final conservative gain and end fades on the Waveform-rendered mix."""
from pathlib import Path
import numpy as np
import soundfile as sf
import json
P=Path(__file__).resolve().parent
src=P/'Exported/TriviTV Deep Session 01 - Low Tide Export 1.wav'
x,sr=sf.read(src,always_2d=True)
assert sr==48000 and len(x)==128*sr and x.shape[1]==2
assert sf.info(src).subtype=='PCM_24'
assert abs(x).max()<.95
x[:int(.05*sr)]*=np.linspace(0,1,int(.05*sr))[:,None]
x[-sr:]*=np.linspace(1,0,sr)[:,None]
gain=min(10**(-25/20)/np.sqrt(np.mean(x*x)),10**(-6/20)/abs(x).max());x*=gain
dst=P.parent/'TriviTV-Deep-Session-01-Low-Tide-128s-v1.wav'
sf.write(dst,x,sr,subtype='PCM_24')
freq=np.fft.rfftfreq(len(x),1/sr);power=(abs(np.fft.rfft(x,axis=0))**2).sum(axis=1)
bands={f'{a}-{b}Hz':round(float(power[(freq>=a)&(freq<b)].sum()/power.sum()*100),2) for a,b in [(0,40),(40,80),(80,160),(160,500),(500,2000),(2000,6000),(6000,24001)]}
assert bands['0-40Hz']<1 and bands['40-80Hz']<15
report={'file':dst.name,'duration':128,'sample_rate':sr,'bit_depth':24,'bpm':120,'bpm_ramp':False,'changes_seconds':[32,64,96],'native_waveform_render':str(src),'final_mastering':'Gain to -25dBFS RMS, 50ms start fade and 1s end fade after Waveform render','gain_db':float(20*np.log10(gain)),'peak_dbfs':float(20*np.log10(abs(x).max())),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x)))),'band_energy_pct':bands,'clipped_samples':int(np.sum(abs(x)>=1)),'status':'Listening review pending; not in game playlist'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
