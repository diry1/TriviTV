import {spawn} from 'node:child_process';
let owned;
try{
 try{const response=await fetch('http://127.0.0.1:3016');if(!response.ok)throw Error();}
 catch{owned=spawn(process.execPath,['preview.mjs'],{cwd:new URL('./',import.meta.url),stdio:'ignore'});for(let i=0;i<50;i++){try{if((await fetch('http://127.0.0.1:3016')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}}
 await import('./tv-qa.mjs');
}finally{owned?.kill();}
