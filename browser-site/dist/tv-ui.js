import {localApi,clearProgress} from './local-state.js';
import {translate} from './i18n.js';
import {audio} from './audio-player.js';
const $=s=>document.querySelector(s), t=s=>translate(s,'uk');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const app=$('#app');
let config,state=null,session=null,mode='trivia',selected=new Set(),screen='home',categoryPage=0,busy=false,dialog=null,snapshot='',lastScreen='',lastQuestion='',lastPhase='',creditPage=0;
let returnFocus='settings';
try{session=JSON.parse(localStorage.getItem('trivitv-browser-session'));}catch{}
const nav=(row,col)=>`data-row="${row}" data-col="${col}"`;
function button(id,label,row,col,cls='secondary',disabled=false){return `<button id="${id}" class="${cls}" ${nav(row,col)} ${disabled?'disabled':''}>${label}</button>`;}
function available(){return [...selected].reduce((n,c)=>n+(config.pools.uk.Europe.categories[c]||0),0);}
function saveSettings(){try{localStorage.setItem('trivitv-browser-settings',JSON.stringify({mode,categories:[...selected]}));}catch{}}
function home(){const modes=[['trivia','✳','Вікторина','1–8 гравців','Зіграйте самі або запросіть друзів із телефонами.'],['millionaire','◇','Мільйонер','1 гравець','15 сходинок, 50:50 та шлях до мільйона.'],['imposter','◉','Імпостер','3–8 гравців','Таємне слово на телефонах. Знайдіть імпостера.'],['duel','▦','Битва за поле','2 гравці','Обирайте клітинки. Відповідайте. Зберіть п’ять у ряд.']];return `<section class="tv-home all-modes-home"><div class="screen-title"><div><div class="eyebrow">УКРАЇНСЬКА · ЄВРОПА</div><h1>Оберіть гру</h1></div><span id="pool-availability" class="pool-count">${available()} запитань</span></div><div class="tv-modes">${modes.map(([m,icon,name,count,desc],i)=>`<button id="mode-${m}" data-mode="${m}" ${nav(Math.floor(i/2),i%2)} class="mode ${mode===m?'active':''}" aria-pressed="${mode===m}"><span class="mode-icon">${icon}</span><strong>${name}</strong><small class="player-count">${count}</small><p>${desc}</p><span class="mode-check">${mode===m?'✓ Обрано':'Обрати'}</span></button>`).join('')}</div><div class="home-actions">${button('settings',`Категорії <span>${selected.size} з ${config.categories.length}</span>`,2,0)}${button('create',['duel','imposter'].includes(mode)?'Створити кімнату →':'Грати одному →',2,1,'primary',!available())}</div><div class="home-extra"><p class="screen-hint">Стрілки — навігація · OK — вибір</p>${mode==='trivia'?button('party-trivia','Вікторина з друзями · 2–8 →',3,1):''}</div></section>`;}
function settings(){const perPage=12,start=categoryPage*perPage,rows=config.categories.slice(start,start+perPage);return `<section class="settings-page"><div class="screen-title"><div><div class="eyebrow">НАЛАШТУВАННЯ</div><h1>Категорії</h1></div><span id="pool-availability" class="pool-count">${available()} запитань</span></div>
 <div class="settings-toolbar">${button('all-categories',selected.size===config.categories.length?'Зняти всі':'Обрати всі',0,0)}<span>${selected.size} з ${config.categories.length} обрано · ${categoryPage+1} / 2</span>${button('settings-done','Готово ✓',0,3,'primary')}</div>
 <div class="tv-categories">${rows.map((c,i)=>`<button id="cat-${start+i}" data-category="${esc(c)}" class="chip ${selected.has(c)?'selected':''}" aria-pressed="${selected.has(c)}" ${nav(1+Math.floor(i/4),i%4)}><strong>${esc(t(c))}</strong><span>${config.pools.uk.Europe.categories[c]}</span><b>${selected.has(c)?'✓':'+'}</b></button>`).join('')}</div><div class="page-actions">${button('categories-prev','← Попередні',4,0,'secondary',categoryPage===0)}<span>Усі категорії разом: 916 запитань</span>${button('categories-next','Наступні →',4,3,'secondary',categoryPage===1)}</div></section>`;}
function prizeLadder(){return `<aside class="prize-ladder" aria-labelledby="ladder-title"><div class="ladder-heading"><span class="eyebrow">МІЛЬЙОНЕР · БАЛИ</span><h2 id="ladder-title">${state.ladder.at(-1)===1000000?'Шлях до мільйона':'Драбина балів'}</h2></div><ol class="ladder-steps" style="--ladder-count:${state.total}" reversed start="${state.total}">${state.ladder.map((value,i)=>{const current=i===state.index,safe=[4,9].includes(i),passed=i<state.index||current&&state.won>=value,failed=current&&state.finishReason==='wrong';return `<li data-step="${i+1}" class="ladder-step ${current?'current':''} ${safe?'milestone':''} ${passed?'passed':''} ${failed?'failed':''}" ${current?'aria-current="step"':''} aria-label="Запитання ${i+1}: ${value.toLocaleString('uk')} балів${safe?', гарантований рівень':''}${current?', поточне':''}"><span class="step-number">${i+1}</span><strong>${value.toLocaleString('uk')}</strong><span class="step-mark" aria-hidden="true">${failed?'×':passed?'✓':safe?'◆':current?'›':''}</span></li>`;}).reverse().join('')}</ol><div class="ladder-status"><div><span>Здобуто</span><strong id="ladder-won">${state.won.toLocaleString('uk')}</strong></div><div><span>Гарантовано</span><strong id="ladder-secured">${state.secured.toLocaleString('uk')}</strong></div></div><small class="ladder-legend">◆ Гарантований рівень</small></aside>`;}
function game(){const q=state.question,revealed=['correct','reveal'].includes(state.phase),p=state.players[0],canAnswer=state.phase==='question'&&!state.questionPaused&&!p.answered,million=state.settings.mode==='millionaire';
 const picked=['answers','correct','reveal'].includes(state.phase);
 let actions='';
 if(state.phase==='question')actions=million?button('fifty',state.usedFifty?'50:50 · використано':'50:50',3,0,'secondary',state.usedFifty||p.answered)+button('walk','Забрати бали',3,1,'secondary',p.answered):button('pause-review',state.questionPaused?'Продовжити ▶':'Пауза Ⅱ',3,0);
 if(state.phase==='reveal')actions=million?button('next',state.finishReason==='wrong'||state.index===state.total-1?'Результат →':'Наступне запитання →',3,1,'primary'):button('next',state.index===state.total-1?'Результат →':'Далі →',3,0,'primary')+button('pause-review',state.review?.paused?'Продовжити ▶':'Пауза Ⅱ',3,1,'review-pause');
 const message=state.phase==='question'?(state.questionPaused?'Гру призупинено':million?'Оберіть одну відповідь':'Оберіть відповідь. Після хвилини — випадковий вибір.'):state.phase==='answers'?'Відкриваємо ваш вибір…':state.phase==='correct'?'Правильна відповідь:':million?(state.finishReason==='wrong'?`Гру завершено · ${state.won.toLocaleString('uk')} балів`:'Правильна відповідь:'):'Правильна відповідь:';
 return `<section class="tv-game ${million?'millionaire-game':''}">${million?'<div class="millionaire-stage">':''}<div class="game-meta"><span>${million?'МІЛЬЙОНЕР':'ВІКТОРИНА'} · ${state.index+1} / ${state.total}</span><span class="tag">${esc(t(q.category))}</span><strong class="prize">${million?`<small>НА КОНУ</small> ${state.ladder[state.index].toLocaleString('uk')} балів`:`${p.score} балів`}</strong>${!million?'<strong id="answer-countdown" class="timer" role="timer" aria-live="off"></strong>':''}</div>
 <div class="question-box"><h1 class="question" data-no-translate>${esc(q.text)}</h1></div>
 <div class="answers ${state.phase==='answers'?'revealing-picks':state.phase==='correct'?'revealing-correct':''}" data-stage="${state.phase}">${q.choices.map((choice,i)=>`<button id="answer-${i}" data-answer="${i}" ${nav(1+Math.floor(i/2),i%2)} class="answer ${picked&&p.answer===i?'picked':''} ${revealed&&i===q.correct?'correct':''} ${revealed&&p.answer===i&&i!==q.correct?'incorrect':''}" ${!canAnswer||q.eliminated.includes(i)?'disabled':''}><span>${'ABCD'[i]}</span><strong data-no-translate>${q.eliminated.includes(i)?'—':esc(choice)}</strong><b>${revealed&&i===q.correct?'✓':picked&&p.answer===i?'●':''}</b></button>`).join('')}</div>
 <div class="game-bottom"><div class="feedback" role="status"><span>${message}</span>${revealed&&state.finishReason!=='wrong'?`<strong data-no-translate>${esc(q.choices[q.correct])}</strong>`:''}${p.autoPicked?'<small>Випадковий вибір за таймером</small>':''}</div><div class="game-actions">${!million&&state.phase==='reveal'?'<div class="countdown-ring"><svg viewBox="0 0 48 48" aria-hidden="true"><circle class="ring-track" cx="24" cy="24" r="20"/><circle id="review-ring" class="ring-fill" cx="24" cy="24" r="20" pathLength="100" stroke-dasharray="100"/></svg></div>':''}${actions}</div></div>
 ${million?`</div>${prizeLadder()}`:''}</section>`;
}
function results(){const million=state.settings.mode==='millionaire';return `<section class="tv-results"><div class="eyebrow">${million?'МІЛЬЙОНЕР':'ВІКТОРИНА'} · РЕЗУЛЬТАТ</div><div class="trophy">✦</div><h1>${state.finishReason==='walked'?'Вдалий вихід!':'Гру завершено!'}</h1><div class="big-score">${(million?state.won:state.players[0].score).toLocaleString('uk')} <small>балів</small></div><p>${state.finishReason==='completed'?'Ви пройшли всі запитання. Зіграємо ще?':state.finishReason==='wrong'?'Кожне запитання — нова нагода дізнатися більше.':'Ви забрали здобуті бали.'}</p><div class="result-actions">${button('restart','Зіграти ще →',0,0,'primary')}${button('finish','Обрати іншу гру',0,1)}</div></section>`;}
const creditSections=[['Джерела запитань','База адаптована з OpenTriviaQA її спільноти авторів. Українські переклади та відбір для Європи збережено з наданої тестової версії TriviTV.','https://github.com/uberspot/OpenTriviaQA'],['Ліцензія CC BY-SA 4.0','Дані та переклади поширюються за Creative Commons Attribution–ShareAlike 4.0. При повторному використанні зберігайте авторство та умову ShareAlike.','https://creativecommons.org/licenses/by-sa/4.0/'],['Зміни та походження','Нормалізовано категорії, відсіяно структурні помилки, додано українські переклади та редакційний відбір ЄС. Збережено ID, варіанти відповідей і правильні відповіді. Ревізія джерела: dcc1cdf36c2985ed5c849d1f2265c5041ffcdfb9.','/questions.json'],['Тестова база','916 запитань у 20 категоріях. Переклади — чернетки; відбір консервативний, без незалежної перевірки всіх фактів. Складність не оцінена. Нових запитань не створено.','/credits.html']];
function credits(){const [heading,text,url]=creditSections[creditPage];return `<section class="tv-credits"><div class="screen-title"><h1>Джерела та ліцензія</h1><span>${creditPage+1} / 4</span></div><article><h2>${heading}</h2><p>${text}</p><a href="${url}" ${nav(0,0)}>Повне джерело ↗</a></article><div class="page-actions">${button('credits-prev','← Назад',1,0,'secondary',creditPage===0)}${button('credits-close','До гри',1,1,'primary')}${button('credits-next','Далі →',1,2,'secondary',creditPage===3)}</div></section>`;}
function showDialog(kind){dialog=kind;render();}
function modal(){return `<div class="modal-backdrop"><section class="tv-dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title"><h2 id="dialog-title">${dialog==='walk'?'Забрати здобуті бали?':'Завершити цю гру?'}</h2><p>${dialog==='walk'?'Поточний підйом завершиться.':'Ви повернетеся до вибору гри.'}</p><div>${button('dialog-cancel','Продовжити гру',0,0,'primary')}${button('dialog-confirm',dialog==='walk'?'Забрати бали':'Завершити',0,1)}</div></section></div>`;}
function focusNode(node){node?.focus({preventScroll:true});}
function render(preferred){
 const previous=document.activeElement?.id;
 let current=screen;
 if(state&&screen!=='credits')current=state.phase==='finished'?'results':state.phase==='lobby'?'lobby':'game';
 app.innerHTML=(current==='home'?home():current==='settings'?settings():current==='credits'?credits():current==='results'?results():current==='lobby'?`<section class="tv-results"><h1>Продовжити гру?</h1>${button('start','Почати →',0,0,'primary')}</section>`:game())+(dialog?modal():'');
 document.body.dataset.screen=current;
 $('#home').hidden=!state||screen==='credits';$('#home').textContent='Завершити гру';$('#home').dataset.row='-1';$('#home').dataset.col='1';
 $('#home').onclick=()=>showDialog('leave');
 const changed=current!==lastScreen||state?.question?.id!==lastQuestion;
 const defaultFocus=current==='home'?`mode-${mode}`:current==='settings'?'settings-done':current==='credits'?'credits-close':current==='results'?'restart':current==='lobby'?'start':state.phase==='question'?[...app.querySelectorAll('[data-answer]:not(:disabled)')][0]?.id:state.phase==='reveal'?'next':null;
 for(const el of app.querySelectorAll('button'))el.onclick=()=>handleClick(el);
 if(dialog)focusNode($('#dialog-cancel'));
 else if(preferred&&$(`#${preferred}`)&&!$(`#${preferred}`).disabled)focusNode($(`#${preferred}`));
 else if((changed||state?.phase!==lastPhase)&&defaultFocus)focusNode($(`#${defaultFocus}`));
 else if(previous&&$(`#${previous}`)&&!$(`#${previous}`).disabled)focusNode($(`#${previous}`));
 else if(defaultFocus)focusNode($(`#${defaultFocus}`));
 audio.sync(state,current);
 lastScreen=current;lastQuestion=state?.question?.id;lastPhase=state?.phase;
 saveSettings();fitText();countdown();
}
async function startGame(){await execute(async()=>{const value=await localApi('/api/rooms',{mode,language:'uk',region:'Europe',categories:[...selected]});session=value;try{localStorage.setItem('trivitv-browser-session',JSON.stringify({code:value.code,role:'host',playerId:value.playerId}));}catch{}state=await localApi('/api/rooms/local/action',{type:'start'});screen='home';snapshot=JSON.stringify(state);render();});}
async function action(type,extra={}){await execute(async()=>{state=await localApi('/api/rooms/local/action',{type,questionId:state.question?.id,...extra});snapshot=JSON.stringify(state);render();});}
async function execute(work){if(busy)return;busy=true;try{await work();}catch(error){notify(error.message);}finally{busy=false;}}
function leave(){clearProgress();state=null;session=null;dialog=null;snapshot='';screen='home';try{localStorage.removeItem('trivitv-browser-session');}catch{}render();}
function handleClick(el){
 if(el.disabled)return;
 audio.cue(['settings-done','credits-close','dialog-cancel','categories-prev','credits-prev'].includes(el.id)?'back':'press');
 if(el.dataset.mode){mode=el.dataset.mode;render(el.id);return;}
 if(el.dataset.category){const c=el.dataset.category;selected.has(c)?selected.delete(c):selected.add(c);render(el.id);return;}
 if(el.dataset.answer!==undefined){action('answer',{choice:Number(el.dataset.answer)});return;}
 switch(el.id){
  case 'multiplayer':case 'party-trivia':location.href='./multi/host.html?mode=trivia&create=1';break;
  case 'create':case 'restart':if(['duel','imposter'].includes(mode))location.href='./multi/host.html?mode='+mode+'&create=1';else startGame();break;
  case 'start':action('start');break;
  case 'settings':screen='settings';categoryPage=0;render();break;
  case 'settings-done':screen='home';render('settings');break;
  case 'all-categories':selected=selected.size===config.categories.length?new Set():new Set(config.categories);render(el.id);break;
  case 'categories-next':categoryPage=1;render('cat-12');break;
  case 'categories-prev':categoryPage=0;render('cat-0');break;
  case 'pause-review':action((state.phase==='question'?state.questionPaused:state.review?.paused)?'resume':'pause');break;
  case 'next':action('next',{skipReview:state.settings.mode==='trivia'});break;
  case 'fifty':action('fifty');break;
  case 'walk':showDialog('walk');break;
  case 'finish':leave();break;
  case 'dialog-cancel':dialog=null;render();break;
  case 'dialog-confirm':{const kind=dialog;dialog=null;kind==='walk'?action('walk'):leave();break;}
  case 'credits-prev':creditPage--;render(el.id);break;
  case 'credits-next':creditPage++;render(el.id);break;
  case 'credits-close':screen='home';render(returnFocus);break;
 }
}
function notify(text){$('#notice').textContent=text;$('#notice').hidden=false;clearTimeout(notify.timer);notify.timer=setTimeout(()=>$('#notice').hidden=true,5000);}
function countdown(){
 audio.tick();
 if(!state)return;
 const timer=$('#answer-countdown');if(timer){const remaining=state.questionPaused?state.questionRemainingMs:Math.max(0,(state.questionEndsAt||0)-Date.now());const s=Math.ceil(remaining/1000);timer.textContent=state.phase!=='question'?'':state.questionPaused?'Пауза':`${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;}
 if(state.review){const ms=state.review.paused?state.review.remainingMs:Math.max(0,state.review.endsAt-Date.now());$('#review-ring')?.setAttribute('stroke-dashoffset',String(100*(1-ms/state.review.durationMs)));}
}
// Explicit logical rows/columns, never off-screen geometry or browser spatial navigation.
function remote(key,repeat=false){
 if(['Enter',' ','MediaPlayPause'].includes(key)&&repeat)return true;
 if(['Escape','BrowserBack','GoBack'].includes(key)){audio.cue('back');if(dialog){dialog=null;render();}else if(screen==='settings'){screen='home';render('settings');}else if(screen==='credits'){screen='home';render(returnFocus);}else if(state)showDialog('leave');return true;}
 if(key==='MediaPlayPause'&&state?.settings.mode==='trivia'&&['question','reveal'].includes(state.phase)){action((state.phase==='question'?state.questionPaused:state.review?.paused)?'resume':'pause');return true;}
 const scope=dialog?$('.tv-dialog'):document;
 const nodes=[...scope.querySelectorAll('button[data-row]:not(:disabled),a[data-row]')].filter(el=>el.getClientRects().length&&!el.closest('[hidden]'));
 if(!nodes.length)return false;
 const active=document.activeElement;
 if(key==='Enter'||key===' '){if(nodes.includes(active))active.click();else focusNode(nodes[0]);return true;}
 if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(key))return false;
 if(!nodes.includes(active)){focusNode(nodes.find(n=>n.id===`mode-${mode}`)||nodes[0]);return true;}
 const row=Number(active.dataset.row),col=Number(active.dataset.col),vertical=['ArrowUp','ArrowDown'].includes(key),sign=['ArrowDown','ArrowRight'].includes(key)?1:-1;
 let target;
 if(vertical){const rows=[...new Set(nodes.map(n=>Number(n.dataset.row)))].filter(r=>(r-row)*sign>0).sort((a,b)=>(a-b)*sign);if(rows.length)target=nodes.filter(n=>Number(n.dataset.row)===rows[0]).sort((a,b)=>Math.abs(Number(a.dataset.col)-col)-Math.abs(Number(b.dataset.col)-col))[0];}
 else target=nodes.filter(n=>Number(n.dataset.row)===row&&(Number(n.dataset.col)-col)*sign>0).sort((a,b)=>(Number(a.dataset.col)-Number(b.dataset.col))*sign)[0];
 if(target&&target!==active)audio.cue('highlight');focusNode(target||active);return true;
}
window.TriviTVRemote={key:remote,back:()=>remote('Escape')};
document.addEventListener('keydown',e=>{if(remote(e.key,e.repeat)){e.preventDefault();e.stopImmediatePropagation();}},true);
function fitText(){
 for(const node of document.querySelectorAll('.question,.answer>strong,.feedback')){
  node.style.fontSize='';const min=node.classList.contains('feedback')?12:document.documentElement.clientHeight<600?16:18;
  let size=parseFloat(getComputedStyle(node).fontSize);
  while(size>min&&(node.scrollHeight>node.clientHeight+1||node.scrollWidth>node.clientWidth+1)){size--;node.style.fontSize=`${size}px`;}
 }
}
window.addEventListener('resize',fitText);
// Footer is part of the explicit focus map; the logo and fixed language are not stops.
$('.logo').tabIndex=-1;$('.logo').removeAttribute('href');$('.language-picker').hidden=true;
const creditLink=$('footer a');creditLink.id='credits';creditLink.dataset.row='5';creditLink.dataset.col='0';creditLink.textContent='Джерела · CC BY-SA 4.0';
creditLink.onclick=e=>{e.preventDefault();returnFocus=document.activeElement?.id||'settings';screen='credits';creditPage=0;render();};
$('footer span').textContent='Стрілки · OK';$('.header-note').textContent='УКРАЇНСЬКА · ЄВРОПА';document.title='TriviTV · Українська · Європа';
for(const [kind,label,col] of [['music','Музика',1],['effects','Звуки',2]]){
 const control=document.createElement('button');control.id=`audio-${kind}`;control.className='quiet';control.dataset.row='5';control.dataset.col=col;
 const update=()=>{control.textContent=`${label}: ${audio.settings[kind]?'увімк.':'вимк.'}`;control.setAttribute('aria-pressed',String(audio.settings[kind]));};update();
 if(kind==='music')window.addEventListener('trivitv-audio-error',()=>{control.textContent='Музика: збій';control.setAttribute('aria-label',`Помилка музики: ${audio.status.lastError}. Натисніть, щоб вимкнути.`);});
 control.onclick=()=>{audio.toggle(kind);update();if(kind==='effects'&&audio.settings.effects)audio.cue('press');};$('footer').append(control);
}
try{
 config=await localApi('/api/config');selected=new Set(config.categories);
 try{const saved=JSON.parse(localStorage.getItem('trivitv-browser-settings'));if(saved){mode=['trivia','millionaire','imposter','duel'].includes(saved.mode)?saved.mode:'trivia';selected=new Set(saved.categories.filter(c=>config.categories.includes(c)));}}catch{}
 const launch=new URLSearchParams(location.search);if(['trivia','millionaire'].includes(launch.get('mode')))mode=launch.get('mode');if(launch.get('start')==='1'){session=null;state=null;history.replaceState(null,'',location.pathname);await startGame();}
 if(session){try{state=await localApi('/api/rooms/local');if(state.phase==='lobby')state=await localApi('/api/rooms/local/action',{type:'start'});}catch{session=null;}}
 render();
 setInterval(async()=>{if(!state||busy)return;try{const next=await localApi('/api/rooms/local');const json=JSON.stringify(next);if(json!==snapshot){state=next;snapshot=json;if(screen!=='credits')render();}}catch(error){notify(error.message);}},100);
 setInterval(countdown,100);
}catch(error){app.innerHTML=`<section><h1>Не вдалося завантажити гру</h1><p>${esc(error.message)}</p></section>`;}
