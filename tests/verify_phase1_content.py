"""Offline audit of the staged public site. Accepts unmodified and patched checkout paths."""
import sys,json,re
from pathlib import Path
from urllib.parse import urlparse,unquote
from lxml import html,etree
old,new=map(Path,sys.argv[1:3]); base='https://twindowclean.com'
def sitemap(folder):
 return etree.parse(str(folder/'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
def doc(folder, url):
 return html.fromstring((folder / (urlparse(url).path.lstrip('/') or 'index.html')).read_text())
urls=sitemap(new);oldurls=sitemap(old);retired=base+'/sliding-door-screen-repair.html'
assert len(set(urls))==len(urls)==92 and set(oldurls)-set(urls)=={retired}
assert oldurls==list(dict.fromkeys(oldurls)) and len(oldurls)==93
assert 'noindex' in doc(new,retired).xpath('string(//meta[@name="robots"]/@content)')
assert (old/'robots.txt').read_bytes()==(new/'robots.txt').read_bytes()
scope=re.compile(r'sliding[- ]screen[- ]door|sliding[- ]door[- ]screen|rollers? (?:and|or)|track straightening|oversize screens, doors|\$107\.98|\$129\.98|mosquiteros? de puerta corrediza',re.I)
changed=[];schemas=0
for url in urls:
 a=doc(old,url);b=doc(new,url);file=urlparse(url).path.lstrip('/') or 'index.html'
 if (new/file).read_bytes()!=(old/file).read_bytes():changed.append(file)
 assert b.xpath('//link[@rel="canonical"]/@href')==[url],file
 assert len(b.xpath('//h1'))==1 and len(b.xpath('//meta[@name="viewport"]'))==1,file
 assert 'noindex' not in str(b.xpath('//meta[@name="robots"]/@content')),file
 assert len(b.xpath('//form[@id="service-request"]'))==1,file
 assert etree.tostring(a.xpath('//form[@id="service-request"]')[0],method='html')==etree.tostring(b.xpath('//form[@id="service-request"]')[0],method='html'),file
 scripts=lambda d:[(el.get('src'),el.text) for el in d.xpath('//script[not(@type="application/ld+json")]')]
 assert scripts(a)==scripts(b),file
 assert b.xpath('//a[starts-with(@href,"tel:")]'),file
 assert not any('sliding-door-screen-repair.html' in h for h in b.xpath('//a/@href')),file
 for src in b.xpath('//script[@type="application/ld+json"]/text()'):
  json.loads(src);schemas+=1;assert not scope.search(src),(file,'schema')
 for t in b.xpath('//body//text()[not(ancestor::style or ancestor::script)]|//img/@alt|//meta/@content'):
  assert not scope.search(str(t)),(file,str(t)[:180])
 for el in b.xpath('//ul[@class="work-strip"]'):
  assert int(el.get('data-n'))==len(el.xpath('./li')),(file,'gallery count')
for city,n in [('hesperia',13),('victorville',10)]:
 d=doc(new,base+'/screen-repair-'+city+'.html')
 text=' '.join(' '.join(d.xpath('//main//text()[not(ancestor::script or ancestor::style)]')).split())
 assert str(n) in text and 'all-weather' in text and 'separate return' in text
 assert all(x in text for x in ('$53.99','$64.99','$84.99','$149'))
 before=d.xpath('//section[@id="quote"]/preceding::h2/text()')
 assert any(('Hesperia home' in h or 'screen preparation in Victorville' in h) for h in before)
 assert '"scr"' in d.xpath('string(//*[@id="quote"]/@data-default-services)')
 assert d.xpath('//button[@id="rq-send"]') and d.xpath('//button[@id="rq-text"]')
 for src in d.xpath('//img/@src|//link[@rel="stylesheet"]/@href|//script[@src]/@src'):
  if not urlparse(src).netloc:assert (new/unquote(urlparse(src).path.lstrip('/'))).is_file(),src
 assert not any('hub-screen-repair-01' in a or 'sliding-screen-door' in a for a in d.xpath('//img/@src'))
print('PASS 93 published URLs compared with 92 proposed URLs; a single door offer retired and no internal links to it.')
print('PASS All 92 active pages: self-canonical, viewport, one H1, identical form markup and script elements, telephone CTA, valid gallery counts.')
print('PASS',schemas,'structured-data blocks parsed; no flagged door service/price references in body, image descriptions, metadata or structured data.')
print('PASS Both city pages: correct minimum and packages, two visits, verified case ahead of form, screen preselection, phone and form controls, local assets present.')
print('PASS robots.txt identical. Updated active HTML:',len(changed),'pages. Retired HTML: 1. Combined:',len(changed)+1)
