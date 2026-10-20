from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Machinedrum groove','Short bass','Sampled chord washes','Wood and air','Reverse textures']")
start=s.index("kick=sample(");end=s.index('def sec(')
s=s[:start]+'''kick=sample('BD Machinedrum Smooth Vinyl SP.wav')
snare=sample('SD Machinedrum Hollow Vinyl SP 03.wav')
hat=sample('CH Machinedrum Snap Vinyl SP 02.wav')
air=sample('Perc Machinedrum Air Vinyl SP 03.wav')
wood=sample('Woodblock Acoustic Sat Vinyl SP.wav')
tom=sample('Tom Casio Soft Vinyl SP.wav')
chord=sample('FX Mellow Chord Vinyl SP Eb.wav')
''' +s[end:]
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-110+np.sqrt(110**2+8*b)) # 110 to 114 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''def pitched(z,semitones):
    ratio=2**(semitones/12)
    return np.interp(np.arange(0,len(z),ratio),np.arange(len(z)),z)
def soften(z,seconds):
    z=z[:int(seconds*SR)].copy(); m=min(1200,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=soften(chord,2.8)
# E-flat tonal center, asymmetric three/one/two/two-bar harmonic rhythm.
shifts=[0,0,0,3,-2,-2,5,5]
for bar in range(29):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    # Broken accents over a steady house pulse, alternating one-bar answers.
    for x,g in [(0,.09),(1,.062),(2,.078),(3,.064)]:put('Machinedrum groove',kick[:14000],sec(b+x),g)
    for x in [1.02,3.02]:put('Machinedrum groove',snare[:13000],sec(b+x),.038,-.08)
    hats=[.5,1.5,2.5,3.5] if bar%2==0 else [.5,1.25,1.75,2.5,3.5]
    for j,x in enumerate(hats):put('Machinedrum groove',hat[:4500],sec(b+x+.035),.018 if j%2 else .025,.24)
    for j,x in enumerate([.75,2.25,3.75] if bar%2==0 else [1.75,2.75]):
        put('Wood and air',wood[:6000],sec(b+x),.014,(-1)**j*.35)
    put('Wood and air',air[:13000],sec(b+2.75),.021,-.3)
    if bar%4==3:
        for j,x in enumerate([3,3.5]):put('Wood and air',pitched(tom,j*3),sec(b+x),.025,(-1)**j*.22)
    if t>43:
        for j,x in enumerate([.25,1.75,2.25,3.75]):put('Wood and air',hat[:3000],sec(b+x),.008,(-1)**j*.25)
    # Sparse mid-bass punctuation replaces the preceding tracks' continuous bass ostinato.
    for x,semi in [(.75,0),(2.5,7)]:
        note=39+shift+semi;tt=np.arange(round(.3*SR))/SR;f=440*2**((note-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.4*np.sin(4*np.pi*f*tt))*np.exp(-tt*9)*np.minimum(tt/.01,1)*np.minimum((.3-tt)/.04,1)
        put('Short bass',z,sec(b+x),.05)
    # The pack's actual chord sample carries the harmony; no synthesized chord/lead layers.
    if bar%2==0 or bar%8==3:
        z=pitched(chord,shift)
        put('Sampled chord washes',z,sec(b+.25),.055,-.16)
        put('Sampled chord washes',z,sec(b+.25)+.61,.011,.28)
    if bar%4==2:
        z=soften(pitched(chord,shift)[::-1],1.2)
        put('Reverse textures',z,sec(b+2),.016,.3)
stems['Machinedrum groove']=eq(stems['Machinedrum groove'],90,-8,-3,9500)
stems['Short bass']=eq(stems['Short bass'],85,-5,-2,5000)
stems['Sampled chord washes']=eq(stems['Sampled chord washes'],260,-1,-4,7000)
stems['Wood and air']=eq(stems['Wood and air'],350,0,-4,8000)
stems['Reverse textures']=eq(stems['Reverse textures'],400,0,-5,6000)
tt=np.arange(N)/SR;beat=110*tt/60+2*tt*tt/3600
duck=1-.12*np.exp(-(beat%1)*10)
stems['Sampled chord washes']*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-07-Sample-Groove-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Sample Groove House.tracktionedit')
s=s.replace('114*s/60','110*s/60').replace('114+s/15','110+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':110,'bpm_end':114")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['sparse mid-bass only; harmony and textures from pack samples']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Sample-based house trivia; Machinedrum kit, sampled Eb chord, woodblock/tom/air accents, asymmetric harmony and sparse bass')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)

