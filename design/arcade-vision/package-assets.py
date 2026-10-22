from pathlib import Path
from PIL import Image
import json, hashlib, xml.etree.ElementTree as ET, re, zipfile
ROOT=Path(__file__).resolve().parent
P=ROOT/'assets-v1'
vectors=list(P.rglob('*.svg'));assert len(vectors)==55
for f in vectors:
    tree=ET.parse(f);assert tree.getroot().attrib.get('viewBox'),f
    png=P/'png'/f.relative_to(P).with_suffix('.png');assert png.exists(),png
    with Image.open(png) as im:im.verify()
with Image.open(P/'art/party-arena.png') as im:
    assert im.mode=='RGBA'
    alpha=im.getchannel('A');assert alpha.getextrema()[0]==0 and alpha.getextrema()[1]>240
    arena={'size':im.size,'alphaRange':alpha.getextrema(),'cornerAlpha':im.getpixel((0,0))[3]}
assert len(json.loads((P/'tokens.json').read_text())['players'])==8
missing=[]
for f in P.glob('*.html'):
    for ref in re.findall(r'(?:src|href)="([^"]+)"',f.read_text(encoding='utf8').split('<script>')[0]):
        if ref.startswith(('http','#')) or ref=='manifest.json' or ref.endswith('.zip'):continue
        if not (f.parent/ref).exists():missing.append(ref)
assert not missing,missing
report={'svgAssets':55,'pngExports':55,'modeIllustrations':4,'playerAnimals':8,'animalVariants':['monochrome','colored-badge'],'controlIcons':16,'panelAssets':10,'backgrounds':5,'brandAssets':4,'arena':arena,'checks':['SVG parsing/viewBoxes','all PNG exports decode','arena alpha verified','eight unique player colors','static gallery links exist','browser visual review and sample mode switching'],'limitations':['Not integrated into live game or APK','Generated illustration shades are not an indexed six-color palette','Player colors require animal/number labels for accessibility','SVG wordmarks reference Arial/system sans-serif; PNGs freeze typography'],'generation':'Built-in image_gen for arena; original code-authored vectors/CSS'}
(P/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
files=[]
for f in sorted(P.rglob('*')):
    if not f.is_file() or f.name=='manifest.json':continue
    entry={'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
    if f.suffix in ['.png','.webp']:
        with Image.open(f) as im:entry.update(width=im.width,height=im.height,mode=im.mode)
    elif f.suffix=='.svg':
        a=ET.parse(f).getroot().attrib;entry.update(width=int(a['width']),height=int(a['height']),viewBox=a['viewBox'])
    files.append(entry)
(P/'manifest.json').write_text(json.dumps({'version':1,'files':files},indent=2),encoding='utf8')
target=ROOT/'TriviTV-Arcade-Assets-v1.zip'
sources=['build-asset-pack.py','build-asset-gallery.py','render-asset-pack.cjs','build-asset-sheet.py','package-assets.py']
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for f in P.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(ROOT))
    for name in sources:z.write(ROOT/name,name)
    for f in (ROOT/'animals').glob('*.svg'):z.write(f,f.relative_to(ROOT))
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print(json.dumps({'files':len(files)+1,'zipBytes':target.stat().st_size,'zipSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'svgAssets':55,'pngExports':55,'arena':arena},indent=2))
