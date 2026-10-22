import CATEGORY_DIFFICULTY from './category-difficulty.mjs';
export {CATEGORY_DIFFICULTY};
// Five stars are reserved for future per-question expert ratings; 4–5 share
// the hard bucket. Category defaults are editorial estimates, not calibration.
export function difficultyStars(q){
  if(Number.isInteger(q.difficultyStars)&&q.difficultyStars>=1&&q.difficultyStars<=5)return q.difficultyStars;
  return CATEGORY_DIFFICULTY[q.category]??3;
}
export function bucket(q){const stars=difficultyStars(q);return stars<=2?0:stars===3?1:2;}
export function weightsAt(index,total){
  const progress=total<=1?0:Math.max(0,Math.min(1,index/(total-1)));
  return [.6-.3*progress,.3+.2*progress,.1+.1*progress];
}
function random(){return crypto.getRandomValues(new Uint32Array(1))[0]/4294967296;}
export function weightedQuestions(pool,count,rng=random,progress=null){
  // Unique IDs, sampling without replacement, within the already eligible pool.
  const unique=[...new Map(pool.map(q=>[q.id,q])).values()];
  count=Math.max(0,Math.min(Math.floor(count),unique.length));
  const groups=[[],[],[]];for(const q of unique)groups[bucket(q)].push(q);
  const selected=[];
  for(let i=0;i<count;i++){
    const weights=weightsAt(progress?progress.startIndex+i:i,progress?progress.rampLength:count).map((w,b)=>groups[b].length?w:0);
    // Missing/depleted buckets are renormalized across available buckets.
    let roll=rng()*weights.reduce((a,b)=>a+b,0),chosen=weights.findLastIndex(w=>w>0);
    for(let b=0;b<3;b++){roll-=weights[b];if(weights[b]>0&&roll<0){chosen=b;break;}}
    const group=groups[chosen],j=Math.min(group.length-1,Math.floor(rng()*group.length));
    selected.push(group[j]);group[j]=group.at(-1);group.pop();
  }
  return selected;
}
// Question-level selection for the accepted Ukrainian difficulty build.
export const TRIVIA_MIXES=[[.35,.50,.15,0,0],[.20,.45,.30,.05,0],[.10,.35,.40,.15,0],[.05,.30,.40,.23,.02],[.05,.25,.40,.27,.03]];
export function triviaMixAt(index){return TRIVIA_MIXES[Math.min(4,Math.floor(Math.max(0,index)/5))].slice();}
export function millionaireStarsAt(index){return index===0?1:index<5?2:index<10?3:index<14?4:5;}
export function millionaireAvailability(pool){const counts=[0,0,0,0,0];for(const q of new Map(pool.map(q=>[q.id,q])).values())counts[difficultyStars(q)-1]++;const required=[1,4,5,4,1];return {counts,required,missing:required.map((n,i)=>Math.max(0,n-counts[i])),ok:required.every((n,i)=>counts[i]>=n)};}
export function millionaireQuestions(pool,rng=random){const status=millionaireAvailability(pool);if(!status.ok)throw Error('Для «Мільйонера» бракує запитань: '+status.missing.map((n,i)=>n?`${i+1}★ — ${n}`:null).filter(Boolean).join(', ')+'. Оберіть більше категорій.');const groups=Array.from({length:5},()=>[]);for(const q of new Map(pool.map(q=>[q.id,q])).values())groups[difficultyStars(q)-1].push(q);return Array.from({length:15},(_,i)=>{const g=groups[millionaireStarsAt(i)-1];return g.splice(Math.min(g.length-1,Math.floor(rng()*g.length)),1)[0]});}
function seeded(seed){let n=seed>>>0;n=Math.imul(n^(n>>>16),0x7feb352d);n=Math.imul(n^(n>>>15),0x846ca68b);n=(n^(n>>>16))||1;return ()=>{n^=n<<13;n^=n>>>17;n^=n<<5;return (n>>>0)/4294967296;};}
function stageSchedule(stage,seed){const size=stage<4?5:100,mix=TRIVIA_MIXES[Math.min(stage,4)],rng=seeded((seed^Math.imul(stage+1,2654435761))>>>0),offset=rng(),counts=[0,0,0,0,0];for(let i=0;i<size;i++){const x=(i+offset)/size;let sum=0;for(let s=0;s<5;s++){sum+=mix[s];if(x<sum||s===4){counts[s]++;break;}}}const used=[0,0,0,0,0],result=[];for(let i=0;i<size;i++){let best=-1,score=-Infinity;for(let s=0;s<5;s++){if(used[s]>=counts[s])continue;const value=counts[s]*(i+1)/size-used[s]+rng()*.0001;if(value>score){score=value;best=s;}}used[best]++;result.push(best);}return result;}
export function triviaQuestions(pool,count,rng=random,progress={}){const unique=[...new Map(pool.map(q=>[q.id,q])).values()],groups=Array.from({length:5},()=>[]);for(const q of unique)groups[difficultyStars(q)-1].push(q);const start=progress.startIndex||0,seed=progress.seed??Math.floor(rng()*4294967296),cache=new Map(),result=[];for(let i=0;i<Math.min(count,unique.length);i++){const index=start+i,stage=index<20?Math.floor(index/5):4+Math.floor((index-20)/100),position=index<20?index%5:(index-20)%100;if(!cache.has(stage))cache.set(stage,stageSchedule(stage,seed));let target=cache.get(stage)[position];if(!groups[target].length){const candidates=groups.map((g,s)=>g.length?s:-1).filter(s=>s>=0);target=candidates.sort((a,b)=>Math.abs(a-target)-Math.abs(b-target)||a-b)[0];}const g=groups[target];result.push(g.splice(Math.min(g.length-1,Math.floor(rng()*g.length)),1)[0]);}return result;}
