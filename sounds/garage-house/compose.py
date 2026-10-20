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
stems={k:np.zeros((N,2)) for k in ['Garage drums','Syncopated bass','Chord replies','Warm stabs','Soft air']}
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
chords=[[60,63,67,70],[56,60,63,67],[58,62,65,68],[55,58,62,65]]
roots=[48,44,46,43]
def stab(note,dur):
    tt=np.arange(round(SR*dur))/SR;f=440*2**((note-69)/12)
    z=np.sin(2*np.pi*f*tt)+.28*np.sin(4*np.pi*f*tt)+.09*np.sin(6*np.pi*f*tt)
    return z*np.minimum(tt/.018,1)*np.exp(-tt*5.5)*np.minimum((dur-tt)/.065,1)
for bar in range(31):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Garage drums',kick[:15000],sec(b+x),.083)
    for x in [1.015,3.015]:put('Garage drums',rim[:11500],sec(b+x),.039,-.06)
    for j in range(8):
        x=j*.5+(.085 if j%2 else 0)
        put('Garage drums',conga[:4000],sec(b+x),.009 if j%2==0 else .025,.24)
    for x in [1.585,3.585]:put('Garage drums',clave[:6800],sec(b+x),.011,-.2)
    # Quiet ghost claps and shakers provide shuffle rather than a lead motif.
    if bar%2==1:put('Garage drums',rim[:6500],sec(b+2.82),.008,-.12)
    for x in [.83,2.83]:put('Garage drums',maraca[:3300],sec(b+x),.006,-.28)
    if t>43:
        for x in [.33,1.83,2.33,3.83]:put('Garage drums',maraca[:3000],sec(b+x),.007,.2)
    for x,semi,d in [(.585,0,.24),(1.33,7,.16),(1.83,12,.2),(2.585,0,.27),(3.33,10,.17),(3.83,7,.15)]:
        put('Syncopated bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.049)
    for x in [.33,1.585,2.83]:
        for j,n in enumerate(chords[c]):
            z=stab(n,.58)
            put('Warm stabs',z,sec(b+x),.029,(j-1.5)*.16)
            put('Warm stabs',z,sec(b+x)+.38,.003,-(j-1.5)*.16)
    if bar%4 in [1,3]:
        for j,n in enumerate(chords[c][1:]):
            put('Chord replies',stab(n,.38),sec(b+3.33),.020,(j-1)*.2)
    for j,n in enumerate(chords[c][:3]):
        d=min(2.8,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        put('Soft air',np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)**2,t,.005,(j-1)*.25)
stems['Garage drums']=eq(stems['Garage drums'],65,-5,-3.5,9000)
stems['Syncopated bass']=eq(stems['Syncopated bass'],76,-4,-2,5000)
stems['Warm stabs']=eq(stems['Warm stabs'],230,0,-3.5,7500)
stems['Chord replies']=eq(stems['Chord replies'],260,0,-3.5,7000)
stems['Soft air']=eq(stems['Soft air'],350,0,-4,6000)
tt=np.arange(N)/SR;beat=120*tt/60+2*tt*tt/3600
duck=1-.17*np.exp(-(beat%1)*12)
for k in ['Warm stabs','Soft air']:stems[k]*=duck[:,None]
fade=np.ones(N);fade[:4800]=np.linspace(0,1,4800);fade[-12000:]=np.linspace(1,0,12000)
for k in stems:stems[k]*=fade[:,None]
mix=sum(stems.values())
# Match conservative clean draft RMS, with peak headroom; no sub-bass boost.
gain=min(10**(-25/20)/np.sqrt(np.mean(mix*mix)),.52/abs(mix).max())
for k,z in stems.items():save(P/(k+'.wav'),z*gain)
master=BASE/'sounds/TriviTV-House-06-Garage-60s-v1.wav';save(master,mix*gain)
tree=ET.parse(BASE/'sounds/trivia-clean-v2/TriviTV Trivia Clean v2.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Garage House.tracktionedit';edit.set('projectID',str(target))
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
report={'duration':60,'sample_rate':SR,'bit_depth':24,'bpm_start':120,'bpm_end':124,'samples':sources,'synthesized':['syncopated bass','warm chord stabs','midrange chord replies','soft air'],'analysis':stats(mix*gain),'purpose':'Garage house trivia bed; shuffled hats, syncopated bass, warm midrange stabs and gentle late lift','method':'Scripted composition/rendering; separate processed stems in Waveform'}
(P/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
