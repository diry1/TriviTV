// Android plays bundled music directly; browser previews retain HTML audio.
export function nativeMusic(bridge){
 let path='',volume=.42,loop=false,position=0,started=0,paused=true,ended=false,duration=0;
 const time=()=>paused?position:position+(performance.now()-started)/1000;
 const player={
  get src(){return path;},set src(value){path=value;position=0;paused=true;ended=false;bridge.load(value);},
  get volume(){return volume;},set volume(value){volume=value;bridge.volume(value);},
  get loop(){return loop;},set loop(value){loop=value;bridge.loop(value);},
  get currentTime(){return time();},set currentTime(value){position=value;started=performance.now();bridge.seek(value);},
  get duration(){return duration;},get paused(){return paused;},get ended(){return ended;},
  play(){bridge.play();return Promise.resolve();},
  pause(){position=time();paused=true;bridge.pause();},
  event(event,source,value,message){
   if(source!==path)return;
   if(event==='prepared'){duration=value;player.onloadedmetadata?.();}
   if(event==='playing'){position=value;started=performance.now();paused=false;ended=false;}
   if(event==='paused'){position=value;paused=true;}
   if(event==='ended'){position=value;paused=true;ended=true;player.onended?.();}
   if(event==='error'){paused=true;player.onerror?.({message});}
  }
 };
 return player;
}
