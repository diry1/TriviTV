from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Soul drums','Warm bass','Chord responses','Warm chords','Breath pad']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-116+np.sqrt(116**2+8*b)) # 116 to 120 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''chords=[[58,62,65,69,72],[55,58,62,65,69],[60,64,67,70,74],[53,57,60,64,67]]
roots=[46,43,48,41]
def warm(n,d):
    tt=np.arange(round(SR*d))/SR;f=440*2**((n-69)/12)
    z=(np.sin(2*np.pi*f*tt)+.22*np.sin(2*np.pi*f*2.001*tt)+.08*np.sin(2*np.pi*f*3*tt))
    env=np.minimum(tt/.045,1)*np.exp(-tt*1.9)*np.minimum((d-tt)/.12,1)
    return z*env
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Soul drums',kick[:15500],sec(b+x),.085)
    for x in [1,3]:put('Soul drums',rim[:12000],sec(b+x),.037,-.08)
    for j in range(8):
        x=j*.5+(.045 if j%2 else 0)
        put('Soul drums',conga[:4000],sec(b+x),.01 if j%2==0 else .023,.22)
    if bar%2==1:put('Soul drums',clave[:7500],sec(b+3.545),.012,-.18)
    for x in [.75,2.75]:put('Soul drums',maraca[:4500],sec(b+x),.007,-.28)
    if t>42:
        for x in [.25,1.75,2.25,3.75]:put('Soul drums',maraca[:3200],sec(b+x),.006,.22)
    for x,semi,d in [(.5,0,.32),(1.25,7,.2),(1.75,12,.23),(2.5,0,.32),(3.25,7,.22)]:
        put('Warm bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.05)
    # Midrange chord voicings, with breathing space; no high repeated alarm-like motif.
    for x in [.25,2.5]:
        for j,n in enumerate(chords[c]):
            z=warm(n,1.3)
            put('Warm chords',z,sec(b+x),.025,(j-2)*.14)
            put('Warm chords',z,sec(b+x)+.39,.003,-(j-2)*.14)
    if bar%4 in [1,3]:
        for j,n in enumerate(chords[c][1:4]):
            put('Chord responses',warm(n,.72),sec(b+3.25),.018,(j-1)*.22)
    for j,n in enumerate(chords[c][:3]):
        d=min(3,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.08*np.sin(2*np.pi*f*2*tt))*np.sin(np.pi*tt/d)**2
        put('Breath pad',z,t,.006,(j-1)*.25)
stems['Soul drums']=eq(stems['Soul drums'],65,-5,-3.5,9000)
stems['Warm bass']=eq(stems['Warm bass'],75,-4,-2,5000)
stems['Warm chords']=eq(stems['Warm chords'],230,0,-3,7500)
stems['Chord responses']=eq(stems['Chord responses'],250,0,-3,7500)
stems['Breath pad']=eq(stems['Breath pad'],300,0,-4,6000)
tt=np.arange(N)/SR;beat=116*tt/60+2*tt*tt/3600
duck=1-.16*np.exp(-(beat%1)*12)
for k in ['Warm chords','Breath pad']:stems[k]*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-05-Soulful-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Soulful House.tracktionedit')
s=s.replace('114*s/60','116*s/60').replace('114+s/15','116+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':116,'bpm_end':120")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['warm bass','warm chord voicings','midrange chord responses','breath pad']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Soulful house trivia bed; warm midrange harmony, swung percussion, no high repeating motif, gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
