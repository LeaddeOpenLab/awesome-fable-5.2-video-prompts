"""Render the imported index using the Opus repository's card layout."""
import html, json, shutil
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/'data/videos.json').read_text())
categories={'motion':'Motion Graphics & Typography','explainer':'Explainers & Education','3d':'3D Worlds & Simulations','interactive':'Games & Interactive Experiences','promo':'Product & Brand Videos'}
# Use source category IDs verbatim, including any future categories.
for item in items: categories.setdefault(item['category'],item['category'].replace('-',' ').title())
def asset(item,key): return 'media/'+item['slug']+'/'+Path(urlparse(item[key]).path).name
def card(item,width=33,prefix=''):
 e=html.escape; prompt=prefix+'prompts/'+item['slug']+'.md'; video=prefix+asset(item,'video_url'); preview=prefix+asset(item,'preview_url')
 return f'''<td width="{width}%" valign="top">
<a href="{video}"><img src="{preview}" alt="{e(item['title'])}" width="100%" /></a><br>
<strong>{e(item['title'])}</strong><br>
<sub><a href="{prompt}">{'View prompt' if item.get('prompt') else 'View details'} · GitHub</a> · <a href="{video}">Watch video ↗</a> · <a href="{item['post_url']}">@{e(item['author'])} · Original post ↗</a></sub><br>
<sub>{e(categories[item['category']])} · {'Public prompt' if item.get('prompt') else 'Prompt not published'} · {item['posted_at'][:10]}</sub>
</td>'''
def table(videos,cols=3,prefix=''):
 rows=[]
 for i in range(0,len(videos),cols): rows.append('<tr>\n'+'\n'.join(card(v,100//cols,prefix) for v in videos[i:i+cols])+'\n</tr>')
 return '<table>\n'+'\n'.join(rows)+'\n</table>\n'
backup=ROOT/'data/upstream';backup.mkdir(exist_ok=True)
if not (backup/'README.md').exists(): shutil.copy2(ROOT/'README.md',backup/'README.md')
public=[v for v in items if v.get('prompt')]
updated_at=json.loads((ROOT/'data/catalog.json').read_text())['updated_at']
catalog=json.loads((ROOT/'data/catalog.json').read_text())
(ROOT/'data/banner.svg').write_text((ROOT/'data/banner-template.svg').read_text().replace('{{TOTAL}}',str(catalog.get('total',len(items)))).replace('{{ADDED}}',str(catalog.get('recently_added',0))).replace('{{UPDATED_AT}}',updated_at))
lines=['# Awesome Fable 5.2 Video Prompts','','![Fable 5.2 — total examples and latest update](data/banner.svg)','','**Creator-shared prompts, visual previews, and original sources — curated by Leadde Open Lab.** Explore Fable 5.2 videos, animation, 3D worlds and interactive projects.','','**☆ Star this repo to keep the prompts handy for your next project.**','',f'{catalog.get('total',len(items))} video examples · {len(set(v["category"] for v in items))} categories. Videos, posters and animated previews are archived in `media/`.','','[Featured creations](#featured-creations) · [Start with a prompt](#start-here) · [Latest additions](#recently-added) · [Browse the full repository](#browse-the-full-library)','','## Featured creations','','Read the creator’s prompt on GitHub, watch the archived video, or open the original post.','',table(public[:6],2),'## Start here','','| Creative direction | Shared prompt |','| --- | --- |']
for cat in categories:
 v=next((v for v in public if v['category']==cat),None)
 if v: lines.append(f'| {categories[cat]} | [{v["title"]}](prompts/{v["slug"]}.md) |')
lines+=['','## Recently added','',table(items[:6]),'## Browse the full library','']
(ROOT/'data/categories').mkdir(exist_ok=True)
for cat,label in categories.items():
 selected=[v for v in items if v['category']==cat]
 if not selected: continue
 lines.append(f'- [{label}](data/categories/{cat}.md) ({len(selected)})')
 (ROOT/f'data/categories/{cat}.md').write_text(f'# {label}\n\n[← Full library](../../README.md)\n\n{len(selected)} examples · Original creator links on every card.\n\n'+table(selected,prefix='../../'))
for cat,label in categories.items():
 selected=[v for v in items if v['category']==cat]
 if selected: lines+=['',f'## {label} — homepage picks','',table(selected[:6]),f'[Browse all {len(selected)} examples →](data/categories/{cat}.md)']
lines+=['','## Attribution and source','','Imported from [yihui-dev/awesome-fable5-2-videos](https://github.com/yihui-dev/awesome-fable5-2-videos). All original index fields, creator credits, prompt text and source-post links are preserved. The original README is archived in [data/upstream/README.md](data/upstream/README.md).','','Entries without a disclosed prompt are labelled **Prompt not published**; their post text is not presented as a prompt. Videos and images remain the work of their original creators. The upstream repository’s MIT license is preserved in [LICENSE](LICENSE).','','## Clone with all videos', '', 'Individual case videos are stored with Git LFS.', '', '```bash', 'git lfs install', 'git clone https://github.com/LeaddeOpenLab/awesome-fable-5.2-video-prompts.git', 'cd awesome-fable-5.2-video-prompts', 'git lfs pull', '```', '', '## Data and maintenance','','- [Original machine-readable index](data/videos.json)','- [Local media paths and tags](data/local-media.json)','- `python3 scripts/download-media.py` downloads only media URLs already in the index.','- `python3 scripts/build-catalog.py` rebuilds the cards.','- `python3 scripts/check-catalog.py` checks local media, prompts and source links.','','X discovery is not started by this repository or these scripts.','']
(ROOT/'README.md').write_text('\n'.join(lines))
local=[]
for v in items:
 p=ROOT/'prompts'/f'{v["slug"]}.md'
 original=backup/'prompts'/p.name;original.parent.mkdir(exist_ok=True)
 if not original.exists(): shutil.copy2(p,original)
 text=original.read_text()
 for key in ('video_url','poster_url','preview_url'):
  if v.get(key): text=text.replace(v[key],'../'+asset(v,key))
 p.write_text(text+f'\n**Tags:** Fable 5.2 · {categories[v["category"]]} · '+('Public prompt' if v.get('prompt') else 'Prompt not published')+'\n')
 local.append({'slug':v['slug'],'post_url':v['post_url'],'prompt_path':str(p.relative_to(ROOT)),'tags':['fable-5-2',v['category'],'public-prompt' if v.get('prompt') else 'prompt-not-published'],**{key.replace('_url','_path'):asset(v,key) for key in ('video_url','poster_url','preview_url')}})
(ROOT/'data/local-media.json').write_text(json.dumps(local,indent=2,ensure_ascii=False)+'\n')
print(f'Rendered {len(items)} entries, {len(public)} public prompts')
