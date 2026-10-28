#!/usr/bin/env python3
"""Local static release checks; no external requests or payments."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,hashlib,base64,html,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
pages=json.loads((ROOT/'site-pages.json').read_text())
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
for key,info in pages.items():
 file=ROOT/('index.html' if key=='home' else info['path'].strip('/')+'/index.html');text=file.read_text();p=Scan();p.feed(text)
 ids=[a['id'] for t,a in p.tags if 'id' in a];assert len(ids)==len(set(ids)),(key,'duplicate IDs')
 canonical=next(a['href'] for t,a in p.tags if t=='link' and a.get('rel')=='canonical');assert canonical=='https://calledtogoministry.org'+info['path']
 assert html.unescape(re.search(r'<title>(.*?)</title>',text)[1])==info['title']
 panels=[a for t,a in p.tags if t=='section' and a.get('class')=='tab-panel' and 'hidden' not in a];assert [a['id'] for a in panels]==['panel-'+key]
 links=[a for t,a in p.tags if t=='a' and a.get('data-tab')];assert len(links)==8;assert next(a['data-tab'] for a in links if a.get('aria-selected')=='true')==key
 for a in links:assert a['href']==pages[a['data-tab']]['path']
 policy=next(a['content'] for t,a in p.tags if t=='meta' and a.get('http-equiv')=='Content-Security-Policy')
 script_policy=policy.split('script-src ')[1].split(';')[0];assert 'unsafe-inline' not in script_policy and 'unsafe-eval' not in script_policy
 for attrs,script in re.findall(r'<script([^>]*)>(.*?)</script>',text,re.S):
  token='sha256-'+base64.b64encode(hashlib.sha256(script.encode()).digest()).decode();assert token in script_policy,(key,'stale script hash')
  if 'ld+json' in attrs:assert json.loads(script)['@context']=='https://schema.org'
 for tag,attrs in p.tags:
  for name in ['src','poster']:
   value=attrs.get(name,'')
   if value and not value.startswith(('https:','data:')):assert (ROOT/value.lstrip('/')).is_file(),(key,'missing asset',value)
  href=attrs.get('href','')
  if href.startswith('/'):
   parts=urlsplit(href);target=ROOT/(parts.path.lstrip('/') or 'index.html')
   if target.is_dir():target=target/'index.html'
   assert target.is_file(),(key,'broken link',href)
   if parts.fragment:assert ('id="'+unquote(parts.fragment)+'"') in target.read_text(),(key,'broken fragment',href)
 assert not re.search(r'\son(?:load|click|error)=',text),(key,'inline handler')
 print('PASS',info['path'],'canonical, active content, crawlable navigation, schema, CSP hashes and local links')
sitemap=ET.parse(ROOT/'sitemap.xml');locs=[x.text for x in sitemap.findall('.//{*}loc')];assert set(locs)=={'https://calledtogoministry.org'+p['path'] for p in pages.values()}
assert 'Manually emailed within 2 working days' in (ROOT/'book/index.html').read_text()
print('PASS sitemap coverage and pre-rendered book content')
