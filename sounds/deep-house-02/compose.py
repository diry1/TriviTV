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
stems={k:np.zeros((N,2)) for k in ['Vintage drums','Muted bass','Cm9 chord samples','Conga conversation','Distant chord tails']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 909 House Vinyl SP.wav')
clap=sample('Clap House Vinyl SP 01.wav')
hat=sample('CH Vintage Drag Vinyl SP.wav')
openhat=sample('OH House Vinyl SP.wav')
muted=sample('Conga Vintage Muted Vinyl SP.wav')
opened=sample('Conga Vintage Open Vinyl SP.wav')
shaker=sample('Shaker House Vinyl SP.wav')
chord=sample('FX House Chord Vinyl SP Cm9.wav')
def sec(b):return 15*(-113+np.sqrt(113**2+8*b)) # 113 to 117 BPM in 60s
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
def transpose(z,n):
    return np.interp(np.arange(0,len(z),2**(n/12)),np.arange(len(z)),z)
def taper(z,d):
    z=z[:int(d*SR)].copy();m=min(1500,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=taper(chord,3.2)
# Sampled minor-ninth harmony, long C pedal then Ab/F responses, unlike prior four-chord synth beds.
shifts=[0,0,0,0,-4,-4,5,0]
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    for x in [0,1,2,3]:put('Vintage drums',kick[:15000],sec(b+x),.082)
    for x in [1.015,3.015]:put('Vintage drums',clap[:12500],sec(b+x),.031,-.08)
    for j,x in enumerate([.53,1.53,2.53,3.53]):put('Vintage drums',hat[:4500],sec(b+x),.023 if j%2 else .019,.24)
    if bar%2:put('Vintage drums',openhat[:8000],sec(b+3.53),.009,-.2)
    for j,x in enumerate([.75,2.25] if bar%2==0 else [1.75,3.25]):
        z=muted if j==0 else opened
        put('Conga conversation',z[:14000],sec(b+x),.026 if j==0 else .019,(-1)**j*.3)
    for x in [.25,2.75]:put('Conga conversation',shaker[:5000],sec(b+x),.008,-.2)
    if t>43:
        for x in [1.25,3.75]:put('Conga conversation',shaker[:3500],sec(b+x),.008,.2)
    root=48+shift
    for x,n,d in [(.5,root,.31),(2.5,root,.3),(3.25,root+7,.18)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.32*np.sin(4*np.pi*f*tt))*np.exp(-tt*7)*np.minimum(tt/.012,1)*np.minimum((d-tt)/.045,1)
        put('Muted bass',z,sec(b+x),.048)
    z=transpose(chord,shift)
    if bar%2==0:
        put('Cm9 chord samples',z,sec(b+.75),.052,-.13)
        put('Cm9 chord samples',z,sec(b+.75)+.52,.010,.24)
    else:
        put('Cm9 chord samples',taper(z,.65),sec(b+2.75),.034,.1)
    if bar%4==3:
        tail=taper(z[::-1],1.45)
        put('Distant chord tails',tail,sec(b+1.5),.012,-.25)
stems['Vintage drums']=eq(stems['Vintage drums'],80,-7,-3.5,9000)
stems['Muted bass']=eq(stems['Muted bass'],80,-5,-2,5000)
stems['Cm9 chord samples']=eq(stems['Cm9 chord samples'],280,-1,-3.5,7500)
stems['Conga conversation']=eq(stems['Conga conversation'],230,0,-4,8000)
stems['Distant chord tails']=eq(stems['Distant chord tails'],400,0,-5,6000)
tt=np.arange(N)/SR;beat=113*tt/60+2*tt*tt/3600
duck=1-.15*np.exp(-(beat%1)*12)
stems['Cm9 chord samples']*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-08-Deep-Vintage-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Deep Vintage House.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(113*s/60+2*s*s/3600),bpm=str(113+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':113,'bpm_end':117,'samples':sources,'synthesized':['muted mid-bass only; Cm9 harmony and textures from pack samples'],'analysis':stats(mix*gain),'purpose':'Deep vintage house trivia bed; Vintage House sampled drums and congas, sampled Cm9 harmony with long C pedal, subtle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
