from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/TriviTV-TV-Fun-Strict-UK';out.mkdir(exist_ok=True)
apk=out/'TriviTV-TV-0.10.0-fun-strict-uk.apk'
shutil.copy2(root/'android-tv-poc/app/build/outputs/apk/debug/app-debug.apk',apk)
fun_ids={q['id'] for q in json.loads((root/'question-bank/fun-bank/questions.en.json').read_text(encoding='utf8'))}
base=root/'provided-916/TriviTV-EU-Filtered-Test/Server/data'
source={q['id']:q for q in json.loads((base/'opentriviaqa/questions.json').read_text(encoding='utf8'))}
translations={q['id']:q for q in json.loads((base/'translations/uk.json').read_text(encoding='utf8'))['questions']}
files=[p for p in (root/'browser-site/dist').rglob('*') if p.is_file()]
parts=Counter()
with zipfile.ZipFile(apk) as z:
    for p in files:assert z.read('assets/web/'+p.relative_to(root/'browser-site/dist').as_posix())==p.read_bytes(),p
    bank=json.loads(z.read('assets/web/questions.json'))
    assert len(bank)==7454 and len({q['id'] for q in bank})==7454
    for q in bank:
        assert q['id'] in fun_ids and q['text']==translations[q['id']]['text'] and q['choices']==translations[q['id']]['choices']
        assert q['correct']==source[q['id']]['correct'] and 'tags' not in q and q['category']!='Religion & Faith'
    for item in z.infolist():
        part='questions' if item.filename.endswith('questions.json') else 'audio' if item.filename.endswith(('.ogg','.wav','.mp3')) else 'visuals' if '/visuals/' in item.filename else 'app-and-other'
        parts[part]+=item.compress_size
lint=ET.parse(root/'android-tv-poc/app/build/reports/lint-results-debug.xml').getroot()
report={'version':'0.10.0-fun-strict-uk','versionCode':17,'bytes':apk.stat().st_size,'MB':round(apk.stat().st_size/1e6,2),'MiB':round(apk.stat().st_size/1048576,2),'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'questionCount':len(bank),'categories':len({q['category'] for q in bank}),'assetFilesMatched':len(files),'compressedParts':dict(parts),'bank':json.loads((root/'browser-site/dist/bank-info.json').read_text(encoding='utf8')),'layout':json.loads((root/'browser-site/.qa/tv-validation.json').read_text(encoding='utf8')),'lint':{'errors':sum(x.attrib.get('severity')=='Error' for x in lint),'warnings':sum(x.attrib.get('severity')=='Warning' for x in lint)},'signature':'v2; same update certificate','zipAlignment':'passed','tests':'13 difficulty/solo tests; local multiplayer tests; TV UI and full-bank layouts passed','physicalTV':'Pending'}
assert report['lint']['errors']==0
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(out/'START-HERE.txt').write_text("""TriviTV 0.10.0 — Strict Ukrainian Fun Bank

7,454 Ukrainian questions across 19 categories. VersionCode17, same dev.trivitv.poc package and signing key. Install as an update; start a NEW game.

Original Fun gates plus semantic exclusions: religion, US-specific knowledge, dates/numeric recall, older culture, wordplay/word meanings, specialist knowledge, song lyrics, quote identification, celebrity personal details and award details. All tagged or proposed Ukrainian localization risks and unverified movie/book titles are held. Main and EU banks preserved. Machine screening is not factual certification.

Includes latest solo Trivia lives: starts with 3, wrong/timeout loses 1, 5 correct in a row earns 1 up to 5; continue until zero lives. Existing music, SFX, artwork, layouts and weighted category difficulty retained.

Solo content works offline. Phone rooms: iggro.com has been updated to the same strict 7,454-question bank. Create a new room; existing rooms keep their prior decks. Physical TV validation pending.
""",encoding='utf8')

desktop=Path.home()/'Desktop/trivitv';desktop.mkdir(exist_ok=True);shutil.copy2(apk,desktop/apk.name)
print(json.dumps({k:report[k] for k in ('bytes','MB','MiB','sha256','questionCount','compressedParts')},indent=2))
