from pathlib import Path
import subprocess,sys
p=Path(__file__).parent
s=(p.parent/'deep-house/compose.py').read_text()
s=s.replace("['House drums','Round bass','Glass accents','Deep chords','Air pad']","['Garage drums','Syncopated bass','Chord replies','Warm stabs','Soft air']")
s=s.replace('15*(-114+np.sqrt(114**2+8*b)) # 114 to 118 BPM in 60s','15*(-120+np.sqrt(120**2+8*b)) # 120 to 124 BPM in 60s')
a=s.index('chords=');b=s.index('fade=np.ones(N)')
s=s[:a]+'''chords=[[60,63,67,70],[56,60,63,67],[58,62,65,68],[55,58,62,65]]
roots=[48,44,46,43]
def stab(note,dur):
    tt=np.arange(round(SR*dur))/SR;f=440*2**((note-69)/12)
    z=np.sin(2*np.pi*f*tt)+.28*np.sin(4*np.pi*f*tt)+.09*np.sin(6*np.pi*f*tt)
    return z*np.minimum(tt/.018,1)*np.exp(-tt*5.5)*np.minimum((dur-tt)/.065,1)
for bar in range(31):
    b=bar*4;t=sec(b)
    if t>=60:break
    c=(bar//2)%4
    for x in [0,1,2,3]:put('Garage drums',kick[:15000],sec(b+x),.083)
    for x in [1.015,3.015]:put('Garage drums',rim[:11500],sec(b+x),.039,-.06)
    for j in range(8):
        x=j*.5+(.085 if j%2 else 0)
        put('Garage drums',conga[:4000],sec(b+x),.009 if j%2==0 else .025,.24)
    for x in [1.585,3.585]:put('Garage drums',clave[:6800],sec(b+x),.011,-.2)
    # Quiet ghost claps and shakers provide shuffle rather than a lead motif.
    if bar%2==1:put('Garage drums',rim[:6500],sec(b+2.82),.008,-.12)
    for x in [.83,2.83]:put('Garage drums',maraca[:3300],sec(b+x),.006,-.28)
    if t>43:
        for x in [.33,1.83,2.33,3.83]:put('Garage drums',maraca[:3000],sec(b+x),.007,.2)
    for x,semi,d in [(.585,0,.24),(1.33,7,.16),(1.83,12,.2),(2.585,0,.27),(3.33,10,.17),(3.83,7,.15)]:
        put('Syncopated bass',voice(roots[c]+semi,d,'bass'),sec(b+x),.049)
    for x in [.33,1.585,2.83]:
        for j,n in enumerate(chords[c]):
            z=stab(n,.58)
            put('Warm stabs',z,sec(b+x),.029,(j-1.5)*.16)
            put('Warm stabs',z,sec(b+x)+.38,.003,-(j-1.5)*.16)
    if bar%4 in [1,3]:
        for j,n in enumerate(chords[c][1:]):
            put('Chord replies',stab(n,.38),sec(b+3.33),.020,(j-1)*.2)
    for j,n in enumerate(chords[c][:3]):
        d=min(2.8,60-t);tt=np.arange(round(d*SR))/SR;f=440*2**((n-69)/12)
        put('Soft air',np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)**2,t,.005,(j-1)*.25)
stems['Garage drums']=eq(stems['Garage drums'],65,-5,-3.5,9000)
stems['Syncopated bass']=eq(stems['Syncopated bass'],76,-4,-2,5000)
stems['Warm stabs']=eq(stems['Warm stabs'],230,0,-3.5,7500)
stems['Chord replies']=eq(stems['Chord replies'],260,0,-3.5,7000)
stems['Soft air']=eq(stems['Soft air'],350,0,-4,6000)
tt=np.arange(N)/SR;beat=120*tt/60+2*tt*tt/3600
duck=1-.17*np.exp(-(beat%1)*12)
for k in ['Warm stabs','Soft air']:stems[k]*=duck[:,None]
''' +s[b:]
s=s.replace('TriviTV-Trivia-03-Deep-House-60s-v1.wav','TriviTV-House-06-Garage-60s-v1.wav').replace('TriviTV Deep House.tracktionedit','TriviTV Garage House.tracktionedit')
s=s.replace('114*s/60','120*s/60').replace('114+s/15','120+s/15').replace("'bpm_start':114,'bpm_end':118","'bpm_start':120,'bpm_end':124")
s=s.replace("['bass','deep extended chords','glass accents','air pad']","['syncopated bass','warm chord stabs','midrange chord replies','soft air']")
s=s.replace('Deep house trivia question bed; restrained four-on-the-floor groove and gentle late lift','Garage house trivia bed; shuffled hats, syncopated bass, warm midrange stabs and gentle late lift')
(p/'compose.py').write_text(s)
subprocess.run([sys.executable,str(p/'compose.py')],check=True)
