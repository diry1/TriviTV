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
stems={k:np.zeros((N,2)) for k in ['Soul drums','Warm bass','Chord responses','Warm chords','Breath pad']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 808 Warm Vinyl SP.wav')
rim=sample('Clap 808 Standard Vinyl SP.wav')
conga=sample('CH 808 Standard Vinyl SP 01.wav')
clave=sample('OH 808 Standard Vinyl SP 01.wav')
maraca=sample('Maraca 808 Vinyl SP 01.wav')
def sec(b):return 15*(-116+np.sqrt(116**2+8*b)) # 116 to 120 BPM in 60s
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
chords=[[58,62,65,69,72],[55,58,62,65,69],[60,64,67,70,74],[53,57,60,64,67]]
roots=[46,43,48,41]
def warm(n,d):
    tt=np.arange(round(SR*d))/SR;f=440*2**((n-69)/12)
    z=(np.sin(2*np.pi*f*tt)+.22*np.sin(2*np.pi*f*2.001*tt)+.08*np.sin(2*np.pi*f*3*tt))
    env=np.minimum(tt/.045,1)*np.exp(-tt*1.9)*np.minimum((d-tt)/.12,1)
    return z*env
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Soul drums',kick[:15500],sec(b+x),.085)
    for x in [1,3]:put('Soul drums',rim[:12000],sec(b+x),.037,-.08)
    for j in range(8):
        x=j*.5+(.045 if j%2 else 0)
        put('Soul drums',conga[:4000],sec(b+x),.01 if j%2==0 else .023,.22)
    if bar%2==1:put('Soul drums',clave[:7500],sec(b+3.545),.012,-.18)
    for x in [.75,2.75]:put('Soul drums',maraca[:4500],sec(b+x),.007,-.28)
    if t>42:
        for x in [.25,1.75,2.25,3.75]:put('Soul drums',maraca[:3200],sec(b+x),.006,.22)
    for x,semi,d in [(.5,0,.32),(1.25,7,.2),(1.75,12,.23),(2.5,0,.32),(3.25,7,.22)]:
        put('Warm bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.05)
    # Midrange chord voicings, with breathing space; no high repeated alarm-like motif.
    for x in [.25,2.5]:
        for j,n in enumerate(chords[c]):
            z=warm(n,1.3)
            put('Warm chords',z,sec(b+x),.025,(j-2)*.14)
            put('Warm chords',z,sec(b+x)+.39,.003,-(j-2)*.14)
    if bar%4 in [1,3]:
        for j,n in enumerate(chords[c][1:4]):
            put('Chord responses',warm(n,.72),sec(b+3.25),.018,(j-1)*.22)
    for j,n in enumerate(chords[c][:3]):
        d=min(3,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.08*np.sin(2*np.pi*f*2*tt))*np.sin(np.pi*tt/d)**2
        put('Breath pad',z,t,.006,(j-1)*.25)
stems['Soul drums']=eq(stems['Soul drums'],65,-5,-3.5,9000)
stems['Warm bass']=eq(stems['Warm bass'],75,-4,-2,5000)
stems['Warm chords']=eq(stems['Warm chords'],230,0,-3,7500)
stems['Chord responses']=eq(stems['Chord responses'],250,0,-3,7500)
stems['Breath pad']=eq(stems['Breath pad'],300,0,-4,6000)
tt=np.arange(N)/SR;beat=116*tt/60+2*tt*tt/3600
duck=1-.16*np.exp(-(beat%1)*12)
for k in ['Warm chords','Breath pad']:stems[k]*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-05-Soulful-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Soulful House.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(116*s/60+2*s*s/3600),bpm=str(116+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':116,'bpm_end':120,'samples':sources,'synthesized':['warm bass','warm chord voicings','midrange chord responses','breath pad'],'analysis':stats(mix*gain),'purpose':'Soulful house trivia bed; warm midrange harmony, swung percussion, no high repeating motif, gentle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
