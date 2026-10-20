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
stems={k:np.zeros((N,2)) for k in ['Soft drums','Warm bass','Floating notes','Electric keys','Cloud pad']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 808 Warm Vinyl SP.wav')
rim=sample('Clap 808 Standard Vinyl SP.wav')
conga=sample('CH 808 Standard Vinyl SP 01.wav')
clave=sample('OH 808 Standard Vinyl SP 01.wav')
maraca=sample('Maraca 808 Vinyl SP 01.wav')
def sec(b):return 15*(-104+np.sqrt(104**2+8*b)) # 104 to 108 BPM in 60s
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
chords=[[62,66,69,73,76],[59,62,66,69,73],[55,59,62,66,69],[57,61,64,69,71]]
roots=[47,43,45,42]
def ep(n,d):
    tt=np.arange(round(SR*d))/SR;f=440*2**((n-69)/12)
    z=np.sin(2*np.pi*f*tt+.6*np.exp(-tt*6)*np.sin(2*np.pi*f*2*tt))
    z+=.1*np.sin(2*np.pi*f*3*tt)*np.exp(-tt*9)
    return z*np.minimum(tt/.018,1)*np.exp(-tt*2)*np.minimum((d-tt)/.12,1)
for bar in range(27):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Soft drums',kick[:15000],sec(b+x),.063)
    for x in [1,3]:put('Soft drums',rim[:11000],sec(b+x),.023,-.1)
    for x in [.54,1.54,2.54,3.54]:put('Soft drums',conga[:4200],sec(b+x),.017,.22)
    if bar%2==1:put('Soft drums',clave[:7500],sec(b+3.54),.008,-.2)
    if t>43:
        for x in [.25,1.75,2.25,3.75]:put('Soft drums',maraca[:3200],sec(b+x),.006,-.25)
    for x,semi,d in [(.5,0,.4),(1.75,7,.28),(2.5,0,.4),(3.5,12,.25)]:
        put('Warm bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.044)
    for x in [.25,2.5]:
        for j,n in enumerate(chords[c]):
            z=ep(n,1.6)
            put('Electric keys',z,sec(b+x),.021,(j-2)*.16)
            put('Electric keys',z,sec(b+x)+.43,.004,-(j-2)*.16)
    if bar%2==0:
        for j,x in enumerate([1.25,3]):
            z=ep(chords[c][2+j]+12,1.3)
            put('Floating notes',z,sec(b+x),.018,(-1)**j*.3)
            put('Floating notes',z,sec(b+x)+.65,.004,(-1)**(j+1)*.3)
    for j,n in enumerate(chords[c][:4]):
        d=min(3,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n+12-69)/12)
        z=(np.sin(2*np.pi*f*tt)+np.sin(2*np.pi*f*1.0015*tt))*.5*np.sin(np.pi*tt/d)**2
        put('Cloud pad',z,t,.008,(j-1.5)*.18)
stems['Soft drums']=eq(stems['Soft drums'],65,-5,-4,8500)
stems['Warm bass']=eq(stems['Warm bass'],75,-4,-2,5000)
stems['Electric keys']=eq(stems['Electric keys'],230,0,-3,8000)
stems['Floating notes']=eq(stems['Floating notes'],400,0,-4,7500)
stems['Cloud pad']=eq(stems['Cloud pad'],400,0,-4,6000)
tt=np.arange(N)/SR;beat=104*tt/60+2*tt*tt/3600
duck=1-.13*np.exp(-(beat%1)*10)
for k in ['Electric keys','Cloud pad']:stems[k]*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-04-Chillhouse-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Chillhouse.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(104*s/60+2*s*s/3600),bpm=str(104+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':104,'bpm_end':108,'samples':sources,'synthesized':['warm bass','electric-piano-style keys','floating notes','cloud pad'],'analysis':stats(mix*gain),'purpose':'Chillhouse trivia question bed; spacious electric keys, soft drums, restrained bass and subtle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
