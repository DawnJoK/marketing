import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../dist');
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.avif':'image/avif','.woff':'font/woff','.woff2':'font/woff2','.mp4':'video/mp4','.json':'application/json'};
const server = http.createServer((req,res) => {
  let pathname;
  try {pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname);} catch {res.writeHead(400).end();return;}
  let file = path.resolve(root, '.' + pathname);
  if (file !== root && !file.startsWith(root + path.sep)) {res.writeHead(403).end();return;}
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file,'index.html');
  if (!fs.existsSync(file)) {res.writeHead(404).end('Not found');return;}
  res.setHeader('Content-Type',types[path.extname(file)] || 'application/octet-stream');
  res.setHeader('Access-Control-Allow-Origin','*');
  // Keep the same captured files usable in a local preview after publication.
  if (/\.(mjs|json)$/.test(file)) {
    const body=fs.readFileSync(file,'utf8').replace(/https?:\/\/[^/\s"'`]+\/mirror\//g, 'http://127.0.0.1:4173/mirror/');
    res.end(body);return;
  }
  fs.createReadStream(file).pipe(res);
});
server.listen(4173, '127.0.0.1',()=>console.log('Local: http://127.0.0.1:4173'));
