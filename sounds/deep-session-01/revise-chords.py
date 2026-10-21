"""Replace parts 06/07 with quieter simple triads; preserve the original edit."""
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt
import xml.etree.ElementTree as ET
import json
P=Path(__file__).resolve().parent;V=P/'v2';A=V/'voices';A.mkdir(parents=True,exist_ok=True);sr=48000
mapping={}
for old,new,notes in [('Dm9 trem keys','Soft D minor',[57,62,65]),('Fmaj7 warm keys','Soft F major',[57,60,65])]:
    ref,_=sf.read(P/'voices'/(old+'.wav'),always_2d=True)
    t=np.arange(round(.46*sr))/sr
    env=(1-np.exp(-t/.014))*np.exp(-t/ .105)*np.minimum((.46-t)/.06,1)
    z=sum(np.sin(2*np.pi*440*2**((n-69)/12)*t)+.10*np.sin(4*np.pi*440*2**((n-69)/12)*t) for n in notes)/3
    z=sosfilt(butter(3,1350,fs=sr,output='sos'),z*env)
    y=np.column_stack([z,z])*.7071
    # About 5.2dB less energy per hit than the former chord, independent of length.
    y*=.55*np.sqrt(np.sum(ref*ref)/np.sum(y*y))
    sf.write(A/(new+'.wav'),y,sr,subtype='PCM_24');mapping[old]=(new,len(y)/sr)
    echo=new+' echo';e=sosfilt(butter(3,1100,fs=sr,output='sos'),y,axis=0)*.17
    sf.write(A/(echo+'.wav'),e,sr,subtype='PCM_24')
    mapping['Dm9 soft echo' if old.startswith('Dm') else 'Fmaj7 soft echo']=(echo,len(e)/sr)
tree=ET.parse(P/'TriviTV Deep Session 01 - Low Tide.tracktionedit');edit=tree.getroot()
target=V/'Low Tide v2.tracktionedit';edit.set('projectID',str(target));edit.find('TRANSPORT').set('position','0')
changed=[]
for tr in edit.findall('TRACK'):
    tr.set('solo','0');tr.set('mute','0')
    if tr.get('name','').startswith('06'):tr.set('name','06 Soft groove chords')
    elif tr.get('name','').startswith('07'):tr.set('name','07 Quiet chord echoes')
    else:continue
    for c in tr.findall('AUDIOCLIP'):
        old=Path(c.get('source')).stem;new,d=mapping[old]
        c.set('source',str(A/(new+'.wav')));c.set('name',new);c.set('length',str(min(d,128-float(c.get('start')))));changed.append(c.get('id'))
ET.indent(tree);tree.write(target,encoding='utf-8',xml_declaration=True)
(V/'revision.json').write_text(json.dumps({'change':'06 replaced with original soft D-minor/F-major triad stabs; matching 07 echoes replaced to remove former timbre','old_track':'06 Sampled ninth keys','new_track':'06 Soft groove chords','chord_energy_change_db':round(float(20*np.log10(.55)),2),'duration':128,'bpm':120,'other_tracks':'01–05 unchanged','changed_clip_count':len(changed)},indent=2))
print(target)
