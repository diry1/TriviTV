from pathlib import Path
import soundfile as sf,numpy as np,json
p=Path(__file__).resolve().parent
x,sr=sf.read(p/'Exported/Low Tide v2 Export 1.wav',always_2d=True)
assert sr==48000 and len(x)==128*sr
x[:2400]*=np.linspace(0,1,2400)[:,None];x[-sr:]*=np.linspace(1,0,sr)[:,None]
x*=10**(json.loads((p/'validation.json').read_text())['gain_db']/20)
assert abs(x).max()<1
sf.write(p.parent/'TriviTV-Deep-Session-01-Low-Tide-128s-v2.wav',x,sr,subtype='PCM_24')
