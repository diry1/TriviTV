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
stems={k:np.zeros((N,2)) for k in ['Disco drums','Octave bass','Retro arpeggio','Analog chords','Soft lead']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 808 Warm Vinyl SP.wav')
rim=sample('Clap 808 Standard Vinyl SP.wav')
conga=sample('CH 808 Standard Vinyl SP 01.wav')
clave=sample('OH 808 Standard Vinyl SP 01.wav')
maraca=sample('Maraca 808 Vinyl SP 01.wav')
def sec(b):return 15*(-112+np.sqrt(112**2+8*b)) # 112 to 116 BPM in 60s
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
def analog(note,dur,kind):
    tt=np.arange(round(SR*dur))/SR; f=440*2**((note-69)/12)
    env=np.minimum(tt/.012,1)*np.minimum((dur-tt)/.06,1)
    if kind=='bass':
        z=sum(np.sin(2*np.pi*f*h*tt)/h**1.7 for h in range(1,6))*np.exp(-tt*7)
    elif kind=='chord':
        z=sum((np.sin(2*np.pi*f*h*tt)+np.sin(2*np.pi*f*1.002*h*tt))*.5/h**1.8 for h in range(1,7))*np.exp(-tt*1.5)
    else:
        z=(np.sin(2*np.pi*f*tt+.3*np.sin(2*np.pi*5*tt))+.18*np.sin(4*np.pi*f*tt))*np.exp(-tt*(7 if kind=='arp' else 2.5))
    return z*env
chords=[[62,65,69,72],[58,62,65,69],[65,69,72,76],[60,64,67,70]]
roots=[38,34,41,36]
for bar in range(29):
    beat=bar*4;t=sec(beat)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Disco drums',kick[:16000],sec(beat+x),.082)
    for x in [1,3]:put('Disco drums',rim[:12500],sec(beat+x),.038,-.06)
    for j in range(8):put('Disco drums',conga[:4200],sec(beat+j*.5),.014 if j%2==0 else .023,.22)
    if bar%2==1:put('Disco drums',clave[:7500],sec(beat+3.5),.011,-.22)
    for j in range(8):
        note=roots[c]+(12 if j%2 else 0)
        if j==7 and bar%2:note+=7
        put('Octave bass',analog(note,.21,'bass'),sec(beat+j*.5),.052 if j%2 else .063)
    for x in [0,2]:
        for j,n in enumerate(chords[c]):put('Analog chords',analog(n,1.05,'chord'),sec(beat+x),.021,(j-1.5)*.16)
    order=[0,2,1,3,2,1,3,1]
    for j,ix in enumerate(order):
        if bar%4==3 and j in [2,6]:continue
        z=analog(chords[c][ix]+12,.36,'arp');pan=(-1)**j*.22
        put('Retro arpeggio',z,sec(beat+j*.5+.25),.019,pan)
        put('Retro arpeggio',z,sec(beat+j*.5+.25)+.27,.004,-pan)
    if bar%4 in [1,3]:
        for j,(x,n) in enumerate([(1,chords[c][2]+12),(2.5,chords[c][1]+12)]):
            put('Soft lead',analog(n,.75,'lead'),sec(beat+x),.018,(-1)**j*.15)
    if t>43:
        for x in [.25,1.75,2.25,3.75]:put('Disco drums',maraca[:3200],sec(beat+x),.007,-.2)
stems['Disco drums']=eq(stems['Disco drums'],62,-5,-3,10000)
stems['Octave bass']=eq(stems['Octave bass'],68,-4,-2,5000)
stems['Analog chords']=eq(stems['Analog chords'],220,0,-3,8500)
stems['Retro arpeggio']=eq(stems['Retro arpeggio'],350,0,-4,8000)
stems['Soft lead']=eq(stems['Soft lead'],350,0,-3,6500)
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-Trivia-04-Italo-Disco-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Italo Disco.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(112*s/60+2*s*s/3600),bpm=str(112+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':112,'bpm_end':116,'samples':sources,'synthesized':['octave bass','analog synth chords','retro arpeggio','soft lead'],'analysis':stats(mix*gain),'purpose':'Italo disco trivia question bed; octave bass and retro arpeggio with gentle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
