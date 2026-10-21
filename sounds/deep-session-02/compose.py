"""Amber Rooms: prepare a native Waveform sample arrangement in the background."""
from pathlib import Path
import numpy as np,soundfile as sf,json,math,ast
from scipy.signal import butter,sosfilt,resample_poly
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
PACK=Path(r'C:\Users\User\Downloads\Torrents\All the Samples from Mars 2025 Update [Samples from Mars]')
SR=48000;BPM=118;BEAT=60/BPM;DURATION=256*BEAT
A=P/'voices';A.mkdir(parents=True,exist_ok=True);voices={};sources={};events=[]
# Reuse file/voice helpers only, without executing the previous arrangement.
code=ast.parse((P.parent/'deep-session-01/compose.py').read_text())
exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['filt','voice','sample','shift','event']],type_ignores=[]),'voice-helpers','exec'),globals())
voice('Smooth Machinedrum kick',filt(sample('BD Machinedrum Smooth Vinyl SP.wav'),80,6200),.105)
voice('Mellow Perkons snare',filt(sample('SD Mellow Perkons.wav'),270,6500),.036,-.12)
hat=sample('CH Submerge 808 Loops 120.wav')
hat=resample_poly(hat,60,59) # 120 BPM source into 118 BPM grid; tiny drum pitch shift.
voice('Submerge 808 hats',filt(hat,950,7000),.025,.22)
voice('Acoustic air shaker',filt(sample('Shaker Acoustic Air Vinyl SP Clean 02.wav'),1200,7200),.016,-.22)
voice('Tite Perkons rim',filt(sample('Rim Tite Perkons Clean 02.wav'),650,5000),.022,.28)
voice('Thin Perkons open hat',filt(sample('OH Thin Perkons 02.wav'),1200,6800)[:11000],.012,-.15)
guit=filt(sample('FX Guit Tone Vinyl SP G.wav'),350,2200)
for semitone,label in [(4,'B'),(2,'A'),(0,'G')]:
    z=shift(guit,semitone);z=z[:min(len(z),int(.7*SR))]
    z*=np.minimum(np.arange(len(z))/(.028*SR),1)
    voice('Distant guitar '+label,z,.012,.18)
chords={'Bm':[59,62,66],'A':[57,61,64],'G':[55,59,62]}
for name,notes in chords.items():
    t=np.arange(int(.5*SR))/SR
    x=sum(np.sin(2*np.pi*440*2**((n-69)/12)*t)+.11*np.sin(4*np.pi*440*2**((n-69)/12)*t) for n in notes)/3
    env=(1-np.exp(-t/.020))*np.exp(-t/ .16)*np.minimum((.5-t)/.065,1)
    voice('Velvet '+name,filt(x*env,250,1500),.040,-.08)
    voice('Velvet echo '+name,filt(x*env,550,1000),.004,.24)
for note in [43,45,47,50,52,54]:
    t=np.arange(int(.32*SR))/SR;f=440*2**((note-69)/12)
    z=(np.sin(2*np.pi*f*t)+.22*np.sin(4*np.pi*f*t))*np.minimum(t/.015,1)*np.exp(-t*7)*np.minimum((.32-t)/.05,1)
    voice('Warm bass '+str(note),filt(z,76,1500),.050)
for bar in range(64):
    section=bar//16;b=bar*4;name=['Bm','A','G','A'][(bar//4)%4];root={'Bm':47,'A':45,'G':43}[name]
    for beat in [0,1,2,3]:event('01 Smooth kick','Smooth Machinedrum kick',(b+beat)*BEAT)
    for beat in [1.025,3.025]:event('02 Mellow backbeat','Mellow Perkons snare',(b+beat)*BEAT)
    # Repeating two-bar bass figure, with modest space in the third section.
    bass=[(.25,root),(.75,root),(2.25,root),(3.5,root+7)] if bar%2==0 else [(.25,root),(1.75,root+7),(2.75,root)]
    if section==2:bass=bass[:2]+bass[-1:]
    for beat,n in bass:event('05 Warm bass','Warm bass '+str(n),(b+beat)*BEAT)
    hits=[.5,2.5] if bar%2==0 else [1.5,3.25]
    if section==2 and bar%2==0:hits=[2.5]
    for beat in hits:
        event('06 Velvet groove chords','Velvet '+name,(b+beat)*BEAT)
        if section in [0,2]:event('07 Distant guitar and air','Velvet echo '+name,(b+beat+.75)*BEAT)
    if section in [1,3]:
        for beat in [.75,2.75]:event('04 Organic percussion','Acoustic air shaker',(b+beat)*BEAT)
    if section in [0,3] and bar%2:
        event('04 Organic percussion','Tite Perkons rim',(b+2.25)*BEAT)
    if section==1 and bar%4==3:event('04 Organic percussion','Thin Perkons open hat',(b+3.5)*BEAT)
    if section in [1,2] and bar%8==4:
        event('07 Distant guitar and air','Distant guitar '+('B' if name=='Bm' else name),(b+1.75)*BEAT)
for bar in range(0,64,8):event('03 Submerge hat loop','Submerge 808 hats',bar*4*BEAT)
tree=ET.parse(P.parent/'deep-session-01/TriviTV Deep Session 01 - Low Tide.tracktionedit');edit=tree.getroot()
target=P/'Amber Rooms.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
ET.SubElement(seq,'TEMPO',startBeat='0',bpm=str(BPM),curve='1')
edit.find('TRANSPORT').attrib.update(loopPoint1='0',loopPoint2=str(DURATION),position='0',looping='0')
edit.find('CLICKTRACK').set('enabled','0');ident=110000
for i,name in enumerate(sorted(set(e['track'] for e in events))):
    ident+=1;tr=ET.SubElement(edit,'TRACK',id=str(ident),name=name,solo='0',mute='0',colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0','ffd3a387','ff90a0da'][i]);ET.SubElement(tr,'MODIFIERS')
    for e in events:
        if e['track']!=name:continue
        ident+=1;ET.SubElement(tr,'AUDIOCLIP',name=e['voice'],start=str(e['start']),length=str(e['length']),offset='0',id=str(ident),source=str(A/(e['voice']+'.wav')),sync='0',pan='0',proxyAllowed='0',resamplingQuality='lagrange',fadeIn='0.002',fadeOut='0.005')
    ident+=1;ET.SubElement(tr,'PLUGIN',type='volume',id=str(ident),enabled='1',volume='0.6376281380653381')
    ident+=1;ET.SubElement(tr,'PLUGIN',type='level',id=str(ident),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
ET.indent(tree);tree.write(target,encoding='utf-8',xml_declaration=True)
data={'title':'Amber Rooms','duration':DURATION,'bpm':BPM,'key':'B minor','changes_seconds':[16*4*BEAT,32*4*BEAT,48*4*BEAT],'samples':sources,'events':events,'synthesized':'Soft simple triads and muted bass','status':'Draft 2 of 3, listening review pending'}
(P/'arrangement.json').write_text(json.dumps(data,indent=2));print(f'{target}: {len(events)} clips, {DURATION:.3f}s')
