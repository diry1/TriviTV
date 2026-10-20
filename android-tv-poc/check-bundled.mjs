import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(new URL('../browser-site/package.json',import.meta.url));
const {chromium}=require('playwright');
const root=new URL('./app/src/main/assets/web/',import.meta.url);
const browser=await chromium.launch({channel:'msedge',headless:true});
try{
 const context=await browser.newContext({viewport:{width:1920,height:1080},offline:true});
 await context.route('**/*',async route=>{
  const url=new URL(route.request().url());
  if(url.host!=='appassets.androidplatform.net')return route.abort();
  const name=url.pathname==='/'?'index.html':url.pathname.slice(1);
  try{
   const type=name.endsWith('.js')?'text/javascript':name.endsWith('.json')?'application/json':name.endsWith('.css')?'text/css':name.endsWith('.txt')?'text/plain':'text/html';
   await route.fulfill({status:200,contentType:type,body:await fs.readFile(new URL(name,root))});
  }catch{await route.fulfill({status:404,body:'Not found'});}
 });
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://appassets.androidplatform.net/?language=uk');
 await page.locator('#create').waitFor();
 assert.match(await page.locator('#pool-availability').innerText(),/916/);
 // Exercise the same DOM activation used by the native OK mapping.
 const ok=()=>page.evaluate(()=>{const a=document.activeElement;if(a&&a!==document.body&&a.click&&!a.disabled)a.click();});
 await page.locator('#create').focus();await ok();
 await page.locator('.answer').first().waitFor();
 await page.evaluate(()=>window.TriviTVRemote.key('ArrowRight',false));
 assert.match(await page.evaluate(()=>document.activeElement.dataset.answer),/^[0-3]$/);
 await ok();await page.waitForFunction(()=>document.querySelector('.answers')?.dataset.stage!=='question');
 await page.reload();await page.locator('.answer').first().waitFor();
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({offlineSecureOrigin:true,available:916,remoteDomMapping:true,startAnswerReload:true,browserErrors:errors.length,physicalAndroidRuntimeTested:false}));
}finally{await browser.close();}
