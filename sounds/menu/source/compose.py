from pathlib import Path
import numpy as np
import wave, json, shutil, xml.etree.ElementTree as ET

OUT=Path(__file__).parent
ROOT=Path(r'C:\Users\User\Downloads\Torrents\All the Samples from Mars 2025 Update [Samples from Mars]')
SR=48000; N=SR*30; BEAT=60/128
stems={k:np.zeros((N,2)) for k in ['Drums','Bass','Chords','Plucks']}
sources={}
def readwav(p):
    with wave.open(str(p),'rb') as w:
        ch=w.getnchannels(); sr=w.getframerate(); width=w.getsampwidth(); b=w.readframes(w.getnframes())
    if width==3:
        q=np.frombuffer(b,np.uint8).reshape(-1,3).astype(np.int32)
        z=q[:,0]+(q[:,1]<<8)+(q[:,2]<<16); z=np.where(z>=8388608,z-16777216,z)/8388608
    elif width==2: z=np.frombuffer(b,'<i2')/32768
    elif width==4: z=np.frombuffer(b,'<i4')/2147483648
    else: raise ValueError(width)
    z=z.reshape(-1,ch).mean(axis=1)
    return np.interp(np.arange(round(len(z)*SR/sr))*sr/SR,np.arange(len(z)),z)
def put(track,z,beat,gain=1,pan=0):
    start=round(beat*BEAT*SR); inds=(np.arange(len(z))+start)%N
    stereo=np.column_stack([z*np.sqrt((1-pan)/2),z*np.sqrt((1+pan)/2)])*gain
    np.add.at(stems[track],inds,stereo)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p)
    shutil.copy2(p,OUT/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-8)
kick=sample('BD Bump Perkons.wav')
clap=sample('Clap Chill Perkons Clean 01.wav')
hat=sample('CH Soft Perkons 01.wav')
shaker=sample('Shaker Soft Perkons 01.wav')
def tone(midi,duration,kind):
    t=np.arange(round(duration*SR))/SR; f=440*2**((midi-69)/12)
    attack=np.minimum(t/.006,1); release=np.minimum((duration-t)/.04,1)
    if kind=='bass':
        z=np.sin(2*np.pi*f*t)+.23*np.sin(4*np.pi*f*t)+.1*np.sin(6*np.pi*f*t)
        env=attack*np.exp(-t*5)*release
    elif kind=='pluck':
        z=np.sin(2*np.pi*f*t+1.4*np.exp(-t*12)*np.sin(2*np.pi*2*f*t))+.18*np.sin(2*np.pi*3*f*t)
        env=attack*np.exp(-t*8)*release
    else:
        z=np.sin(2*np.pi*f*t)+.22*np.sin(2*np.pi*f*2.002*t)+.08*np.sin(2*np.pi*f*3*t)
        env=np.minimum(t/.035,1)*np.exp(-t*2.5)*release
    return z*env
# Original D major / B minor / G major / A suspended progression.
chords=[[62,66,69,73],[59,62,66,69],[55,59,62,66],[57,62,64,69]]
roots=[38,35,31,33]
motifs=[[74,78,81,78,76],[73,74,78,76,73],[71,74,78,74,69],[73,76,74,73,69]]
for bar in range(16):
    base=bar*4; c=(bar//2)%4
    for b,g in [(0,.28),(1.5,.19),(2,.25),(3.25,.17)]: put('Drums',kick,base+b,g)
    for b in [1,3]: put('Drums',clap,base+b,.095,-.05)
    for i in range(8): put('Drums',hat[:int(.12*SR)],base+i*.5+(0.035 if i%2 else 0),.028 if i%2==0 else .045,.23)
    for i in range(4): put('Drums',shaker[:int(.14*SR)],base+i+.75,.022,-.3)
    for b,n,d,g in [(0,roots[c],.32,.18),(.75,roots[c],.16,.11),(1.5,roots[c]+12,.20,.13),(2.5,roots[c],.23,.15),(3.25,roots[c]+7,.18,.10)]:
        put('Bass',tone(n,d,'bass'),base+b,g)
    for b in [.5,2.5]:
        for n in chords[c]: put('Chords',tone(n,.62,'chord'),base+b,.033,-.16 if n%2 else .16)
    # Leave alternate bars spacious; introduce a slightly different response in half two.
    positions=[.25,1,1.75,2.75,3.5] if bar%2==0 else [.5,2,3.25]
    notes=motifs[c] if bar<8 else motifs[c][::-1]
    for j,b in enumerate(positions):
        n=notes[j]; z=tone(n,.5,'pluck'); pan=(-.25 if j%2 else .25)
        put('Plucks',z,base+b,.075 if bar%2==0 else .05,pan)
        put('Plucks',z,base+b+.75,.016,-pan)

mix=sum(stems.values()); peak=abs(mix).max(); scale=.72/peak
def save(p,z):
    with wave.open(str(p),'wb') as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        v=np.round(np.clip(z,-1,.999999)*8388607).astype(np.int32).flatten()
        b=np.column_stack([v&255,(v>>8)&255,(v>>16)&255]).astype(np.uint8)
        w.writeframes(b.tobytes())
for name,z in stems.items(): save(OUT/(name+'.wav'),z*scale)
save(OUT/'TriviTV-Menu-30s-v1.wav',mix*scale)
save(OUT/'TriviTV-Menu-Loop-Test-60s.wav',np.tile(mix*scale,(2,1)))
# Use the structure saved by the installed Waveform version.
template=Path(r'C:\Users\User\Documents\trivitv\trivitv Edit 1.tracktionedit')
tree=ET.parse(template); edit=tree.getroot()
edit.set('projectID',str(OUT/'TriviTV Menu.tracktionedit'))
for tr in edit.findall('TRACK'): edit.remove(tr)
edit.find('TEMPOSEQUENCE/TEMPO').set('bpm','128.0')
master=edit.find('MASTERVOLUME/PLUGIN'); master.set('volume','0.6376281380653381')
transport=edit.find('TRANSPORT'); transport.set('looping','1'); transport.set('loopPoint1','0.0'); transport.set('loopPoint2','30.0')
for i,name in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(2000+i*10),name=name,colour=['ff00ffaa','ff00aaff','ffbb88ff','ffffbb55'][i])
    ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=name,start='0.0',length='30.0',offset='0.0',id=str(2001+i*10),source=str(OUT/(name+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(2002+i*10),enabled='1',volume='0.6376281380653381')
    ET.SubElement(tr,'PLUGIN',type='level',id=str(2003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
ET.indent(tree); tree.write(OUT/'TriviTV Menu.tracktionedit',encoding='utf-8',xml_declaration=True)
report={'duration':30,'sampleRate':SR,'bpm':128,'bars':16,'peak_dBFS':float(20*np.log10(abs(mix*scale).max())),'rms_dBFS':float(20*np.log10(np.sqrt(np.mean((mix*scale)**2)))),'boundary_step':float(abs((mix*scale)[0]-(mix*scale)[-1]).max()),'samples':sources,'method':'Original synthesis and sample sequencing rendered with Python; separate stems prepared for Waveform.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

