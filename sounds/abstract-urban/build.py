from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Broken tape drums','Muted bass','Chord fragments','Found percussion','Dust textures']")
a=s.index('kick=sample(');b=s.index('def sec(')
s=s[:a]+'''kick=sample('BD Club Smack Vinyl SP 02.wav')
snare=sample('SD Tape Res Vinyl SP.wav')
hat=sample('CH Tape Snap Vinyl SP 01.wav')
rim=sample('Rim Tape Skin Vinyl SP.wav')
glitch=sample('Perc Tape Glitch Vinyl SP 01.wav')
shaker=sample('Shaker Acoustic Slap Vinyl SP.wav')
breath=sample('FX Vox Breath Vinyl SP.wav')
chord=sample('FX Club Chord Vinyl SP 02.wav')
''' +s[b:]
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-82+np.sqrt(82**2+8*b)) # 82 to 86 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''def transpose(z,n):
    return np.interp(np.arange(0,len(z),2**(n/12)),np.arange(len(z)),z)
def cut(z,d):
    z=z[:int(d*SR)].copy();m=min(1000,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
# The unlabelled chord is treated as an abstract texture, not assigned an unverified key.
chord=transpose(chord,-5)
for bar in range(22):
    b=bar*4;t=sec(b)
    if t>=60:break
    pattern=bar%4
    kicks=[[0,1.65,2.75],[0,.85,2.5],[0,1.75,2.65,3.5],[.15,2,2.85]][pattern]
    for j,x in enumerate(kicks):put('Broken tape drums',kick[:13000],sec(b+x),.075 if j==0 else .055)
    for x in [1.055,3.07]:put('Broken tape drums',snare[:15000],sec(b+x),.033,-.08)
    for j in range(8):
        if j==4 and pattern==2:continue
        x=j*.5+(.10 if j%2 else 0)
        put('Broken tape drums',hat[:3500],sec(b+x),.010 if j%2==0 else .018,.23)
    if pattern in [1,3]:put('Broken tape drums',snare[:4500],sec(b+2.82),.006,-.12)
    for j,x in enumerate([.8,2.3] if pattern<2 else [1.8,3.65]):
        put('Found percussion',rim[:6000],sec(b+x),.012,(-1)**j*.35)
    put('Found percussion',cut(glitch,.18),sec(b+3.35),.012,-.3)
    if t>42:
        for x in [.3,1.8,2.3,3.8]:put('Found percussion',shaker[:4200],sec(b+x),.009, .2)
    # Low melodic density: single C/G punctuation, not another house bass ostinato.
    for x,n in ([(.2,48),(2.65,55)] if pattern%2==0 else [(.85,48),(2.5,46)]):
        d=.27;tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.17*np.sin(4*np.pi*f*tt))*np.exp(-tt*8)*np.minimum(tt/.014,1)*np.minimum((d-tt)/.045,1)
        put('Muted bass',z,sec(b+x),.033)
    # Different source offsets and lengths give a chopped collage rather than a repeated lead.
    offset=int([.0,.13,.27,.07][pattern]*SR)
    fragment=cut(chord[offset:], [.42,.23,.65,.31][pattern])
    for j,x in enumerate([[.45,2.2],[1.6],[.3,3.35],[2.45]][pattern]):
        z=fragment if j==0 else fragment[::-1].copy()
        z=cut(z,.5)
        put('Chord fragments',z,sec(b+x),.028,(-1)**pattern*.23)
        put('Dust textures',z,sec(b+x)+.51,.005,(-1)**(pattern+1)*.3)
    if pattern==3:put('Dust textures',cut(breath,.7),sec(b+2.3),.007,-.25)
stems['Broken tape drums']=eq(stems['Broken tape drums'],90,-8,-4,8500)
stems['Muted bass']=eq(stems['Muted bass'],90,-6,-2,4500)
stems['Chord fragments']=eq(stems['Chord fragments'],350,-2,-5,6000)
stems['Found percussion']=eq(stems['Found percussion'],500,0,-5,7000)
stems['Dust textures']=eq(stems['Dust textures'],600,0,-7,4000)
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-Urban-01-Abstract-Hip-Hop-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Abstract Urban.tracktionedit')
s=s.replace('114*s/60','82*s/60').replace('114+s/15','82+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':82,'bpm_end':86")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['sparse mid-bass; all other parts use pack samples']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Abstract hip hop urban trivia bed; broken tape beat, chopped unpitched chord collage, found percussion and subtle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
