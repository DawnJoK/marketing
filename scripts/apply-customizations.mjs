import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../dist');
const style='<style id="site-branding-overrides">#__framer-badge-container,.__framer-badge{display:none!important}</style>';
let count=0;
function visit(dir) {
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})) {
    const file=path.join(dir,entry.name);
    if(entry.isDirectory()) {visit(file);continue;}
    if(!entry.name.endsWith('.html')) continue;
    const html=fs.readFileSync(file,'utf8');
    if(html.includes('id="site-branding-overrides"')) continue;
    if(!html.includes('</head>')) throw new Error(`Missing document head: ${file}`);
    fs.writeFileSync(file,html.replace('</head>',style+'</head>'));
    count++;
  }
}
visit(root);
console.log(`Removed visible Framer branding on ${count} pages.`);
