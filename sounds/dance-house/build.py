from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Dance drums','Bouncy bass','Piano hook','Bright chords','Air pad']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-120+np.sqrt(120**2+8*b)) # 120 to 124 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''chords=[[60,64,67,71],[55,59,62,69],[57,60,64,67],[53,57,60,64]]
roots=[48,43,45,41]
def piano(n,d):
    tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
    z=sum(np.sin(2*np.pi*f*h*tt)*np.exp(-tt*(3+h*.9))/h**1.7 for h in range(1,7))
    return z*np.minimum(tt/.006,1)*np.minimum((d-tt)/.04,1)
for bar in range(31):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Dance drums',kick[:15000],sec(b+x),.09)
    for x in [1,3]:put('Dance drums',rim[:12000],sec(b+x),.042,-.06)
    for j in range(8):put('Dance drums',conga[:3800],sec(b+j*.5),.012 if j%2==0 else .026,.2)
    for x in [1.5,3.5]:put('Dance drums',clave[:7000],sec(b+x),.013,-.17)
    if t>42:
        for x in [.25,1.75,2.25,3.75]:put('Dance drums',maraca[:3200],sec(b+x),.009,-.25)
    for x,semi in [(.5,0),(1.25,7),(1.75,12),(2.5,0),(3.25,7),(3.75,12)]:
        put('Bouncy bass',voice(roots[c]+semi,.22,'bass'),sec(b+x),.052)
    for x in [.5,1.75,2.5,3.5]:
        for j,n in enumerate(chords[c]):
            z=piano(n,.7)
            put('Bright chords',z,sec(b+x),.024,(j-1.5)*.17)
            put('Bright chords',z,sec(b+x)+.375,.003,-(j-1.5)*.17)
    positions=[.25,1.5,2.75] if bar%2==0 else [.75,2.25]
    for j,x in enumerate(positions):
        n=chords[c][[2,3,1][j]]+12
        z=piano(n,.6)
        put('Piano hook',z,sec(b+x),.023,(-1)**j*.25)
        put('Piano hook',z,sec(b+x)+.375,.004,(-1)**(j+1)*.25)
    for j,n in enumerate(chords[c][:3]):
        d=min(2.5,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n+12-69)/12)
        put('Air pad',np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)**2,t,.005,(j-1)*.3)
stems['Dance drums']=eq(stems['Dance drums'],65,-5,-3,10000)
stems['Bouncy bass']=eq(stems['Bouncy bass'],75,-4,-2,5000)
stems['Bright chords']=eq(stems['Bright chords'],220,0,-3,8500)
stems['Piano hook']=eq(stems['Piano hook'],350,0,-3,8000)
stems['Air pad']=eq(stems['Air pad'],400,0,-3,6500)
tt=np.arange(N)/SR;beat=120*tt/60+2*tt*tt/3600
duck=1-.24*np.exp(-(beat%1)*12)
for k in ['Bright chords','Air pad']:stems[k]*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-02-Dance-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Dance House.tracktionedit')
s=s.replace('114*s/60','120*s/60').replace('114+s/15','120+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':120,'bpm_end':124")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['bouncy bass','piano-style chords','piano hook','air pad']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Dance house trivia question bed; brighter piano groove, restrained bass and gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
