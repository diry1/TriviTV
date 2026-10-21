import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--mute-audio']});
try{
 const page=await browser.newPage({viewport:{width:960,height:540}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.clock.install();await page.goto('http://127.0.0.1:3016');await page.locator('#mode-millionaire').click();await page.locator('#create').click();await page.locator('#answer-0').waitFor();
 assert.equal(await page.locator('.ladder-step').count(),15);assert.equal(await page.locator('.ladder-step.current').getAttribute('data-step'),'1');
 assert.deepEqual(await page.locator('.ladder-step.milestone').evaluateAll(nodes=>nodes.map(n=>n.dataset.step)),['10','5']);
 assert.equal(await page.locator('.ladder-step').first().getAttribute('data-step'),'15');
 assert.equal(await page.locator('#answer-countdown').count(),0);
 for(let i=0;i<5;i++){
  const correct=await page.evaluate(()=>{const g=JSON.parse(localStorage.getItem('trivitv-browser-progress-v1'));return g.questions[g.index].correct;});
  await page.locator('#answer-'+correct).click();await page.clock.runFor(1600);
  assert.equal(await page.locator('.ladder-step.current').getAttribute('data-step'),String(i+1));
  assert.equal(await page.locator('.ladder-step.current.passed').count(),1);
  if(i===4){assert.match(await page.locator('#ladder-secured').innerText(),/1.?000/);assert.match(await page.locator('#ladder-won').innerText(),/1.?000/);}
  await page.locator('#next').click();await page.locator('#answer-0').waitFor();
 }
 assert.equal(await page.locator('.ladder-step.current').getAttribute('data-step'),'6');
 const sizes=[{width:960,height:540},{width:1280,height:720},{width:1920,height:1080},{width:390,height:844}];
 for(const size of sizes){
  await page.setViewportSize(size);
  const issues=await page.evaluate(()=>{const issues=[];for(const el of document.querySelectorAll('.ladder-step,.prize-ladder,.question,.answer>strong,.game-actions')){const b=el.getBoundingClientRect();if(b.x<0||b.y<0||b.right>innerWidth+1||b.bottom>innerHeight+1||el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2)issues.push({class:el.className,text:el.textContent,rect:{x:b.x,y:b.y,w:b.width,h:b.height},scroll:[el.scrollWidth,el.scrollHeight],client:[el.clientWidth,el.clientHeight]});}return issues;});
  assert.deepEqual(issues,[],JSON.stringify({size,issues}));
  await page.screenshot({path:`.qa/millionaire-${size.width}.png`});
 }
 await page.setViewportSize({width:960,height:540});
 const wrong=await page.evaluate(()=>{const g=JSON.parse(localStorage.getItem('trivitv-browser-progress-v1'));return (g.questions[g.index].correct+1)%4;});
 await page.locator('#answer-'+wrong).click();await page.clock.runFor(1600);
 assert.equal(await page.locator('.ladder-step.current.failed').getAttribute('data-step'),'6');assert.match(await page.locator('#ladder-won').innerText(),/1.?000/);
 await page.reload();await page.locator('.prize-ladder').waitFor();assert.equal(await page.locator('.ladder-step.current.failed').count(),1);
 assert.deepEqual(errors,[]);
 await fs.writeFile('.qa/millionaire-validation.json',JSON.stringify({visibleSteps:15,currentRung:true,milestones:[1000,32000],earnedAndGuaranteed:true,wrongAnswerFallback:true,reload:true,viewports:sizes,pageErrors:errors},null,2));
 console.log('Millionaire QA passed: all15 visible, progression, guarantee/failure states, reload and four viewport sizes.');
}finally{await browser.close();}
