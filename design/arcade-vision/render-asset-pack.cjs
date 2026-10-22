const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.join(__dirname,'assets-v1');
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);}
(async()=>{
 for(const f of walk(root).filter(f=>f.endsWith('.svg'))){
  const rel=path.relative(root,f),dst=path.join(root,'png',rel.replace('.svg','.png'));
  fs.mkdirSync(path.dirname(dst),{recursive:true});
  const meta=await sharp(f).metadata();
  const width=rel.startsWith('backgrounds')?1920:meta.width*2;
  await sharp(f).resize({width}).png().toFile(dst);
 }
 await sharp(path.join(root,'art/party-arena.png')).webp({quality:90,alphaQuality:100}).toFile(path.join(root,'art/party-arena.webp'));
 console.log('Exported all SVGs as PNG and arena as WebP.');
})();
