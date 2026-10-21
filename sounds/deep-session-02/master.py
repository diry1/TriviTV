"""Master the actual native Waveform export, without changing its tempo."""
from pathlib import Path
import numpy as np,soundfile as sf,json
P=Path(__file__).resolve().parent
src=P/'Exported/Amber Rooms Export 1.wav'
x,sr=sf.read(src,always_2d=True)
assert sr==48000 and x.shape[1]==2 and 129<len(x)/sr<132
assert sf.info(src).subtype=='PCM_24' and abs(x).max()<.95
# Keep the rounded kick without reproducing the speaker-buzzing low band.
pad=sr;y=np.pad(x,((pad,pad),(0,0)),mode='reflect')
hz=np.maximum(np.fft.rfftfreq(len(y),1/sr),.001)
response=1/np.sqrt(1+(78/hz)**8)*10**((-8/(1+(hz/150)**4))/20)
x=np.fft.irfft(np.fft.rfft(y,axis=0)*response[:,None],n=len(y),axis=0)[pad:-pad]
x[:int(.08*sr)]*=np.linspace(0,1,int(.08*sr))[:,None]
x[-sr:]*=np.linspace(1,0,sr)[:,None]
gain=min(10**(-25/20)/np.sqrt(np.mean(x*x)),10**(-6/20)/abs(x).max());x*=gain
out=P.parent/'TriviTV-Deep-Session-02-Amber-Rooms-130s-v1.wav';sf.write(out,x,sr,subtype='PCM_24')
f=np.fft.rfftfreq(len(x),1/sr);power=(abs(np.fft.rfft(x,axis=0))**2).sum(axis=1)
bands={f'{a}-{b}Hz':round(float(power[(f>=a)&(f<b)].sum()/power.sum()*100),2) for a,b in [(0,40),(40,80),(80,160),(160,500),(500,2000),(2000,6000),(6000,24001)]}
report={'master':str(out),'native_waveform_export':str(src),'sample_rate':sr,'bit_depth':24,'duration':len(x)/sr,'bpm':118,'tempo_ramp':False,'changes_seconds':[32.542,65.085,97.627],'key':'B minor','peak_dbfs':float(20*np.log10(abs(x).max())),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x)))),'gain_db':float(20*np.log10(gain)),'band_energy_pct':bands,'clipped_samples':int(np.sum(abs(x)>=1)),'review_status':'Pending; not in game pool'}
report['master_eq']='78Hz high-pass and gentle -8dB low shelf around150Hz; speaker-friendly low end'
assert report['clipped_samples']==0 and bands['0-40Hz']<1 and bands['40-80Hz']<15
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
