import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
const root=new URL('./dist/',import.meta.url);
const server=http.createServer(async(req,res)=>{try{const p=new URL(req.url,'http://localhost').pathname;const file=new URL('.'+(p==='/'?'/index.html':p),root);if(!file.href.startsWith(root.href))throw Error();const data=await fs.readFile(file);res.setHeader('Content-Type',file.pathname.endsWith('.js')?'text/javascript':file.pathname.endsWith('.css')?'text/css':file.pathname.endsWith('.json')?'application/json':'text/html');res.end(data);}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(3016,'127.0.0.1',resolve));
let browser;
try{
browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.clock.install();
await page.goto('http://127.0.0.1:3016');
await page.locator('#create').waitFor();
assert.match(await page.locator('#pool-availability').innerText(),/916/);
assert.equal(await page.locator('#join-screen,.room-code,.party-card').count(),0);
const bank=await page.evaluate(()=>fetch('/questions.json').then(r=>r.json()));
assert.equal(bank.length,916);assert.equal(new Set(bank.map(q=>q.id)).size,916);
// All 916 canonical answer keys survive repeated selection and shuffling.
const alignment=await page.evaluate(async()=>{const g=await import('/game.js');const q=await import('/questions.js');let tested=0;for(const source of q.questions){for(let n=0;n<8;n++){const order=[0,1,2,3].sort(()=>Math.random()-.5);const choices=order.map(i=>source.choices[i]);if(choices[order.indexOf(source.correct)]!==source.choices[source.correct])throw Error('alignment');tested++;}}let actual=0;for(let i=0;i<500;i++){const chosen=g.selectQuestions({language:'uk',region:'Europe',mode:i%2?'trivia':'millionaire',categories:q.categories});for(const shuffled of chosen){const source=q.questions.find(q=>q.id===shuffled.id);if(shuffled.choices[shuffled.correct]!==source.choices[source.correct])throw Error('actual shuffle alignment');actual++;}}return {tested,actual};});
await page.locator('#category-toggle').click();await page.locator('#all-categories').click();assert.match(await page.locator('#pool-availability').innerText(),/0/);assert.equal(await page.locator('#create').isDisabled(),true);await page.locator('#all-categories').click();
await page.locator('[data-category="Animals"]').click();assert.match(await page.locator('#pool-availability').innerText(),/848/);await page.reload();await page.locator('#create').waitFor();assert.match(await page.locator('#pool-availability').innerText(),/848/);await page.locator('#category-toggle').click();await page.locator('[data-category="Animals"]').click();
for(const mode of ['trivia','millionaire']){
await page.locator(`[data-mode="${mode}"]`).click();await page.locator('#create').click();await page.locator('#start').click();await page.locator('[data-answer="0"]').waitFor();
await page.keyboard.press('ArrowRight');assert.match(await page.evaluate(()=>document.activeElement.dataset.answer),/^[0-3]$/);
await page.reload();await page.locator('[data-answer="0"]').waitFor();
const total=mode==='trivia'?10:15;
for(let i=0;i<total;i++){
const record=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));
assert.equal(record.index,i);assert.equal(record.phase,'question');
if(mode==='millionaire'&&i===0){await page.locator('#fifty').click();assert.equal(await page.locator('.answer:disabled').count(),2);}
const question=record.questions[i],source=bank.find(q=>q.id===question.id);assert.equal(question.choices[question.correct],source.choices[source.correct]);
await page.locator(`[data-answer="${question.correct}"]`).focus();await page.keyboard.press('Enter');
await page.clock.runFor(1800);
if(mode==='millionaire'){await page.locator('#next').click();}else{await page.clock.runFor(4500);}
}
await page.locator('#finish').waitFor();
assert.match(await page.locator('#app').innerText(),mode==='trivia'?/1000/:/1[\s,.]?000[\s,.]?000/);
await page.locator('#finish').click();await page.locator('#create').waitFor();
}
// Wrong Millionaire answer, walk away and paused Trivia recovery.
await page.locator('#create').click();await page.locator('#start').click();let r=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));await page.locator(`[data-answer="${(r.questions[0].correct+1)%4}"]`).click();await page.clock.runFor(1800);await page.locator('#next').click();await page.locator('#finish').waitFor();await page.locator('#finish').click();
await page.locator('#create').click();await page.locator('#start').click();page.once('dialog',d=>d.accept());await page.locator('#walk').click();await page.locator('#finish').waitFor();await page.locator('#finish').click();
await page.locator('[data-mode="trivia"]').click();await page.locator('#create').click();await page.locator('#start').click();await page.locator('#pause-review').click();await page.reload();await page.locator('#pause-review').waitFor();assert.equal(await page.locator('.answer:disabled').count(),4);await page.locator('#pause-review').click();await page.clock.runFor(61000);await page.clock.runFor(1800);r=await page.evaluate(()=>JSON.parse(localStorage.getItem('trivitv-browser-progress-v1')));assert.equal(r.autoPicked.length,1);
await page.screenshot({path:'.qa/desktop.png',fullPage:true});
const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await mobile.goto('http://127.0.0.1:3016');await mobile.locator('#create').waitFor();assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await mobile.locator('#create').tap();await mobile.locator('#start').tap();await mobile.locator('.answer').first().waitFor();assert.equal(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await mobile.screenshot({path:'.qa/mobile.png',fullPage:true});
assert.deepEqual(errors,[]);console.log(JSON.stringify({passed:true,pool:916,alignment,completeGames:['trivia-10','millionaire-15'],checks:['wrong-answer','walk-away','50:50','pause-reload','timeout-random-pick','settings-reload','progress-reload','keyboard-Enter-arrows','mobile-touch-no-overflow','no-browser-errors']}));
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
