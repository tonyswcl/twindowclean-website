"""Offline release checks. No network requests or customer submissions.

Preservation comparisons use the audited main revision (override TWC_SEO_BASE_REF
only when deliberately establishing a new reviewed baseline).
"""
import json
import os
import subprocess
import unittest
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://twindowclean.com'
BASE_REF = os.environ.get('TWC_SEO_BASE_REF', '3ae392605bd4a336ab5930cce071e8f167a5e9bc')
RETIRED = '/sliding-door-screen-repair.html'


def baseline(path):
    return subprocess.check_output(['git', 'show', f'{BASE_REF}:{path}'], cwd=ROOT)


def document(path):
    return html.fromstring((ROOT / path).read_bytes())


def normalized(text):
    return ' '.join(text.split())


def faqs(doc):
    result = {}
    for source in doc.xpath('//script[@type="application/ld+json"]/text()'):
        schema = json.loads(source)
        if schema.get('@type') == 'FAQPage':
            for question in schema['mainEntity']:
                result[question['name']] = question['acceptedAnswer']['text']
    return result


class SeoRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.urls = etree.parse(str(ROOT / 'sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
        cls.paths = {urlparse(u).path: urlparse(u).path.lstrip('/') or 'index.html' for u in cls.urls}
        cls.docs = {url: document(path) for url, path in cls.paths.items()}

    def test_crawl_graph_and_resources(self):
        self.assertEqual(len(self.urls), len(set(self.urls)))
        edges = {}
        for path, doc in self.docs.items():
            self.assertEqual(doc.xpath('//link[@rel="canonical"]/@href'), [BASE + path], path)
            self.assertEqual(len(doc.xpath('//h1')), 1, path)
            self.assertFalse(doc.xpath('//meta[@name="robots" and contains(@content,"noindex")]'), path)
            ids = doc.xpath('//@id')
            self.assertEqual(len(ids), len(set(ids)), path)
            edges[path] = set()
            refs = doc.xpath('//a/@href|//img/@src|//script/@src|//link/@href')
            for srcset in doc.xpath('//img/@srcset|//source/@srcset'):
                refs.extend(part.strip().split()[0] for part in srcset.split(','))
            for ref in refs:
                target = urlparse(urljoin(BASE + path, ref))
                if target.netloc != 'twindowclean.com' or target.scheme not in ('http', 'https'):
                    continue
                local = unquote(target.path).lstrip('/') or 'index.html'
                self.assertTrue((ROOT / local).is_file(), (path, ref))
                if target.path in self.docs:
                    edges[path].add(target.path)
                    if target.fragment:
                        self.assertIn(unquote(target.fragment), self.docs[target.path].xpath('//@id'), (path, ref))
        reached, pending = set(), deque(['/'])
        while pending:
            current = pending.popleft()
            if current not in reached:
                reached.add(current)
                pending.extend(edges.get(current, set()) - reached)
        self.assertEqual(set(self.docs) - reached, set(), 'Orphaned canonical pages')

    def test_only_unsupported_offer_retired(self):
        old = etree.fromstring(baseline('sitemap.xml')).xpath('//*[local-name()="loc"]/text()')
        self.assertEqual(set(old) - set(self.urls), {BASE + RETIRED})
        self.assertEqual(set(self.urls) - set(old), set())
        retired = document(RETIRED.lstrip('/'))
        self.assertEqual(retired.xpath('//meta[@name="robots"]/@content'), ['noindex,follow'])
        self.assertFalse(retired.xpath('//script[@type="application/ld+json"]'))
        for path, doc in self.docs.items():
            self.assertFalse(any(RETIRED in ref for ref in doc.xpath('//a/@href')), path)

    def test_forms_scripts_and_intake_infrastructure_preserved(self):
        for path, doc in self.docs.items():
            old = html.fromstring(baseline(self.paths[path]))
            for xpath in ('//form[@id="service-request"]', '//script[not(@type="application/ld+json")]', '//section[@id="quote"]/@data-default-services'):
                serialize = lambda d: [etree.tostring(x, method='html') if isinstance(x, etree._Element) else x for x in d.xpath(xpath)]
                self.assertEqual(serialize(doc), serialize(old), (path, xpath))
        for path in ('robots.txt', 'CNAME', 'assets/request.js', 'assets/request.css', 'assets/tags.js', 'main.js', 'style.css'):
            self.assertEqual((ROOT / path).read_bytes(), baseline(path), path)

    def test_changed_faq_answers_visible_and_structured_data_parseable(self):
        for path, doc in self.docs.items():
            for source in doc.xpath('//script[@type="application/ld+json"]/text()'):
                json.loads(source)
            old = faqs(html.fromstring(baseline(self.paths[path])))
            visible = normalized(' '.join(doc.xpath('//body//text()[not(ancestor::script or ancestor::style)]')))
            for question, answer in faqs(doc).items():
                self.assertIn(normalized(question), visible, (path, question))
                if old.get(question) != answer:
                    self.assertIn(normalized(answer), visible, (path, question))

    def test_reading_and_writing_reviews_are_distinct(self):
        for filename in ('index.html', 'pigeon-proofing.html'):
            doc = document(filename)
            reading = doc.xpath('//a[contains(.,"Read our Google reviews")]/@href')
            writing = doc.xpath('//a[contains(.,"Leave a review")]/@href')
            self.assertTrue(reading, filename)
            self.assertTrue(writing, filename)
            self.assertTrue(all('/review' not in ref for ref in reading), filename)
            self.assertTrue(all(ref.endswith('/review') for ref in writing), filename)


if __name__ == '__main__':
    unittest.main(verbosity=2)
