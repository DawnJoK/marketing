from pathlib import Path
from urllib.parse import urljoin,urlsplit
from urllib.request import Request,urlopen
import re,json,hashlib
root=Path(__file__).resolve().parents[1]
source=root/'dist/mirror/framerusercontent.com/sites/4nHYQx2yRdfCawW7aBBb5U/shared-lib.CNqhiUol.mjs'
text=source.read_text(encoding='utf-8')
pattern=re.compile(r'new URL\([`"\x27]([^`"\x27]+\.framercms)[`"\x27],[`"\x27]([^`"\x27]+)[`"\x27]\)')
urls=set()
for name,base in pattern.findall(text):
    base=re.sub(r'https?://[^/]+/mirror/framerusercontent.com/','https://framerusercontent.com/',base)
    urls.add(urljoin(base,name).replace('/modules/','/cms/'))
manifest=json.loads((root/'capture-manifest.json').read_text(encoding='utf-8'))
for url in sorted(urls):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:data=r.read()
    p=urlsplit(url);local='/mirror/'+p.netloc+p.path
    file=root/'dist'/local.lstrip('/');file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
    manifest['assets'][url]={'path':local,'bytes':len(data),'type':'application/octet-stream','sha256':hashlib.sha256(data).hexdigest()}
    print(local,len(data),flush=True)
(root/'capture-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
