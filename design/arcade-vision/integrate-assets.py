from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[2]
pack=R/'design/arcade-vision/assets-v1';dist=R/'browser-site/dist';v=dist/'visuals'
v.mkdir(exist_ok=True)
for folder in ['avatars','modes','icons','panels','backgrounds','brand']:
    shutil.copytree(pack/folder,v/folder,dirs_exist_ok=True)
(v/'art').mkdir(exist_ok=True)
shutil.copy2(pack/'art/party-arena.webp',v/'art/party-arena.webp')
for name in ['wordmark-navy','wordmark-cream']:
    shutil.copy2(pack/f'png/brand/{name}.png',v/f'brand/{name}.png')
shutil.copy2(pack/'tokens.json',v/'tokens.json')
shutil.copy2(pack/'PROMPT.md',v/'ART-PROVENANCE.md')

p=dist/'index.html';s=p.read_text(encoding='utf8')
if '/visuals/arcade.css' in s:
    print('Runtime artwork refreshed; integration hooks already exist. Skin CSS preserved.')
    raise SystemExit(0)
s=s.replace('<link rel="stylesheet" href="/tv-layout.css" />','<link rel="stylesheet" href="/tv-layout.css" />\n    <link rel="stylesheet" href="/visuals/arcade.css" />');p.write_text(s,encoding='utf8')
p=dist/'tv-ui.js';s=p.read_text(encoding='utf8')
s=s.replace('${nav(Math.floor(i/2),i%2)}','${nav(0,i)}')
s=s.replace('<span class="mode-icon">${icon}</span>','<span class="mode-icon"><img src="./visuals/modes/${m===\'duel\'?\'turf\':m}.svg" alt="" aria-hidden="true"></span>')
s=s.replace("`,2,0)}${button('create'","`,1,0)}${button('create'")
s=s.replace("'Грати одному →',2,1,","'Грати одному →',1,3,")
s=s.replace("'Вікторина з друзями · 2–8 →',3,1)","'Вікторина з друзями · 2–8 →',2,3)")
s=s.replace("document.body.dataset.screen=current;","document.body.dataset.screen=current;document.body.dataset.visualMode=state?.settings?.mode||mode;")
s=s.replace("$('.logo').tabIndex=-1;","document.body.classList.add('arcade-ui','solo-tv');$('.logo').innerHTML='<img src=\"./visuals/brand/wordmark-cream.png\" alt=\"TriviTV\">';$('.logo').tabIndex=-1;")
p.write_text(s,encoding='utf8')

# Shared multiplayer visuals use paths relative to the module, so native, /tv/ and / all work.
p=R/'multiplayer/public/multi/party-ui.js';s=p.read_text(encoding='utf8')
s="import {modeArt} from './visual-identity.js';\n"+s
s=s.replace('<span>${m.icon}</span>','<span>${modeArt(id)}</span>')
p.write_text(s,encoding='utf8')
p=R/'multiplayer/public/multi/app.js';s=p.read_text(encoding='utf8')
s="import {playerVisual,animalBadge,modeArt,visuals} from './visual-identity.js';\n"+s
s=s.replace("function update(value){","function update(value){value.players=value.players.map((p,i)=>({...p,color:playerVisual(p,i).color}));")
a=s.index('function playerDot(');b=s.index('\nfunction votes',a)
s=s[:a]+'''function playerDot(p,index){const identity=playerVisual(p,index);return `<i class="player-dot" style="--player-color:${identity.color}" title="${esc(p.name)} · ${index+1}" aria-label="${esc(p.name)}, гравець ${index+1}"><img src="${animalBadge(p,index)}" alt="" aria-hidden="true"><span>${index+1}</span></i>`;}'''+s[b:]
s=s.replace("document.body.dataset.phase=phase||'setup';","document.body.dataset.phase=phase||'setup';document.body.dataset.visualMode=state?.mode||newMode;")
s=s.replace('<strong>${m.name}</strong><small>${m.description}</small></a>','${modeArt(id)}<strong>${m.name}</strong><small>${m.description}</small></a>')
s=s.replace("const host=document.body.dataset.role", "document.body.classList.add('arcade-ui','party-app');document.querySelector('.logo').innerHTML=`<img src=\"${new URL('brand/wordmark-cream.png',visuals).href}\" alt=\"TriviTV\">`;\nconst host=document.body.dataset.role")
p.write_text(s,encoding='utf8')
for rel in ['multiplayer/public/multi/host.html','multiplayer/public/index.html']:
    p=R/rel;s=p.read_text(encoding='utf8');href='../visuals/arcade.css' if '/multi/' in rel else '/visuals/arcade.css';s=s.replace('<script type="module"',f'<link rel="stylesheet" href="{href}"><script type="module"');p.write_text(s,encoding='utf8')
p=R/'multiplayer/prepare.mjs';s=p.read_text(encoding='utf8');s+='\nawait fs.cp(\'../browser-site/dist/visuals\',\'public/visuals\',{recursive:true});\n';p.write_text(s,encoding='utf8')
p=R/'browser-site/preview.mjs';s=p.read_text(encoding='utf8');s=s.replace("file.pathname.endsWith('.ogg')?", "file.pathname.endsWith('.svg')?'image/svg+xml':file.pathname.endsWith('.png')?'image/png':file.pathname.endsWith('.webp')?'image/webp':file.pathname.endsWith('.ogg')?");p.write_text(s,encoding='utf8')
p=R/'android-tv-poc/app/build.gradle';s=p.read_text();s=s.replace('versionCode 13','versionCode 14').replace("versionName '0.6.0-turf-war'","versionName '0.7.0-arcade-visuals'");p.write_text(s)
print('Integrated runtime artwork, source links, player visuals and APK version.')
