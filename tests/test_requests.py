"""Hermetic customer-flow tests. Every external request is intercepted; no leads are sent."""
import json, os, unittest
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from lxml import html
from playwright.sync_api import sync_playwright

BASE=os.environ.get('TWC_TEST_URL','http://127.0.0.1:8010')
ROOT=Path(__file__).resolve().parents[1]
class StaticInventory(unittest.TestCase):
 def test_public_inventory(self):
  import xml.etree.ElementTree as ET
  from collections import Counter
  urls=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
  self.assertEqual(len(urls),93)
  for url in urls:
   path=urlparse(url).path.lstrip('/') or 'index.html';s=(ROOT/path).read_text();d=html.fromstring(s)
   self.assertEqual(d.xpath('string(//link[@rel="canonical"]/@href)'),url,path)
   self.assertEqual(len(d.xpath('//form[@id="service-request"]')),1,path)
   self.assertFalse(d.xpath('//*[@id="pdfBtn" or @id="shareBtn" or @id="ov"]'),path)
   self.assertFalse(d.xpath('//script[contains(@src,"quote.js") or contains(@src,"q3d")]'),path)
   ids=d.xpath('//@id');self.assertTrue(all(n==1 for n in Counter(ids).values()),path)
   for script in d.xpath('//script[@type="application/ld+json"]/text()'):json.loads(script)
   for href in d.xpath('//a/@href'):
    if href.startswith('#') and len(href)>1:self.assertIn(href[1:],ids,path+href)
 def test_homepage_sequence(self):
  d=html.fromstring((ROOT/'index.html').read_text())
  headings=[' '.join(x.itertext()).strip() for x in d.xpath('//main//h2')]
  self.assertEqual(headings[:3],['Choose the service you need','Real properties. Careful work.','Tell Tony what your property needs'])
  self.assertFalse(d.xpath('//*[@id="screen-options"]'))
  self.assertEqual(len(d.xpath('//*[@id="work"]//img')),4)
  self.assertEqual(len(html.fromstring((ROOT/'screen-repair.html').read_text()).xpath('//*[@id="screen-options"]//*[@data-screen-package]')),3)

class BrowserRequests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=sync_playwright().start()
 @classmethod
 def tearDownClass(cls):cls.p.stop()
 def open(self,engine='chromium',device=None,hub='success',spree='success'):
  opts={'headless':True}
  if engine=='chromium':opts['executable_path']='/usr/bin/chromium';opts['args']=['--no-sandbox']
  if engine=='webkit' and os.environ.get('TWC_WEBKIT_EXECUTABLE'):opts['executable_path']=os.environ['TWC_WEBKIT_EXECUTABLE']
  browser=getattr(self.p,engine).launch(**opts);self.addCleanup(browser.close)
  context=browser.new_context(**(self.p.devices[device] if device else {'viewport':{'width':1440,'height':1000}}));page=context.new_page()
  self.posts=[];self.errors=[];self.events=[]
  page.on('pageerror',lambda error:self.errors.append(str(error)))
  def route(r):
   u=r.request.url
   if u.startswith(BASE+'/assets/request.js'):
    # Stub only the OS protocol launch boundary, which cannot open a real phone/email app in headless tests.
    source=(ROOT/'assets/request.js').read_text().replace('location.href=href;','window.__gateDrafts.push(href);')
    r.fulfill(status=200,content_type='application/javascript',body=source);return
   if u.startswith(BASE):r.continue_();return
   if '/website-intake' in u or 'formspree.io/f/' in u:
    body=r.request.post_data_json;self.posts.append((u,body));mode=hub if '/website-intake' in u else spree
    if mode=='network':r.abort('failed');return
    if mode=='error':r.fulfill(status=503,content_type='application/json',body='{"ok":false}');return
    if mode=='generic':reply={'ok':True}
    elif mode=='wrong_id':reply={'ok':True,'receipt_status':'received','inquiry_id':'wrong'}
    else:reply={'ok':True,'receipt_status':'received','inquiry_id':body['hub_ref']}
    r.fulfill(status=200,headers={'Access-Control-Allow-Origin':'*'},content_type='application/json',body=json.dumps(reply));return
   r.abort('blockedbyclient')
  context.route('**/*',route)
  page.add_init_script('window.__gateDrafts=[];window.dataLayer=[];window.gtag=(...args)=>window.dataLayer.push(args);')
  page.goto(BASE+'/index.html');page.locator('#service-request').wait_for();return page
 def fill(self,page):
  page.locator('input[name="services"][value="win"]').check();page.locator('input[name="services"][value="scr"]').check()
  page.locator('#rq-name').fill('Synthetic Request Test');page.locator('#rq-phone').fill('202-555-0147');page.locator('#rq-email').fill('synthetic@example.invalid');page.locator('#rq-address').fill('Hesperia 92345');page.locator('#rq-notes').fill('Synthetic request for browser verification only.');page.locator('#rq-consent').check()
 def test_desktop_form_receipts_and_privacy(self):
  page=self.open();self.fill(page);page.locator('#rq-send').click();page.wait_for_url('**/request-received.html')
  self.assertIn('Your request was received',page.locator('h1').inner_text());self.assertEqual(len(self.posts),2)
  self.assertEqual(self.posts[0][1]['hub_ref'],self.posts[1][1]['hub_ref']);self.assertEqual(self.posts[0][1]['services'],['win','scr'])
  self.assertNotIn('Synthetic',page.url);stored=page.evaluate('Object.values(sessionStorage).join(" ")');self.assertNotIn('Synthetic',stored);self.assertFalse(self.errors)
 def test_failure_never_success(self):
  page=self.open(hub='error',spree='network');self.fill(page);page.locator('#rq-send').click();page.wait_for_function('document.querySelector("#rq-error").textContent.includes("Receipt could not")')
  self.assertTrue(page.url.endswith('/index.html'));self.assertTrue(page.locator('#rq-send').is_enabled());self.assertEqual(page.locator('#rq-name').input_value(),'Synthetic Request Test')
  first=[p['hub_ref'] for _,p in self.posts];page.locator('#rq-send').click();page.wait_for_function('document.querySelector("#rq-send").disabled===false');self.assertEqual(set(first),{p['hub_ref'] for _,p in self.posts});self.assertFalse(self.errors)
 def test_generic_ok_and_wrong_id_not_persistence(self):
  for mode in ['generic','wrong_id']:
   page=self.open(hub=mode,spree='error');self.fill(page);page.locator('#rq-send').click();page.wait_for_function('document.querySelector("#rq-error").textContent.includes("Receipt could not")');self.assertTrue(page.url.endswith('/index.html'))
 def test_formspree_fallback_honest_pending(self):
  page=self.open(hub='error');self.fill(page);page.locator('#rq-send').click();page.wait_for_url('**/request-received.html');self.assertIn('synchronization has not been confirmed',page.locator('#receipt-detail').inner_text())
 def test_hub_fallback_honest_email_failure(self):
  page=self.open(spree='error');self.fill(page);page.locator('#rq-send').click();page.wait_for_url('**/request-received.html');self.assertIn('email copy was not confirmed',page.locator('#receipt-detail').inner_text())
 def test_screen_return_validation_and_packages(self):
  page=self.open();page.goto(BASE+'/screen-repair.html');page.locator('[data-screen-package="2"]').click();self.assertEqual(page.locator('#rq-screen-package').input_value(),'2');self.assertTrue(page.locator('#rq-screen-return').is_visible());page.locator('#rq-return-mode').select_option('request')
  self.fill(page);page.locator('input[name="services"][value="win"]').uncheck();page.locator('#rq-send').click();self.assertIn('return date after pickup',page.locator('#rq-error').inner_text());self.assertFalse(self.posts)
  pickup=(date.today()+timedelta(days=10)).isoformat();returned=(date.today()+timedelta(days=12)).isoformat();page.locator('#rq-requested_date').fill(pickup);page.locator('#rq-screen_return_date').fill(returned);page.locator('#rq-send').click();page.wait_for_url('**/request-received.html');self.assertEqual(self.posts[0][1]['screen_return_date'],returned);self.assertFalse(self.errors)
 def test_draft_without_consent_saves_nothing(self):
  page=self.open();self.fill(page);page.locator('#rq-consent').uncheck();page.locator('#rq-email-action').click(no_wait_after=True);self.assertFalse(self.posts);self.assertIn('No callback request was saved',page.locator('#rq-status').inner_text());self.assertTrue(page.locator('#rq-open-draft').get_attribute('href').startswith('mailto:twindowclean@gmail.com'))
 def test_handoff_capture_then_form_same_id(self):
  page=self.open();self.fill(page);page.locator('#rq-email-action').click(no_wait_after=True);page.wait_for_function('document.querySelector("#rq-status").textContent.includes("Callback request saved")');self.assertEqual(len(self.posts),1);self.assertEqual(self.posts[0][1]['kind'],'email_handoff');self.assertTrue(page.evaluate('window.__gateDrafts[0]').startswith('mailto:twindowclean@gmail.com'))
  first=self.posts[0][1]['hub_ref'];page.locator('#rq-send').click();page.wait_for_url('**/request-received.html');self.assertEqual({p['hub_ref'] for _,p in self.posts},{first});self.assertEqual([p['kind'] for _,p in self.posts if '/website-intake' in _],['email_handoff','form'])
 def test_handoff_capture_failure_does_not_claim_sent(self):
  page=self.open(hub='error');self.fill(page);page.locator('#rq-text').click(no_wait_after=True);page.wait_for_function('document.querySelector("#rq-error").textContent.includes("not confirmed")');self.assertTrue(page.locator('#rq-open-draft').is_visible());self.assertIn('sms:+17145590300',page.locator('#rq-open-draft').get_attribute('href'));self.assertNotIn('saved',page.locator('#rq-status').inner_text())
 def test_refresh_retry_and_changed_request(self):
  page=self.open(hub='error',spree='error');self.fill(page);page.locator('#rq-send').click();page.wait_for_function('!document.querySelector("#rq-send").disabled');first=self.posts[0][1]['hub_ref']
  page.reload();self.fill(page);page.locator('#rq-send').click();page.wait_for_function('!document.querySelector("#rq-send").disabled');self.assertEqual(self.posts[2][1]['hub_ref'],first)
  page.locator('#rq-notes').fill('A changed synthetic request.');page.locator('#rq-send').click();page.wait_for_function('!document.querySelector("#rq-send").disabled');self.assertNotEqual(self.posts[4][1]['hub_ref'],first)
  stored=page.evaluate('JSON.stringify(sessionStorage)');self.assertNotIn('Synthetic',stored);self.assertNotIn('2025550147',stored)
 def test_analytics_excludes_customer_details(self):
  page=self.open(hub='error',spree='error');self.fill(page);page.locator('#rq-send').click();page.wait_for_function('!document.querySelector("#rq-send").disabled');events=page.evaluate('JSON.stringify(window.dataLayer)')
  for private in ['Synthetic Request Test','2025550147','synthetic@example.invalid','Hesperia 92345','Synthetic request for browser verification only.']:self.assertNotIn(private,events)
 def test_mobile_validation_field_clear_of_fixed_header(self):
  page=self.open('webkit','iPhone 13');page.set_viewport_size({'width':320,'height':812});self.fill(page);page.locator('#rq-email').fill('invalid-address');page.locator('#rq-send').click()
  bounds=page.locator('#rq-email').bounding_box();nav=page.locator('#nav').bounding_box();self.assertGreater(bounds['y'],nav['y']+nav['height']+8);self.assertTrue(page.locator('#rq-email').evaluate('(el)=>el===document.activeElement'));self.assertFalse(self.errors)
 def test_device_layouts_and_webkit(self):
  for engine,device in [('chromium','iPhone 13'),('chromium','Pixel 7'),('webkit','iPhone 13'),('webkit',None)]:
   page=self.open(engine,device);self.fill(page)
   self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(engine,device));self.assertFalse(self.errors,(engine,device))
   self.assertTrue(page.locator('#rq-text' if device else '#rq-send').evaluate('(el)=>el.classList.contains("request-primary")'))
   page.locator('#rq-send').click();page.wait_for_url('**/request-received.html');self.assertFalse(self.errors)
 def test_direct_confirmation_not_false_success(self):
  page=self.open();page.goto(BASE+'/request-received.html');self.assertEqual(page.locator('h1').inner_text(),'Check your service request')
 def test_keyboard_validation(self):
  page=self.open();page.locator('#rq-send').focus();page.keyboard.press('Enter');self.assertIn('Choose at least one',page.locator('#rq-error').inner_text());self.assertTrue(page.locator('input[name="services"]').first.evaluate('(el)=>el===document.activeElement'));self.assertFalse(self.posts)

if __name__=='__main__':unittest.main(verbosity=2)
