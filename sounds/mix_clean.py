from pathlib import Path
import numpy as np
import wave, ast, json, xml.etree.ElementTree as ET
P=Path(__file__).parent; SR=48000
src=ast.parse((P.parent/'audio/menu-v1/compose.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='save'],type_ignores=[]),'writer','exec'))
def read(p):
    with wave.open(str(p),'rb') as w:
        assert w.getframerate()==SR and w.getsampwidth()==3
        q=np.frombuffer(w.readframes(w.getnframes()),np.uint8).reshape(-1,3).astype(np.int32)
        v=q[:,0]+(q[:,1]<<8)+(q[:,2]<<16)
        return (np.where(v>=8388608,v-16777216,v)/8388608).reshape(-1,2)
def db(x):return float(20*np.log10(max(x,1e-12)))
def stats(z):
    # Sum channel powers, not a mono downmix, to avoid hiding stereo energy.
    sp=np.abs(np.fft.rfft(z,axis=0))**2
    f=np.fft.rfftfreq(len(z),1/SR); power=sp.sum(axis=1); total=power.sum()
    return {'peak_dbfs':db(abs(z).max()),'rms_dbfs':db(np.sqrt(np.mean(z*z))),
        'band_energy_pct':{f'{a}-{b}Hz':round(float(power[(f>=a)&(f<b)].sum()/total*100),2) for a,b in [(0,40),(40,80),(80,160),(160,500),(500,2000),(2000,6000),(6000,24001)]},
        'clipped_samples':int(np.sum(abs(z)>=1))}
def eq(z,hp,lowcut=0,highcut=0,lp=14000):
    # Smooth frequency-domain EQ with reflected padding, cropped after processing.
    pad=SR; x=np.pad(z,((pad,pad),(0,0)),mode='reflect')
    f=np.fft.rfftfreq(len(x),1/SR); safe=np.maximum(f,.001)
    highpass=1/np.sqrt(1+(hp/safe)**8)
    low_shelf=lowcut/(1+(safe/145)**4)
    high_shelf=highcut/(1+(4200/safe)**4)
    response=highpass*10**((low_shelf+high_shelf)/20)/np.sqrt(1+(safe/lp)**8)
    y=np.fft.irfft(np.fft.rfft(x,axis=0)*response[:,None],n=len(x),axis=0)[pad:-pad]
    return y
report={}
for kind in ['trivia','menu']:
    folder=P/'trivia-01' if kind=='trivia' else P/'menu/source'
    out=P/(kind+'-clean-v2');out.mkdir(exist_ok=True)
    names=['Mellow beats','Warm bass','Soft keys','Clock percussion','Vinyl backdrop'] if kind=='trivia' else ['Drums','Bass','Chords','Plucks']
    original={n:read(folder/(n+'.wav')) for n in names}; cleaned={}
    for n,z in original.items():
        if n in ['Warm bass','Bass']: y=eq(z,58,-5,-2,6500)*10**(-4/20)
        elif n in ['Mellow beats','Drums']: y=eq(z,48,-4,-2.5,11000)*10**(-1/20)
        elif n in ['Soft keys','Chords']: y=eq(z,170,-1,-1.5,11000)
        elif n=='Vinyl backdrop':y=eq(z,350,0,-4,6500)*10**(-6/20)
        else:y=eq(z,300,0,-3,10000)*10**(-1.5/20)
        ramp=np.ones(len(y));ramp[:240]=np.linspace(0,1,240);ramp[-240:]=np.linspace(1,0,240)
        cleaned[n]=y*ramp[:,None]
    before=sum(original.values());after=sum(cleaned.values())
    # Do not peak-normalize bass attenuation away; preserve conservative playback level.
    gain=min(1,.63/abs(after).max())
    for n,y in cleaned.items():save(out/(n+'.wav'),y*gain)
    filename='TriviTV-Trivia-01-60s-clean-v2.wav' if kind=='trivia' else 'TriviTV-Menu-30s-clean-v2.wav'
    save(P/filename,after*gain)
    template=folder/('TriviTV Trivia 01.tracktionedit' if kind=='trivia' else 'TriviTV Menu.tracktionedit')
    tree=ET.parse(template);edit=tree.getroot()
    project=out/('TriviTV '+kind.title()+' Clean v2.tracktionedit');edit.set('projectID',str(project))
    for tr in edit.findall('TRACK'):
        for clip in tr.findall('AUDIOCLIP'):clip.set('source',str(out/(tr.get('name')+'.wav')))
    tree.write(project,encoding='utf-8',xml_declaration=True)
    report[kind]={'before':stats(before),'after':stats(after*gain),'stem_before':{n:stats(z) for n,z in original.items()},'stem_after':{n:stats(z*gain) for n,z in cleaned.items()}}
(P/'mix-clean-v2-analysis.json').write_text(json.dumps(report,indent=2))
for kind,r in report.items(): print(kind,json.dumps({'before':r['before'],'after':r['after']},indent=2))
