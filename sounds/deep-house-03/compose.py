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
stems={k:np.zeros((N,2)) for k in ['LM1 drums','Soft bass','A chord cuts','Cabasa and rim','Dub echoes']}
sources={}; rng=np.random.default_rng(6128)
def sample(name):
    p=next(ROOT.rglob(name)); sources[name]=str(p); shutil.copy2(p,P/'samples'/name)
    z=readwav(p); return z/max(abs(z).max(),1e-9)
kick=sample('BD LM1 Vinyl SP Clean 02.wav')
snare=sample('SD LM1 Vinyl SP 02.wav')
hat=sample('CH LM1 Standard Vinyl SP 02.wav')
rim=sample('Rim LM1 Vinyl SP 02.wav')
cabasa=sample('Cabasa LM1 Vinyl SP 01.wav')
tamb=sample('Tamb LM1 Vinyl SP 01.wav')
chord=sample('FX Mellow Chord Vinyl SP A.wav')
def sec(b):return 15*(-115+np.sqrt(115**2+8*b)) # 115 to 119 BPM in 60s
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
    z=z[:int(d*SR)].copy();m=min(1800,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=cut(chord,2.6)
# A-centered two-chord dialogue with a contrasting D turnaround every eight bars.
shifts=[0,0,0,0,-2,-2,-2,5]
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    for x,g in [(0,.076),(1,.064),(2,.076),(3,.064)]:put('LM1 drums',kick[:15000],sec(b+x),g)
    for x in [1.02,3.02]:put('LM1 drums',snare[:11500],sec(b+x),.028,-.08)
    for j,x in enumerate([.56,1.56,2.56,3.56]):put('LM1 drums',hat[:4200],sec(b+x),.019 if j%2 else .023,.25)
    # Sparse rim answers and brushed cabasa replace the preceding conga conversation.
    for j,x in enumerate([.75,2.75] if bar%2==0 else [1.75,3.25]):
        put('Cabasa and rim',rim[:5500],sec(b+x),.014,(-1)**j*.3)
    for x in [.3,1.3,2.3,3.3]:put('Cabasa and rim',cabasa[:7000],sec(b+x),.009,-.25)
    if t>43:
        for x in [1.56,3.56]:put('Cabasa and rim',tamb[:7000],sec(b+x),.009,.18)
    root=45+shift
    for x,n,d in [(.56,root,.3),(1.8,root+7,.18),(2.56,root,.34)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*6)*np.minimum(tt/.014,1)*np.minimum((d-tt)/.05,1)
        put('Soft bass',z,sec(b+x),.047)
    z=transpose(chord,shift)
    positions=[.25,2.75] if bar%2==0 else [1.5]
    for j,x in enumerate(positions):
        short=cut(z,.9 if j==0 else .5)
        put('A chord cuts',short,sec(b+x),.046,(-1)**j*.12)
        # Darkening stereo echoes rather than a lead melody or reversed chord swell.
        for delay,g,pan in [(.39,.010,.3),(.78,.005,-.3),(1.17,.002,.2)]:
            put('Dub echoes',short,sec(b+x)+delay,g,pan)
stems['LM1 drums']=eq(stems['LM1 drums'],100,-10,-3.5,9000)
stems['Soft bass']=eq(stems['Soft bass'],85,-7,-2,5000)
stems['A chord cuts']=eq(stems['A chord cuts'],280,-1,-3.5,7000)
stems['Cabasa and rim']=eq(stems['Cabasa and rim'],400,0,-4.5,7500)
stems['Dub echoes']=eq(stems['Dub echoes'],500,0,-6,4500)
tt=np.arange(N)/SR;beat=115*tt/60+2*tt*tt/3600
duck=1-.13*np.exp(-(beat%1)*12)
stems['A chord cuts']*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-09-Deep-Dub-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Deep Dub House.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
for s in range(61):ET.SubElement(seq,'TEMPO',startBeat=str(115*s/60+2*s*s/3600),bpm=str(115+s/15),curve='1.0')
for i,k in enumerate(stems):
    tr=ET.SubElement(edit,'TRACK',id=str(4000+i*10),name=k,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0'][i]);ET.SubElement(tr,'MODIFIERS')
    ET.SubElement(tr,'AUDIOCLIP',name=k,start='0.0',length='60.0',offset='0.0',id=str(4001+i*10),source=str(P/(k+'.wav')),sync='0',pan='0.0',proxyAllowed='1',resamplingQuality='lagrange')
    ET.SubElement(tr,'PLUGIN',type='volume',id=str(4002+i*10),enabled='1',volume='0.6376281380653381');ET.SubElement(tr,'PLUGIN',type='level',id=str(4003+i*10),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
tree.write(target,encoding='utf-8',xml_declaration=True)
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':115,'bpm_end':119,'samples':sources,'synthesized':['soft mid-bass only; A-centered sampled chord and processed delay textures'],'analysis':stats(mix*gain),'purpose':'Deep dub house trivia bed; LM1 sample kit, sampled A chord cuts, dark stereo echoes, cabasa/rim and gentle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
