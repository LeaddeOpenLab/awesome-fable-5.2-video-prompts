"""Download only media referenced by the cloned source index; never searches X."""
import concurrent.futures, json, subprocess
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT/'data/videos.json').read_text())
jobs=[]
for item in items:
    for key in ('video_url','poster_url','preview_url'):
        url=item.get(key)
        if url:
            path=ROOT/'media'/item['slug']/Path(urlparse(url).path).name
            jobs.append((url,path))
def download(job):
    url,path=job
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.stat().st_size: return None
    tmp=path.with_suffix(path.suffix+'.part')
    p=subprocess.run(['curl','-fL','-C','-','--retry','2','--connect-timeout','20','--max-time','900','-sS',url,'-o',str(tmp)],capture_output=True)
    if p.returncode: return {'url':url,'error':p.stderr.decode()[-300:]}
    tmp.rename(path)
    return None
if __name__=='__main__':
    errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=48) as pool:
        for i,result in enumerate(pool.map(download,jobs),1):
            if result: errors.append(result)
            if i%30==0: print(f'{i}/{len(jobs)} assets, {len(errors)} failures',flush=True)
    (ROOT/'data/media-download-errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(f'Done: {len(jobs)-len(errors)}/{len(jobs)} assets',flush=True)
    raise SystemExit(bool(errors))
