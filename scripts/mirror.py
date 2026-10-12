"""Capture the supplied public Framer site without redesigning its output."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin,urlsplit,unquote
from concurrent.futures import ThreadPoolExecutor,as_completed
import re,json,hashlib,time

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ORIGIN='https://wondrous-satisfaction-878713.framer.app'
PAGES=['/','/work/support-copilot','/work/underwriting-risk-copilot','/work/clinical-note-summarizer','/work/catalog-intelligence-engine']
ALLOWED={'framerusercontent.com','fonts.gstatic.com','fonts.googleapis.com','app.framerstatic.com'}
URL_RE=re.compile(r'https?://[^\s<>"\x27`\\)]+')
IMPORT_RE=re.compile(r'(?:\bfrom\s*|\bimport\s*\(?\s*)["\x27]([^"\x27]+)["\x27]')
CSS_RE=re.compile(r'url\(["\x27]?([^\s)"\x27]+)')
MODULE_RE=re.compile(r'["\x27`]([^"\x27`\s]+\.mjs)["\x27`]')

def normalized(url):
    p=urlsplit(url.replace('&amp;','&'))
    return p._replace(query='',fragment='').geturl()

def local_path(url):
    p=urlsplit(url)
    return '/mirror/'+p.netloc+unquote(p.path)

def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r:
                return r.read(),r.headers.get('Content-Type','')
        except Exception:
            if attempt==2:raise
            time.sleep(1)

def discover(text,base):
    found=set()
    for url in URL_RE.findall(text):
        if urlsplit(url).netloc in ALLOWED and urlsplit(url).path and not urlsplit(url).path.endswith('/'):found.add(normalized(url))
    for url in IMPORT_RE.findall(text)+CSS_RE.findall(text)+MODULE_RE.findall(text):
        if url.startswith(('./','../','/','https://')) or url.endswith('.mjs'):
            url=urljoin(base,url)
            if urlsplit(url).netloc in ALLOWED:found.add(normalized(url))
    return found

records={}; texts={}; pending=set(); failed={}
for page in PAGES:
    data,typ=fetch(ORIGIN+page)
    text=data.decode('utf-8')
    filename=DIST/('index.html' if page=='/' else page.lstrip('/')+'/index.html')
    filename.parent.mkdir(parents=True,exist_ok=True)
    texts[str(filename)]=(text,ORIGIN+page)
    pending |= discover(text,ORIGIN+page)
    print('PAGE',page,len(data),flush=True)

with ThreadPoolExecutor(max_workers=10) as pool:
    while pending:
        batch=sorted(pending-records.keys()-failed.keys());pending=set()
        if not batch:break
        futures={pool.submit(fetch,u):u for u in batch}
        for future in as_completed(futures):
            url=futures[future]
            try:
                data,typ=future.result()
                path=DIST/local_path(url).lstrip('/')
                path.parent.mkdir(parents=True,exist_ok=True)
                records[url]={'path':local_path(url),'bytes':len(data),'type':typ,'sha256':hashlib.sha256(data).hexdigest()}
                if any(x in typ for x in ['javascript','text/','json']) or urlsplit(url).path.endswith(('.mjs','.js','.css')):
                    text=data.decode('utf-8');texts[str(path)]=(text,url)
                    pending |= discover(text,url)
                else:path.write_bytes(data)
            except Exception as e:
                failed[url]=str(e);print('FAILED',url,str(e),flush=True)
        print('ASSETS',len(records),'next',len(pending-records.keys()-failed.keys()),flush=True)

def rewrite(text,base):
    def replace(match):
        url=match.group(0);key=normalized(url)
        return records[key]['path'] if key in records else url
    text=URL_RE.sub(replace,text)
    # Keep relative module imports: the mirrored directory tree is identical.
    # Framer uses the published origin as a URL base; preserve that metadata.
    return text

for path,(text,base) in texts.items():Path(path).write_text(rewrite(text,base),encoding='utf-8')
manifest={'source':ORIGIN,'pages':PAGES,'assets':records,'failed':failed}
(ROOT/'capture-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('COMPLETE',len(records),'assets;',len(failed),'failures',flush=True)
