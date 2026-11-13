#!/usr/bin/env python3
"""Build the Fable 5.2 showcase using the existing Leadde page layout."""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
SITE = ROOT / 'site'
REPO = 'https://github.com/LeaddeOpenLab/awesome-fable-5.2-video-prompts'
BASE = 'https://leaddeopenlab.github.io/awesome-fable-5.2-video-prompts/'
E = lambda x: html.escape(str(x or ''), quote=True)
CATS = {'motion':'Motion Graphics & Typography','explainer':'Explainers & Education','3d':'3D Worlds & Simulations','interactive':'Games & Interactive Experiences','promo':'Product & Brand Videos'}
MEDIA = {x['slug']:x for x in json.loads((ROOT/'data/local-media.json').read_text())}
VIDEOS = json.loads((ROOT/'data/videos.json').read_text())
category_ids = {}
for key in CATS:
    content = (ROOT/f'data/categories/{key}.md').read_text()
    for slug in re.findall(r'prompts/([\w-]+)\.md', content): category_ids.setdefault(slug,key)
items=[]
for v in VIDEOS:
    m=MEDIA[v['slug']]
    items.append({'id':v['slug'],'title':v['title'],'author':v['author'],'source':v['post_url'],'category':v['category'],'date':v['posted_at'][:10], 'description':v.get('post_text') or v['title'],'prompt':v.get('prompt') or '', 'poster':m['poster_path'],'video':m['video_path'],'github':f"{REPO}/blob/main/prompts/{v['slug']}.md"})
for p in (ROOT/'data/library').glob('*.json'):
    v=json.loads(p.read_text()); ev=v.get('analysis',{}).get('caseEvidence',{}); ident=p.stem
    prompt=ev.get('prompt',{}).get('englishText') or v.get('promptTranslations',{}).get('en') or ''
    if ev.get('prompt',{}).get('status') not in ('full_original','fragment'): prompt=''
    items.append({'id':ident,'title':ev.get('title') or v.get('summaryEn') or ident,'author':v['post']['author']['username'],'source':v['post']['canonicalUrl'],'category':{'canvas-interactive':'interactive','games-interactive':'interactive','3d-scenes':'3d','blender':'3d','other-animation':'motion','external-video-model':'promo'}.get(v.get('analysis',{}).get('category'),'3d'),'date':v['post']['publishedAt'][:10], 'description':v.get('summary') or '', 'prompt':prompt,'poster':v.get('coverPath') or '', 'video':'','github':f'{REPO}/blob/main/prompts/{ident}.md'})
items.sort(key=lambda x:(x['date'],x['id']),reverse=True)
by_id={x['id']:x for x in items}
selected_ids=['grafikcem-937806','kaif9998-761287','ici-dab-098351','0kncn-543073','kplikethebird-902732','furkancavlakcom-695521','joshvlc-958575','rezait00-767656','higgsfield-ai-490135']
selected=[by_id[x] for x in selected_ids]
hero=selected[0]

def asset(p,prefix='./'):
    return prefix+'assets/source/'+p if p else ''

def page_url(x,prefix='./'):
    return prefix+'prompts/'+x['id']+'/'

def media(x,prefix='./',featured=False):
    poster=asset(x['poster'],prefix)
    if not x['video']:
        return f'<a href="{page_url(x,prefix)}"><img src="{E(poster)}" alt="" width="800" height="500" loading="lazy"></a>' if poster else '<div class="catalog-placeholder">Fable 5.2</div>'
    video=asset(x['video'],prefix)
    return f'''<a href="{page_url(x,prefix)}" tabindex="-1" aria-hidden="true"><img src="{E(poster)}" alt="" width="800" height="500" loading="lazy"></a><video class="card-video" data-card-video="{'spotlight' if featured else 'hover'}" data-prompt-id="{E(x['id'])}" data-src="{E(video)}" muted playsinline loop preload="none" aria-hidden="true"></video><button class="play" data-prompt-id="{E(x['id'])}" aria-label="Preview {E(x['title'])}" data-preview="{E(video)}" data-poster="{E(poster)}" data-title="{E(x['title'])}" data-link="{page_url(x,prefix)}" data-repo-link="{E(x['github'])}"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 3l12 7-12 7z" fill="currentColor"/></svg><span>Play preview</span></button>'''

def card(x,prefix='./',mode='catalog',featured=False):
    title=E(x['title']); cat=E(CATS[x['category']]); desc=E(x['description'][:190]); id=E(x['id'])
    badge='<div class="editor-pick">Editor’s pick</div>' if featured else ''
    return f'''<article class="card{' card-featured' if featured else ''}" data-prompt-id="{id}" data-card data-mode="{mode}" data-category="{x['category']}" data-new="{str(x['date']>='2026-11-10').lower()}" data-search="{E((x['title']+' '+x['author']+' '+CATS[x['category']]).lower())}"{' hidden' if mode=='catalog' and prefix=='./' else ''}><div class="card-media">{media(x,prefix,featured)}</div><div class="card-info">{badge}<div class="card-top"><span>{cat}</span><span class="tool">{'Public prompt' if x['prompt'] else 'Prompt not published'}</span></div><h3><a href="{page_url(x,prefix)}">{title}</a></h3><p>{desc}</p><div class="card-bottom"><a href="{E(x['source'])}">@{E(x['author'])} ↗</a><a href="{E(x['github'])}" data-placement="catalog-prompt">View details on GitHub ↗</a></div></div></article>'''

def document(title,description,body,path='',image=None):
    prefix='../'*len([p for p in path.split('/') if p]) or './'
    canonical=BASE+path
    image=image or hero['poster']
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="repository-url" content="{REPO}"><title>{E(title)} | Leadde Open Lab</title><meta name="description" content="{E(description[:155])}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description[:155])}"><meta property="og:image" content="{BASE}assets/source/{E(image)}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/prompts.js" defer></script><script src="{prefix}assets/site.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="header"><div class="wrap"><a class="brand" href="{prefix}" aria-label="Leadde Open Lab home"><img src="{prefix}assets/leadde-logo.png" width="106" height="27" alt="Leadde"><span>Open Lab</span></a><nav class="nav" aria-label="Main navigation"><a class="nav-secondary" href="{prefix}#collection">Collection</a><a class="nav-secondary" href="{prefix}#how-to-use">How to use</a><a class="github" href="{REPO}">GitHub ↗</a></nav></div></header><main id="main">{body}</main><footer class="footer"><div class="wrap"><div class="footer-top"><span>An open collection by <a href="https://leadde.ai">Leadde</a>.</span><div class="footer-links"><a href="{REPO}">GitHub ↗</a><a href="{REPO}/issues/new">Suggest a correction</a><a href="https://leadde.ai">Leadde.ai ↗</a></div></div><p class="footer-note">Videos and prompts are credited to their original creators. Prompt availability follows the source repository.</p></div></footer><dialog class="dialog" data-preview-dialog aria-labelledby="preview-title"><div class="dialog-bar"><h2 id="preview-title">Creator preview</h2><button class="dialog-close" data-close aria-label="Close preview">×</button></div><video controls muted playsinline loop preload="none" aria-label="Creator video preview"></video><div class="dialog-foot"><span>Creator video preview</span><div class="dialog-actions"><a class="text-link" data-preview-repo-link href="{REPO}">View details on GitHub ↗</a><a class="text-link" data-preview-link href="{prefix}">Details →</a></div></div><div data-star-hint hidden></div><pre id="preview-prompt" hidden></pre></dialog></body></html>'''

def write(path,html):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html,encoding='utf-8')

if OUT.exists(): shutil.rmtree(OUT)
shutil.copytree(SITE/'assets',OUT/'assets')
shutil.copytree(SITE/'public',OUT,dirs_exist_ok=True)
(OUT/'assets/source').mkdir(parents=True)
for x in items:
    for key in ('poster','video'):
        source=x[key]
        if source and (ROOT/source).is_file():
            dest=OUT/'assets/source'/source;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/source,dest)
write('assets/prompts.js','window.sitePrompts = '+json.dumps({x['id']:x['prompt'] for x in items},ensure_ascii=False).replace('<','\\u003c')+';')
counts={k:sum(x['category']==k for x in items) for k in CATS}
filters='<button class="filter" data-filter="all" aria-pressed="true">All categories</button>'+''.join(f'<button class="filter" data-filter="{k}" aria-pressed="false">{v} <small>{counts[k]}</small></button>' for k,v in CATS.items())
hero_media=asset(hero['poster']);hero_video=asset(hero['video'])
hero_html=f'''<section class="hero"><div class="hero-copy"><div class="eyebrow">Fable 5.2, in motion</div><h1>Claude Fable <span>Video Prompts</span> &amp; Animation Examples</h1><p>Explore creator-shared Fable 5.2 videos, animation, 3D worlds and interactive projects. Watch the work and find the original prompt when available.</p><div class="actions"><a class="button" href="#collection">Explore the collection <span>↓</span></a><a class="text-link" href="{REPO}">View on GitHub <span>↗</span></a></div><p class="hero-note">{len(items)} creator examples · {len(CATS)} collections.<br>Curated by Leadde Open Lab.</p></div><div class="hero-art"><div class="hero-picture"><a href="{page_url(hero)}"><img src="{hero_media}" alt="Fable 5.2 launch animation" width="800" height="500" fetchpriority="high"></a><video class="hero-video" data-hero-video data-prompt-id="{hero['id']}" data-src="{hero_video}" muted playsinline loop preload="none" aria-hidden="true"></video><button class="hero-pause" data-hero-toggle hidden>Pause preview</button><span class="corner-label">FEATURED VIDEO</span></div><div class="hero-caption"><div><strong>{E(hero['title'])}</strong><p>By @{E(hero['author'])} · Fable 5.2</p></div><a href="{E(hero['github'])}" class="text-link">View prompt on GitHub ↗</a></div></div></section>'''
selected_html=''.join(card(x,mode='selected',featured=i<3) for i,x in enumerate(selected))
all_html=''.join(card(x) for x in items)
topics=''.join(f'<article class="topic"><div class="topic-number">0{i+1} / COLLECTION</div><h3>{v}</h3><p>{counts[k]} examples from Fable 5.2 creators.</p><a class="text-link" href="./collections/{k}/">Explore collection <span>↗</span></a></article>' for i,(k,v) in enumerate(CATS.items()))
public=[x for x in selected if x['prompt']][:3]
examples=''.join(f'''<article class="card prompt-example"><div class="card-media">{media(x)}</div><div class="card-info"><div class="card-top"><span>{E(CATS[x['category']])}</span></div><h3>{E(x['title'])}</h3><p>{E(x['description'][:160])}</p><div class="prompt-block"><div class="prompt-header"><span>Creator’s shared prompt</span><button class="copy" data-copy="home-{x['id']}" data-prompt-id="{x['id']}">Copy prompt</button></div><pre id="home-{x['id']}">{E(x['prompt'])}</pre></div><p class="prompt-credit"><a href="{E(x['source'])}">Original post by @{E(x['author'])} ↗</a></p><div class="dialog-actions"><a class="text-link" href="{E(x['github'])}">View on GitHub ↗</a><a class="text-link" href="{page_url(x)}">Details →</a></div></div></article>''' for x in public)
body=f'''<div class="wrap">{hero_html}<div class="index-strip"><span>Fable 5.2 video &amp; animation prompts</span><span>{len(items)} library examples · {sum(bool(x['prompt']) for x in items)} shared prompts</span><span>Original creators, always credited</span></div><section class="collection" id="collection"><nav class="collection-nav" aria-label="Browse prompts"><button class="filter" data-browse="selected" aria-pressed="true">Selected examples</button><button class="filter" data-browse="latest" aria-pressed="false">Latest additions</button><button class="filter" data-browse="all" aria-pressed="false">All examples</button></nav><div class="section-heading"><div><div class="kicker">Selected work</div><h2>Fable 5.2 in the hands of creators.</h2><p>Start with our picks, then explore the full library.</p><p class="catalog-meta">Library updated <time>{json.loads((ROOT/'data/catalog.json').read_text())['updated_at']}</time></p></div><label class="search"><span class="sr-only">Search the full library</span><input data-search type="search" placeholder="Search videos, creators…"></label></div><div class="filters"><div class="filter-options" role="group" aria-label="Filter by collection">{filters}</div><span class="result-count" data-count aria-live="polite">9 examples</span></div><div class="grid showcase-grid">{selected_html}{all_html}</div><button class="button load-more" data-more hidden>Show more examples</button><p class="no-results" data-empty hidden>No matching examples.</p><div class="collection-bottom"><p>Every example links to its creator and source details.</p><a class="text-link" href="{REPO}#browse-the-full-library">Browse on GitHub ↗</a></div></section><section class="collection prompt-examples" id="prompt-examples"><div class="section-heading"><div><div class="kicker">Copy a prompt</div><h2>Three Fable 5.2 prompts to explore.</h2><p>These prompts were shared publicly by their creators.</p></div></div><div class="grid">{examples}</div></section></div><section class="topics"><div class="wrap"><div class="kicker">A closer look</div><h2>Explore five creative directions.</h2><div class="topic-grid">{topics}</div></div></section><div class="wrap"><section class="how" id="how-to-use"><div class="how-intro"><div class="kicker">From prompt to project</div><h2>How to use Fable 5.2 prompts.</h2><p>Open a case, check whether the creator published a prompt, and review the original post and required tools.</p></div><div class="steps"><div><div class="step-number">01</div><h3>Find an example</h3><p>Browse by category or search for a creator or project.</p></div><div><div class="step-number">02</div><h3>Read the source</h3><p>Open the creator’s post and the repository detail page for context.</p></div><div><div class="step-number">03</div><h3>Make your version</h3><p>When a prompt is public, adapt its inputs and test it in your own coding workspace.</p></div></div></section><section class="closing"><div><h2>Keep a few good ideas close.</h2><p>Explore the complete Fable 5.2 collection on GitHub.</p></div><a class="button light" href="{REPO}">View on GitHub <span>↗</span></a></section></div>'''
write('index.html',document('Fable 5.2 Video Prompts & Animation Examples','Creator-shared Fable 5.2 videos, prompts, animation, 3D worlds and interactive projects.',body))
pages=['']
for key,name in CATS.items():
    group=[x for x in items if x['category']==key]
    path=f'collections/{key}/'
    body=f'''<div class="wrap"><div class="page-head"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../">Collection</a><span>/</span><span>{E(name)}</span></nav><div class="eyebrow">{len(group)} examples</div><h1>{E(name)} with Fable 5.2</h1><p>Explore creator examples, videos and original sources.</p><a class="text-link" href="{REPO}/blob/main/data/categories/{key}.md">Browse this category on GitHub ↗</a></div><section class="collection"><div class="grid">{''.join(card(x,'../../') for x in group)}</div></section></div>'''
    write(path+'index.html',document(f'{name} — Fable 5.2','Fable 5.2 creator examples and prompts.',body,path));pages.append(path)
for x in items:
    path=f"prompts/{x['id']}/"; prefix='../../'; poster=asset(x['poster'],prefix)
    player=f'<video class="detail-video" data-prompt-id="{E(x["id"])}" controls muted playsinline preload="none" poster="{E(poster)}" src="{E(asset(x["video"],prefix))}" aria-label="Creator video"></video>' if x['video'] else f'<img class="detail-video" src="{E(poster)}" alt="{E(x["title"])}">'
    prompt=f'<section class="prompt-block" id="prompt"><div class="prompt-header"><h2>The shared prompt</h2><button class="copy" data-copy="prompt-text" data-prompt-id="{E(x["id"])}">Copy prompt</button></div><pre id="prompt-text">{E(x["prompt"])}</pre></section>' if x['prompt'] else '<section class="prompt-block"><h2>Prompt not published</h2><p>The creator did not publish a reusable prompt for this example.</p></section>'
    body=f'''<div class="wrap"><div class="page-head"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../">Collection</a><span>/</span><a href="../../collections/{x['category']}/">{E(CATS[x['category']])}</a><span>/</span><span>Example</span></nav><div class="eyebrow">Fable 5.2</div><h1>{E(x['title'])}</h1><p>{E(x['description'][:300])}</p></div><div class="detail"><div class="detail-main">{player}<div class="media-caption"><span>Creator preview</span><a href="{E(x['source'])}">Original post by @{E(x['author'])} ↗</a></div>{prompt}</div><aside class="detail-sidebar" aria-label="Source notes"><section class="side-section"><h2>About this example</h2><div class="meta-row"><span>Creator</span><span>@{E(x['author'])}</span></div><div class="meta-row"><span>Category</span><span>{E(CATS[x['category']])}</span></div><div class="meta-row"><span>Published</span><span>{x['date']}</span></div><div class="meta-row"><span>Prompt</span><span>{'Public' if x['prompt'] else 'Not published'}</span></div></section><section class="side-section"><h2>Source</h2><p><a href="{E(x['github'])}">Repository detail ↗</a></p><p><a href="{E(x['source'])}">Original creator post ↗</a></p></section></aside></div></div>'''
    write(path+'index.html',document(x['title'],x['description'],body,path,x['poster']));pages.append(path)
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE+p}</loc></url>\n' for p in pages)+'</urlset>')
write('sitemap.txt',''.join(BASE+p+'\n' for p in pages))
write('.nojekyll','')
print(f'Built {len(pages)} pages from {len(items)} Fable examples')
