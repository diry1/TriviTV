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
stems={k:np.zeros((N,2)) for k in ['Island percussion','Light bass','Mallet melody','Offbeat chords','Seaside air']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD 808 Air Vinyl SP.wav')
rim=sample('Rim 808 Standard Vinyl SP.wav')
conga=sample('Conga 808 Lo Vinyl SP Clean 02.wav')
clave=sample('Clave 808 Standard Vinyl SP.wav')
maraca=sample('Maraca 808 Vinyl SP 01.wav')
def sec(b):return 10*(-94+np.sqrt(94**2+12*b)) # 94 to 100 BPM in 60s
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
chords=[[65,69,72,76],[62,65,69,72],[58,62,65,69],[60,65,67,72]]
roots=[41,38,34,36]
phrases=[[77,81,79,76],[77,74,72,69],[74,77,76,72],[76,79,77,72]]
for bar in range(25):
    b=bar*4; t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x,g in [(0,.12),(2,.09),(3.5,.04)]:put('Island percussion',kick,sec(b+x),g)
    for x in [1,3]:put('Island percussion',rim[:12000],sec(b+x),.044,-.12)
    for j,x in enumerate([.75,1.5,2.75,3.5]):
        z=conga if j%2 else np.interp(np.arange(len(conga))*1.25,np.arange(len(conga)),conga,right=0)
        put('Island percussion',z[:18000],sec(b+x),.045 if j%2 else .033,(-1)**j*.3)
    for x in ([0,1.5,3] if bar%2==0 else [1,2.5]):put('Island percussion',clave[:8000],sec(b+x),.019,.28)
    for j in range(8):
        put('Island percussion',maraca[:6500],sec(b+j*.5+.025*(j%2)),.014 if j%2 else .008,-.3)
    if t>42:
        for x in [.25,1.75,2.25,3.75]:put('Island percussion',maraca[:4000],sec(b+x),.010,.2)
    for x,n in [(0,roots[c]),(1.75,roots[c]+7),(2.5,roots[c]),(3.5,roots[c]+12)]:put('Light bass',voice(n,.38,'bass'),sec(b+x),.075)
    for x in [.5,1.5,2.5,3.5]:
        for j,n in enumerate(chords[c]):put('Offbeat chords',voice(n,.28,'chord'),sec(b+x),.017,(j-1.5)*.13)
    positions=[.25,1.5,2.25,3.5] if bar%2==0 else [.75,2.75]
    for j,x in enumerate(positions):
        note=phrases[c][j] if bar<16 else phrases[c][(j+1)%4]
        z=voice(note,.9,'mallet');pan=(-1)**j*.22
        put('Mallet melody',z,sec(b+x),.042,pan)
        put('Mallet melody',z,sec(b+x)+.36,.007,-pan)
# Quiet original surf-like air, no stock recording: filtered noise with slow overlapping swells.
noise=rng.normal(0,1,(N,2))
air=eq(noise,600,0,-7,4200)
t=np.arange(N)/SR
swells=.45+.35*np.sin(2*np.pi*t/9.7+.4)**2+.2*np.sin(2*np.pi*t/15.3)**2
stems['Seaside air']=air*swells[:,None]*.0012
stems['Island percussion']=eq(stems['Island percussion'],60,-4,-3,10000)
stems['Light bass']=eq(stems['Light bass'],68,-4,-2,5000)
stems['Offbeat chords']=eq(stems['Offbeat chords'],190,0,-2,8500)
stems['Mallet melody']=eq(stems['Mallet melody'],300,0,-3,8500)
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-Trivia-02-Caribbean-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Caribbean.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(94*s/60+3*s*s/3600),bpm=str(94+s*.1),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':94,'bpm_end':100,'samples':sources,'synthesized':['bass','mallet keys','offbeat chords','surf-like air'],'analysis':stats(mix*gain),'purpose':'Caribbean/beach trivia question bed; gentle late percussion lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
