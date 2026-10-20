from pathlib import Path
import numpy as np
import wave, json, shutil, ast, xml.etree.ElementTree as ET

OUT=Path(__file__).parent
BASE=OUT.parents[1]
SR=48000; N=SR*60
ROOT=Path(r'C:\Users\User\Downloads\Torrents\All the Samples from Mars 2025 Update [Samples from Mars]')
# Reuse PCM decoding, original synth voices and 24-bit writing without executing the menu composition.
original=ast.parse((BASE/'audio/menu-v1/compose.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in original.body if isinstance(n,ast.FunctionDef) and n.name in ['readwav','tone','save']],type_ignores=[]),'audio_helpers','exec'))
stems={k:np.zeros((N,2)) for k in ['Mellow beats','Warm bass','Soft keys','Clock percussion','Vinyl backdrop']}
rng=np.random.default_rng(20261020)
sources={}; events=[]
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p)
    shutil.copy2(p,OUT/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-8)
kick=sample('BD 808 Warm Vinyl SP.wav')
rim=sample('Rim 808 Standard Vinyl SP.wav')
hat=sample('CH 808 Standard Vinyl SP 01.wav')
conga=sample('Conga 808 Lo Vinyl SP Clean 01.wav')
def put(track,z,t,gain=1,pan=0):
    start=round(t*SR)
    if start>=N:return
    z=z[:N-start]
    stems[track][start:start+len(z)]+=np.column_stack([z*np.sqrt((1-pan)/2),z*np.sqrt((1+pan)/2)])*gain
def seconds(beat):
    # Gentle continuous accelerando, 88 to 96 BPM across one minute.
    return 60/8*(-88+np.sqrt(88**2+16*beat))
chords=[[60,64,67,71],[57,60,64,67],[53,57,60,64],[55,60,62,67]]
roots=[36,33,29,31]
for bar in range(23):
    c=(bar//2)%4; b=bar*4; t=seconds(b)
    if t>=60:break
    for beat,g in [(0,.20),(1.75,.10),(2.5,.14)]: put('Mellow beats',kick,seconds(b+beat),g)
    for beat in [1,3]: put('Mellow beats',rim,seconds(b+beat),.065,-.12)
    for beat in [.5,1.5,2.5,3.5]: put('Mellow beats',hat[:int(SR*.10)],seconds(b+beat),.023,.25)
    if t>24:
        for beat in [1.25,3.75]:put('Mellow beats',conga[:int(SR*.20)],seconds(b+beat),.028,-.24)
    for beat,semi in [(0,0),(1.5,7),(2.75,12)]:
        put('Warm bass',tone(roots[c]+semi,.42,'bass'),seconds(b+beat),.12 if semi==0 else .075)
    for beat in [.25,2.25]:
        for i,note in enumerate(chords[c]):
            z=tone(note,.95,'chord')
            put('Soft keys',z,seconds(b+beat),.036,(i-1.5)*.17)
            put('Soft keys',z,seconds(b+beat)+.41,.008,-(i-1.5)*.17)
    if bar%2==1:
        for j,note in enumerate([chords[c][2]+12,chords[c][1]+12]):
            put('Soft keys',tone(note,.65,'pluck'),seconds(b+2+j*.75),.027,(-1)**j*.25)
# Soft wooden clock tick; faster density only in the last 16 seconds.
t=0.
while t<59.85:
    progress=t/60
    duration=.045; tt=np.arange(round(duration*SR))/SR
    noise=rng.normal(0,1,len(tt)); noise=np.convolve(noise,np.ones(5)/5,'same')
    tick=(np.sin(2*np.pi*1350*tt)*.55+noise*.45)*np.exp(-tt*125)*np.minimum(tt/.0015,1)
    tick/=max(abs(tick).max(),1e-8)
    put('Clock percussion',tick,t,.015+.012*progress,(-1 if len(events)%2 else 1)*.18)
    events.append(t)
    bpm=88+8*progress
    density=1 if t<44 else (1+(t-44)/16*.6)
    t+=60/bpm/density
# Original low-level vinyl-like bed: band-limited hiss, soft pops and slow amplitude flutter.
noise=rng.normal(0,1,N)
low=np.convolve(noise,np.ones(35)/35,'same')
high=np.convolve(noise,np.ones(4)/4,'same')-low
bed=high*.0018
for _ in range(390):
    start=int(rng.integers(0,N-1200)); length=int(rng.integers(35,420))
    pulse=rng.normal(0,1,length)*np.exp(-np.arange(length)/(length*.18))
    pulse=np.convolve(pulse,np.ones(5)/5,'same')
    bed[start:start+length]+=pulse*float(rng.uniform(.002,.010))
flutter=1+.12*np.sin(2*np.pi*np.arange(N)/SR*.56)
stems['Vinyl backdrop'][:,0]=bed*flutter
stems['Vinyl backdrop'][:,1]=np.roll(bed,43)*flutter
# Short fade only at the boundaries; music stays present until the question expires.
fade=np.ones(N); fade[:2400]=np.linspace(0,1,2400); fade[-7200:]=np.linspace(1,0,7200)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values()); scale=.66/abs(mix).max()
for k,z in stems.items():save(OUT/(k+'.wav'),z*scale)
master=BASE/'sounds/TriviTV-Trivia-01-60s-v1.wav'; save(master,mix*scale)
tree=ET.parse(BASE/'audio/menu-v1/TriviTV Menu.tracktionedit'); edit=tree.getroot()
edit.set('projectID',str(OUT/'TriviTV Trivia 01.tracktionedit'))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for tempo in seq.findall('TEMPO'):seq.remove(tempo)
for sec in range(61):
    beat=(88*sec+4*sec*sec/60)/60
    ET.SubElement(seq,'TEMPO',startBeat=str(beat),bpm=str(88+8*sec/60),curve='1.0')
trans=edit.find('TRANSPORT');trans.set('looping','0');trans.set('loopPoint1','0.0');trans.set('loopPoint2','60.0');trans.set('position','0.0')
edit.find('MASTERVOLUME/PLUGIN').set('volume','0.6376281380653381')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(3000+i*10),name=k,colour=['ff50bca0','ff489bce','ffac91db','ffe2bc79','ff9c9c9c'][i])
    ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(3001+i*10),source=str(OUT/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(3002+i*10),enabled='1',volume='0.6376281380653381')
    ET.SubElement(tr,'PLUGIN',type='level',id=str(3003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
ET.indent(tree);tree.write(OUT/'TriviTV Trivia 01.tracktionedit',encoding='utf-8',xml_declaration=True)
report={'duration_seconds':60,'sample_rate':SR,'bit_depth':24,'tempo_bpm':[88,96],'tick_interval_first':events[1]-events[0],'tick_interval_last':events[-1]-events[-2],'peak_dbfs':float(20*np.log10(abs(mix*scale).max())),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean((mix*scale)**2)))),'samples':sources,'vinyl_bed':'Original synthetic vinyl-like hiss and crackle','method':'Scripted composition and rendering, five stems in Waveform edit','clipped_samples':int(np.sum(abs(mix*scale)>=1))}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
