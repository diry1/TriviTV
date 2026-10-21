import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRoom,join,setRemotePlayer,act,tick,view} from '../src/engine.js';
import {} from '../src/party-engine.js';
const bank=JSON.parse(fs.readFileSync(new URL('../src/bank.json',import.meta.url)));
const categories=[...new Set(bank.map(q=>q.category))];
function make(mode){const r=createRoom('XYZ234',bank,categories,1000,{mode});if(mode==='duel')setRemotePlayer(r,true);while(r.players.length<(mode==='imposter'?3:2))join(r,'P'+r.players.length);return r;}
function startReady(r){act(r,r.host,{type:'start'},1000);for(const p of r.players)act(r,p.token,{type:'ready'},1100);}
test('Imposter min players, phone-only roles, private snapshots and ready barrier',()=>{
 const r=make('imposter');assert.throws(()=>setRemotePlayer(r,true),{status:409});act(r,r.host,{type:'start'},1000);assert.equal(r.phase,'roles');const host=view(r,r.host);assert.equal(host.secret,undefined);assert.equal(host.imposter.word,undefined);assert.equal(host.imposter.imposterId,undefined);assert.ok(!JSON.stringify(host).includes(r.imposter.word));
 const roles=r.players.map(p=>view(r,p.token).secret);assert.equal(roles.filter(x=>x.role==='imposter').length,1);assert.ok(roles.filter(x=>x.role==='group').every(x=>x.word===r.imposter.word));assert.equal(roles.find(x=>x.role==='imposter').word,undefined);
 act(r,r.players[0].token,{type:'ready'},1100);act(r,r.players[0].token,{type:'ready'},1200);assert.equal(r.imposter.ready.length,1);assert.equal(r.phase,'roles');for(const p of r.players.slice(1))act(r,p.token,{type:'ready'},1300);assert.equal(r.phase,'discussion');assert.equal(r.deadline,181300);assert.equal(new Set(r.imposter.turnOrder).size,3);
});
test('Imposter timed phases, pause, private immutable votes and group victory',()=>{
 const r=make('imposter');startReady(r);act(r,r.host,{type:'pause'},10000);tick(r,300000);assert.equal(r.phase,'discussion');act(r,r.host,{type:'resume'},300000);tick(r,r.deadline);assert.equal(r.phase,'voting');const secret=r.imposter.imposterId;const crew=r.players.filter(p=>p.id!==secret),imp=r.players.find(p=>p.id===secret);assert.throws(()=>act(r,crew[0].token,{type:'vote',playerId:crew[0].id},r.deadline-1));act(r,crew[0].token,{type:'vote',playerId:secret},r.deadline-1);assert.equal(view(r,crew[1].token).imposter.votes,undefined);assert.throws(()=>act(r,crew[0].token,{type:'vote',playerId:crew[1].id},r.deadline-1));act(r,crew[1].token,{type:'vote',playerId:secret},r.deadline-1);act(r,imp.token,{type:'vote',playerId:crew[0].id},r.deadline-1);assert.equal(r.phase,'finished');assert.equal(r.imposter.winner,'group');assert.equal(view(r,r.host).imposter.word,r.imposter.word);act(r,r.host,{type:'again'},400000);assert.equal(r.phase,'roles');assert.deepEqual(r.imposter.votes,{});assert.deepEqual(r.imposter.ready,[]);
});
test('Imposter can guess once; other players cannot guess; tie or no votes favors imposter',()=>{
 for(const correct of [true,false]){const r=make('imposter');startReady(r);const imp=r.players.find(p=>p.id===r.imposter.imposterId),crew=r.players.find(p=>p!==imp);assert.throws(()=>act(r,crew.token,{type:'imposter-guess',word:r.imposter.word},1200),{status:403});act(r,imp.token,{type:'imposter-guess',word:correct?' '+r.imposter.word.toUpperCase()+' ':'Невірне слово'},1200);assert.equal(r.phase,'finished');assert.equal(r.imposter.winner,correct?'imposter':'group');}
 const r=make('imposter');startReady(r);tick(r,r.deadline);tick(r,r.deadline);assert.equal(r.phase,'finished');assert.equal(r.imposter.accusedId,null);assert.equal(r.imposter.winner,'imposter');
});
