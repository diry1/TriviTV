from pathlib import Path
import zipfile, hashlib, json, shutil
root=Path(__file__).resolve().parent.parent
out=root/'artifacts/TriviTV-TV-Turf-War'
out.mkdir(exist_ok=True)
source=root/'android-tv-poc/app/build/outputs/apk/debug/app-debug.apk'
target=out/'TriviTV-TV-0.6.0-turf-war.apk'
shutil.copy2(source,target)
assets=root/'browser-site/dist'
with zipfile.ZipFile(target) as archive:
    for file in assets.rglob('*'):
        if file.is_file():
            assert archive.read('assets/web/'+file.relative_to(assets).as_posix())==file.read_bytes(),file
report={'version':'0.6.0-turf-war','versionCode':13,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bundledFiles':sum(f.is_file() for f in assets.rglob('*')),'assetsMatch':True,'serverTests':'27 passed: Trivia, Imposter, Turf privacy/captures/defense/deadlines/cooldowns/five-lines','browserTest':'Four-mode menu and Turf question/selection TV960x540 checked; phone-first hidden bid verified','deployment':'Live https://iggro.com; 18c8e948-0fb0-49d8-b456-b7b9588f5eae','physicalTV':'Pending'}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(out/'START-HERE.txt').write_text('TriviTV 0.6.0 Turf War\n\nInstall over existing TriviTV. Same app ID and signing key. Start a NEW room.\nAll four modes are on the main menu with player counts. Millionaire is solo.\nTurf: exactly two players, remote + phone or two phones, shared 5x5 board. Phone bids first before remote; bids hidden until both commit, then question appears. Bank questions only.\nDifferent squares: each correct answer captures the chosen tile. Attacker has 10 seconds. A correct attacker captures even if opponent correctly answers elsewhere.\nSame free square: first correct wins. Exact server-time tie: no capture. Same owned square: explicit defense; both correct means owner keeps it. Correct attacker captures only if defender is wrong or times out.\nEvery contested tile cools down for the next turn; last free tile is exempt. Five in a straight horizontal, vertical or diagonal line wins. Simultaneous winning lines draw.\nLive service: https://iggro.com. Physical TV testing pending.\n',encoding='utf8')
print(json.dumps(report,indent=2))


