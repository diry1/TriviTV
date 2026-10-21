import * as rules from './game.js';
import { questions,categories } from './questions.js';
const key='trivitv-browser-progress-v1';
let game;
try { game=JSON.parse(localStorage.getItem(key)); if(game && (game.settings.language!=='uk'||game.settings.region!=='Europe'||game.questions.some(q=>!questions.some(source=>source.id===q.id))))game=null; } catch {game=null;}
function persist(){try{localStorage.setItem(key,JSON.stringify(game));}catch{throw Error('Не вдалося зберегти прогрес у браузері. Перевірте налаштування сховища.');}}
export function clearProgress(){game=null;localStorage.removeItem(key);}
function tick(){if(!game)return;let changed=false;for(let i=0;i<100;i++){const deadline=rules.nextDeadline(game);if(deadline===null||Date.now()<deadline)break;changed=rules.advance(game,deadline)||changed;}if(changed)persist();}
export async function localApi(path,body){
  if(path==='/api/config')return {categories,partyDemo:false,bank:{count:916},languages:{uk:{count:916}},pools:{uk:{Europe:{count:916,categories:Object.fromEntries(categories.map(c=>[c,questions.filter(q=>q.category===c).length]))}}}};
  if(path==='/api/rooms'){
    game=rules.createGame({...body,language:'uk',region:'Europe'});
    rules.addPlayer(game,'Гравець',true);persist();
    return {code:'local',role:'host',playerId:game.players[0].id,state:rules.view(game,game.players[0].id)};
  }
  if(!game){const error=Error('Немає збереженої гри');error.status=404;throw error;}
  tick();
  if(body){
    if(body.questionId && body.questionId!==game.questions[game.index].id)throw Error('Запитання змінилося');
    const now=Date.now();
    switch(body.type){
      case 'start':rules.start(game,now);break;
      case 'answer':rules.answer(game,game.players[0].id,body.choice,now);break;
      case 'next':rules.next(game,now,body.skipReview===true&&game.settings.mode==='trivia');break;
      case 'pause':rules.pauseGame(game,now);break;
      case 'resume':rules.resumeGame(game,now);break;
      case 'fifty':rules.fifty(game);break;
      case 'walk':rules.walk(game);break;
      default:throw Error('Невідома дія');
    }
    persist();
  }
  const value=rules.view(game,game.players[0].id);delete value.serverNow;return value;
}
