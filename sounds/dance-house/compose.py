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
stems={k:np.zeros((N,2)) for k in ['Dance drums','Bouncy bass','Piano hook','Bright chords','Air pad']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 808 Warm Vinyl SP.wav')
rim=sample('Clap 808 Standard Vinyl SP.wav')
conga=sample('CH 808 Standard Vinyl SP 01.wav')
clave=sample('OH 808 Standard Vinyl SP 01.wav')
maraca=sample('Maraca 808 Vinyl SP 01.wav')
def sec(b):return 15*(-120+np.sqrt(120**2+8*b)) # 120 to 124 BPM in 60s
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
chords=[[60,64,67,71],[55,59,62,69],[57,60,64,67],[53,57,60,64]]
roots=[48,43,45,41]
def piano(n,d):
    tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
    z=sum(np.sin(2*np.pi*f*h*tt)*np.exp(-tt*(3+h*.9))/h**1.7 for h in range(1,7))
    return z*np.minimum(tt/.006,1)*np.minimum((d-tt)/.04,1)
for bar in range(31):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Dance drums',kick[:15000],sec(b+x),.09)
    for x in [1,3]:put('Dance drums',rim[:12000],sec(b+x),.042,-.06)
    for j in range(8):put('Dance drums',conga[:3800],sec(b+j*.5),.012 if j%2==0 else .026,.2)
    for x in [1.5,3.5]:put('Dance drums',clave[:7000],sec(b+x),.013,-.17)
    if t>42:
        for x in [.25,1.75,2.25,3.75]:put('Dance drums',maraca[:3200],sec(b+x),.009,-.25)
    for x,semi in [(.5,0),(1.25,7),(1.75,12),(2.5,0),(3.25,7),(3.75,12)]:
        put('Bouncy bass',voice(roots[c]+semi,.22,'bass'),sec(b+x),.052)
    for x in [.5,1.75,2.5,3.5]:
        for j,n in enumerate(chords[c]):
            z=piano(n,.7)
            put('Bright chords',z,sec(b+x),.024,(j-1.5)*.17)
            put('Bright chords',z,sec(b+x)+.375,.003,-(j-1.5)*.17)
    positions=[.25,1.5,2.75] if bar%2==0 else [.75,2.25]
    for j,x in enumerate(positions):
        n=chords[c][[2,3,1][j]]+12
        z=piano(n,.6)
        put('Piano hook',z,sec(b+x),.023,(-1)**j*.25)
        put('Piano hook',z,sec(b+x)+.375,.004,(-1)**(j+1)*.25)
    for j,n in enumerate(chords[c][:3]):
        d=min(2.5,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n+12-69)/12)
        put('Air pad',np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)**2,t,.005,(j-1)*.3)
stems['Dance drums']=eq(stems['Dance drums'],65,-5,-3,10000)
stems['Bouncy bass']=eq(stems['Bouncy bass'],75,-4,-2,5000)
stems['Bright chords']=eq(stems['Bright chords'],220,0,-3,8500)
stems['Piano hook']=eq(stems['Piano hook'],350,0,-3,8000)
stems['Air pad']=eq(stems['Air pad'],400,0,-3,6500)
tt=np.arange(N)/SR;beat=120*tt/60+2*tt*tt/3600
duck=1-.24*np.exp(-(beat%1)*12)
for k in ['Bright chords','Air pad']:stems[k]*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-02-Dance-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Dance House.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(120*s/60+2*s*s/3600),bpm=str(120+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':120,'bpm_end':124,'samples':sources,'synthesized':['bouncy bass','piano-style chords','piano hook','air pad'],'analysis':stats(mix*gain),'purpose':'Dance house trivia question bed; brighter piano groove, restrained bass and gentle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
