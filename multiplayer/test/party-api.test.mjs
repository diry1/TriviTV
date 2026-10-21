import {test} from 'node:test';
import assert from 'node:assert/strict';
const base=process.env.TRIVITV_TEST_URL||'http://127.0.0.1:8787';
async function api(path,data,token){const response=await fetch(base+'/api'+path,{method:data?'POST':'GET',headers:{...(data?{'content-type':'application/json'}:{}),...(token?{authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined});const json=await response.json();assert.equal(response.status,200,JSON.stringify(json));return json;}
test('Imposter real service: private roles, ready, discussion, private voting, results and replay',async()=>{
 const {categories}=await api('/config');const h=await api('/rooms',{categories,mode:'imposter'}),path='/rooms/'+h.code;
 const ps=[];for(let i=0;i<3;i++)ps.push(await api(path+'/join',{name:'Імпостер QA '+i}));let s=(await api(path+'/action',{type:'start'},h.token)).state;assert.equal(s.phase,'roles');assert.equal(s.you,undefined);assert.equal(s.secret,undefined);assert.equal(s.imposter.word,undefined);const identities=[];
 for(const p of ps){const state=(await api(path,null,p.token)).state;identities.push({p,id:state.you,role:state.secret.role});await api(path+'/action',{type:'ready'},p.token);}
 s=(await api(path,null,h.token)).state;assert.equal(s.phase,'discussion');assert.ok(s.deadline);await api(path+'/action',{type:'voting'},h.token);
 const imp=identities.find(x=>x.role==='imposter'),crew=identities.filter(x=>x!==imp);
 for(const x of crew)await api(path+'/action',{type:'vote',playerId:imp.id},x.p.token);
 s=(await api(path,null,h.token)).state;assert.equal(s.imposter.votes,undefined);assert.equal(s.imposter.imposterId,undefined);
 s=(await api(path+'/action',{type:'vote',playerId:crew[0].id},imp.p.token)).state;assert.equal(s.phase,'finished');assert.equal(s.imposter.winner,'group');assert.equal(s.imposter.imposterId,imp.id);assert.ok(s.imposter.word);
 s=(await api(path+'/action',{type:'again'},h.token)).state;assert.equal(s.phase,'roles');assert.equal(s.secret,undefined);assert.equal(s.imposter.word,undefined);await api(path+'/action',{type:'close'},h.token);
});
