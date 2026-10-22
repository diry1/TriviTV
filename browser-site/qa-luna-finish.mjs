import {chromium} from 'playwright';
import fs from 'node:fs';
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('file:///C:/Users/User/Documents/ChatGPT/TriviTV/question-bank/semantic-tagging/luna-finish-v1/review.html');
await page.locator('article').first().waitFor();
if(await page.locator('article').count()!==50)throw Error('Expected 50 cards');
if(!(await page.locator('#count').innerText()).includes('38926'))throw Error('Incomplete bank');
await page.locator('#next').click();if(!(await page.locator('#count').innerText()).startsWith('51'))throw Error('Pagination');
await page.locator('#pool').selectOption('fun');if(!(await page.locator('#count').innerText()).includes('17315'))throw Error('Fun membership changed');
await page.locator('#pool').selectOption('');await page.locator('#category').selectOption('General Knowledge');if(!(await page.locator('#count').innerText()).includes('6838'))throw Error('Category incomplete');
await page.locator('#category').selectOption('');await page.locator('#search').fill('topic:animals');if(!await page.locator('article').count())throw Error('Tag search');
await page.locator('#search').fill('');await page.screenshot({path:'../question-bank/semantic-tagging/luna-finish-v1/preview.png'});
for(const width of [1440,390]){await page.setViewportSize({width,height:1000});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow');}
if(errors.length)throw Error(errors.join(';'));
fs.writeFileSync('../question-bank/semantic-tagging/luna-finish-v1/ui-validation.json',JSON.stringify({desktop:true,mobile:true,cards:50,pagination:true,category:true,pool:true,search:true,errors},null,2));
await browser.close();console.log('UI validation passed');
