from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['LM1 drums','Soft bass','A chord cuts','Cabasa and rim','Dub echoes']")
a=s.index('kick=sample(');b=s.index('def sec(')
s=s[:a]+'''kick=sample('BD LM1 Vinyl SP Clean 02.wav')
snare=sample('SD LM1 Vinyl SP 02.wav')
hat=sample('CH LM1 Standard Vinyl SP 02.wav')
rim=sample('Rim LM1 Vinyl SP 02.wav')
cabasa=sample('Cabasa LM1 Vinyl SP 01.wav')
tamb=sample('Tamb LM1 Vinyl SP 01.wav')
chord=sample('FX Mellow Chord Vinyl SP A.wav')
''' +s[b:]
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-115+np.sqrt(115**2+8*b)) # 115 to 119 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''def transpose(z,n):
    return np.interp(np.arange(0,len(z),2**(n/12)),np.arange(len(z)),z)
def cut(z,d):
    z=z[:int(d*SR)].copy();m=min(1800,len(z)//3)
    z[:m]*=np.linspace(0,1,m);z[-m:]*=np.linspace(1,0,m)
    return z
chord=cut(chord,2.6)
# A-centered two-chord dialogue with a contrasting D turnaround every eight bars.
shifts=[0,0,0,0,-2,-2,-2,5]
for bar in range(30):
    b=bar*4;t=sec(b)
    if t>=60:break
    shift=shifts[bar%8]
    for x,g in [(0,.076),(1,.064),(2,.076),(3,.064)]:put('LM1 drums',kick[:15000],sec(b+x),g)
    for x in [1.02,3.02]:put('LM1 drums',snare[:11500],sec(b+x),.028,-.08)
    for j,x in enumerate([.56,1.56,2.56,3.56]):put('LM1 drums',hat[:4200],sec(b+x),.019 if j%2 else .023,.25)
    # Sparse rim answers and brushed cabasa replace the preceding conga conversation.
    for j,x in enumerate([.75,2.75] if bar%2==0 else [1.75,3.25]):
        put('Cabasa and rim',rim[:5500],sec(b+x),.014,(-1)**j*.3)
    for x in [.3,1.3,2.3,3.3]:put('Cabasa and rim',cabasa[:7000],sec(b+x),.009,-.25)
    if t>43:
        for x in [1.56,3.56]:put('Cabasa and rim',tamb[:7000],sec(b+x),.009,.18)
    root=45+shift
    for x,n,d in [(.56,root,.3),(1.8,root+7,.18),(2.56,root,.34)]:
        tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        z=(np.sin(2*np.pi*f*tt)+.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*6)*np.minimum(tt/.014,1)*np.minimum((d-tt)/.05,1)
        put('Soft bass',z,sec(b+x),.047)
    z=transpose(chord,shift)
    positions=[.25,2.75] if bar%2==0 else [1.5]
    for j,x in enumerate(positions):
        short=cut(z,.9 if j==0 else .5)
        put('A chord cuts',short,sec(b+x),.046,(-1)**j*.12)
        # Darkening stereo echoes rather than a lead melody or reversed chord swell.
        for delay,g,pan in [(.39,.010,.3),(.78,.005,-.3),(1.17,.002,.2)]:
            put('Dub echoes',short,sec(b+x)+delay,g,pan)
stems['LM1 drums']=eq(stems['LM1 drums'],100,-10,-3.5,9000)
stems['Soft bass']=eq(stems['Soft bass'],85,-7,-2,5000)
stems['A chord cuts']=eq(stems['A chord cuts'],280,-1,-3.5,7000)
stems['Cabasa and rim']=eq(stems['Cabasa and rim'],400,0,-4.5,7500)
stems['Dub echoes']=eq(stems['Dub echoes'],500,0,-6,4500)
tt=np.arange(N)/SR;beat=115*tt/60+2*tt*tt/3600
duck=1-.13*np.exp(-(beat%1)*12)
stems['A chord cuts']*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-09-Deep-Dub-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Deep Dub House.tracktionedit')
s=s.replace('114*s/60','115*s/60').replace('114+s/15','115+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':115,'bpm_end':119")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['soft mid-bass only; A-centered sampled chord and processed delay textures']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Deep dub house trivia bed; LM1 sample kit, sampled A chord cuts, dark stereo echoes, cabasa/rim and gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)

