const fail=(ok,message,status=409)=>{if(!ok)throw Object.assign(Error(message),{status});};
const random=n=>crypto.getRandomValues(new Uint32Array(1))[0]%n;
const shuffle=a=>[...a].map(v=>({v,r:random(2**30)})).sort((a,b)=>a.r-b.r).map(x=>x.v);
// Original Ukrainian word collection; not copied from the reference website.
export const WORDS=[['Їжа','Вареники'],['Їжа','Кавун'],['Їжа','Морозиво'],['Їжа','Піца'],['Їжа','Попкорн'],['Їжа','Борщ'],['Тварини','Пінгвін'],['Тварини','Жирафа'],['Тварини','Їжак'],['Тварини','Дельфін'],['Тварини','Кіт'],['Тварини','Панда'],['Місця','Бібліотека'],['Місця','Аеропорт'],['Місця','Пляж'],['Місця','Зоопарк'],['Місця','Кінотеатр'],['Місця','Стадіон'],['Речі','Парасоля'],['Речі','Рюкзак'],['Речі','Велосипед'],['Речі','Дзеркало'],['Речі','Навушники'],['Речі','Компас'],['Заняття','Риболовля'],['Заняття','Танці'],['Заняття','Малювання'],['Заняття','Плавання'],['Природа','Веселка'],['Природа','Вулкан'],['Природа','Сніжинка'],['Природа','Водоспад'],['Транспорт','Трамвай'],['Транспорт','Підводний човен'],['Транспорт','Повітряна куля'],['Музика','Гітара'],['Музика','Барабан'],['Музика','Піаніно'],['Спорт','Футбол'],['Спорт','Шахи']];
export function minPlayers(r){return r.mode==='imposter'?3:2;}
export function maxPlayers(r){return r.mode==='duel'?2:8;}
export function beginImposter(r,now){const [category,word]=WORDS[random(WORDS.length)];r.imposter={word,category,imposterId:r.players[random(r.players.length)].id,ready:[],votes:{},turnOrder:shuffle(r.players.map(p=>p.id)),winner:null};r.phase='roles';r.deadline=null;r.paused=false;r.revision++;}
export function startDiscussion(r,now){r.phase='discussion';r.deadline=now+180000;r.remaining=180000;r.revision++;}
export function startVoting(r,now){r.phase='voting';r.paused=false;r.deadline=now+60000;r.remaining=60000;r.revision++;}
export function finishVoting(r){const counts=Object.values(r.imposter.votes).reduce((a,id)=>(a[id]=(a[id]||0)+1,a),{});const best=Math.max(0,...Object.values(counts)),top=Object.keys(counts).filter(id=>counts[id]===best);r.imposter.accusedId=top.length===1?top[0]:null;r.imposter.winner=r.imposter.accusedId===r.imposter.imposterId?'group':'imposter';r.phase='finished';r.deadline=null;r.paused=false;r.revision++;}
export function partyTick(r,now){if(r.paused||r.deadline===null||now<r.deadline)return;if(r.mode==='imposter'){if(r.phase==='discussion')startVoting(r,now);else if(r.phase==='voting')finishVoting(r);}else if(r.mode==='duel'&&r.phase==='claim'){for(const p of r.players){if(p.claimPending){const tile=claimable(r,p.id)[0];if(tile!==undefined)r.duel.boards[p.id][tile]=true;p.claimPending=false;}}finishClaims(r);}}
export function claimable(r,id){const b=r.duel.boards[id];return b.flatMap((owned,i)=>!owned&&(i%5===0||neighbors(i).some(j=>b[j]))?[i]:[]);}
const neighbors=i=>[i%5>0?i-1:-1,i%5<4?i+1:-1,i>=5?i-5:-1,i<20?i+5:-1].filter(n=>n>=0);
export function connected(board){const seen=new Set(),queue=board.flatMap((v,i)=>v&&i%5===0?[i]:[]);for(const i of queue){if(seen.has(i))continue;seen.add(i);if(i%5===4)return true;for(const j of neighbors(i))if(board[j]&&!seen.has(j))queue.push(j);}return false;}
export function beginDuel(r){r.duel={boards:Object.fromEntries(r.players.map(p=>[p.id,Array(25).fill(false)])),winners:[]};}
export function revealDuel(r,now){r.phase='claim';r.deadline=now+20000;r.remaining=20000;for(const p of r.players)p.claimPending=p.answers[r.index]===r.questions[r.index].correct;r.revision++;finishClaims(r);}
function finishClaims(r){if(r.players.some(p=>p.claimPending))return;r.duel.winners=r.players.filter(p=>connected(r.duel.boards[p.id])).map(p=>p.id);r.phase=r.duel.winners.length?'finished':'reveal';if(r.index===r.questions.length-1&&r.phase!=='finished'){const best=Math.max(...r.players.map(p=>p.score));r.duel.winners=r.players.filter(p=>p.score===best).map(p=>p.id);r.phase='finished';}r.deadline=null;r.revision++;}
export function partyAction(r,who,body,now){
 if(r.mode==='imposter'){
  if(body.type==='ready'){fail(who.player&&r.phase==='roles','Зараз підтвердження недоступне');if(!r.imposter.ready.includes(who.player.id))r.imposter.ready.push(who.player.id);r.revision++;if(r.imposter.ready.length===r.players.length)startDiscussion(r,now);return true;}
  if(body.type==='vote'){fail(who.player&&r.phase==='voting'&&!r.paused,'Зараз голосування недоступне');fail(!Object.hasOwn(r.imposter.votes,who.player.id),'Голос уже прийнято');fail(body.playerId!==who.player.id&&r.players.some(p=>p.id===body.playerId),'Оберіть іншого гравця');r.imposter.votes[who.player.id]=body.playerId;r.revision++;if(Object.keys(r.imposter.votes).length===r.players.length)finishVoting(r);return true;}
  if(body.type==='voting'){fail(who.role==='host', 'Лише ведучий керує грою',403);fail(r.phase==='discussion','Спершу перегляньте ролі');startVoting(r,now);return true;}
  if(body.type==='imposter-guess'){fail(who.player?.id===r.imposter?.imposterId&&['discussion','voting'].includes(r.phase)&&!r.paused,'Зараз відповідь недоступна',403);const guess=String(body.word||'').normalize('NFC').trim().toLocaleLowerCase('uk');fail(guess.length>0&&guess.length<=40,'Введіть слово');r.imposter.guess=guess;r.imposter.winner=guess===r.imposter.word.toLocaleLowerCase('uk')?'imposter':'group';r.imposter.guessedCorrect=r.imposter.winner==='imposter';r.phase='finished';r.deadline=null;r.revision++;return true;}
  if(body.type==='again'){fail(who.role==='host','Лише ведучий керує грою',403);fail(r.phase==='finished','Раунд ще триває');beginImposter(r,now);return true;}
 }
 if(r.mode==='duel'&&body.type==='claim'){fail(who.player&&r.phase==='claim'&&!r.paused&&who.player.claimPending,'Зараз вибір клітинки недоступний');fail(body.questionId===r.questions[r.index].id,'Раунд уже змінився');fail(Number.isInteger(body.tile)&&claimable(r,who.player.id).includes(body.tile),'Оберіть доступну клітинку');r.duel.boards[who.player.id][body.tile]=true;who.player.claimPending=false;r.revision++;finishClaims(r);return true;}
 return false;
}
export function partyView(r,who){
 if(r.mode==='imposter'){
  if(!r.imposter)return {};
  const ended=r.phase==='finished',secret=who.player&&r.phase!=='lobby'?{role:who.player.id===r.imposter.imposterId?'imposter':'group',...(who.player.id!==r.imposter.imposterId?{word:r.imposter.word}:{})}:undefined;
  return {secret,imposter:{category:r.imposter.category,ready:r.imposter.ready,turnOrder:r.imposter.turnOrder,voted:Object.keys(r.imposter.votes),...(ended?{word:r.imposter.word,imposterId:r.imposter.imposterId,accusedId:r.imposter.accusedId,winner:r.imposter.winner,votes:r.imposter.votes,guess:r.imposter.guess,guessedCorrect:r.imposter.guessedCorrect}:{})}};
 }
 if(r.mode==='duel'&&r.duel)return {duel:{boards:r.duel.boards,winners:r.duel.winners,claimable:who.player&&who.player.claimPending?claimable(r,who.player.id):[],pending:r.players.filter(p=>p.claimPending).map(p=>p.id)}};
 return {};
}
