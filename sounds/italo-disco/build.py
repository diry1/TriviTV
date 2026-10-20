from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Disco drums','Octave bass','Retro arpeggio','Analog chords','Soft lead']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-112+np.sqrt(112**2+8*b)) # 112 to 116 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''def analog(note,dur,kind):
    tt=np.arange(round(SR*dur))/SR; f=440*2**((note-69)/12)
    env=np.minimum(tt/.012,1)*np.minimum((dur-tt)/.06,1)
    if kind=='bass':
        z=sum(np.sin(2*np.pi*f*h*tt)/h**1.7 for h in range(1,6))*np.exp(-tt*7)
    elif kind=='chord':
        z=sum((np.sin(2*np.pi*f*h*tt)+np.sin(2*np.pi*f*1.002*h*tt))*.5/h**1.8 for h in range(1,7))*np.exp(-tt*1.5)
    else:
        z=(np.sin(2*np.pi*f*tt+.3*np.sin(2*np.pi*5*tt))+.18*np.sin(4*np.pi*f*tt))*np.exp(-tt*(7 if kind=='arp' else 2.5))
    return z*env
chords=[[62,65,69,72],[58,62,65,69],[65,69,72,76],[60,64,67,70]]
roots=[38,34,41,36]
for bar in range(29):
    beat=bar*4;t=sec(beat)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Disco drums',kick[:16000],sec(beat+x),.082)
    for x in [1,3]:put('Disco drums',rim[:12500],sec(beat+x),.038,-.06)
    for j in range(8):put('Disco drums',conga[:4200],sec(beat+j*.5),.014 if j%2==0 else .023,.22)
    if bar%2==1:put('Disco drums',clave[:7500],sec(beat+3.5),.011,-.22)
    for j in range(8):
        note=roots[c]+(12 if j%2 else 0)
        if j==7 and bar%2:note+=7
        put('Octave bass',analog(note,.21,'bass'),sec(beat+j*.5),.052 if j%2 else .063)
    for x in [0,2]:
        for j,n in enumerate(chords[c]):put('Analog chords',analog(n,1.05,'chord'),sec(beat+x),.021,(j-1.5)*.16)
    order=[0,2,1,3,2,1,3,1]
    for j,ix in enumerate(order):
        if bar%4==3 and j in [2,6]:continue
        z=analog(chords[c][ix]+12,.36,'arp');pan=(-1)**j*.22
        put('Retro arpeggio',z,sec(beat+j*.5+.25),.019,pan)
        put('Retro arpeggio',z,sec(beat+j*.5+.25)+.27,.004,-pan)
    if bar%4 in [1,3]:
        for j,(x,n) in enumerate([(1,chords[c][2]+12),(2.5,chords[c][1]+12)]):
            put('Soft lead',analog(n,.75,'lead'),sec(beat+x),.018,(-1)**j*.15)
    if t>43:
        for x in [.25,1.75,2.25,3.75]:put('Disco drums',maraca[:3200],sec(beat+x),.007,-.2)
stems['Disco drums']=eq(stems['Disco drums'],62,-5,-3,10000)
stems['Octave bass']=eq(stems['Octave bass'],68,-4,-2,5000)
stems['Analog chords']=eq(stems['Analog chords'],220,0,-3,8500)
stems['Retro arpeggio']=eq(stems['Retro arpeggio'],350,0,-4,8000)
stems['Soft lead']=eq(stems['Soft lead'],350,0,-3,6500)
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-Trivia-04-Italo-Disco-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Italo Disco.tracktionedit')
s=s.replace('114*s/60','112*s/60').replace('114+s/15','112+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':112,'bpm_end':116")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['octave bass','analog synth chords','retro arpeggio','soft lead']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Italo disco trivia question bed; octave bass and retro arpeggio with gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
