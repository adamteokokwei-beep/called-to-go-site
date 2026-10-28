#!/usr/bin/env python3
"""Build crawlable static entry pages and script hashes from the home index.
Edit index.html + site-pages.json, then run python3 build_pages.py.
The custom domain serves this repository at its root; no build runs on visitors.
"""
from pathlib import Path
import re,json,hashlib,base64,html
ROOT=Path(__file__).resolve().parent
PAGES=json.loads((ROOT/'site-pages.json').read_text())
ORIGIN='https://calledtogoministry.org'
source=(ROOT/'index.html').read_text()
source=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>\n?','',source)
# Refresh the metadata used by the instant tab navigation from the same source.
source=re.sub(r'var SITE_PAGES = .*?;\nvar yrEl',lambda m:'var SITE_PAGES = '+json.dumps(PAGES,ensure_ascii=False)+';\nvar yrEl',source,count=1)
SOCIAL=['https://www.facebook.com/profile.php?id=61584538259532','https://www.tiktok.com/@tin.grace.teo','https://www.instagram.com/randomqinqin/','https://www.youtube.com/@TeoTinGrace']

def structured(key):
 person={'@type':'Person','@id':ORIGIN+'/#christine','name':'Christine Grace Masiba Cabason','alternateName':'Christine Cabason','url':ORIGIN+'/her-story/','image':ORIGIN+'/img/37399b22fb9d.webp','jobTitle':'Worship leader, prayer minister and missionary','homeLocation':{'@type':'Place','name':'Johor Bahru, Malaysia'},'sameAs':SOCIAL}
 org={'@type':'Organization','@id':ORIGIN+'/#ministry','name':'Called to Go Ministry','url':ORIGIN+'/','logo':ORIGIN+'/images/favicon-192.png','sameAs':SOCIAL}
 web={'@type':'WebSite','@id':ORIGIN+'/#website','name':'Called to Go Ministry','url':ORIGIN+'/','inLanguage':'en','publisher':{'@id':org['@id']}}
 page={'@type':'WebPage','@id':ORIGIN+PAGES[key]['path']+'#webpage','url':ORIGIN+PAGES[key]['path'],'name':PAGES[key]['title'],'description':PAGES[key]['description'],'isPartOf':{'@id':web['@id']},'about':{'@id':person['@id']},'inLanguage':'en'}
 graph=[org,person,web,page]
 if key=='book':
  book={'@type':'Book','@id':ORIGIN+'/book/#called-to-go','name':'Called to Go','author':{'@id':person['@id']},'bookFormat':'https://schema.org/EBook','inLanguage':'en','url':ORIGIN+'/book/','image':ORIGIN+'/images/book-cover.jpg','offers':{'@type':'Offer','price':'4.99','priceCurrency':'USD','url':ORIGIN+'/book/','availability':'https://schema.org/InStock'}}
  graph.append(book);page['mainEntity']={'@id':book['@id']}
 if key=='songs':
  music={'@type':'MusicRecording','@id':ORIGIN+'/songs/#everyday-is-christmas','name':'Everyday Is Christmas (每一天是圣诞节)','byArtist':{'@id':person['@id']},'inLanguage':'zh','url':ORIGIN+'/songs/','sameAs':'https://www.youtube.com/shorts/guNQ0ZcwlE8'}
  graph.append(music);page['mainEntity']={'@id':music['@id']}
 if key=='story':page['mainEntity']={'@id':person['@id']}
 return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,separators=(',',':'))

def render(key):
 page=PAGES[key];s=source
 s=re.sub(r'<title>.*?</title>','<title>'+html.escape(page['title'])+'</title>',s,count=1)
 for pattern,value in [(r'(<meta name="description" content=")[^"]*',page['description']),(r'(<meta property="og:title" content=")[^"]*',page['title']),(r'(<meta name="twitter:title" content=")[^"]*',page['title']),(r'(<meta property="og:description" content=")[^"]*',page['description']),(r'(<meta name="twitter:description" content=")[^"]*',page['description']),(r'(<meta property="og:url" content=")[^"]*',ORIGIN+page['path']),(r'(<link rel="canonical" href=")[^"]*',ORIGIN+page['path'])]:
  s=re.sub(pattern,lambda m:m[1]+html.escape(value,quote=True),s,count=1)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda m:'<script type="application/ld+json">'+structured(key)+'</script>',s,count=1,flags=re.S)
 for k in PAGES:
  pattern=r'(<section class="tab-panel" id="panel-'+k+r'"[^>]*)(>)'
  s=re.sub(pattern,lambda m:re.sub(r'\s+hidden(?=\s|$)','',m[1])+(' hidden' if k!=key else '')+m[2],s,count=1)
  pattern=r'(<a class="tab-btn[^>]*data-tab="'+k+r'"[^>]*aria-selected=")[^"]*(")'
  s=re.sub(pattern,lambda m:m[1]+('true' if k==key else 'false')+m[2],s,count=1)
 # All inline executable scripts require exact hashes; no unsafe-inline/eval for scripts.
 hashes=[]
 for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',s,re.S):
  hashes.append("'sha256-"+base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()+"'")
 policy="default-src 'self'; script-src 'self' "+' '.join(hashes)+"; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://i.ytimg.com; media-src 'self'; connect-src 'self' https://called-to-go-chatbot.adamteokokwei.workers.dev; frame-src https://www.youtube-nocookie.com; object-src 'none'; base-uri 'self'; form-action 'self' https://www.paypal.com"
 s=s.replace('<meta charset="utf-8">','<meta charset="utf-8">\n<meta http-equiv="Content-Security-Policy" content="'+policy+'">',1)
 return s

for key,page in PAGES.items():
 target=ROOT/('index.html' if key=='home' else page['path'].strip('/')+'/index.html')
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(render(key))
# Only canonical, real addresses belong in the sitemap (no hash sections).
urls='\n'.join('  <url><loc>'+ORIGIN+p['path']+'</loc></url>' for p in PAGES.values())
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'\n</urlset>\n')
print('Built',len(PAGES),'static entry pages with canonical metadata and CSP hashes.')
