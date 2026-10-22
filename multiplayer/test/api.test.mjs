import {test} from 'node:test';
import assert from 'node:assert/strict';
const base=process.env.TRIVITV_TEST_URL||'http://127.0.0.1:8787';
async function api(path,data,token){const r=await fetch(base+'/api'+path,{method:data?'POST':'GET',headers:{...(data?{'content-type':'application/json'}:{}),...(token?{authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined});return {status:r.status,...await r.json()};}
test('real Worker/SQLite room lifecycle, WebSocket, private answers, reconnect, permissions',async()=>{
 const config=await api('/config');assert.equal(config.count,JSON.parse(await (await import('node:fs/promises')).readFile(new URL('../src/bank.json',import.meta.url),'utf8')).length);
 const host=await api('/rooms',{categories:config.categories,remotePlayer:false});assert.equal(host.status,200);
 const path='/rooms/'+host.code;
 const a=await api(path+'/join',{name:'Оля'}),b=await api(path+'/join',{name:'Макс'});
 assert.equal((await api(path)).status,401);
 const snapshot=await api(path,null,a.token);assert.equal(snapshot.state.players.length,2);assert.ok(!JSON.stringify(snapshot.state).includes(host.token));
 const socket=new WebSocket(base.replace('http','ws')+'/api'+path+'/socket',['trivitv',a.token]);
 const messages=[];socket.addEventListener('message',e=>messages.push(JSON.parse(e.data)));
 await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
 assert.equal((await api(path+'/action',{type:'start'},a.token)).status,403);
 let result=await api(path+'/action',{type:'start'},host.token);assert.equal(result.state.phase,'question');assert.equal(result.state.question.correct,undefined);
 assert.equal((await api(path+'/join',{name:'Late'})).status,409);
 await api(path+'/action',{type:'answer',questionId:result.state.question.id,choice:0},a.token);
 result=await api(path,null,b.token);assert.equal(result.state.players[0].answer,undefined);
 result=await api(path+'/action',{type:'answer',questionId:result.state.question.id,choice:1},b.token);assert.equal(result.state.phase,'reveal');assert.ok(Number.isInteger(result.state.question.correct));
 assert.equal((await api(path+'/action',{type:'next'},b.token)).status,403);
 assert.equal((await api(path,null,a.token)).state.players[0].answered,true);
 await new Promise(resolve=>setTimeout(resolve,150));assert.ok(messages.some(m=>m.state.phase==='reveal'));
 await api(path+'/action',{type:'close'},host.token);assert.equal((await api(path,null,a.token)).status,410);socket.close();
 const blocked=await fetch(base+'/api/config',{headers:{Origin:'https://evil.example'}});assert.equal(blocked.status,403);
 const cors=await fetch(base+'/api/config',{headers:{Origin:'https://appassets.androidplatform.net'}});assert.equal(cors.headers.get('access-control-allow-origin'),'https://appassets.androidplatform.net');
});

test('real mixed remote/phone room and optional remote player',async()=>{
 const c=await api('/config');const h=await api('/rooms',{categories:c.categories});const path='/rooms/'+h.code;let s=(await api(path,null,h.token)).state;assert.equal(s.players.length,1);assert.equal(s.you,s.players[0].id);
 assert.equal((await api(path+'/action',{type:'start'},h.token)).status,409);
 const p=await api(path+'/join',{name:'Phone'});s=(await api(path+'/action',{type:'start'},h.token)).state;
 const q=s.question;await api(path+'/action',{type:'answer',questionId:q.id,choice:0},h.token);s=(await api(path,null,p.token)).state;assert.equal(s.phase,'question');assert.equal(s.players[0].answer,undefined);s=(await api(path+'/action',{type:'answer',questionId:q.id,choice:1},p.token)).state;assert.equal(s.phase,'reveal');await api(path+'/action',{type:'close'},h.token);
});
