const fail=(ok,message,status=409)=>{if(!ok)throw Object.assign(Error(message),{status});};
const current=r=>r.questions[r.index%r.questions.length];
export const isTurf=r=>r.mode==='duel'&&r.duel?.version===2;
export function fiveInRow(board,id){
 const lines=[];for(let n=0;n<5;n++){lines.push(Array.from({length:5},(_,i)=>n*5+i));lines.push(Array.from({length:5},(_,i)=>i*5+n));}
 lines.push([0,6,12,18,24],[4,8,12,16,20]);return lines.filter(line=>line.every(i=>board[i]===id));
}
export function availableTiles(r){const d=r.duel,empty=d.board.flatMap((owner,i)=>owner===null?[i]:[]);return d.board.flatMap((_,i)=>d.cooldowns[i]!==r.index||empty.length===1&&empty[0]===i?[i]:[]);}
export function startTurf(r,now){r.duel={version:2,board:Array(25).fill(null),cooldowns:{},bids:{},answerTimes:{},winners:[],winningLines:[],outcome:[]};beginSelection(r,now);}
export function beginSelection(r,now){r.duel.bids={};r.duel.answerTimes={};r.duel.playerEnds={};r.duel.firstCorrectAt=null;r.duel.outcome=[];r.duel.before=null;r.duel.attacking=[];r.duel.contested=false;r.duel.defended=false;r.phase='selection';r.deadline=now+90000;r.remaining=90000;r.paused=false;r.revision++;}
function canBid(r,p){const phone=r.players.find(p=>p.controller!=='remote');return !(p.controller==='remote'&&phone&&!Object.hasOwn(r.duel.bids,phone.id));}
function revealBids(r,now){const d=r.duel;d.before=[...d.board];const [a,b]=r.players;d.contested=d.bids[a.id]===d.bids[b.id];d.defended=d.contested&&r.players.some(p=>d.before[d.bids[p.id]]===p.id);d.attacking=r.players.filter(p=>{const owner=d.before[d.bids[p.id]];return owner!==null&&owner!==p.id;}).map(p=>p.id);r.phase='bids';r.deadline=now+3500;r.remaining=3500;r.revision++;}
export function beginTurfQuestion(r,now){fail(r.phase==='bids','Спершу оберіть клітинки');const d=r.duel;d.questionStartedAt=now;d.playerEnds=Object.fromEntries(r.players.map(p=>[p.id,now+(d.attacking.includes(p.id)?10000:60000)]));r.phase='question';r.deadline=Math.min(...Object.values(d.playerEnds));r.remaining=r.deadline-now;r.revision++;}
function answered(r,p){return Object.hasOwn(p.answers,r.index);}
function correct(r,p){return p.answers[r.index]===current(r).correct;}
function finalise(r){const d=r.duel;for(const p of r.players)if(correct(r,p))p.score+=100;d.winners=r.players.filter(p=>fiveInRow(d.board,p.id).length).map(p=>p.id);d.winningLines=d.winners.flatMap(id=>fiveInRow(d.board,id));r.phase=d.winners.length?'finished':'reveal';r.deadline=null;r.paused=false;r.revision++;}
export function resolveTurf(r){const d=r.duel,[a,b]=r.players;
 if(d.contested){const tile=d.bids[a.id],owner=d.before[tile];let winner=null;
  if(d.defended){const attacker=r.players.find(p=>p.id!==owner),defender=r.players.find(p=>p.id===owner);if(correct(r,attacker)&&!correct(r,defender))winner=attacker.id;else winner=owner;}
  else{const winners=r.players.filter(p=>correct(r,p));if(winners.length===1)winner=winners[0].id;else if(winners.length===2){const at=d.answerTimes[a.id],bt=d.answerTimes[b.id];if(at!==bt)winner=at<bt?a.id:b.id;}}
  d.board[tile]=winner||owner;d.cooldowns[tile]=r.index+1;d.outcome=[{tile,owner:d.board[tile],kind:d.defended&&correct(r,a)&&correct(r,b)?'defended':winner?'battle-won':'battle-tie'}];
 }else{
  const next=[...d.before];d.outcome=r.players.map(p=>{const tile=d.bids[p.id],ok=correct(r,p);if(ok)next[tile]=p.id;return {tile,owner:ok?p.id:d.before[tile],kind:ok?(d.attacking.includes(p.id)?'captured':'claimed'):'missed'};});d.board=next;
 }
 finalise(r);
}
function planNext(r,now){const d=r.duel;
 if(d.contested&&!d.defended&&r.players.some(p=>correct(r,p))){d.firstCorrectAt??=Math.min(...r.players.filter(p=>correct(r,p)).map(p=>d.answerTimes[p.id]));if(r.players.every(p=>answered(r,p))||now>=d.firstCorrectAt+100){resolveTurf(r);return;}r.deadline=d.firstCorrectAt+100;return;}
 if(r.players.every(p=>answered(r,p))){resolveTurf(r);return;}
 const future=r.players.filter(p=>!answered(r,p)).map(p=>d.playerEnds[p.id]);r.deadline=Math.min(...future);
}
export function turfTick(r,now){if(r.paused||r.deadline===null||now<r.deadline)return;
 if(r.phase==='selection'){for(const p of r.players)if(!Object.hasOwn(r.duel.bids,p.id))r.duel.bids[p.id]=availableTiles(r)[0];revealBids(r,now);return;}
 if(r.phase==='bids'){beginTurfQuestion(r,now);return;}
 if(r.phase==='question'){for(const p of r.players)if(!answered(r,p)&&now>=r.duel.playerEnds[p.id]){p.answers[r.index]=null;r.duel.answerTimes[p.id]=null;r.revision++;}planNext(r,now);}
}
export function turfAction(r,who,body,now){
 if(body.type==='start'){fail(who.role==='host','Лише ведучий керує грою',403);fail(r.phase==='lobby'&&r.players.length===2,'Потрібно рівно 2 гравці');startTurf(r,now);return true;}
 if(!isTurf(r))return false;
 if(body.type==='bid'){fail(who.player&&r.phase==='selection'&&!r.paused,'Зараз вибір недоступний');fail(body.round===r.index,'Раунд уже змінився');fail(canBid(r,who.player),'Спершу клітинку обирає гравець із телефона');fail(!Object.hasOwn(r.duel.bids,who.player.id),'Клітинку вже обрано');fail(Number.isInteger(body.tile)&&availableTiles(r).includes(body.tile),'Клітинка на паузі');r.duel.bids[who.player.id]=body.tile;r.revision++;if(r.players.every(p=>Object.hasOwn(r.duel.bids,p.id)))revealBids(r,now);return true;}
 if(body.type==='question'){fail(who.role==='host','Лише ведучий керує грою',403);beginTurfQuestion(r,now);return true;}
 if(body.type==='answer'){fail(who.player&&r.phase==='question'&&!r.paused,'Відповідь зараз недоступна');fail(body.questionId===current(r).id&&body.round===r.index,'Раунд уже змінився');fail(!answered(r,who.player),'Відповідь уже прийнято');fail(now<r.duel.playerEnds[who.player.id],'Час відповіді минув');fail(Number.isInteger(body.choice)&&body.choice>=0&&body.choice<4,'Оберіть відповідь',400);who.player.answers[r.index]=body.choice;r.duel.answerTimes[who.player.id]=now;r.revision++;planNext(r,now);return true;}
 if(body.type==='next'){fail(who.role==='host','Лише ведучий керує грою',403);fail(r.phase==='reveal','Раунд ще триває');r.index++;beginSelection(r,now);return true;}
 if(body.type==='pause'){fail(who.role==='host','Лише ведучий керує грою',403);fail(['selection','bids','question'].includes(r.phase)&&!r.paused,'Пауза недоступна');r.duel.pausedAt=now;r.remaining=Math.max(0,r.deadline-now);r.deadline=null;r.paused=true;r.revision++;return true;}
 if(body.type==='resume'){fail(who.role==='host','Лише ведучий керує грою',403);fail(r.paused,'Гру не призупинено');const delta=now-r.duel.pausedAt;for(const id of Object.keys(r.duel.playerEnds))r.duel.playerEnds[id]+=delta;if(r.duel.firstCorrectAt!==null)r.duel.firstCorrectAt+=delta;r.deadline=now+r.remaining;r.paused=false;r.revision++;return true;}
 return false;
}
export function turfView(r,who,now){const d=r.duel,visible=r.phase!=='selection',showQuestion=['question','reveal','finished'].includes(r.phase),reveal=['reveal','finished'].includes(r.phase),q=current(r);const you=who.player;
 return {mode:'duel',minPlayers:2,maxPlayers:2,code:r.code,role:who.role,you:you?.id,phase:r.phase,index:r.index,total:null,revision:r.revision,serverNow:now,expiresAt:r.expiresAt,deadline:r.deadline,paused:r.paused,remaining:r.remaining,
 question:showQuestion?{id:q.id,text:q.text,category:q.category,choices:q.choices,...(reveal?{correct:q.correct}:{})}:null,
 players:r.players.map(p=>({id:p.id,name:p.name,color:p.color,score:p.score,answered:answered(r,p),...(reveal||p===you?{answer:p.answers[r.index]}:{})})),
 duel:{version:2,board:d.board,cooldowns:d.cooldowns,winners:d.winners,winningLines:d.winningLines,outcome:d.outcome,contested:d.contested,defended:d.defended,attacking:visible?d.attacking:[],bids:visible?d.bids:you&&Object.hasOwn(d.bids,you.id)?{[you.id]:d.bids[you.id]}:{},selected:r.players.filter(p=>Object.hasOwn(d.bids,p.id)).map(p=>p.id),available:r.phase==='selection'?availableTiles(r):[],canBid:!!(you&&r.phase==='selection'&&!r.paused&&!Object.hasOwn(d.bids,you.id)&&canBid(r,you)),playerEnds:r.phase==='question'?d.playerEnds:{},pausedAt:r.paused?d.pausedAt:null}};
}
