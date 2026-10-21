from pathlib import Path
import json, hashlib
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
from math import gcd

P=Path(__file__).parent; SR=48000; OUT=P/'audio';OUT.mkdir(exist_ok=True)
def smooth(x):
    x=sosfilt(butter(2,180,btype='highpass',fs=SR,output='sos'),x)
    x=sosfilt(butter(2,7500,btype='lowpass',fs=SR,output='sos'),x)
    n=min(240,len(x)//4);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    return x
def load(name):
    x,sr=sf.read(P/'source/kenney/Audio'/name,always_2d=True);x=x.mean(axis=1)
    if sr!=SR:g=gcd(sr,SR);x=resample_poly(x,SR//g,sr//g)
    active=np.flatnonzero(abs(x)>max(abs(x).max()*.002,1e-5))
    if len(active):x=x[max(0,active[0]-100):min(len(x),active[-1]+500)]
    return smooth(x)
def note(freq,d=.20):
    t=np.arange(round(d*SR))/SR
    return (np.sin(2*np.pi*freq*t)+.12*np.sin(4*np.pi*freq*t))*np.minimum(t/.012,1)*np.exp(-t*14)*np.minimum((d-t)/.04,1)
def melody(freqs,gap=.105,d=.24):
    z=np.zeros(round(((len(freqs)-1)*gap+d)*SR))
    for i,f in enumerate(freqs):
        x=note(f,d);a=round(i*gap*SR);z[a:a+len(x)]+=x
    return smooth(z)
events=[]
def event(id,title,description,variants,level):
    entries=[]
    for i,(x,source) in enumerate(variants):
        # Category-dependent levels: common navigation quieter than result notifications.
        rms=np.sqrt(np.mean(x*x)); gain=min(10**(level/20)/max(rms,1e-9),.5/max(abs(x).max(),1e-9))
        x=x*gain;name=f'{id}-{chr(97+i)}.wav';sf.write(OUT/name,x,SR,subtype='PCM_16')
        entries.append({'label':chr(65+i),'file':'audio/'+name,'source':source,'duration':round(len(x)/SR,3),'peakDbfs':round(float(20*np.log10(max(abs(x).max(),1e-12))),2),'rmsDbfs':round(float(20*np.log10(max(np.sqrt(np.mean(x*x)),1e-12))),2)})
    events.append({'id':id,'title':title,'description':description,'selected':'A','variants':entries})
def k(name):return (load(name+'.ogg'),'Kenney Interface Sounds / '+name+'.ogg (CC0), trimmed/EQ/gain/fades')
def original(x):return(x,'Original synthesized TriviTV cue; CC0')

def soft_tone(freq,d=.65):
    t=np.arange(round(d*SR))/SR
    return (np.sin(2*np.pi*freq*t)+.075*np.sin(4*np.pi*freq*t))*np.minimum(t/.035,1)*np.exp(-t*4)*np.minimum((d-t)/.16,1)

def timeout(variant):
    # A modern descending, sustained closure with a warm unresolved final interval.
    z=np.zeros(round(2.1*SR))
    pitches=[659.25,523.25,440] if variant==0 else [587.33,493.88,392]
    for start,f in zip([0,.40,.86],pitches):
        x=soft_tone(f,1.12);a=round(start*SR);z[a:a+len(x)]+=x
    a=round(.86*SR);x=soft_tone(pitches[-1]*1.189207,1.12)*.24;z[a:a+len(x)]+=x
    return smooth(z)

def countdown(variant):
    z=np.zeros(SR*3)
    freqs=[523.25,587.33,659.25] if variant==0 else [440,493.88,587.33]
    for i,f in enumerate(freqs):
        x=soft_tone(f,.58)*[.78,.87,1][i]
        z[i*SR:i*SR+len(x)]+=x
        if variant==1:
            x=soft_tone(f,.18)*.18;a=round((i+.36)*SR);z[a:a+len(x)]+=x
    return smooth(z)

def reveal(variant):
    z=np.zeros(round(.55*SR))
    freqs=[392,493.88,587.33] if variant==0 else [440,554.37]
    for i,f in enumerate(freqs):
        x=soft_tone(f,.35)*.65;a=round(i*.065*SR);z[a:a+len(x)]+=x
    return smooth(z)
event('highlight','Menu highlight','Very soft focus tick; should tolerate repeated arrow navigation.',[k('tick_001'),k('select_001')],-34)
event('press','Button pressed','Selected by you: former 4.B (switch_002), at its original level.',[k('switch_002')],-31)
events[-1]['approval']='User selected former unavailable B; exact processed audio preserved.'
event('back','Back / cancel','Selected by you: former 1.B (select_001), at its original level.',[k('select_001')],-34)
events[-1]['approval']='User selected former highlight B; exact processed audio preserved.'
event('unavailable','Unavailable action','Selected by you: former 3.A (back_001), at its original level.',[k('back_001')],-31)
events[-1]['approval']='User selected back A from revision 2; exact processed audio preserved.'
event('question','Question appears','Brief attention cue before reading.',[k('question_001'),k('open_001')],-28)
event('locked','Answer locked','Firm acknowledgement of the submitted answer.',[k('confirmation_001'),k('select_004')],-27)
event('choices','Choices revealed','New soft layered reveal accents; both previous choices replaced.',[original(reveal(0)),original(reveal(1))],-29)
event('correct','Correct answer','Short rising warm chime, with no bass impact.',[original(melody([523.25,659.25,783.99])),original(melody([587.33,880],.14,.30))],-24)
event('incorrect','Incorrect answer','Gentle falling cue, without a harsh buzzer.',[original(melody([440,349.23],.12,.25)),original(melody([392,329.63,293.66],.09,.22))],-26)
event('warning','Last three seconds','Full 3-second cue: gentle pulses at 3, 2, 1. Trigger once at 3 seconds remaining.',[original(countdown(0)),original(countdown(1))],-29)
event('expired','Time expired','2.1-second modern falling tones with a soft sustained ending; gentle failure cue.',[original(timeout(0)),original(timeout(1))],-26)
event('complete','Round complete','A modest celebration, longer than a correct-answer cue.',[original(melody([523.25,659.25,783.99,1046.5],.13,.38)),original(melody([392,523.25,659.25,783.99],.14,.4))],-24)
manifest={'status':'draft-for-user-audition','sampleRate':SR,'format':'mono PCM16 WAV','sourcePage':'https://kenney.nl/assets/interface-sounds','license':'Kenney source CC0; original synthesized cues dedicated to CC0. Source license preserved in source/kenney/License.txt.','events':events}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
# A labelled audio reel offers a fallback if opening the audition page is inconvenient.
reel=[];segments=[];position=0
for e in events:
    x,_=sf.read(P/e['variants'][0]['file']);segments.append({'event':e['title'],'start':round(position/SR,3)})
    reel.extend([x,np.zeros(round(.8*SR))]);position+=len(x)+round(.8*SR)
sf.write(P/'TriviTV-SFX-Audition-A.wav',np.concatenate(reel),SR,subtype='PCM_16')
(P/'reel-order.json').write_text(json.dumps(segments,indent=2))
report=[]
for e in events:
    for v in e['variants']:
        x,sr=sf.read(P/v['file']);assert sr==SR and len(x)>0 and np.isfinite(x).all() and abs(x).max()<1
        report.append(v['file'])
(P/'validation.json').write_text(json.dumps({'validatedFiles':report,'count':len(report),'clipping':False,'subjectiveReview':'pending; not listened to by agent','sourceZipSha256':hashlib.sha256((P/'source/kenney_interface-sounds.zip').read_bytes()).hexdigest()},indent=2))
template=(P/'page-template.html').read_text()
(P/'index.html').write_text(template.replace('/*MANIFEST*/',json.dumps(manifest)))
print('Created and verified',len(report),'cues, 12 events, manifest, audition reel and offline review page.')
