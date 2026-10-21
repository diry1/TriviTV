import fs from 'node:fs/promises';
import {build} from 'esbuild';
await fs.copyFile('../browser-site/dist/questions.json','src/bank.json');
await build({entryPoints:['qr-entry.js'],bundle:true,format:'esm',outfile:'public/multi/qr.js',minify:true});
console.log('Prepared unchanged 916-question bank, TV assets and local QR encoder.');


await fs.copyFile('../browser-site/dist/i18n.js','public/multi/labels.js');
await fs.cp('public/multi','../browser-site/dist/multi',{recursive:true});

await fs.cp('../browser-site/dist','public/tv',{recursive:true});
await fs.writeFile('public/tv/index.html',(await fs.readFile('public/tv/index.html','utf8')).replaceAll('href="/','href="/tv/').replaceAll('src="/','src="/tv/'));
