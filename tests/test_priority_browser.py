"""Rendered priority-page checks. External traffic is blocked; these tests never submit a lead."""
import os
import unittest
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

BASE = os.environ.get('TWC_TEST_URL', 'http://127.0.0.1:8010')
PAGES = [
    'index.html', 'screen-repair-hesperia.html', 'screen-repair-victorville.html',
    'apple-valley.html', 'window-cleaning-apple-valley.html', 'window-cleaning.html',
    'commercial-window-cleaning-hesperia.html', 'pigeon-proofing.html',
    'solar-panel-bird-mesh-cost.html',
]


class PriorityBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()

    @classmethod
    def tearDownClass(cls):
        cls.p.stop()

    def browser(self, engine):
        opts = {'headless': True}
        if engine == 'chromium':
            opts.update(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        elif os.environ.get('TWC_WEBKIT_EXECUTABLE'):
            opts['executable_path'] = os.environ['TWC_WEBKIT_EXECUTABLE']
        browser = getattr(self.p, engine).launch(**opts)
        self.addCleanup(browser.close)
        return browser

    def context(self, browser, **opts):
        context = browser.new_context(**opts)
        self.addCleanup(context.close)
        def route(r):
            if urlparse(r.request.url).netloc == urlparse(BASE).netloc and r.request.method in ('GET', 'HEAD'):
                r.continue_()
            else:
                r.abort('blockedbyclient')
        context.route('**/*', route)
        return context

    def test_priority_layout_navigation_and_images(self):
        for engine, width in [('chromium', 320), ('chromium', 390), ('chromium', 1440), ('webkit', 390)]:
            context = self.context(self.browser(engine), viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            for path in PAGES:
                with self.subTest(engine=engine, width=width, path=path):
                    page.goto(BASE + '/' + path)
                    page.locator('#service-request').wait_for()
                    self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), path)
                    self.assertTrue(page.locator('h1').is_visible())
                    if width < 768:
                        toggle = page.locator('#navToggle')
                        toggle.click()
                        self.assertEqual(toggle.get_attribute('aria-expanded'), 'true')
                        self.assertTrue(page.locator('#navLinks').is_visible())
                        page.keyboard.press('Escape')
                        self.assertEqual(toggle.get_attribute('aria-expanded'), 'false')
                    # Scroll genuine photos into view so lazy-loading failures are checked too.
                    for photo in page.locator('main img').all():
                        photo.scroll_into_view_if_needed()
                        photo.evaluate('(el) => el.decode().catch(() => {})')
                        self.assertTrue(photo.evaluate('(el) => el.complete && el.naturalWidth > 0'), photo.get_attribute('src'))
                    self.assertFalse(errors, (path, errors))
                    screenshots = os.environ.get('TWC_SCREENSHOT_DIR')
                    if screenshots and width == 390 and engine == 'chromium':
                        folder = Path(screenshots)
                        folder.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(folder / (path.removesuffix('.html') + '-mobile.png')), full_page=True)

    def test_service_information_available_without_javascript(self):
        context = self.context(self.browser('chromium'), java_script_enabled=False, viewport={'width': 390, 'height': 900})
        page = context.new_page()
        for path in PAGES:
            with self.subTest(path=path):
                page.goto(BASE + '/' + path)
                self.assertTrue(page.locator('h1').inner_text().strip())
                # The service name, lead and section headings must not rely on JS to become visible.
                hidden = page.locator('main h1, main h2, main .lead, main .tagline').evaluate_all('''els => els.filter(el => {
                    for (let node = el; node; node = node.parentElement) {
                        const css = getComputedStyle(node);
                        if (css.display === 'none' || css.visibility === 'hidden' || Number(css.opacity) === 0) return true;
                    }
                    return false;
                }).map(el => el.textContent.trim())''')
                self.assertEqual(hidden, [], (path, hidden))
                self.assertTrue(page.locator('main a[href^="tel:"]').count(), path)

    def test_city_screen_request_defaults_and_return_fields(self):
        context = self.context(self.browser('chromium'), viewport={'width': 390, 'height': 900})
        page = context.new_page()
        for city in ['hesperia', 'victorville']:
            with self.subTest(city=city):
                page.goto(BASE + '/screen-repair-' + city + '.html')
                self.assertTrue(page.locator('input[name="services"][value="scr"]').is_checked())
                self.assertTrue(page.locator('#rq-text').is_visible())
                page.locator('#rq-return-mode').select_option('request')
                self.assertTrue(page.locator('#rq-screen_return_date').is_visible())
                self.assertEqual(page.locator('input[name="services"]:checked').count(), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
