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
stems={k:np.zeros((N,2)) for k in ['Boom bap drums','Simple bass','Warm sample phrase','Light percussion','Sample tails']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD Club Smack Vinyl SP 02.wav')
snare=sample('SD Tape Res Vinyl SP.wav')
hat=sample('CH Tape Snap Vinyl SP 01.wav')
rim=sample('Rim Tape Skin Vinyl SP.wav')
shaker=sample('Shaker Acoustic Slap Vinyl SP.wav')
chord=sample('FX Club Chord Vinyl SP 02.wav')
def sec(b):return 15*(-88+np.sqrt(88**2+8*b)) # 88 to 92 BPM in 60s
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
def cut(z,d):
    z=z[:int(d*SR)].copy();m=min(1000,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
# Straightforward two-bar boom-bap loop, with regular backbeats and no glitch/reverse effects.
chord=transpose(chord,-2)
for bar in range(23):
    b=bar*4;t=sec(b)
    if t>=60:break
    kicks=[0,1.5,2,2.75] if bar%2==0 else [0,.75,2,3.5]
    for j,x in enumerate(kicks):put('Boom bap drums',kick[:14000],sec(b+x),.085 if x in [0,2] else .055)
    for x in [1,3]:put('Boom bap drums',snare[:14000],sec(b+x),.042,-.05)
    for j in range(8):
        x=j*.5+(.035 if j%2 else 0)
        put('Boom bap drums',hat[:3800],sec(b+x),.014 if j%2==0 else .021,.18)
    for x in [.75,2.75]:put('Light percussion',shaker[:4500],sec(b+x),.007,-.2)
    if t>44:
        for x in [1.75,3.75]:put('Light percussion',rim[:5000],sec(b+x),.008,.2)
    # A short root/fifth bass pattern stays easy to follow.
    for x,n,d in [(0,48,.35),(1.5,48,.23),(2,48,.35),(3.5,55,.22)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.22*np.sin(4*np.pi*f*tt))*np.exp(-tt*6)*np.minimum(tt/.012,1)*np.minimum((d-tt)/.045,1)
        put('Simple bass',z,sec(b+x),.04)
    # Same warm, forward-played sample phrase repeats predictably every two bars.
    for x,d,g in ([(.25,.8,.038),(2.25,.5,.029)] if bar%2==0 else [(.25,.8,.038),(2.75,.5,.029)]):
        z=cut(chord,d)
        put('Warm sample phrase',z,sec(b+x),g,-.08)
        put('Sample tails',z,sec(b+x)+.38,.004,.2)
stems['Boom bap drums']=eq(stems['Boom bap drums'],85,-8,-3.5,9000)
stems['Simple bass']=eq(stems['Simple bass'],85,-6,-2,4500)
stems['Warm sample phrase']=eq(stems['Warm sample phrase'],300,-2,-4,6500)
stems['Light percussion']=eq(stems['Light percussion'],450,0,-4,7500)
stems['Sample tails']=eq(stems['Sample tails'],500,0,-6,4500)
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-Urban-02-Oldschool-Rap-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Oldschool Rap.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(88*s/60+2*s*s/3600),bpm=str(88+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':88,'bpm_end':92,'samples':sources,'synthesized':['sparse mid-bass; all other parts use pack samples'],'analysis':stats(mix*gain),'purpose':'Simple oldschool rap instrumental trivia bed; two-bar boom-bap loop, steady backbeats, simple bass and warm forward sample phrase','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
