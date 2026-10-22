import fs from 'node:fs/promises';
import {build} from 'esbuild';
const categoryDefaults=JSON.parse(await fs.readFile('../game-rules/category-difficulty.json','utf8'));
await fs.writeFile('../game-rules/category-difficulty.mjs','// Generated from category-difficulty.json by multiplayer/prepare.mjs.\nexport default '+JSON.stringify(categoryDefaults,null,2)+';\n');
for(const name of ['difficulty.mjs','category-difficulty.mjs'])await fs.copyFile('../game-rules/'+name,'../browser-site/dist/'+name);
await fs.copyFile('../browser-site/dist/questions.json','src/bank.json');
const runtimeBank=JSON.parse(await fs.readFile('src/bank.json','utf8'));
await fs.writeFile('src/bank-info.json',JSON.stringify({count:runtimeBank.length,categories:[...new Set(runtimeBank.map(q=>q.category))]}));
await fs.writeFile('public/questions-runtime.json',JSON.stringify(runtimeBank.map(({id,text,category,choices,correct,difficultyStars})=>({id,text,category,choices,correct,...(difficultyStars?{difficultyStars}:{})}))));
await build({entryPoints:['qr-entry.js'],bundle:true,format:'esm',outfile:'public/multi/qr.js',minify:true});
console.log(`Prepared ${runtimeBank.length} Ukrainian questions, TV assets and local QR encoder.`);


await fs.copyFile('../browser-site/dist/i18n.js','public/multi/labels.js');
await fs.cp('public/multi','../browser-site/dist/multi',{recursive:true});

await fs.cp('../browser-site/dist','public/tv',{recursive:true});
await fs.writeFile('public/tv/index.html',(await fs.readFile('public/tv/index.html','utf8')).replaceAll('href="/','href="/tv/').replaceAll('src="/','src="/tv/'));

await fs.cp('../browser-site/dist/visuals','public/visuals',{recursive:true});
