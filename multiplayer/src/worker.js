import bankInfo from './bank-info.json';
let bankPromise;
async function loadBank(env){
 if(!bankPromise)bankPromise=env.ASSETS.fetch(new Request('https://iggro.com/questions-runtime.json')).then(async response=>{requireThat(response.ok,'База запитань недоступна',503);const bank=await response.json();requireThat(bank.length===bankInfo.count,'База запитань застаріла',503);return bank;}).catch(error=>{bankPromise=null;throw error;});
 return bankPromise;
}
import {createRoom,join,identity,act,tick,view,requireThat,setRemotePlayer} from './engine.js';
const json=(data,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store'}});
const origins=new Set(['https://iggro.com','https://www.iggro.com','https://appassets.androidplatform.net']);
async function body(request){requireThat(Number(request.headers.get('content-length')||0)<=4096,'Запит завеликий',413);const text=await request.text();requireThat(text.length<=4096,'Запит завеликий',413);try{const v=JSON.parse(text);requireThat(v&&typeof v==='object'&&!Array.isArray(v),'Некоректний запит');return v;}catch(e){throw Object.assign(Error('Некоректний запит'),{status:400});}}
export default {async fetch(request,env){
 const url=new URL(request.url),origin=request.headers.get('Origin');
 const allowed=!origin||origins.has(origin)||origin===url.origin;
 if(url.pathname.startsWith('/api/')){
  if(!allowed)return json({error:'Недозволене джерело'},403);
  const cors={'Access-Control-Allow-Origin':origin||url.origin,'Access-Control-Allow-Headers':'Authorization, Content-Type','Access-Control-Allow-Methods':'GET, POST, OPTIONS','Vary':'Origin'};
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:cors});
  let result;
  try{
   if(url.pathname==='/api/config')result=json(bankInfo);
   else if(url.pathname==='/api/rooms'&&request.method==='POST'){
    const ip=request.headers.get('CF-Connecting-IP')||'local';
    const id=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(ip)))).map(x=>x.toString(16).padStart(2,'0')).join('');
    const limit=await env.LIMITS.get(env.LIMITS.idFromName(id)).fetch('https://limit/');requireThat(limit.ok,'Забагато нових кімнат. Спробуйте пізніше.',429);
    const data=await body(request);let code;
    for(let i=0;i<5;i++){
     code=Array.from(crypto.getRandomValues(new Uint8Array(6)),n=>'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'[n%32]).join('');
     result=await env.ROOMS.get(env.ROOMS.idFromName(code)).fetch('https://room/init',{method:'POST',body:JSON.stringify({...data,code})});if(result.status!==409)break;
    }
   }else{
    const match=url.pathname.match(/^\/api\/rooms\/([A-Z2-9]{6})(\/(?:join|action|socket))?$/);
    requireThat(match,'Не знайдено',404);const suffix=match[2]||'';
    result=await env.ROOMS.get(env.ROOMS.idFromName(match[1])).fetch(new Request('https://room'+(suffix||'/'),request));
   }
  }catch(error){result=json({error:error.status?error.message:'Сервіс тимчасово недоступний'},error.status||500);}
  if(result.status===101)return result;
  const headers=new Headers(result.headers);for(const [k,v]of Object.entries(cors))headers.set(k,v);
  return new Response(result.body,{status:result.status,headers});
 }
 if(url.pathname==='/health')return json({ok:true,version:'multiplayer-1'});
 return env.ASSETS.fetch(request);
}};
export class Limiter{
 constructor(ctx){this.ctx=ctx;}
 async fetch(){return this.ctx.blockConcurrencyWhile(async()=>{const now=Date.now();let value=await this.ctx.storage.get('rate');if(!value||now>=value.until)value={count:0,until:now+3600000};value.count++;await this.ctx.storage.put('rate',value);await this.ctx.storage.setAlarm(value.until);return new Response('',{status:value.count<=20?200:429});});}
 async alarm(){await this.ctx.storage.deleteAll();}
}
export class Room{
 constructor(ctx,env){this.ctx=ctx;this.env=env;}
 async save(room){await this.ctx.storage.put('room',room);await this.ctx.storage.setAlarm(room.deadline!==null&&!room.paused?Math.min(room.deadline,room.expiresAt):room.expiresAt);}
 broadcast(room){for(const ws of this.ctx.getWebSockets()){try{const secret=ws.deserializeAttachment()?.secret;ws.send(JSON.stringify({state:view(room,secret)}));if(room.phase==='closed')ws.close(1000,'Room closed');}catch{ws.close(1008,'Session expired');}}}
 async fetch(request){return this.ctx.blockConcurrencyWhile(async()=>{
  try{
   const path=new URL(request.url).pathname;let room=await this.ctx.storage.get('room');
   if(path==='/init'){
    requireThat(!room,'Кімната вже існує',409);const data=await body(request);const bank=await loadBank(this.env);room=createRoom(data.code,bank,data.categories,Date.now(),data);setRemotePlayer(room,room.mode!=='imposter'&&data.remotePlayer!==false);await this.save(room);return json({code:room.code,token:room.host,role:'host'});
   }
   requireThat(room,'Кімнату не знайдено',404);const prior=room.revision;tick(room);await this.save(room);if(room.revision!==prior)this.broadcast(room);requireThat(room.phase!=='closed','Кімната закрита або термін минув',410);
   if(path==='/join'&&request.method==='POST'){const data=await body(request);const p=join(room,data.name);await this.save(room);this.broadcast(room);return json({code:room.code,token:p.token,role:'player'});}
   const protocols=(request.headers.get('Sec-WebSocket-Protocol')||'').split(',').map(s=>s.trim());
   const secret=path==='/socket'?protocols[1]:request.headers.get('Authorization')?.replace(/^Bearer /,'');identity(room,secret);
   if(path==='/socket'){
    requireThat(request.headers.get('Upgrade')?.toLowerCase()==='websocket','Потрібен WebSocket',426);requireThat(protocols[0]==='trivitv','Невірний протокол');
    const old=this.ctx.getWebSockets().filter(ws=>ws.deserializeAttachment()?.secret===secret);for(const ws of old)ws.close(1000,'Reconnected');
    requireThat(this.ctx.getWebSockets().length<32,'Забагато з’єднань',429);
    const [client,server]=Object.values(new WebSocketPair());this.ctx.acceptWebSocket(server);server.serializeAttachment({secret});server.send(JSON.stringify({state:view(room,secret)}));return new Response(null,{status:101,webSocket:client,headers:{'Sec-WebSocket-Protocol':'trivitv'}});
   }
   if(path==='/action'&&request.method==='POST'){act(room,secret,await body(request));await this.save(room);this.broadcast(room);if(!room.players.some(p=>p.token===secret)&&secret!==room.host)return json({left:true});}
   else requireThat(path==='/'&&request.method==='GET','Не знайдено',404);
   return json({state:view(room,secret)});
  }catch(error){return json({error:error.status?error.message:'Не вдалося виконати дію'},error.status||500);}
 });}
 async alarm(){await this.ctx.blockConcurrencyWhile(async()=>{const room=await this.ctx.storage.get('room');if(!room)return;tick(room);this.broadcast(room);if(room.phase==='closed'){await this.ctx.storage.deleteAll();}else await this.save(room);});}
 async webSocketMessage(ws,message){if(message==='ping'){ws.send('pong');return;}ws.close(1008,'Use room API');}
 webSocketClose(ws,code){ws.close(code);}
}
