import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const browser=await chromium.launch({channel:'msedge',headless:true});
const expectedBank=JSON.parse(await fs.readFile(new URL('./dist/questions.json',import.meta.url),'utf8'));const expectedCount=expectedBank.length;const categoryCount=new Set(expectedBank.map(q=>q.category)).size;const report={};
try{
 const page=await browser.newPage({viewport:{width:960,height:540}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.clock.install();await page.goto('http://127.0.0.1:3016');await page.locator('#create').waitFor();
 const fits=async()=>{assert.equal(await page.evaluate(()=>document.documentElement.scrollHeight<=innerHeight+1&&document.documentElement.scrollWidth<=innerWidth+1),true);for(const el of await page.locator('button:not(:disabled)').all()){if(!await el.isVisible())continue;const b=await el.boundingBox();assert.ok(b.x>=0&&b.y>=0&&b.x+b.width<=await page.evaluate(()=>innerWidth)+1&&b.y+b.height<=await page.evaluate(()=>innerHeight)+1,'off-screen '+await el.getAttribute('id'));}};
 await fits();assert.ok((await page.locator('#pool-availability').innerText()).replace(/\s/g,'').includes(String(expectedCount)));
 assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-trivia');
 await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-millionaire');assert.equal(await page.locator('#mode-millionaire').getAttribute('aria-pressed'),'true');
 await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-imposter');assert.equal(await page.locator('#mode-imposter').getAttribute('aria-pressed'),'true');assert.match(await page.locator('#create').innerText(),/кімнату/);
 await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-duel');
 await page.keyboard.press('ArrowDown');assert.equal(await page.evaluate(()=>document.activeElement.id),'create');
 await page.keyboard.press('ArrowUp');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-duel');
 await page.keyboard.press('ArrowLeft');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-imposter');
 await page.keyboard.press('ArrowLeft');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-millionaire');
 await page.keyboard.press('ArrowLeft');assert.equal(await page.evaluate(()=>document.activeElement.id),'mode-trivia');
 await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'create');await page.keyboard.press('ArrowLeft');assert.equal(await page.evaluate(()=>document.activeElement.id),'settings');
 await page.keyboard.press('Enter');await fits();assert.equal(await page.locator('[data-category]').count(),12);
 await page.locator('#categories-next').click();await fits();assert.equal(await page.locator('[data-category]').count(),categoryCount-12);
 await page.locator('#cat-12').click();await page.locator('#categories-prev').click();await page.locator('#all-categories').click();assert.ok((await page.locator('#pool-availability').innerText()).replace(/\s/g,'').includes(String(expectedCount)));
 await page.locator('#all-categories').click();await page.locator('#settings-done').click();assert.equal(await page.locator('#create').isDisabled(),true);
 await page.locator('#settings').click();await page.locator('#all-categories').click();await page.locator('#settings-done').click();
 await page.screenshot({path:'.qa/tv-home-960.png'});
 for(const mode of ['trivia','millionaire']){
  await page.locator(`[data-mode="${mode}"]`).click();await page.clock.runFor(200);await page.locator('#create').focus();await page.keyboard.press('Enter');await page.locator('#answer-0').waitFor();await fits();
  await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>document.activeElement.id),'answer-1');
  await page.keyboard.press('ArrowDown');assert.equal(await page.evaluate(()=>document.activeElement.id),'answer-3');
  await page.keyboard.press('ArrowLeft');assert.equal(await page.evaluate(()=>document.activeElement.id),'answer-2');
  await page.keyboard.press('ArrowUp');assert.equal(await page.evaluate(()=>document.activeElement.id),'answer-0');
  await page.reload();await page.locator('#answer-0').waitFor();
  if(mode==='trivia'){await page.locator('#pause-review').click();await page.reload();await page.locator('#pause-review').waitFor();assert.equal(await page.locator('.answer:disabled').count(),4);await page.locator('#pause-review').click();}
  if(mode==='millionaire'){await page.locator('#fifty').click();assert.equal(await page.locator('.answer:disabled').count(),2);}
  for(let i=0;i<(mode==='trivia'?10:15);i++){
   const g=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));assert.equal(g.index,i);
   await page.locator(`#answer-${g.questions[i].correct}`).click();await page.clock.runFor(1600);await fits();if(mode==='millionaire')await page.locator('#next').click();else await page.clock.runFor(4300);
  }
  if(mode==='trivia'){let g=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));assert.equal(g.survival.round,10);assert.equal(g.lifeState.lives,5);for(let n=0;n<5;n++){g=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));await page.locator(`#answer-${(g.questions[g.index].correct+1)%4}`).click();await page.clock.runFor(5900);}}
  await page.locator('#restart').waitFor();await fits();assert.match(await page.locator('.big-score').innerText(),mode==='trivia'?/1.?000/:/1.?000.?000/);await page.locator('#finish').click();
 }
 // Wrong answer, walk-away dialog and timeout retain the original rules.
 await page.locator('#create').click();await page.locator('#answer-0').waitFor();let g=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));await page.locator(`#answer-${(g.questions[0].correct+1)%4}`).click();await page.clock.runFor(1600);await page.locator('#next').click();await page.locator('#restart').waitFor();await page.locator('#finish').click();
 await page.locator('#create').click();await page.locator('#walk').click();await fits();assert.equal(await page.evaluate(()=>document.activeElement.id),'dialog-cancel');await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>document.activeElement.id),'dialog-confirm');await page.keyboard.press('Enter');await page.locator('#restart').waitFor();await page.locator('#finish').click();
 await page.locator('[data-mode="trivia"]').click();await page.locator('#create').click();await page.locator('#answer-0').waitFor();await page.clock.runFor(61700);g=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));assert.equal(g.autoPicked.length,1);await page.locator('#home').click();await page.locator('#dialog-confirm').click();
 // A repeated/held OK never activates a second control after a screen transition.
 await page.locator('#settings').focus();await page.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',repeat:true,bubbles:true,cancelable:true})));assert.equal(await page.locator('[data-category]').count(),0);
 await page.locator('#credits').click();for(let i=0;i<4;i++){await fits();if(i<3)await page.locator('#credits-next').click();}await page.locator('#credits-close').click();
 for(const size of [{width:1280,height:720},{width:1920,height:1080},{width:3840,height:2160},{width:390,height:844}]){await page.setViewportSize(size);await fits();if(size.width===390)await page.screenshot({path:'.qa/tv-mobile.png'});}
 await page.setViewportSize({width:1280,height:720});await page.screenshot({path:'.qa/tv-home-1280.png'});
 assert.deepEqual(errors,[]);report.functional={completeGames:['Trivia continues after 10, ends at zero lives','Millionaire 15/15'],navigation:'exact expected focus sequence',noScroll:true,settingsPaging:true,pauseAndProgressReload:true,lifeline:true,creditsPaging:true,browserErrors:errors};
 // Test-only instrumented rendering; no hooks are added to the deployed app.
 const geometry=await browser.newPage({viewport:{width:960,height:540}});
 await geometry.route('**/tv-ui.js',async route=>{const response=await route.fetch();await route.fulfill({response,body:await response.text()+`\nwindow.__geometry={show(s){busy=true;state=s;screen='home';dialog=null;render();},settings(){state=null;screen='settings';render();}};`});});
 await geometry.goto('http://127.0.0.1:3016');await geometry.locator('#create').waitFor();
 report.geometry=await geometry.evaluate(async()=>{const {questions,categories}=await import('/questions.js'),rules=await import('/game.js');const issues=[];for(const mode of ['trivia','millionaire']){const g=rules.createGame({mode,region:'Europe',language:'uk',categories});rules.addPlayer(g,'Гравець',true);rules.start(g);for(const q of questions){g.questions=Array.from({length:mode==='millionaire'?15:10},()=>q);g.index=0;g.answers={};g.scores[g.players[0].id]=0;g.phase='question';window.__geometry.show(rules.view(g,g.players[0].id));for(const selector of ['.question','.answer>strong','.answer','.game-actions']){for(const el of document.querySelectorAll(selector)){const b=el.getBoundingClientRect();if(b.bottom>innerHeight-15||b.right>innerWidth+1||el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2)issues.push({mode,id:q.id,selector,rect:{y:b.y,h:b.height},scroll:el.scrollHeight,client:el.clientHeight,font:getComputedStyle(el).fontSize});}}}}return {questions:questions.length,modes:2,issues:issues.slice(0,12),issueCount:issues.length};});
 assert.equal(report.geometry.issueCount,0,JSON.stringify(report.geometry));
 await geometry.screenshot({path:'.qa/tv-question-960.png'});console.log(JSON.stringify(report));await fs.writeFile('.qa/tv-validation.json',JSON.stringify(report,null,2));
}finally{await browser.close();}

