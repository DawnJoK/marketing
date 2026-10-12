import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../dist');
const origin=process.argv[2];
if(!origin || !/^https?:\/\//.test(origin)) throw new Error('Provide an absolute asset origin');
let count=0;
function visit(dir) {
  for(const item of fs.readdirSync(dir,{withFileTypes:true})) {
    const file=path.join(dir,item.name);
    if(item.isDirectory()) {visit(file);continue;}
    if(!/\.(mjs|json)$/.test(file)) continue;
    const text=fs.readFileSync(file,'utf8');
    const next=text.replace(/(?:https?:\/\/[^\s<>"'`\\)]+)?\/mirror\//g,origin+'/mirror/');
    if(next!==text){fs.writeFileSync(file,next);count++;}
  }
}
visit(root);console.log(`Set the asset origin in ${count} runtime files.`);
