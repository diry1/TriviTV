import http from 'node:http';
import fs from 'node:fs/promises';
const root=new URL('./dist/',import.meta.url);
const server=http.createServer(async(req,res)=>{try{const p=new URL(req.url,'http://localhost').pathname;const file=new URL('.'+(p==='/'?'/index.html':p),root);if(!file.href.startsWith(root.href))throw Error();const data=await fs.readFile(file);res.setHeader('Content-Type',file.pathname.endsWith('.js')?'text/javascript':file.pathname.endsWith('.css')?'text/css':file.pathname.endsWith('.json')?'application/json':file.pathname.endsWith('.txt')?'text/plain':'text/html');res.setHeader('Cache-Control','no-store');res.end(data);}catch{res.writeHead(404);res.end();}});
server.listen(3016,'127.0.0.1',()=>console.log('TriviTV preview: http://127.0.0.1:3016'));
