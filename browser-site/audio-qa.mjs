import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--autoplay-policy=no-user-gesture-required','--mute-audio']});
try{
 const page=await browser.newPage({viewport:{width:960,height:540}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.clock.install();await page.goto('http://127.0.0.1:3016');await page.locator('#create').waitFor();
 await page.waitForFunction(()=>window.TriviTVAudio?.status.playing);
 const durations=await page.evaluate(async()=>{const config=(await import('./audio-config.js')).default;return Promise.all([config.menu,...config.tracks,...Object.values(config.cues)].map(src=>new Promise((resolve,reject)=>{const a=new Audio(src);a.onloadedmetadata=()=>resolve({src,duration:a.duration});a.onerror=()=>reject(Error(src));a.load();})));});
 assert.equal(durations.length,15);for(const a of durations){assert.ok(a.duration>0);if(a.src.includes('menu-deep-house'))assert.ok(Math.abs(a.duration-60)<.1);if(a.src.includes('session-low-tide-user'))assert.ok(Math.abs(a.duration-128)<.1);if(a.src.includes('session-amber-rooms'))assert.ok(Math.abs(a.duration-130.1695)<.1);}
 await page.locator('#create').click();await page.locator('#answer-0').waitFor();
 await page.waitForFunction(()=>window.TriviTVAudio.status.playing);
 const track=await page.evaluate(()=>TriviTVAudio.status.src);assert.match(track,/session-/);
 await page.locator('#pause-review').click();assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),false);
 await page.locator('#pause-review').click();await page.waitForFunction(()=>TriviTVAudio.status.playing);
 await page.clock.runFor(49000);assert.equal(await page.evaluate(()=>TriviTVAudio.status.history.includes('warning')),false);
 await page.clock.runFor(1500);assert.ok(await page.evaluate(()=>TriviTVAudio.status.history.includes('warning')));
 assert.equal(durations.find(a=>a.src.includes('countdown-10s')).duration,10);
 await page.locator('#pause-review').click();assert.equal(await page.evaluate(()=>TriviTVAudio.status.warning),false);
 await page.clock.runFor(2000);await page.locator('#pause-review').click();
 await page.clock.runFor(500);assert.equal(await page.evaluate(()=>TriviTVAudio.status.warning),true);
 await page.clock.runFor(10600);assert.ok(await page.evaluate(()=>TriviTVAudio.status.history.includes('expired')));
  assert.equal(await page.evaluate(()=>TriviTVAudio.status.src),track);
 await page.clock.runFor(1600);
 await page.locator('#next').waitFor();
 assert.equal(await page.evaluate(()=>document.activeElement.id),'next');
 await page.locator('#pause-review').click();
 assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),false);
 await page.clock.runFor(5000);
 await page.locator('#next').click();await page.locator('#answer-0').waitFor();
 assert.equal(await page.evaluate(()=>TriviTVAudio.status.src),track);
 await page.waitForFunction(()=>TriviTVAudio.status.playing);
 await page.evaluate(()=>document.querySelector('#session-music').dispatchEvent(new Event('ended')));
 await page.waitForFunction(previous=>TriviTVAudio.status.src!==previous,track);
 await page.clock.runFor(50500);assert.equal(await page.evaluate(()=>TriviTVAudio.status.warning),true);
 await page.locator('#answer-0').click();assert.equal(await page.evaluate(()=>TriviTVAudio.status.warning),false);
 await page.locator('#home').click();await page.locator('#dialog-confirm').click();
 await page.locator('#mode-millionaire').click();await page.locator('#create').click();await page.locator('#answer-0').waitFor();await page.waitForFunction(()=>TriviTVAudio.status.playing);
 const millionaireTrack=await page.evaluate(()=>TriviTVAudio.status.src);
 const correct=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')).questions[0].correct);
 await page.locator('#answer-'+correct).click();await page.clock.runFor(950);assert.ok(await page.evaluate(()=>TriviTVAudio.status.history.includes('correct')));
 await page.clock.runFor(650);await page.locator('#next').click();await page.locator('#answer-0').waitFor();
 assert.equal(await page.evaluate(()=>TriviTVAudio.status.src),millionaireTrack);
 const q=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')).questions[1].correct);
 await page.locator('#answer-'+((q+1)%4)).click();await page.clock.runFor(950);assert.ok(await page.evaluate(()=>TriviTVAudio.status.history.includes('incorrect')));
 await page.evaluate(()=>TriviTVAudio.suspend(true));assert.equal(await page.evaluate(()=>TriviTVAudio.status.playing),false);
 await page.locator('#audio-music').click();await page.reload();await page.locator('#audio-music').waitFor();assert.equal(await page.evaluate(()=>TriviTVAudio.settings.music),false);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight),true);
 assert.deepEqual(errors,[]);const report={audioFiles:durations,musicAutoplay:true,bothModes:true,pauseResume:true,tenSecondAcceleratingCountdown:true,countdownPauseResume:true,timeout:true,correctIncorrect:true,continuousAcrossQuestions:true,gameMusicTracks:2,menuDeepHouseSeconds:60,gameMusicSeconds:[128,130.1695],playlistAdvance:true,reviewNextDefault:true,skipPausedReview:true,nativeSuspendBridge:true,mutePersistence:true,screenFits:true,pageErrors:errors,physicalTvTested:false};
 await fs.writeFile('.qa/audio-validation.json',JSON.stringify(report,null,2));console.log('Audio QA passed: 15 assets, both modes, pause/resume, warning/timeout, results, mute persistence and bounds.');
}finally{await browser.close();}



