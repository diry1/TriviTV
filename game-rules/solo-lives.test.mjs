import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const bank=JSON.parse(await fs.readFile(new URL('../browser-site/dist/questions.json',import.meta.url),'utf8'));
globalThis.fetch=async()=>({ok:true,json:async()=>bank});
const r=await import('../browser-site/dist/game.js');
const settings={mode:'trivia',language:'uk',region:'Europe',categories:r.categories};
function game(mode='trivia',players=1){const g=r.createGame({...settings,mode},{answersRevealMs:1,correctRevealMs:1});for(let i=0;i<players;i++)r.addPlayer(g,'Player '+i,true);r.start(g,0);return g;}
function respond(g,right=true){const q=g.questions[g.index];r.answer(g,g.players[0].id,right?q.correct:(q.correct+1)%4,1);r.advance(g,2);r.advance(g,3);}
function next(g){r.next(g,4,true);}
test('solo starts at 3, streak earns lives up to 5; wrong resets, zero ends',()=>{const g=game();assert.equal(g.lifeState.lives,3);for(let i=0;i<15;i++){respond(g);next(g);}assert.equal(g.lifeState.lives,5);assert.equal(g.lifeState.streak,0);assert.equal(g.survival.round,15);respond(g,false);assert.equal(g.lifeState.lives,4);next(g);for(let i=0;i<4;i++){respond(g,false);next(g);}assert.equal(g.phase,'finished');assert.equal(g.finishReason,'no-lives');});
test('no repeated IDs across queues; serialized reload preserves streak and lives',()=>{let g=game();const ids=new Set();for(let i=0;i<35;i++){assert.ok(!ids.has(g.questions[g.index].id));ids.add(g.questions[g.index].id);respond(g);g=JSON.parse(JSON.stringify(g));next(g);}assert.equal(g.survival.round,35);assert.ok(g.questions.length<=10);assert.equal(g.lifeState.lives,5);});
test('timeout costs a life and breaks streak without random success',()=>{const g=game();respond(g);next(g);r.advance(g,60004);r.advance(g,60005);assert.equal(g.lifeState.lives,2);assert.equal(g.lifeState.streak,0);assert.equal(g.answers[g.players[0].id],null);assert.equal(g.scores[g.players[0].id],100);});
test('multiplayer and Millionaire do not enable lives',()=>{assert.equal(game('trivia',2).lifeState.enabled,false);assert.equal(game('millionaire').lifeState,null);});
test('pool exhaustion refills and preserves global progress',()=>{const g=game();g.questions=[g.questions[0]];g.survival.seenIds=bank.map(q=>q.id);g.survival.round=99;respond(g);next(g);assert.equal(g.phase,'question');assert.equal(g.survival.round,100);assert.equal(g.survival.cycle,1);assert.equal(g.questions.length,10);});
test('pause and reload preserve question time and life progress',()=>{let g=game();respond(g);next(g);r.pauseGame(g,1000);g=JSON.parse(JSON.stringify(g));assert.equal(g.lifeState.streak,1);assert.equal(g.lifeState.lives,3);assert.equal(g.questionPaused,true);assert.equal(r.advance(g,999999),false);});
