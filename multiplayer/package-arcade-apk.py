from pathlib import Path
import zipfile, hashlib, json, shutil, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
out=root/'artifacts/TriviTV-TV-Arcade';out.mkdir(exist_ok=True)
target=out/'TriviTV-TV-0.7.0-arcade-visuals.apk'
shutil.copy2(root/'android-tv-poc/app/build/outputs/apk/debug/app-debug.apk',target)
assets=root/'browser-site/dist'
with zipfile.ZipFile(target) as z:
 for f in assets.rglob('*'):
  if f.is_file():assert z.read('assets/web/'+f.relative_to(assets).as_posix())==f.read_bytes(),f
visuals=assets/'visuals'
report={'version':'0.7.0-arcade-visuals','versionCode':14,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bundledFiles':sum(f.is_file() for f in assets.rglob('*')),'assetsMatch':True,'visualFiles':sum(f.is_file() for f in visuals.rglob('*')),'serverTests':'27 local tests passed','soloQA':'Trivia10/10 and Millionaire15/15; all916questions in both layouts; no clipping; remote/settings/pause/lifeline/reload passed','audioQA':'15assets; continuous music/pause/countdown/mute/bounds passed','multiplayerBrowser':'Phone-first Turf bid privacy, independent capture/colors/animal badges; Imposter3phone role barrier/discussion, TV secret hidden; phone390px checked','deployment':'e1fc3fc8-e66d-487e-8a69-e2992f130151 at https://iggro.com','physicalTV':'Pending'}
issues=ET.parse(root/'android-tv-poc/app/build/reports/lint-results-debug.xml').getroot()
report['lint']={'errors':sum(x.attrib.get('severity')=='Error' for x in issues),'warnings':sum(x.attrib.get('severity')=='Warning' for x in issues)}
assert report['lint']['errors']==0
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(out/'START-HERE.txt').write_text('''TriviTV 0.7.0 — Arcade visuals

Install this APK over the existing TriviTV app. Same dev.trivitv.poc package and update signing key; versionCode14.
Main menu, Trivia, Millionaire, Imposter, Turf War, QR lobby and phone controllers now use the new screenshot-inspired palette and artwork. Animal player badges replace generic human silhouettes. Eight player colors remain distinct and are paired with animal and number. Mode cards use game symbols, not animals.

The question bank, game rules, selected music, sound effects and countdown remain in place. TV wrapper now explicitly serves SVG/PNG/WebP with their correct image types. Runtime artwork uses lightweight SVG plus a169KB WebP arena, rather than full design masters.

Use arrows and OK to choose one of four cards. Press Down for Settings/Play. Trivia has a separate friends/room action. Imposter requires3–8phones; Turf supports remote+onephone or two phones; Millionaire is solo.

Matching phone site is live at https://iggro.com. Reload the phone page if it was already open. Start a new room for testing.

Checks: full solo games/all916question layouts,27local multiplayer tests, continuous audio checks, Android build/lint and exact bundled asset comparison. Physical TV listening/remote verification remains pending.
''',encoding='utf8')
print(json.dumps(report,indent=2))
