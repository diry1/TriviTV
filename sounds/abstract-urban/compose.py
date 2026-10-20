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
stems={k:np.zeros((N,2)) for k in ['Broken tape drums','Muted bass','Chord fragments','Found percussion','Dust textures']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD Club Smack Vinyl SP 02.wav')
snare=sample('SD Tape Res Vinyl SP.wav')
hat=sample('CH Tape Snap Vinyl SP 01.wav')
rim=sample('Rim Tape Skin Vinyl SP.wav')
glitch=sample('Perc Tape Glitch Vinyl SP 01.wav')
shaker=sample('Shaker Acoustic Slap Vinyl SP.wav')
breath=sample('FX Vox Breath Vinyl SP.wav')
chord=sample('FX Club Chord Vinyl SP 02.wav')
def sec(b):return 15*(-82+np.sqrt(82**2+8*b)) # 82 to 86 BPM in 60s
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
# The unlabelled chord is treated as an abstract texture, not assigned an unverified key.
chord=transpose(chord,-5)
for bar in range(22):
    b=bar*4;t=sec(b)
    if t>=60:break
    pattern=bar%4
    kicks=[[0,1.65,2.75],[0,.85,2.5],[0,1.75,2.65,3.5],[.15,2,2.85]][pattern]
    for j,x in enumerate(kicks):put('Broken tape drums',kick[:13000],sec(b+x),.075 if j==0 else .055)
    for x in [1.055,3.07]:put('Broken tape drums',snare[:15000],sec(b+x),.033,-.08)
    for j in range(8):
        if j==4 and pattern==2:continue
        x=j*.5+(.10 if j%2 else 0)
        put('Broken tape drums',hat[:3500],sec(b+x),.010 if j%2==0 else .018,.23)
    if pattern in [1,3]:put('Broken tape drums',snare[:4500],sec(b+2.82),.006,-.12)
    for j,x in enumerate([.8,2.3] if pattern<2 else [1.8,3.65]):
        put('Found percussion',rim[:6000],sec(b+x),.012,(-1)**j*.35)
    put('Found percussion',cut(glitch,.18),sec(b+3.35),.012,-.3)
    if t>42:
        for x in [.3,1.8,2.3,3.8]:put('Found percussion',shaker[:4200],sec(b+x),.009, .2)
    # Low melodic density: single C/G punctuation, not another house bass ostinato.
    for x,n in ([(.2,48),(2.65,55)] if pattern%2==0 else [(.85,48),(2.5,46)]):
        d=.27;tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.17*np.sin(4*np.pi*f*tt))*np.exp(-tt*8)*np.minimum(tt/.014,1)*np.minimum((d-tt)/.045,1)
        put('Muted bass',z,sec(b+x),.033)
    # Different source offsets and lengths give a chopped collage rather than a repeated lead.
    offset=int([.0,.13,.27,.07][pattern]*SR)
    fragment=cut(chord[offset:], [.42,.23,.65,.31][pattern])
    for j,x in enumerate([[.45,2.2],[1.6],[.3,3.35],[2.45]][pattern]):
        z=fragment if j==0 else fragment[::-1].copy()
        z=cut(z,.5)
        put('Chord fragments',z,sec(b+x),.028,(-1)**pattern*.23)
        put('Dust textures',z,sec(b+x)+.51,.005,(-1)**(pattern+1)*.3)
    if pattern==3:put('Dust textures',cut(breath,.7),sec(b+2.3),.007,-.25)
stems['Broken tape drums']=eq(stems['Broken tape drums'],90,-8,-4,8500)
stems['Muted bass']=eq(stems['Muted bass'],90,-6,-2,4500)
stems['Chord fragments']=eq(stems['Chord fragments'],350,-2,-5,6000)
stems['Found percussion']=eq(stems['Found percussion'],500,0,-5,7000)
stems['Dust textures']=eq(stems['Dust textures'],600,0,-7,4000)
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-Urban-01-Abstract-Hip-Hop-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Abstract Urban.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(82*s/60+2*s*s/3600),bpm=str(82+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':82,'bpm_end':86,'samples':sources,'synthesized':['sparse mid-bass; all other parts use pack samples'],'analysis':stats(mix*gain),'purpose':'Abstract hip hop urban trivia bed; broken tape beat, chopped unpitched chord collage, found percussion and subtle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
