import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'capture-manifest.json'),'utf8'));
const missing=[];
for(const [url,asset] of Object.entries(manifest.assets)) {
  if(manifest.failed[url]) continue;
  if(!fs.existsSync(path.join(root,'dist',asset.path))) missing.push(url);
}
for(const route of manifest.pages) {
  const file=path.join(root,'dist',route==='/'?'index.html':route+'/index.html');
  if(!fs.existsSync(file)) missing.push(route);
}
if(missing.length) {console.error('Missing files:',missing);process.exit(1);}
console.log(`Verified ${manifest.pages.length} pages and ${Object.keys(manifest.assets).length-Object.keys(manifest.failed).filter(u=>manifest.assets[u]).length} captured assets.`);
