"""Homeowner guides (/blog/): structure, links, images, social preview, dates and claims. Offline, needs lxml."""
import datetime
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urljoin, urlparse

from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://twindowclean.com'
BLOG = ROOT / 'blog'
# Claims the site may not make (owner decisions; see the private repo _seo/system/d-writing-standard.md).
BANNED = [r'\b\d+\s?% (?:of )?(?:solar )?(?:heat|glare|UV)', r'warranty (?:stays|remains|is) (?:intact|safe|untouched)',
          r'keeps? your warranty', r'voids? most', r'whatever the size of the house', r'for most High Desert roofs',
          r'(?<!not )\bpet-proof\b', r'—', r'–', r'more pigeon calls than anywhere', r'arrays are usually a full day']
# The only outside links a guide may carry: government and Cornell Lab sources it cites. Never other businesses.
SOURCES = {'www.fws.gov', 'www.federalregister.gov', 'www.ecfr.gov', 'www.allaboutbirds.org'}


def local(url):
    return ROOT / (urlparse(url).path.lstrip('/') or 'index.html')


class Blog(unittest.TestCase):
    def pages(self):
        return sorted(p for p in BLOG.glob('*.html') if not p.name.startswith('_'))

    def test_sitemap_lists_exactly_the_published_guides(self):
        locs = etree.parse(str(ROOT / 'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
        listed = {u for u in locs if '/blog/' in u}
        self.assertEqual(listed, {f'{BASE}/blog/{p.name}' for p in self.pages()})

    def test_each_page(self):
        for page in self.pages():
            doc = html.fromstring(page.read_bytes())
            name = f'/blog/{page.name}'
            self.assertEqual(doc.xpath('//link[@rel="canonical"]/@href'), [BASE + name], name)
            self.assertEqual(doc.xpath('//meta[@property="og:url"]/@content'), [BASE + name], name)
            self.assertEqual(len(doc.xpath('//h1')), 1, name)
            title = doc.xpath('//title/text()')[0]
            self.assertLessEqual(len(title), 70, name)
            desc = doc.xpath('//meta[@name="description"]/@content')[0]
            self.assertLessEqual(len(desc), 160, name)
            og_image = doc.xpath('//meta[@property="og:image"]/@content')
            self.assertEqual(len(og_image), 1, name)
            self.assertTrue(og_image[0].startswith(BASE + '/assets/og/') and local(og_image[0]).is_file(), (name, og_image))
            self.assertTrue(doc.xpath('//meta[@property="og:image:width"]/@content') and
                            doc.xpath('//meta[@property="og:image:height"]/@content'), name)
            for source in doc.xpath('//script[@type="application/ld+json"]/text()'):
                data = json.loads(source)
                self.assertNotIn('aggregateRating', json.dumps(data), name)
            for img in doc.xpath('//main//img'):
                self.assertTrue(img.get('alt'), (name, img.get('src')))
                self.assertTrue(img.get('width') and img.get('height'), (name, img.get('src')))
            for ref in doc.xpath('//main//a/@href'):
                target = urlparse(urljoin(BASE + name, ref))
                if target.netloc in SOURCES:
                    self.assertEqual(target.scheme, 'https', (name, ref))
                    continue
                self.assertEqual(target.netloc, 'twindowclean.com', (name, ref, 'no links to other businesses'))
                self.assertTrue((ROOT / (target.path.lstrip('/') or 'index.html')).is_file(), (name, ref))
            text = ' '.join(doc.xpath('//main//text()'))
            for pattern in BANNED:
                self.assertIsNone(re.search(pattern, text, re.I), (name, pattern))
            for para in doc.xpath('//main//p'):
                words = ' '.join(para.text_content().split())
                if '$450' in words and '$50' in words:
                    self.assertIn('$125', words, (name, 'pigeon price rule without the two story charge'))

    def test_article_metadata(self):
        for page in self.pages():
            if page.name == 'index.html':
                continue
            doc = html.fromstring(page.read_bytes())
            name = f'/blog/{page.name}'
            self.assertEqual(doc.xpath('//meta[@property="og:type"]/@content'), ['article'], name)
            articles = [json.loads(s) for s in doc.xpath('//script[@type="application/ld+json"]/text()')]
            articles = [a for a in articles if a.get('@type') in ('Article', 'BlogPosting')]
            self.assertEqual(len(articles), 1, name)
            a = articles[0]
            self.assertEqual(a['headline'], ' '.join(doc.xpath('string(//h1)').split()), name)
            self.assertEqual(a['mainEntityOfPage'], BASE + name, name)
            shown = doc.xpath('//main//time/@datetime')
            self.assertEqual(shown, [a['datePublished']], (name, 'visible date and datePublished differ'))
            datetime.date.fromisoformat(a['datePublished'])
            datetime.date.fromisoformat(a['dateModified'])
            self.assertTrue(a['author']['name'] and a['publisher']['name'], name)
            self.assertTrue(local(a['publisher']['logo']['url']).is_file(), name)
            images = a['image'] if isinstance(a['image'], list) else [a['image']]
            self.assertTrue(images, name)
            for url in images:
                self.assertTrue(url.startswith(BASE + '/') and local(url).is_file(), (name, url))

    def test_index_links_every_article(self):
        index = html.fromstring((BLOG / 'index.html').read_bytes())
        linked = set(index.xpath('//main//a/@href'))
        for page in self.pages():
            if page.name != 'index.html':
                self.assertIn(page.name, linked, page.name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
