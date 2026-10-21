"""Prepare processed sampler voices and a native Waveform clip arrangement.
Final mix is exported by Waveform. No tempo ramp or duplicated 60s master.
"""
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt,resample_poly
import xml.etree.ElementTree as ET
import json,math

P=Path(__file__).resolve().parent; ROOT=P.parents[1]
PACK=Path(r'C:\Users\User\Downloads\Torrents\All the Samples from Mars 2025 Update [Samples from Mars]')
SR=48000;DURATION=128;BPM=120
A=P/'voices';A.mkdir(exist_ok=True)
sources={};voices={};events=[]

def filt(x,hp=0,lp=0):
    if hp:x=sosfilt(butter(4,hp,fs=SR,btype='highpass',output='sos'),x)
    if lp:x=sosfilt(butter(3,lp,fs=SR,btype='lowpass',output='sos'),x)
    return x
def voice(name,x,gain,pan=0):
    x=np.asarray(x).copy();n=min(160,len(x)//5)
    x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    y=x[:,None]*np.array([math.sqrt((1-pan)/2),math.sqrt((1+pan)/2)])[None,:]*gain
    sf.write(A/(name+'.wav'),y,SR,subtype='PCM_24');voices[name]=y
def sample(name):
    p=next(p for p in PACK.rglob(name) if 'WAV' in p.parts)
    sources[name]=str(p);x,sr=sf.read(p,always_2d=True);x=x.mean(axis=1)
    x=resample_poly(x,SR//math.gcd(sr,SR),sr//math.gcd(sr,SR))
    return x/max(abs(x).max(),1e-8)
def shift(x,n):return np.interp(np.arange(0,len(x),2**(n/12)),np.arange(len(x)),x)
def event(track,name,t):
    if t<DURATION:events.append({'track':track,'voice':name,'start':t,'length':min(len(voices[name])/SR,DURATION-t)})

voice('Gentle Perkons kick',filt(sample('BD Gentle Perkons 03.wav'),62,6500),.14)
voice('Soft Perkons clap',filt(sample('Clap Soft Perkons Clean 02.wav'),230,7500),.045,-.08)
voice('Friendly 808 hats',filt(sample('CH Friendly 808 Loops 120.wav'),1100,7600),.030,.18)
voice('Quiet Perkons shaker',filt(sample('Shaker Soft Perkons 03.wav'),900,7000),.018,-.25)
voice('Vinyl rim',filt(sample('Rim Acoustic Wood Vinyl SP 02.wav'),500,6000),.023,.2)
dm=filt(shift(sample('FX Trem Keys Vinyl SP D#m9.wav'),-1),230,4800)
fm=filt(shift(sample('FX Sweet Key Vinyl SP F#maj7.wav'),-1),250,4200)
voice('Dm9 trem keys',dm,.065,-.12);voice('Fmaj7 warm keys',fm,.046,.12)
voice('Dm9 soft echo',filt(dm,650,2600),.015,.32)
voice('Fmaj7 soft echo',filt(fm,650,2600),.012,-.3)
for note in [50,53,57,60,62]:
    t=np.arange(int(.34*SR))/SR;f=440*2**((note-69)/12)
    x=(np.sin(2*np.pi*f*t)+.24*np.sin(4*np.pi*f*t))*np.minimum(t/.012,1)*np.exp(-t*6)*np.minimum((.34-t)/.06,1)
    voice('Bass '+str(note),filt(x,78,1800),.075)

for bar in range(64):
    t=bar*2;section=bar//16;local=bar%16
    for beat in range(4):event('01 Perkons kick','Gentle Perkons kick',t+beat*.5)
    # Keep a floor throughout; one short uncluttered phrase in the middle.
    if not(section==2 and local<4):
        for beat in [1,3]:event('02 Perkons clap','Soft Perkons clap',t+beat*.5+.005)
    root=50 if bar%8<6 else 53
    bass=[(.5,root),(2.5,root),(3.25,root+7)] if section!=2 else [(.5,root),(2.75,root)]
    for beat,note in bass:event('05 Muted mid bass','Bass '+str(note),t+beat*.5)
    is_f=bar%8>=6
    chord='Fmaj7 warm keys' if is_f else 'Dm9 trem keys'
    echo='Fmaj7 soft echo' if is_f else 'Dm9 soft echo'
    positions=[.75,2.75] if section in [0,3] else ([1.5] if section==2 else [.75,2.5])
    for beat in positions:
        event('06 Sampled ninth keys',chord,t+beat*.5)
        event('07 Soft stereo echoes',echo,t+beat*.5+.375)
    if section in [1,3]:
        for beat in [.25,2.75]:event('04 Shaker and rim','Quiet Perkons shaker',t+beat*.5)
    if section in [1,2] and bar%2:
        event('04 Shaker and rim','Vinyl rim',t+1.375)
for t in range(0,128,16):event('03 808 loop hats','Friendly 808 hats',t)

tree=ET.parse(ROOT/'sounds/deep-house-02/TriviTV Deep Vintage House.tracktionedit');edit=tree.getroot()
target=P/'TriviTV Deep Session 01 - Low Tide.tracktionedit';edit.set('projectID',str(target))
for tr in edit.findall('TRACK'):edit.remove(tr)
seq=edit.find('TEMPOSEQUENCE')
for e in seq.findall('TEMPO'):seq.remove(e)
ET.SubElement(seq,'TEMPO',startBeat='0',bpm='120',curve='1')
edit.find('TRANSPORT').attrib.update(loopPoint1='0.0',loopPoint2='128.0',position='0',looping='0')
edit.find('CLICKTRACK').set('enabled','0')
ident=90000
for i,name in enumerate(sorted(set(e['track'] for e in events))):
    ident+=1;tr=ET.SubElement(edit,'TRACK',id=str(ident),name=name,colour=['ff61c7a4','ff66a5d4','ffffca76','ffb6a0de','ff75c4d0','ffd3a387','ff90a0da'][i]);ET.SubElement(tr,'MODIFIERS')
    for e in events:
        if e['track']!=name:continue
        ident+=1
        ET.SubElement(tr,'AUDIOCLIP',name=e['voice'],start=str(e['start']),length=str(e['length']),offset='0',id=str(ident),source=str(A/(e['voice']+'.wav')),sync='0',pan='0',proxyAllowed='0',resamplingQuality='lagrange',fadeIn='0.002',fadeOut='0.005')
    ident+=1;ET.SubElement(tr,'PLUGIN',type='volume',id=str(ident),enabled='1',volume='0.6376281380653381')
    ident+=1;ET.SubElement(tr,'PLUGIN',type='level',id=str(ident),enabled='1')
    ET.SubElement(ET.SubElement(tr,'OUTPUTDEVICES'),'DEVICE',name='(default audio output)')
ET.indent(tree);tree.write(target,encoding='utf-8',xml_declaration=True)
(P/'arrangement.json').write_text(json.dumps({'title':'Low Tide','duration':128,'bpm':120,'key':'D minor / F major','changes_seconds':[32,64,96],'sources':sources,'events':events,'method':'Script prepares processed voices and native sample clips; Waveform final rendering'},indent=2))
print(f'Prepared {len(events)} native clips, {len(sources)} samples from all three installed libraries: {target}')

