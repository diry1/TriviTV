from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/TriviTV-TV-Fun-UK';out.mkdir(exist_ok=True)
apk=out/'TriviTV-TV-0.9.0-fun-uk.apk'
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
    assert len(bank)==15054 and len({q['id'] for q in bank})==15054
    for q in bank:
        assert q['id'] in fun_ids and q['text']==translations[q['id']]['text'] and q['choices']==translations[q['id']]['choices']
        assert q['correct']==source[q['id']]['correct'] and 'tags' not in q and q['category']!='Religion & Faith'
    for item in z.infolist():
        part='questions' if item.filename.endswith('questions.json') else 'audio' if item.filename.endswith(('.ogg','.wav','.mp3')) else 'visuals' if '/visuals/' in item.filename else 'app-and-other'
        parts[part]+=item.compress_size
lint=ET.parse(root/'android-tv-poc/app/build/reports/lint-results-debug.xml').getroot()
report={'version':'0.9.0-fun-uk','versionCode':16,'bytes':apk.stat().st_size,'MB':round(apk.stat().st_size/1e6,2),'MiB':round(apk.stat().st_size/1048576,2),'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'questionCount':len(bank),'categories':len({q['category'] for q in bank}),'assetFilesMatched':len(files),'compressedParts':dict(parts),'bank':json.loads((root/'browser-site/dist/bank-info.json').read_text(encoding='utf8')),'layout':json.loads((root/'browser-site/.qa/tv-validation.json').read_text(encoding='utf8')),'lint':{'errors':sum(x.attrib.get('severity')=='Error' for x in lint),'warnings':sum(x.attrib.get('severity')=='Warning' for x in lint)},'signature':'v2; same update certificate','zipAlignment':'passed','tests':'6 selector/solo tests +27local multiplayer tests passed','physicalTV':'Pending'}
assert report['lint']['errors']==0
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(out/'START-HERE.txt').write_text('''TriviTV 0.9.0 — Ukrainian Fun Bank

Install over the existing TriviTV app (same dev.trivitv.poc package/signing key; versionCode16). Start a NEW game/room.

15,054 Ukrainian questions across19categories. Derived only from English Fun Bank candidates with linked Ukrainian drafts.819linked drafts are held for existing Ukrainian wording/terminology/title/unit issues. No religion category; Fun Bank's date/year, US-specific and1950–1989culture gates applied. Some semantic/factual/translation verification remains pending; this is a test pool, not a fully fact-checked bank.

Same layouts, artwork, music and sound effects. Weighted category difficulty remains60/30/10 atstart to30/50/20 atend. Future long-question tagging/frequency penalty remains deferred.

Main-menu navigation updated as requested: focus on a mode selects it; OK moves focus to Start/Create room; the next OK activates that action. All four modes retain the same screen layout.

Bundled content runs without a PC. Phone rooms need internet and the matching iggro.com service. Existing rooms keep their old decks; create a new room.

Checks: clean Android build/lint, same-key signing, zipalignment, exact bundled assets, all15,054questions rendered in both TVlayouts without clipping; complete10Trivia/15Millionaire games, menu/remote/pause/reload/lifeline, selector and room tests. PhysicalTV testing remains pending.
''',encoding='utf8')
desktop=Path.home()/'Desktop/trivitv';desktop.mkdir(exist_ok=True);shutil.copy2(apk,desktop/apk.name)
print(json.dumps({k:report[k] for k in ('bytes','MB','MiB','sha256','questionCount','compressedParts')},indent=2))
