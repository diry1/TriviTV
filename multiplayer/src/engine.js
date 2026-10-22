import {triviaQuestions} from '../../game-rules/difficulty.mjs';
import {isTurf,turfTick,turfAction,turfView} from './turf-engine.js';
import {minPlayers,maxPlayers,beginImposter,beginDuel,revealDuel,partyTick,partyAction,partyView} from './party-engine.js';
import {PLAYER_COLORS} from '../public/multi/player-colors.js';
export const ROOM_TTL=4*60*60*1000;
function assignColors(room){const used=new Set();for(const p of room.players){if(!PLAYER_COLORS.includes(p.color)||used.has(p.color))p.color=PLAYER_COLORS.find(c=>!used.has(c)&&!room.players.some(other=>other!==p&&other.color===c));used.add(p.color);}}
export function requireThat(ok,message,status=400){if(!ok)throw Object.assign(new Error(message),{status});}
export function shuffled(a){return [...a].map(v=>({v,n:crypto.getRandomValues(new Uint32Array(1))[0]})).sort((a,b)=>a.n-b.n).map(x=>x.v);}
export const token=()=>crypto.randomUUID()+crypto.randomUUID();
export function createRoom(code,bank,categories,now=Date.now(),options={}){
 const mode=options.mode||'trivia';requireThat(['trivia','imposter','duel'].includes(mode),'Оберіть режим');
 const available=[...new Set(bank.map(q=>q.category))];
 requireThat(Array.isArray(categories)&&categories.length&&categories.every(c=>available.includes(c)),'Оберіть категорії');
 const pool=bank.filter(q=>categories.includes(q.category));
 let questions=(mode==='trivia'?triviaQuestions(pool,10):shuffled(pool).slice(0,916)).map(q=>{
  const order=shuffled([0,1,2,3]);return {id:q.id,text:q.text,category:q.category,choices:order.map(i=>q.choices[i]),correct:order.indexOf(q.correct)};
 });
 if(mode==='imposter')questions=[];

 requireThat(mode==='imposter'||questions.length,'Немає запитань');
 return {code,mode,host:token(),createdAt:now,expiresAt:now+ROOM_TTL,categories,questions,players:[],index:0,phase:'lobby',deadline:null,paused:false,remaining:0,revision:1};
}
export function identity(room,secret){if(secret===room.host)return {role:'host',player:room.players.find(p=>p.controller==='remote')};const player=room.players.find(p=>p.token===secret);requireThat(player,'Поверніться до входу в кімнату',401);return {role:'player',player};}
export function setRemotePlayer(room,enabled){
 requireThat(room.phase==='lobby','Склад гравців можна змінити лише до початку гри',409);
 requireThat(!enabled||room.mode!=='imposter','Для таємної ролі потрібен телефон',409);
 const existing=room.players.find(p=>p.controller==='remote');
 if(enabled&&!existing){const name=['Гравець TV','TV · пульт','Пульт TV'].find(n=>!room.players.some(p=>p.name===n))||'TV '+crypto.randomUUID().slice(0,4);const player=join(room,name);player.controller='remote';}
 if(!enabled&&existing){room.players=room.players.filter(p=>p!==existing);room.revision++;}
}
export function join(room,name){
 assignColors(room);
 requireThat(room.phase==='lobby','Гру вже розпочато',409);requireThat(room.players.length<maxPlayers(room),'Кімната вже заповнена',409);
 name=String(name??'').normalize('NFC').trim();requireThat(name.length>=1&&name.length<=20&&!/[\p{C}<>]/u.test(name),'Ім’я: 1–20 символів');
 requireThat(!room.players.some(p=>p.name.toLocaleLowerCase()===name.toLocaleLowerCase()),'Це ім’я вже зайняте',409);
 const player={id:crypto.randomUUID(),token:token(),name,color:PLAYER_COLORS.find(c=>!room.players.some(p=>p.color===c)),score:0,answers:{}};room.players.push(player);room.revision++;return player;
}
export function reveal(room,now=Date.now()){if(room.phase!=='question')return;const q=room.questions[room.index];for(const p of room.players)if(p.answers[room.index]===q.correct)p.score+=100;room.phase='reveal';room.deadline=null;room.paused=false;room.revision++;if(room.mode==='duel')revealDuel(room,now);}
export function tick(room,now=Date.now()){if(now>=room.expiresAt){room.phase='closed';room.deadline=null;return;}if(isTurf(room)){turfTick(room,now);return;}if(room.phase==='question'&&!room.paused&&now>=room.deadline)reveal(room,now);partyTick(room,now);}
function begin(room,now){room.phase='question';room.paused=false;room.deadline=now+60000;room.remaining=60000;room.revision++;}
export function act(room,secret,body,now=Date.now()){
 assignColors(room);
 tick(room,now);requireThat(room.phase!=='closed','Кімнату закрито',410);const who=identity(room,secret);
 if(room.mode==='duel'&&turfAction(room,who,body,now))return;
 if(partyAction(room,who,body,now))return;
 if(body.type==='remote-player'){requireThat(who.role==='host','Лише ведучий керує грою',403);requireThat(typeof body.enabled==='boolean','Оберіть режим пульта');setRemotePlayer(room,body.enabled);return;}
 if(body.type==='leave'){requireThat(who.role==='player'&&room.phase==='lobby','Вихід зараз недоступний',409);room.players=room.players.filter(p=>p!==who.player);room.revision++;return;}
 if(body.type==='answer'){
  requireThat(who.player,'Увімкніть гравця з пультом у кімнаті',403);requireThat(room.phase==='question'&&!room.paused,'Зараз відповіді не приймаються',409);
  requireThat(body.questionId===room.questions[room.index].id,'Запитання вже змінилося',409);
  requireThat(Number.isInteger(body.choice)&&body.choice>=0&&body.choice<4,'Оберіть відповідь');
  requireThat(!Object.hasOwn(who.player.answers,room.index),'Відповідь уже прийнято',409);
  who.player.answers[room.index]=body.choice;room.revision++;
  if(room.players.every(p=>Object.hasOwn(p.answers,room.index)))reveal(room,now);return;
 }
 requireThat(who.role==='host','Лише ведучий керує грою',403);
 switch(body.type){
  case 'start':requireThat(room.phase==='lobby'&&room.players.length>=minPlayers(room),'Потрібно щонайменше '+minPlayers(room)+' гравці',409);if(room.mode==='imposter')beginImposter(room,now);else{if(room.mode==='duel')beginDuel(room);begin(room,now);}break;
  case 'next':requireThat(room.phase==='reveal','Дочекайтеся відповідей',409);if(room.index+1===room.questions.length){room.phase='finished';room.revision++;}else{room.index++;begin(room,now);}break;
  case 'pause':requireThat(['question','discussion','voting','claim'].includes(room.phase)&&!room.paused,'Зараз пауза недоступна',409);room.remaining=Math.max(0,room.deadline-now);room.deadline=null;room.paused=true;room.revision++;break;
  case 'resume':requireThat(['question','discussion','voting','claim'].includes(room.phase)&&room.paused,'Гру не призупинено',409);room.deadline=now+room.remaining;room.paused=false;room.revision++;break;
  case 'close':room.phase='closed';room.deadline=null;room.revision++;break;
  default:requireThat(false,'Невідома дія');
 }
}
export function view(room,secret,now=Date.now()){
 assignColors(room);
 const who=identity(room,secret);if(isTurf(room))return turfView(room,who,now);const q=room.questions[room.index],reveal=['reveal','claim','finished'].includes(room.phase);
 return {mode:room.mode||'trivia',minPlayers:minPlayers(room),maxPlayers:maxPlayers(room),...partyView(room,who),code:room.code,role:who.role,you:who.player?.id,phase:room.phase,index:room.index,total:room.questions.length,revision:room.revision,serverNow:now,expiresAt:room.expiresAt,deadline:room.deadline,paused:room.paused,remaining:room.remaining,
  question:['question','reveal','claim'].includes(room.phase)?{id:q.id,text:q.text,category:q.category,choices:q.choices,...(reveal?{correct:q.correct}:{})}:null,
  players:room.players.map(p=>({id:p.id,name:p.name,color:p.color,score:p.score,answered:Object.hasOwn(p.answers,room.index),...(reveal||p.id===who.player?.id?{answer:p.answers[room.index]}:{})}))};
}
