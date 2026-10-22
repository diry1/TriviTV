import {test} from 'node:test';
import assert from 'node:assert/strict';
import {weightedQuestions,weightsAt,difficultyStars,bucket,CATEGORY_DIFFICULTY} from './difficulty.mjs';
const pool=Object.keys(CATEGORY_DIFFICULTY).flatMap(category=>Array.from({length:20},(_,i)=>({id:category+i,category})));
function seeded(seed=1234){return ()=>((seed=(1664525*seed+1013904223)>>>0)/4294967296);}
test('interpolates requested endpoints and midpoint',()=>{
  for(const [i,expected] of [[0,[.6,.3,.1]],[5,[.45,.4,.15]],[10,[.3,.5,.2]]])weightsAt(i,11).forEach((v,j)=>assert.ok(Math.abs(v-expected[j])<1e-10));
  assert.deepEqual(weightsAt(0,1),[.6,.3,.1]);
});
test('category defaults, question overrides, invalid and unknown ratings',()=>{
  assert.equal(Object.keys(CATEGORY_DIFFICULTY).length,20);
  assert.equal(difficultyStars({category:'Animals'}),2);
  assert.equal(difficultyStars({category:'Animals',difficultyStars:5}),5);
  assert.equal(difficultyStars({category:'Animals',difficultyStars:99}),2);
  assert.equal(difficultyStars({category:'Unknown'}),3);
});
test('unique eligible IDs, no mutation, short pools and missing buckets',()=>{
  const original=JSON.stringify(pool),draw=weightedQuestions(pool,15,seeded());
  assert.equal(draw.length,15);assert.equal(new Set(draw.map(q=>q.id)).size,15);assert.equal(JSON.stringify(pool),original);
  const single=pool.filter(q=>q.category==='Sport');
  assert.equal(weightedQuestions(single,100,seeded()).length,20);
  assert.equal(weightedQuestions([single[0],single[0]],10,seeded()).length,1);
  assert.deepEqual(weightedQuestions([],10),[]);
});
test('empirical start/end mixes follow weights and are not monotonically sorted',()=>{
  const rng=seeded(556),counts=[Array(3).fill(0),Array(3).fill(0)];let descents=0;
  for(let n=0;n<12000;n++){
    const q=weightedQuestions(pool,10,rng);counts[0][bucket(q[0])]++;counts[1][bucket(q[9])]++;
    if(q.some((v,i)=>i&&difficultyStars(v)<difficultyStars(q[i-1])))descents++;
  }
  for(const [index,expected] of [[0,[.6,.3,.1]],[1,[.3,.5,.2]]])counts[index].forEach((v,j)=>assert.ok(Math.abs(v/12000-expected[j])<.025,`${index}/${j}: ${v/12000}`));
  assert.ok(descents>10000);
});
test('endless batches hold the late difficulty mix rather than restarting',()=>{const rng=seeded(442),counts=[0,0,0];for(let n=0;n<10000;n++){const draw=weightedQuestions(pool,1,rng,{startIndex:30,rampLength:10});counts[bucket(draw[0])]++;}counts.forEach((v,i)=>assert.ok(Math.abs(v/10000-[.3,.5,.2][i])<.025));});
