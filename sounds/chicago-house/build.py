from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Chicago drums','Round bass','Organ stabs','Soul keys','Air pad']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-118+np.sqrt(118**2+8*b)) # 118 to 122 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''chords=[[55,58,62,65],[60,63,67,70],[53,57,60,64],[58,62,65,69]]
roots=[43,48,41,46]
def organ(n,d):
    tt=np.arange(round(SR*d))/SR;f=440*2**((n-69)/12)
    z=sum(np.sin(2*np.pi*f*h*tt)*v for h,v in [(1,.65),(2,.26),(3,.12),(4,.07)])
    return z*np.minimum(tt/.012,1)*np.minimum((d-tt)/.07,1)*np.exp(-tt*3)
for bar in range(31):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Chicago drums',kick[:16000],sec(b+x),.088)
    for x in [1,3]:put('Chicago drums',rim[:12000],sec(b+x),.044,-.06)
    # Small delayed offbeats provide swing without interrupting the steady kick.
    for j in range(8):
        x=j*.5+(.065 if j%2 else 0)
        put('Chicago drums',conga[:4200],sec(b+x),.011 if j%2==0 else .024,.23)
    for x in [1.565,3.565]:put('Chicago drums',clave[:7000],sec(b+x),.012,-.22)
    if t>42:
        for x in [.315,1.815,2.315,3.815]:put('Chicago drums',maraca[:3300],sec(b+x),.009,-.25)
    for x,semi,d in [(0,0,.24),(.75,0,.18),(1.565,7,.22),(2.5,0,.25),(3.25,10,.18),(3.75,12,.16)]:
        put('Round bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.055)
    for x in [.565,1.75,2.565,3.565]:
        for j,n in enumerate(chords[c]):
            z=organ(n,.48)
            put('Organ stabs',z,sec(b+x),.025,(j-1.5)*.15)
            put('Organ stabs',z,sec(b+x)+.38,.003,-(j-1.5)*.15)
    if bar%2==1:
        for j,x in enumerate([.25,1.565,2.75]):
            n=chords[c][[2,3,1][j]]+12
            tt=np.arange(round(SR*.65))/SR;f=440*2**((n-69)/12)
            z=(np.sin(2*np.pi*f*tt)+.12*np.sin(4*np.pi*f*tt))*np.exp(-tt*7)*np.minimum(tt/.006,1)*np.minimum((.65-tt)/.04,1)
            put('Soul keys',z,sec(b+x),.025,(-1)**j*.22)
    for j,n in enumerate(chords[c][:3]):
        d=min(2.6,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n+12-69)/12)
        put('Air pad',np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)**2,t,.005,(j-1)*.3)
stems['Chicago drums']=eq(stems['Chicago drums'],64,-5,-3,10000)
stems['Round bass']=eq(stems['Round bass'],73,-4,-2,5000)
stems['Organ stabs']=eq(stems['Organ stabs'],220,0,-3,8000)
stems['Soul keys']=eq(stems['Soul keys'],350,0,-3,8000)
stems['Air pad']=eq(stems['Air pad'],400,0,-3,6500)
tt=np.arange(N)/SR;beat=118*tt/60+2*tt*tt/3600
duck=1-.18*np.exp(-(beat%1)*12)
for k in ['Organ stabs','Air pad']:stems[k]*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-03-Chicago-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Chicago House.tracktionedit')
s=s.replace('114*s/60','118*s/60').replace('114+s/15','118+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':118,'bpm_end':122")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['bass','organ-style stabs','soul keys','air pad']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Chicago house trivia question bed; swung hats, organ-style stabs, restrained bass and gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
