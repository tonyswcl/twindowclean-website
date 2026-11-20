"""Homeowner guides (/blog/): structure, links, images and claims. Offline, needs lxml."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urljoin, urlparse

from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://twindowclean.com'
BLOG = ROOT / 'blog'
# Claims the site may not make until Tony confirms the product and terms (see the private repo _seo/system/d-writing-standard.md).
BANNED = [r'\b\d+\s?% (?:of )?(?:solar )?(?:heat|glare|UV)', r'warranty (?:stays|remains) intact', r'(?<!not )\bpet-proof\b',
          r'—', r'–']


class Blog(unittest.TestCase):
    def pages(self):
        return sorted(p for p in BLOG.glob('*.html') if not p.name.startswith('_'))

    def test_index_and_articles_in_sitemap(self):
        locs = etree.parse(str(ROOT / 'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
        for page in self.pages():
            self.assertIn(f'{BASE}/blog/{page.name}', locs, page.name)

    def test_each_page(self):
        for page in self.pages():
            doc = html.fromstring(page.read_bytes())
            name = f'/blog/{page.name}'
            self.assertEqual(doc.xpath('//link[@rel="canonical"]/@href'), [BASE + name], name)
            self.assertEqual(len(doc.xpath('//h1')), 1, name)
            title = doc.xpath('//title/text()')[0]
            self.assertLessEqual(len(title), 70, name)
            desc = doc.xpath('//meta[@name="description"]/@content')[0]
            self.assertLessEqual(len(desc), 160, name)
            for source in doc.xpath('//script[@type="application/ld+json"]/text()'):
                data = json.loads(source)
                self.assertNotIn('aggregateRating', json.dumps(data), name)
            for img in doc.xpath('//main//img'):
                self.assertTrue(img.get('alt'), (name, img.get('src')))
                self.assertTrue(img.get('width') and img.get('height'), (name, img.get('src')))
            for ref in doc.xpath('//main//a/@href'):
                target = urlparse(urljoin(BASE + name, ref))
                self.assertEqual(target.netloc, 'twindowclean.com', (name, ref, 'no links to other businesses'))
                self.assertTrue((ROOT / (target.path.lstrip('/') or 'index.html')).is_file(), (name, ref))
            text = ' '.join(doc.xpath('//main//text()'))
            for pattern in BANNED:
                self.assertIsNone(re.search(pattern, text, re.I), (name, pattern))

    def test_index_links_every_article(self):
        index = html.fromstring((BLOG / 'index.html').read_bytes())
        linked = set(index.xpath('//main//a/@href'))
        for page in self.pages():
            if page.name != 'index.html':
                self.assertIn(page.name, linked, page.name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
