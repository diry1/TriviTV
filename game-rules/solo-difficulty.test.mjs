import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const bank=JSON.parse(await fs.readFile(new URL('../browser-site/dist/questions.json',import.meta.url),'utf8'));
// The browser loader's single relative fetch is supplied the unchanged bank.
globalThis.fetch=async url=>{assert.equal(url,'./questions.json');return {ok:true,json:async()=>bank};};
const {selectQuestions}=await import('../browser-site/dist/game.js');
for(const [mode,count] of [['trivia',10],['millionaire',15]])test(`${mode}: weighted selection preserves source/choice keys and selected categories`,()=>{
  for(let n=0;n<25;n++){
    const selected=selectQuestions({mode,language:'uk',region:'Europe',categories:['Animals','World','People']});
    assert.equal(selected.length,count);assert.equal(new Set(selected.map(q=>q.id)).size,count);
    for(const q of selected){const source=bank.find(s=>s.id===q.id);assert.ok(['Animals','World','People'].includes(q.category));assert.equal(q.choices[q.correct],source.choices[source.correct]);assert.deepEqual([...q.choices].sort(),[...source.choices].sort());}
  }
});
