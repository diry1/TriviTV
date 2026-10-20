from pathlib import Path
import subprocess, sys
p=Path(__file__).parent
source=(p.parent/'caribbean/compose.py').read_text()
source=source.replace("['Island percussion','Light bass','Mallet melody','Offbeat chords','Seaside air']","['House drums','Round bass','Glass accents','Deep chords','Air pad']")
source=source.replace("kick=sample('BD 808 Air Vinyl SP.wav')","kick=sample('BD 808 Warm Vinyl SP.wav')")
source=source.replace("rim=sample('Rim 808 Standard Vinyl SP.wav')","rim=sample('Clap 808 Standard Vinyl SP.wav')")
source=source.replace("conga=sample('Conga 808 Lo Vinyl SP Clean 02.wav')","conga=sample('CH 808 Standard Vinyl SP 01.wav')")
source=source.replace("clave=sample('Clave 808 Standard Vinyl SP.wav')","clave=sample('OH 808 Standard Vinyl SP 01.wav')")
source=source.replace("def sec(b):return 10*(-94+np.sqrt(94**2+12*b)) # 94 to 100 BPM in 60s","def sec(b):return 15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s")
start=source.index('chords=');end=source.index('fade=np.ones(N)')
source=source[:start]+'''chords=[[57,60,64,67,71],[53,57,60,64,67],[55,59,62,65,69],[52,55,59,62,66]]
roots=[45,41,43,40]
for bar in range(30):
    b=bar*4; t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('House drums',kick[:18000],sec(b+x),.095)
    for x in [1,3]:put('House drums',rim[:14000],sec(b+x),.035,-.1)
    for x in [.5,1.5,2.5,3.5]:put('House drums',conga[:4500],sec(b+x),.025,.22)
    if bar%2==1:
        put('House drums',clave[:8500],sec(b+3.5),.012,-.2)
    if t>40:
        for x in [.25,1.75,2.25,3.75]:put('House drums',maraca[:3500],sec(b+x),.008,-.25)
    for x,semi,d in [(.5,0,.25),(1.25,0,.18),(1.75,7,.22),(2.5,0,.28),(3.25,12,.18)]:
        put('Round bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.057)
    for x in [.75,2.5]:
        for j,n in enumerate(chords[c]):
            tt=np.arange(round(SR*1.15))/SR; f=440*2**((n-69)/12)
            env=np.minimum(tt/.025,1)*np.exp(-tt*3)*np.minimum((1.15-tt)/.06,1)
            z=(np.sin(2*np.pi*f*tt)+.24*np.sin(2*np.pi*f*2.001*tt)+.08*np.sin(2*np.pi*f*3*tt))*env
            put('Deep chords',z,sec(b+x),.022,(j-2)*.14)
            put('Deep chords',z,sec(b+x)+.395,.004,-(j-2)*.14)
    if bar%2==0:
        for j,x in enumerate([1.5,3.25]):
            z=voice(chords[c][2+j]+12,.8,'mallet')
            put('Glass accents',z,sec(b+x),.017,(-1)**j*.3)
            put('Glass accents',z,sec(b+x)+.53,.004,(-1)**(j+1)*.3)
    for j,n in enumerate(chords[c][:3]):
        dur=min(2.8,60-t);tt=np.arange(round(SR*dur))/SR;f=440*2**((n+12-69)/12)
        z=np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/dur)**2
        put('Air pad',z,t,.007,(j-1)*.3)
stems['House drums']=eq(stems['House drums'],62,-5,-3,10000)
stems['Round bass']=eq(stems['Round bass'],72,-4,-2,5000)
stems['Deep chords']=eq(stems['Deep chords'],210,0,-2,8500)
stems['Glass accents']=eq(stems['Glass accents'],350,0,-4,8000)
stems['Air pad']=eq(stems['Air pad'],400,0,-3,6500)
# Gentle rhythmic ducking creates space for the kick without heavy pumping.
tt=np.arange(N)/SR;beat=114*tt/60+2*tt*tt/3600
duck=1-.2*np.exp(-(beat%1)*12)
for k in ['Deep chords','Air pad']:stems[k]*=duck[:,None]
''' +source[end:]
source=source.replace('TriviTV-Trivia-02-Caribbean-60s-v1.wav','TriviTV-Trivia-03-Deep-House-60s-v1.wav').replace('TriviTV Caribbean.tracktionedit','TriviTV Deep House.tracktionedit')
source=source.replace('94*s/60+3*s*s/3600','114*s/60+2*s*s/3600').replace('94+s*.1','114+s/15')
source=source.replace("'bpm_start':94,'bpm_end':100","'bpm_start':114,'bpm_end':118")
source=source.replace("['bass','mallet keys','offbeat chords','surf-like air']","['bass','deep extended chords','glass accents','air pad']")
source=source.replace('Caribbean/beach trivia question bed; gentle late percussion lift','Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift')
(p/'compose.py').write_text(source)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
