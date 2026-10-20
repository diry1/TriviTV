from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Vintage drums','Muted bass','Cm9 chord samples','Conga conversation','Distant chord tails']")
a=s.index('kick=sample(');b=s.index('def sec(')
s=s[:a]+'''kick=sample('BD 909 House Vinyl SP.wav')
clap=sample('Clap House Vinyl SP 01.wav')
hat=sample('CH Vintage Drag Vinyl SP.wav')
openhat=sample('OH House Vinyl SP.wav')
muted=sample('Conga Vintage Muted Vinyl SP.wav')
opened=sample('Conga Vintage Open Vinyl SP.wav')
shaker=sample('Shaker House Vinyl SP.wav')
chord=sample('FX House Chord Vinyl SP Cm9.wav')
''' +s[b:]
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-113+np.sqrt(113**2+8*b)) # 113 to 117 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''def transpose(z,n):
    return np.interp(np.arange(0,len(z),2**(n/12)),np.arange(len(z)),z)
def taper(z,d):
    z=z[:int(d*SR)].copy();m=min(1500,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=taper(chord,3.2)
# Sampled minor-ninth harmony, long C pedal then Ab/F responses, unlike prior four-chord synth beds.
shifts=[0,0,0,0,-4,-4,5,0]
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    for x in [0,1,2,3]:put('Vintage drums',kick[:15000],sec(b+x),.082)
    for x in [1.015,3.015]:put('Vintage drums',clap[:12500],sec(b+x),.031,-.08)
    for j,x in enumerate([.53,1.53,2.53,3.53]):put('Vintage drums',hat[:4500],sec(b+x),.023 if j%2 else .019,.24)
    if bar%2:put('Vintage drums',openhat[:8000],sec(b+3.53),.009,-.2)
    for j,x in enumerate([.75,2.25] if bar%2==0 else [1.75,3.25]):
        z=muted if j==0 else opened
        put('Conga conversation',z[:14000],sec(b+x),.026 if j==0 else .019,(-1)**j*.3)
    for x in [.25,2.75]:put('Conga conversation',shaker[:5000],sec(b+x),.008,-.2)
    if t>43:
        for x in [1.25,3.75]:put('Conga conversation',shaker[:3500],sec(b+x),.008,.2)
    root=48+shift
    for x,n,d in [(.5,root,.31),(2.5,root,.3),(3.25,root+7,.18)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.32*np.sin(4*np.pi*f*tt))*np.exp(-tt*7)*np.minimum(tt/.012,1)*np.minimum((d-tt)/.045,1)
        put('Muted bass',z,sec(b+x),.048)
    z=transpose(chord,shift)
    if bar%2==0:
        put('Cm9 chord samples',z,sec(b+.75),.052,-.13)
        put('Cm9 chord samples',z,sec(b+.75)+.52,.010,.24)
    else:
        put('Cm9 chord samples',taper(z,.65),sec(b+2.75),.034,.1)
    if bar%4==3:
        tail=taper(z[::-1],1.45)
        put('Distant chord tails',tail,sec(b+1.5),.012,-.25)
stems['Vintage drums']=eq(stems['Vintage drums'],80,-7,-3.5,9000)
stems['Muted bass']=eq(stems['Muted bass'],80,-5,-2,5000)
stems['Cm9 chord samples']=eq(stems['Cm9 chord samples'],280,-1,-3.5,7500)
stems['Conga conversation']=eq(stems['Conga conversation'],230,0,-4,8000)
stems['Distant chord tails']=eq(stems['Distant chord tails'],400,0,-5,6000)
tt=np.arange(N)/SR;beat=113*tt/60+2*tt*tt/3600
duck=1-.15*np.exp(-(beat%1)*12)
stems['Cm9 chord samples']*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-08-Deep-Vintage-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Deep Vintage House.tracktionedit')
s=s.replace('114*s/60','113*s/60').replace('114+s/15','113+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':113,'bpm_end':117")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['muted mid-bass only; Cm9 harmony and textures from pack samples']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Deep vintage house trivia bed; Vintage House sampled drums and congas, sampled Cm9 harmony with long C pedal, subtle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
