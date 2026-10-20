from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Soft drums','Warm bass','Floating notes','Electric keys','Cloud pad']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-104+np.sqrt(104**2+8*b)) # 104 to 108 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''chords=[[62,66,69,73,76],[59,62,66,69,73],[55,59,62,66,69],[57,61,64,69,71]]
roots=[47,43,45,42]
def ep(n,d):
    tt=np.arange(round(SR*d))/SR;f=440*2**((n-69)/12)
    z=np.sin(2*np.pi*f*tt+.6*np.exp(-tt*6)*np.sin(2*np.pi*f*2*tt))
    z+=.1*np.sin(2*np.pi*f*3*tt)*np.exp(-tt*9)
    return z*np.minimum(tt/.018,1)*np.exp(-tt*2)*np.minimum((d-tt)/.12,1)
for bar in range(27):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Soft drums',kick[:15000],sec(b+x),.063)
    for x in [1,3]:put('Soft drums',rim[:11000],sec(b+x),.023,-.1)
    for x in [.54,1.54,2.54,3.54]:put('Soft drums',conga[:4200],sec(b+x),.017,.22)
    if bar%2==1:put('Soft drums',clave[:7500],sec(b+3.54),.008,-.2)
    if t>43:
        for x in [.25,1.75,2.25,3.75]:put('Soft drums',maraca[:3200],sec(b+x),.006,-.25)
    for x,semi,d in [(.5,0,.4),(1.75,7,.28),(2.5,0,.4),(3.5,12,.25)]:
        put('Warm bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.044)
    for x in [.25,2.5]:
        for j,n in enumerate(chords[c]):
            z=ep(n,1.6)
            put('Electric keys',z,sec(b+x),.021,(j-2)*.16)
            put('Electric keys',z,sec(b+x)+.43,.004,-(j-2)*.16)
    if bar%2==0:
        for j,x in enumerate([1.25,3]):
            z=ep(chords[c][2+j]+12,1.3)
            put('Floating notes',z,sec(b+x),.018,(-1)**j*.3)
            put('Floating notes',z,sec(b+x)+.65,.004,(-1)**(j+1)*.3)
    for j,n in enumerate(chords[c][:4]):
        d=min(3,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n+12-69)/12)
        z=(np.sin(2*np.pi*f*tt)+np.sin(2*np.pi*f*1.0015*tt))*.5*np.sin(np.pi*tt/d)**2
        put('Cloud pad',z,t,.008,(j-1.5)*.18)
stems['Soft drums']=eq(stems['Soft drums'],65,-5,-4,8500)
stems['Warm bass']=eq(stems['Warm bass'],75,-4,-2,5000)
stems['Electric keys']=eq(stems['Electric keys'],230,0,-3,8000)
stems['Floating notes']=eq(stems['Floating notes'],400,0,-4,7500)
stems['Cloud pad']=eq(stems['Cloud pad'],400,0,-4,6000)
tt=np.arange(N)/SR;beat=104*tt/60+2*tt*tt/3600
duck=1-.13*np.exp(-(beat%1)*10)
for k in ['Electric keys','Cloud pad']:stems[k]*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-04-Chillhouse-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Chillhouse.tracktionedit')
s=s.replace('114*s/60','104*s/60').replace('114+s/15','104+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':104,'bpm_end':108")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['warm bass','electric-piano-style keys','floating notes','cloud pad']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Chillhouse trivia question bed; spacious electric keys, soft drums, restrained bass and subtle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
