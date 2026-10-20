from pathlib import Path
import numpy as np
import ast, wave, json, shutil, xml.etree.ElementTree as ET
P=Path(__file__).parent; P.mkdir(exist_ok=True); (P/'samples').mkdir(exist_ok=True)
BASE=P.parents[1]; SR=48000; N=SR*60
def helpers(path,names):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'helpers','exec'),globals())
helpers(BASE/'audio/menu-v1/compose.py',['readwav','save'])
helpers(BASE/'sounds/mix_clean.py',['eq','stats','db'])
ROOT=Path(r'C:\Users\User\Downloads\Torrents\All the Samples from Mars 2025 Update [Samples from Mars]')
stems={k:np.zeros((N,2)) for k in ['Machinedrum groove','Short bass','Sampled chord washes','Wood and air','Reverse textures']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD Machinedrum Smooth Vinyl SP.wav')
snare=sample('SD Machinedrum Hollow Vinyl SP 03.wav')
hat=sample('CH Machinedrum Snap Vinyl SP 02.wav')
air=sample('Perc Machinedrum Air Vinyl SP 03.wav')
wood=sample('Woodblock Acoustic Sat Vinyl SP.wav')
tom=sample('Tom Casio Soft Vinyl SP.wav')
chord=sample('FX Mellow Chord Vinyl SP Eb.wav')
def sec(b):return 15*(-110+np.sqrt(110**2+8*b)) # 110 to 114 BPM in 60s
def put(k,z,t,g=1,pan=0):
    start=round(t*SR)
    if start>=N:return
    z=z[:N-start]; stems[k][start:start+len(z)]+=z[:,None]*np.array([np.sqrt((1-pan)/2),np.sqrt((1+pan)/2)])[None,:]*g
def voice(note,dur,kind):
    t=np.arange(round(SR*dur))/SR; f=440*2**((note-69)/12)
    a=np.minimum(t/.008,1)*np.minimum((dur-t)/.045,1)
    if kind=='mallet':
        z=np.sin(2*np.pi*f*t)*np.exp(-t*5)+.23*np.sin(2*np.pi*f*3.99*t)*np.exp(-t*16)+.07*np.sin(2*np.pi*f*9.2*t)*np.exp(-t*30)
    elif kind=='bass':z=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2*t))*np.exp(-t*5)
    else:z=(np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*2*f*t)+.08*np.sin(2*np.pi*3*f*t))*np.exp(-t*10)
    return z*a
def pitched(z,semitones):
    ratio=2**(semitones/12)
    return np.interp(np.arange(0,len(z),ratio),np.arange(len(z)),z)
def soften(z,seconds):
    z=z[:int(seconds*SR)].copy(); m=min(1200,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=soften(chord,2.8)
# E-flat tonal center, asymmetric three/one/two/two-bar harmonic rhythm.
shifts=[0,0,0,3,-2,-2,5,5]
for bar in range(29):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    # Broken accents over a steady house pulse, alternating one-bar answers.
    for x,g in [(0,.09),(1,.062),(2,.078),(3,.064)]:put('Machinedrum groove',kick[:14000],sec(b+x),g)
    for x in [1.02,3.02]:put('Machinedrum groove',snare[:13000],sec(b+x),.038,-.08)
    hats=[.5,1.5,2.5,3.5] if bar%2==0 else [.5,1.25,1.75,2.5,3.5]
    for j,x in enumerate(hats):put('Machinedrum groove',hat[:4500],sec(b+x+.035),.018 if j%2 else .025,.24)
    for j,x in enumerate([.75,2.25,3.75] if bar%2==0 else [1.75,2.75]):
        put('Wood and air',wood[:6000],sec(b+x),.014,(-1)**j*.35)
    put('Wood and air',air[:13000],sec(b+2.75),.021,-.3)
    if bar%4==3:
        for j,x in enumerate([3,3.5]):put('Wood and air',pitched(tom,j*3),sec(b+x),.025,(-1)**j*.22)
    if t>43:
        for j,x in enumerate([.25,1.75,2.25,3.75]):put('Wood and air',hat[:3000],sec(b+x),.008,(-1)**j*.25)
    # Sparse mid-bass punctuation replaces the preceding tracks' continuous bass ostinato.
    for x,semi in [(.75,0),(2.5,7)]:
        note=39+shift+semi;tt=np.arange(round(.3*SR))/SR;f=440*2**((note-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.4*np.sin(4*np.pi*f*tt))*np.exp(-tt*9)*np.minimum(tt/.01,1)*np.minimum((.3-tt)/.04,1)
        put('Short bass',z,sec(b+x),.05)
    # The pack's actual chord sample carries the harmony; no synthesized chord/lead layers.
    if bar%2==0 or bar%8==3:
        z=pitched(chord,shift)
        put('Sampled chord washes',z,sec(b+.25),.055,-.16)
        put('Sampled chord washes',z,sec(b+.25)+.61,.011,.28)
    if bar%4==2:
        z=soften(pitched(chord,shift)[::-1],1.2)
        put('Reverse textures',z,sec(b+2),.016,.3)
stems['Machinedrum groove']=eq(stems['Machinedrum groove'],90,-8,-3,9500)
stems['Short bass']=eq(stems['Short bass'],85,-5,-2,5000)
stems['Sampled chord washes']=eq(stems['Sampled chord washes'],260,-1,-4,7000)
stems['Wood and air']=eq(stems['Wood and air'],350,0,-4,8000)
stems['Reverse textures']=eq(stems['Reverse textures'],400,0,-5,6000)
tt=np.arange(N)/SR;beat=110*tt/60+2*tt*tt/3600
duck=1-.12*np.exp(-(beat%1)*10)
stems['Sampled chord washes']*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-07-Sample-Groove-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Sample Groove House.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(110*s/60+2*s*s/3600),bpm=str(110+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':110,'bpm_end':114,'samples':sources,'synthesized':['sparse mid-bass only; harmony and textures from pack samples'],'analysis':stats(mix*gain),'purpose':'Sample-based house trivia; Machinedrum kit, sampled Eb chord, woodblock/tom/air accents, asymmetric harmony and sparse bass','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
