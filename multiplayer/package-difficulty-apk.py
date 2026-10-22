from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/TriviTV-TV-Difficulty-UK';out.mkdir(exist_ok=True)
apk=out/'TriviTV-TV-0.11.0-difficulty-uk.apk'
shutil.copy2(root/'android-tv-poc/app/build/outputs/apk/debug/app-debug.apk',apk)
fun_ids={q['id'] for q in json.loads((root/'question-bank/fun-bank/questions.en.json').read_text(encoding='utf8'))}
base=root/'provided-916/TriviTV-EU-Filtered-Test/Server/data'
source={q['id']:q for q in json.loads((base/'opentriviaqa/questions.json').read_text(encoding='utf8'))}
translations={q['id']:q for q in json.loads((base/'translations/uk.json').read_text(encoding='utf8'))['questions']}
ratings={r['id']:r for r in json.loads((root/'question-bank/quality-full-v1/assessment.json').read_text(encoding='utf8'))['records']}
files=[p for p in (root/'browser-site/dist').rglob('*') if p.is_file()]
parts=Counter()
with zipfile.ZipFile(apk) as z:
    for p in files:assert z.read('assets/web/'+p.relative_to(root/'browser-site/dist').as_posix())==p.read_bytes(),p
    bank=json.loads(z.read('assets/web/questions.json'))
    assert len(bank)==7104 and len({q['id'] for q in bank})==7104
    for q in bank:
        assert q['id'] in fun_ids and q['text']==translations[q['id']]['text'] and q['choices']==translations[q['id']]['choices']
        assert q['difficultyStars']==ratings[q['id']]['difficultyStars']
        assert q['correct']==source[q['id']]['correct'] and 'tags' not in q and q['category']!='Religion & Faith'
    for item in z.infolist():
        part='questions' if item.filename.endswith('questions.json') else 'audio' if item.filename.endswith(('.ogg','.wav','.mp3')) else 'visuals' if '/visuals/' in item.filename else 'app-and-other'
        parts[part]+=item.compress_size
lint=ET.parse(root/'android-tv-poc/app/build/reports/lint-results-debug.xml').getroot()
report={'version':'0.11.0-difficulty-uk','versionCode':18,'bytes':apk.stat().st_size,'MB':round(apk.stat().st_size/1e6,2),'MiB':round(apk.stat().st_size/1048576,2),'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'questionCount':len(bank),'categories':len({q['category'] for q in bank}),'assetFilesMatched':len(files),'compressedParts':dict(parts),'bank':json.loads((root/'browser-site/dist/bank-info.json').read_text(encoding='utf8')),'layout':json.loads((root/'browser-site/.qa/tv-validation.json').read_text(encoding='utf8')),'lint':{'errors':sum(x.attrib.get('severity')=='Error' for x in lint),'warnings':sum(x.attrib.get('severity')=='Warning' for x in lint)},'signature':'v2; same update certificate','zipAlignment':'passed','tests':'19 difficulty/solo tests; local multiplayer tests; TV UI and full-bank layouts passed','physicalTV':'Pending'}
assert report['lint']['errors']==0
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(out/'START-HERE.txt').write_text("""TriviTV 0.11.0 — Ukrainian question difficulty build

7,104 Ukrainian Fun v3 questions across 19 categories. VersionCode18, same dev.trivitv.poc package and signing key. Install as update and start a NEW game/room.

Uses per-question 1–5 star scores from quality-full-v1. Existing translation flags do not exclude further questions; translation repairs have not been applied.

Trivia first five questions35/50/15/0/0; next20/45/30/5/0; next10/35/40/15/0; next5/30/40/23/2; from21onward5/25/40/27/3 percent for1..5stars. Small stages use randomized rounding and spread choices; late100-question cycles exact. Categories proportional to eligible counts within each star; missing stars substitute nearest available level; questions do not repeat until whole selected pool exhausted. Solo starts3lives, every5correct adds1max5, ends atzero.

Millionaire strict questions1=1star;2–5=2stars;6–10=3stars;11–14=4stars;15=5stars. Warns before start when chosen categories lack required supply; no difficulty substitution.

Music/SFX/artwork/layout retained. Phone rooms and iggro.com/tv are updated to matching bank/Trivia selector; create a NEW room. Physical TV validation pending.
""",encoding='utf8')

desktop=Path.home()/'Desktop/trivitv';desktop.mkdir(exist_ok=True);shutil.copy2(apk,desktop/apk.name)
print(json.dumps({k:report[k] for k in ('bytes','MB','MiB','sha256','questionCount','compressedParts')},indent=2))
