import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--mute-audio']});
try{
 const page=await browser.newPage();await page.clock.install();
 await page.route('https://appassets.androidplatform.net/**',async route=>{
  const url=new URL(route.request().url());const response=await route.fetch({url:'http://127.0.0.1:3016'+url.pathname+url.search});await route.fulfill({response});
 });
 await page.addInitScript(()=>{
  let path='',ready=false,wanted=false,playing=false;window.nativeCalls=[];
  const emit=(event,value=0,message='')=>window.TriviTVAudio?.nativeEvent(event,path,value,message);
  const begin=()=>{if(ready&&wanted&&!playing){playing=true;emit('playing');}};
  window.TriviTVMusic={
   load(source){path=source;ready=false;wanted=false;playing=false;window.nativeCalls.push(['load',source]);const snapshot=path;setTimeout(()=>{if(path===snapshot){ready=true;emit('prepared',path.includes('menu-')?60:128);begin();}},20);},
   play(){wanted=true;begin();},pause(){wanted=false;playing=false;emit('paused');},
   loop(value){window.nativeCalls.push(['loop',value]);},volume(value){window.nativeCalls.push(['volume',value]);},seek(value){window.nativeCalls.push(['seek',value]);}
  };
 });
 await page.goto('https://appassets.androidplatform.net/');await page.locator('#create').waitFor();await page.clock.runFor(100);
 assert.equal(await page.evaluate(()=>TriviTVAudio.status.backend),'android');assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),true);
 assert.equal(await page.locator('#session-music').count(),0);
 await page.locator('#create').click();await page.clock.runFor(300);assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),true);
 const source=await page.evaluate(()=>TriviTVAudio.status.src);
 await page.locator('#pause-review').click();assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),false);
 await page.locator('#pause-review').click();await page.clock.runFor(100);assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),true);
 await page.evaluate(()=>TriviTVAudio.suspend(true));assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),false);
 await page.evaluate(()=>TriviTVAudio.suspend(false));await page.clock.runFor(100);assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),true);
 await page.evaluate(()=>TriviTVAudio.nativeEvent('ended',TriviTVAudio.status.src,128,''));await page.clock.runFor(100);assert.notEqual(await page.evaluate(()=>TriviTVAudio.status.src),source);
 await page.evaluate(()=>TriviTVAudio.nativeEvent('error',TriviTVAudio.status.src,0,'Test decoder error'));
 assert.match(await page.locator('#audio-music').innerText(),/збій/);assert.match(await page.evaluate(()=>TriviTVAudio.status.lastError),/Test decoder error/);
 await page.locator('#audio-music').click();assert.equal(await page.evaluate(()=>TriviTVAudio.settings.music),false);
 console.log('Native music adapter QA passed: Android path, autoplay requests, pause/resume/suspend, playlist, mute and visible error. Mock bridge; physical Android playback still requires TV check.');
}finally{await browser.close();}
