import config from './audio-config.js';
import {nativeMusic} from './native-music.js';
const bridge=location.hostname==='appassets.androidplatform.net'?window.TriviTVMusic:null;
const music=bridge?nativeMusic(bridge):new Audio(); music.preload='auto';music.volume=.42;
if(!bridge){music.id='session-music';music.hidden=true;document.body.append(music);}
let settings={music:true,effects:true};try{Object.assign(settings,JSON.parse(localStorage.getItem('trivitv-audio-v1')||'{}'));}catch{}
let suspended=false,view=null,currentScreen='home',key='',phase='',warned=false,src='',bag=[],lastTrack='',pending=false;
let active=new Set(),warning=null,delayed=null,highlightAt=0;
const history=[];
let lastError='';
music.onerror=event=>{lastError=event?.message||`Media error ${music.error?.code||'unknown'}`;record('music-error:'+lastError);window.dispatchEvent(new Event('trivitv-audio-error'));};
function record(event){history.push(event);if(history.length>80)history.shift();}
function playMusic(){if(!settings.music||suspended||document.hidden)return;if(music.ended&&view&&view.phase!=='finished'){setMusic(nextTrack(),false);return;}const p=music.play();p?.catch(()=>{pending=true;});}
function stopEffects(){clearTimeout(delayed);for(const a of active)a.pause();active.clear();warning=null;warned=false;music.volume=.42;}
function cue(id,offset=0){
 if(!settings.effects||suspended||document.hidden||!config.cues[id])return;
 if(id==='highlight'){if(performance.now()-highlightAt<75)return;highlightAt=performance.now();}
 const a=new Audio(new URL(config.cues[id],import.meta.url).href);a.volume=.72;a.preload='auto';active.add(a);record(id);music.volume=.24;
 const done=()=>{active.delete(a);if(warning===a)warning=null;if(!active.size)music.volume=.42;};a.onended=done;a.onerror=done;
 const play=()=>a.play()?.catch(done);
 if(offset){a.addEventListener('loadedmetadata',()=>{if(!active.has(a))return;a.currentTime=Math.min(offset,a.duration||offset);play();},{once:true});a.load();}
 else play();return a;
}
function nextTrack(){if(!bag.length)bag=config.tracks.map((_,i)=>i).sort(()=>Math.random()-.5);if(config.tracks[bag[0]]===lastTrack&&bag.length>1)[bag[0],bag[1]]=[bag[1],bag[0]];lastTrack=config.tracks[bag.shift()];return lastTrack;}
function setMusic(path,loop,offset=0){if(src===path){music.loop=loop;return;}music.pause();lastError='';src=path;music.src=bridge?path:new URL(path,import.meta.url).href;music.loop=loop;record(path);music.onloadedmetadata=()=>{if(offset>0)music.currentTime=Math.min(offset,Math.max(0,music.duration-.05));if(!paused()&&view?.phase!=='finished')playMusic();};playMusic();}
function paused(){return suspended||document.hidden||view?.questionPaused||view?.review?.paused;}
music.onended=()=>{if(view&&view.phase!=='finished'&&!paused())setMusic(nextTrack(),false);};
function tick(){
 if(!view||view.phase!=='question'||view.settings.mode==='millionaire'||paused())return;
 const remaining=(view.questionEndsAt||0)-Date.now();
 if(remaining>0&&remaining<=10000&&!warned&&settings.effects){warned=true;warning=cue('warning',Math.max(0,10-remaining/1000));}
}
function sync(state,screen){
 view=state;currentScreen=screen;
 const nextKey=state?.question?`${state.question.id}:${state.index}`:'';
 const nextPhase=state?.phase||'';
 if(!state||state.phase==='lobby'){
  if(key||phase)stopEffects();key='';phase='';warned=false;setMusic(config.menu,true);if(!paused())playMusic();return;
 }
 const changed=nextKey!==key;
 const starting=!key||(phase==='finished'&&nextPhase==='question');
 if(changed||starting){stopEffects();key=nextKey;warned=false;if(starting)setMusic(nextTrack(),false);cue('question');delayed=setTimeout(()=>{if(view?.phase==='question')cue('choices');},230);}
 if(nextPhase!==phase){
  if(nextPhase==='answers'){if(warning){warning.pause();active.delete(warning);warning=null;}cue(state.players[0].autoPicked?'expired':'locked');}
  if(nextPhase==='correct'&&!state.players[0].autoPicked)cue(state.players[0].answer===state.question.correct?'correct':'incorrect');
  if(nextPhase==='finished'){stopEffects();if(state.finishReason==='completed')cue('complete');else if(state.finishReason==='walked')cue('back');music.pause();}
 }
 phase=nextPhase;
 if(paused()){music.pause();if(warning){warning.pause();active.delete(warning);warning=null;warned=false;}}
 else if(nextPhase!=='finished')playMusic();else music.pause();
 tick();
}
function suspend(value){suspended=value;if(value){music.pause();stopEffects();}else if(view?.phase!=='finished'&&!paused())playMusic();}
function toggle(kind){settings[kind]=!settings[kind];try{localStorage.setItem('trivitv-audio-v1',JSON.stringify(settings));}catch{}if(kind==='music'){settings.music?playMusic():music.pause();}else if(!settings.effects)stopEffects();return settings[kind];}
document.addEventListener('visibilitychange',()=>{if(document.hidden){music.pause();stopEffects();}else if(!paused()&&view?.phase!=='finished')playMusic();});
for(const event of ['pointerdown','keydown'])document.addEventListener(event,()=>{if(pending||music.paused){pending=false;if(view?.phase!=='finished'&&!paused())playMusic();}},true);
export const audio={cue,sync,tick,toggle,suspend,nativeEvent:(...args)=>music.event?.(...args),get settings(){return {...settings};},get status(){return {src,playing:!music.paused,currentTime:music.currentTime,backend:bridge?'android':'browser',lastError,settings:{...settings},history:[...history],warning:!!warning,suspended};}};
window.TriviTVAudio=audio;
