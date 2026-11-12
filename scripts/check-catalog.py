"""Offline completeness checks; no requests to X or other services."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/'data/videos.json').read_text())
local=json.loads((ROOT/'data/local-media.json').read_text())
assert len(items)==len(local)
assert len({v['slug'] for v in items})==len(items)
for item,record in zip(items,local):
 assert item['slug']==record['slug']
 assert item['post_url']==record['post_url'] and item['post_url'].startswith('https://')
 prompt=(ROOT/record['prompt_path']).read_text()
 assert item['post_url'] in prompt
 if item.get('prompt'): assert item['prompt'] in prompt
 for key in ('video_path','poster_path','preview_path'):
  path=ROOT/record[key]
  assert path.is_file() and path.stat().st_size>0,path
  if key=='video_path': assert b'ftyp' in path.open('rb').read(64),path
for page in [ROOT/'README.md',*(ROOT/'data/categories').glob('*.md'),*(ROOT/'prompts').glob('*.md')]:
 for target in re.findall(r'(?:href|src)="([^"]+)"|\]\(([^)]+)\)',page.read_text()):
  target=next(t for t in target if t)
  if target.startswith(('http:','https:','#','mailto:')): continue
  assert (page.parent/target.split('#')[0]).exists(),(page,target)
print(f'PASS: {len(items)} videos, {sum(bool(v.get("prompt")) for v in items)} public prompts, all local assets and links')
