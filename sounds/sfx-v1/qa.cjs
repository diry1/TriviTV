const {chromium}=require('C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path=require('path');const fs=require('fs');
(async()=>{
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--mute-audio']});
const page=await browser.newPage({viewport:{width:1100,height:850}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('file:///'+path.join(__dirname,'index.html').replaceAll('\\','/'));
if(await page.locator('.cue').count()!==12)throw Error('Expected 12 events');
const audio=await page.evaluate(async()=>{const results=[];for(const e of pack.events)for(const v of e.variants){const a=new Audio(v.file);await new Promise((resolve,reject)=>{a.onloadedmetadata=resolve;a.onerror=()=>reject(Error(v.file));a.load()});if(!Number.isFinite(a.duration)||a.duration<=0)throw Error(v.file);results.push({file:v.file,duration:a.duration})}return results});
await page.getByRole('button',{name:'Play A',exact:true}).first().click();await page.waitForTimeout(180);if(!(await page.locator('#status').textContent()).includes('Menu highlight'))throw Error('Cue playback failed');
await page.getByRole('button',{name:'Play background music',exact:true}).click();if(!await page.evaluate(()=>!music.paused))throw Error('Music playback failed');
await page.getByRole('button',{name:'Test navigation',exact:true}).click();await page.keyboard.press('ArrowRight');if(await page.locator(':focus').textContent()!=='Millionaire')throw Error('Navigation focus failed');
await page.getByRole('button',{name:'Stop all',exact:true}).click();if(!await page.evaluate(()=>music.paused&&active.size===0))throw Error('Stop failed');
await page.locator('.cue select').first().selectOption('B');const download=page.waitForEvent('download');await page.getByRole('button',{name:'Save my choices',exact:true}).click();const d=await download;await d.saveAs(path.join(__dirname,'.qa-choices.json'));const choices=JSON.parse(fs.readFileSync(path.join(__dirname,'.qa-choices.json')));if(choices.events[0].label!=='B')throw Error('Export selection failed');
await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
if(errors.length)throw Error(errors.join('\n'));
fs.writeFileSync(path.join(__dirname,'browser-validation.json'),JSON.stringify({events:12,loadedAudio:audio.length,playback:true,music:true,keyboardNavigation:true,stop:true,choiceExport:true,mobileOverflow:false,pageErrors:errors},null,2));
await browser.close();console.log('Passed: all manifested audio files, cue/music playback, keyboard navigation, stop, choice export, mobile layout.');
})().catch(e=>{console.error(e);process.exit(1)});

