from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'abstract-urban/compose.py').read_text()
s=s.replace("['Broken tape drums','Muted bass','Chord fragments','Found percussion','Dust textures']","['Boom bap drums','Simple bass','Warm sample phrase','Light percussion','Sample tails']")
s=s.replace('15*(-82+np.sqrt(82**2+8*b)) # 82 to 86 BPM in 60s','15*(-88+np.sqrt(88**2+8*b)) # 88 to 92 BPM in 60s')
a=s.index('# The unlabelled chord');b=s.index('fade=np.ones(N)')
s=s[:a]+'''# Straightforward two-bar boom-bap loop, with regular backbeats and no glitch/reverse effects.
chord=transpose(chord,-2)
for bar in range(23):
    b=bar*4;t=sec(b)
    if t>=60:break
    kicks=[0,1.5,2,2.75] if bar%2==0 else [0,.75,2,3.5]
    for j,x in enumerate(kicks):put('Boom bap drums',kick[:14000],sec(b+x),.085 if x in [0,2] else .055)
    for x in [1,3]:put('Boom bap drums',snare[:14000],sec(b+x),.042,-.05)
    for j in range(8):
        x=j*.5+(.035 if j%2 else 0)
        put('Boom bap drums',hat[:3800],sec(b+x),.014 if j%2==0 else .021,.18)
    for x in [.75,2.75]:put('Light percussion',shaker[:4500],sec(b+x),.007,-.2)
    if t>44:
        for x in [1.75,3.75]:put('Light percussion',rim[:5000],sec(b+x),.008,.2)
    # A short root/fifth bass pattern stays easy to follow.
    for x,n,d in [(0,48,.35),(1.5,48,.23),(2,48,.35),(3.5,55,.22)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.22*np.sin(4*np.pi*f*tt))*np.exp(-tt*6)*np.minimum(tt/.012,1)*np.minimum((d-tt)/.045,1)
        put('Simple bass',z,sec(b+x),.04)
    # Same warm, forward-played sample phrase repeats predictably every two bars.
    for x,d,g in ([(.25,.8,.038),(2.25,.5,.029)] if bar%2==0 else [(.25,.8,.038),(2.75,.5,.029)]):
        z=cut(chord,d)
        put('Warm sample phrase',z,sec(b+x),g,-.08)
        put('Sample tails',z,sec(b+x)+.38,.004,.2)
stems['Boom bap drums']=eq(stems['Boom bap drums'],85,-8,-3.5,9000)
stems['Simple bass']=eq(stems['Simple bass'],85,-6,-2,4500)
stems['Warm sample phrase']=eq(stems['Warm sample phrase'],300,-2,-4,6500)
stems['Light percussion']=eq(stems['Light percussion'],450,0,-4,7500)
stems['Sample tails']=eq(stems['Sample tails'],500,0,-6,4500)
''' +s[b:]
# Keep only the five source samples actually used; no breath or glitch in this version.
s=s.replace("glitch=sample('Perc Tape Glitch Vinyl SP 01.wav')\n",'').replace("breath=sample('FX Vox Breath Vinyl SP.wav')\n",'')
s=s.replace('TriviTV-Urban-01-Abstract-Hip-Hop-60s-v1.wav','TriviTV-Urban-02-Oldschool-Rap-60s-v1.wav').replace('TriviTV Abstract Urban.tracktionedit','TriviTV Oldschool Rap.tracktionedit')
s=s.replace('82*s/60','88*s/60').replace('82+s/15','88+s/15').replace("'bpm_start':82,'bpm_end':86","'bpm_start':88,'bpm_end':92")
s=s.replace('Abstract hip hop urban trivia bed; broken tape beat, chopped unpitched chord collage, found percussion and subtle late lift','Simple oldschool rap instrumental trivia bed; two-bar boom-bap loop, steady backbeats, simple bass and warm forward sample phrase')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
