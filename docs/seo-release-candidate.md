# November 20 SEO release candidate — implementation record

One release against `main` at `3ae392605bd4a336ab5930cce071e8f167a5e9bc` (November 10). Branch: `codex/seo-release-candidate-2026-11-20`. Production release requires owner authorization; no merge or deployment is part of this assignment.

Sources: owner-supplied **Organic Search and Lead Audit, November 18, 2026**, especially pp. 2, 5–13 and URL inventory pp. 14–20; **Phase 1 Review and Test Kit**, README, patch 05, city fixtures and `verify_content.py`. The current repository is the exact kit baseline. Live read-only GET checks on November 20 found all 93 published sitemap URLs HTTP 200 and byte-identical to that revision. HTTP/www root redirects lead to HTTPS; an unknown path returns 404. The kit's prior content work is reused, not recreated. Patches 01–04 (database, edge intake, Hub and receipt attribution) are excluded.

## Single implementation tracker

Primary intents: Hesperia/Victorville screen visitors need torn insect mesh repaired or a missing/bent frame replaced, with pickup and installation. Residential/Apple Valley/Jess Ranch visitors need a clear exterior-versus-interior cleaning estimate and access arrangements. Commercial visitors need storefront/office scope and a recurring/site-visit quote. Pigeon visitors need exclusion scope, safe access and a defensible cost estimate.

States: **COMPLETE** = implemented and verified; **PARTIAL** = implemented but incomplete; **OPEN** = verified problem requiring action; **BLOCKED** = missing evidence/access/authorization; **DEFERRED** = not worthwhile in this release. “Before” preserves the actual starting state; “RC” describes this candidate, not production. P1 is highest priority. No private customer records are stored here.

| Item / source files | Before → RC | Priority | Evidence / action | Verification |
| --- | --- | --- | --- | --- |
| Crawl/index foundation: `robots.txt`, `CNAME`, `sitemap.xml`, canonical tags | COMPLETE → COMPLETE | P1 | Audit p.5: 93 indexed, no manual actions, no unindexed discovery backlog. Live URLs match main. Preserve infrastructure; remove only unsupported offer from sitemap. | Live status/content comparison; full inventory and canonical tests. |
| Pricing/packages/two appointments: `assets/request.js`, `assets/request.css`, `screen-repair.html` | COMPLETE → COMPLETE | P1 | Nov.8–10 commits already implement $53.99 standard, $64.99 all-weather, $84.99 custom frame, $149 screen-only floor, requested pickup/return and owner confirmation. Retain runtime and prices. | Existing screen package/return validation test; baseline form/script comparison. |
| Unsupported door offers: patch05's HTML files, `sliding-door-screen-repair.html`, `sitemap.xml` | OPEN → COMPLETE | P1 | Audit pp.9–10 and existing patch05 identify rollers/tracks, door pricing and nine linking pages. Reuse patch05; replace active references with legitimate window-screen scope. | Unchanged kit checker scans all active visible copy, metadata, alt text and JSON-LD; no links to retired URL. |
| Retired door URL: `sliding-door-screen-repair.html` | OPEN → COMPLETE | P1 | Window-only service is not an equivalent door service. Keep accurate noindex/follow retirement notice with window-service and phone links; self-canonical, no offer schema. GitHub Pages has no configured per-path 410 facility. | Removed only this sitemap URL (93→92); noindex and no inbound marketing links tested. It remains a 200 notice until an owner-approved hosting/status change. |
| Hesperia window screens: `screen-repair-hesperia.html` | PARTIAL → COMPLETE | P1 | 178 impressions/0 clicks; previous title, door claims and generic location copy obscure intent. Clarify window insect mesh versus frames, qualified starting prices/minimum, mobile pickup/return and written scope; retain kit's completed 13-screen combined-job example. | Title/opening/FAQ/offer review; kit city assertions; local crawl and mobile tests. |
| Victorville window screens: `screen-repair-victorville.html` | PARTIAL → COMPLETE | P1 | 115 impressions/0 clicks. Same scope corrections; retain documented 10-new-frame/all-weather project and separate painting-preparation example from kit, without implying one combined job. | Same city/pricing/two-visit checks; unchanged form and explicit other-town photo captions. |
| Screen case photographs: both city pages | BLOCKED → BLOCKED | P2 | Kit documents project wording but does not link these cases to specific city-authenticated photos. Existing portfolio images explicitly remain from other towns. | No new image assets or city relabeling. Owner must supply matching permissioned photo provenance before adding case photos. |
| Onsite promises: `all-weather-mesh.html`, `screen-repair.html`, `screen-repair-{adelanto,apple-valley,oak-hills,phelan}.html`, `crestline.html`, `wrightwood.html` | PARTIAL → COMPLETE | P1 | Inherited snippets/FAQ/offer descriptions contradict approved two-visit screen-only process. Replace immediate onsite promises and qualify eligibility/minimum. | Visible/schema review; all non-schema scripts and form markup unchanged. |
| Frame price comparison: `screen-replacement.html` | OPEN → COMPLETE | P1 | Existing “$10 cheaper” conflicts with published package differences; “built at the truck” implies immediate fabrication. Use actual package prices and neutral custom-fit heading. | Same visible FAQ and JSON-LD answer; kit pricing checks. |
| Mesh benefits: `all-weather-mesh.html`, `reparacion-de-mosquiteros.html`, `screen-repair.html` | PARTIAL → COMPLETE | P2 | Preserve supported material/shading explanation and view/light/airflow tradeoffs; no pet-proof or energy-savings promise. Remove numerical 80% claim where specific manufacturer sheet is unavailable. | English/Spanish copy review; no numeric shading claim retained in changed material copy. |
| Product specification for numerical shading claims | BLOCKED → BLOCKED | P2 | Supplied kit contains no product-specific manufacturer sheet. Do not invent a brand/model or convert shading into utility savings. | Require exact installed product and supporting specification before restoring a percentage. |
| Residential intent: `window-cleaning.html` | PARTIAL → COMPLETE | P1 | 119 impressions/2 clicks. Explain hand detailing, eligible exterior starting price, interior/add-on/oversize access, cleaning versus repair/restoration. Replace blanket cloudy-glass diagnosis with assessment. | Canonical, one H1, changed FAQ visible/schema match, form preservation and mobile checks. |
| Apple Valley / Jess Ranch: `window-cleaning-apple-valley.html`, `apple-valley.html` | PARTIAL → COMPLETE | P1 | Service page 10/0; hub 145/1; “window cleaning apple valley” query 74/1. Prioritize cleaning intent, qualified pricing, access/gate details and reciprocal estimate links. Remove demographic filler and unsupported customer-frequency claims. Jess Ranch remains a section. | Links/fragments and changed FAQ tests; no new pages, unverified jobs or new local photo labels. |
| New Apple Valley/Jess Ranch job example | BLOCKED → BLOCKED | P2 | No permissioned, documented case supplied for this scope. Existing photographs retained with their established captions. | Owner-confirmed scope/location/permission required before publication. |
| Homepage identity/pathways: `index.html` | PARTIAL → COMPLETE | P1 | Existing Hesperia identity and four service cards already work. Put Hesperia in title/owner-operated opening and add direct commercial site-visit path; preserve slogan, four cards and photo sequence. | Existing homepage sequence test, local links and mobile menu checks. |
| Hesperia commercial: `commercial-window-cleaning-hesperia.html` | PARTIAL → COMPLETE | P2 | 89 impressions/0 clicks. Clarify storefront/office search intent, eligible 8–10-pane price, site visit, access, arranged after-hours and recurring options; remove unsupported same-day/generalized street promises. Existing amounts/discounts retained. | Matching visible FAQ/Service data, office/storefront links, identical form/runtime. |
| Completed commercial case / Riverside quote | BLOCKED → BLOCKED | P2 | Audit establishes a historical quote, not completion/payment or publication permission. Do not market it as a completed job. | Confirm outcome/permission in private business records before any case content. |
| Review-reading CTA: `index.html`, `pigeon-proofing.html` | OPEN → COMPLETE | P1 | “Read” links opened `/review` composer. Point reading CTAs to existing entity URL; preserve intentional writing CTAs. | Reading/writing destination distinction tested. |
| Pigeon “See all services”: `pigeon-proofing.html` | OPEN → COMPLETE | P1 | `/#services` is absent. Link to existing `/#g02-pillars-title`. | Full local fragment crawl. |
| Bird-mesh cost: `solar-panel-bird-mesh-cost.html` | OPEN → COMPLETE | P1 | Cost page denies story-height price effect; main pigeon page explicitly adds $125. Align opening, examples, FAQ and offer with existing $450/12, +$50/panel, +$125 two-story pricing; mark examples as calculations, not invoices. Replace stale nonexistent calculator CTA. | Formula/manual checks against `pigeon-proofing.html`; matching FAQ; links/mobile; no pricing rule changed. |
| Bird-mesh scope/warranty: `solar-panel-bird-mesh-cost.html` | PARTIAL → COMPLETE | P2 | Remove universal panel-warranty guarantee; use system-specific clip compatibility and manufacturer/lease review. Clarify affected-area cleanup versus whole-roof wash and first-visit offer eligibility. Main pigeon already includes scope/warranty explanation and real portfolio. | Visible copy/schema match; existing workmanship terms and photos preserved. |
| New San Jacinto/29-panel exclusion case; `solar-panel-bird-mesh-cost.html`, `inland-empire.html` | BLOCKED → BLOCKED | P2 | Audit contains owner-recalled historical amounts; materials/permissions/source linkage not fully established. No new invoice-derived story or photo relabeling. | Verify actual scope, panel count, provenance and permission first. |
| Fontana/travel/price guarantees: `pigeon-proofing-fontana.html`, regional hubs | BLOCKED → BLOCKED | P2 | Audit calls for reconciling existing same-price/no-trip claims with actual route economics. No confirmed replacement policy provided. | Owner confirms current route/quote policy before changing an established offer. |
| Neutral-service form defaults: `pricing.html`, `service-areas.html`, `contact.html`, `reviews.html` | COMPLETE → DEFERRED | P3 | Forms already function and support changing service selection. Audit proposes neutral defaults; this task requires preserving established customer workflows. Do not change preselection or intake. | All defaults/form DOM and receipt code remain baseline-identical. |
| Solar scope / repeat routes: `solar-panel-cleaning.html`, `solar-cleaning-maintenance-plan.html`, city solar pages | PARTIAL → DEFERRED | P3 | Existing service pages and intake retained. Additional route/content expansion has lower demonstrated opportunity than priority pages; no new availability or universal warranty claims added. | Existing links, canonical/schema syntax and form preservation included in full-site checks. |
| Other inventory suggestions: audit pp.14–20 (`about.html`, city hubs, specialist/maintenance/Spanish/commercial/solar/roof pages) | PARTIAL → DEFERRED | P3 | Apply inherited unsupported screen corrections where present; leave other functioning copy and route-specific expansions for evidence of demand and documented jobs. No new town pages or repeated masterplan. | All 92 canonical pages still reachable, no new orphan pages or broken assets. |
| Mobile/performance infrastructure: `style.css`, `main.js`, images/fonts | COMPLETE → COMPLETE | P2 | Audit mobile Lighthouse 91/LCP 2.1s/CLS 0; desktop 100. Responsive images and authentic photography already present. No new library, scripts, images or performance rewrite needed. | Chromium/WebKit viewport checks; prior Lighthouse is a historical lab baseline, not a new field-speed result. |
| Search/AI readability: changed priority HTML | PARTIAL → COMPLETE | P2 | Core intent, scope, price qualifications, examples and FAQ answers are server-served text. Keep legitimate business entity and standard schema. | No-JavaScript mobile checks; JSON-LD parses, changed FAQ answers appear in visible HTML. |
| GA4 and receipt-attribution proposal: kit patches01–04, `assets/tags.js`, `assets/request.js` | BLOCKED → BLOCKED | P1 | Explicit owner hold overrides prior kit analytics sequence. No GA4, key event, Hub, SQL, edge, email delivery or campaign changes. | Baseline byte checks for scripts/form/runtime; no account writes. Offline tests intercept external services. |
| Private November15 record reconciliation | BLOCKED → BLOCKED | P1 | Audit establishes conflicting scheduled/unconfirmed statuses; current signed customer agreement was not supplied for this website release. Do not infer booking or contact customer. | Owner reconciles latest agreement privately; count only confirmed bookings in scorecard. |
| External profiles/citations | BLOCKED → BLOCKED | P2 | External writes explicitly excluded; Bing publication pending. Only the bounded handoff below applies. | No external account mutations; owner verifies outcomes separately. |
| New locations, speculative AI schema, extra tracking, backlinks | DEFERRED → DEFERRED | P3 | No first-party demand/proof warrants broad expansion. No artificial reviews, lead submissions or purchased links. | Diff contains content, tests and this record only. |

## External handoff — no account changes made

- **Verified Google Business Profile:** remove unsupported sliding-screen-door/hardware wording from services and description, consistent with window-only website scope. Preserve the established review-owning entity, primary category, Hesperia service-area identity, existing phone `714-559-0300` and `https://twindowclean.com/`. Keep the residential address private. Confirm actual hours/holiday exceptions and route availability before changing them. Audit p.8 establishes the verified profile and a second verification-required manager record; it does **not** establish a public duplicate. Do not create another listing or remove the verified one.
- **Bing Places:** publication was pending. Check status through the existing account when appropriate; preserve its verification and do not restart it. After publication, review existing name/phone/site/service scope for consistency.
- **Yelp:** existing claimed Hesperia listing and prior removal decision are documented in kit `evidence/platform-sources.md`. No new appeal outcome is established. Review public business identity and respond only with owner-approved wording; do not solicit Yelp reviews or repeat an unsupported removal request.
- **Other citations/community mentions:** use the same real business identity and Hesperia base; correct an observed mismatch through its existing account. No specific new citation discrepancy is proven here, so no bulk listing creation or backlink campaign is proposed. Keep genuine Google review invitations distinct from reading links and consistent with platform rules.

## Measurement at 28 and 56 days after the authorized release

Set **R** to actual production release date, not PR creation. Export existing Search Console Web/Search data at page level for R through R+27 and R+28 through R+55, allowing reporting lag; compare both with the immediately preceding 28 days, and show the cumulative 56 days. No GA4 setup change is needed. Record the November19 Meta campaign and actual website release date as context; never classify an inquiry as organic merely because it arrived after this release.

| Field | Existing evidence / baseline | 28-day and 56-day entry |
| --- | --- | --- |
| Search impressions | Aug18–Nov15: 3,788 vs 756 previous 90 days | Per priority URL + property total, matched 28-day comparison and cumulative 56 days. |
| Organic search clicks | 107 vs 16; 64 from two brand spellings | Same URL/date filters; branded/nonbranded queries only where GSC exposes them. Do not allocate undisclosed queries. |
| CTR by priority page | Hesperia screens 178/0 (0%); Victorville screens 115/0 (0%); residential 119/2 (1.68%); AV hub 145/1 (0.69%); AV glass 10/0 (0%); Hesperia commercial 89/0 (0%); pigeon 28/2 (7.14%); bird-mesh cost 17/0 (0%) | Impressions, clicks, and clicks÷impressions together; provisional at low volume. Historic values are 90-day baselines, not invented pre-release 28-day values. Export the latter at release. |
| Qualified inquiries | Exact organic total unresolved; use existing inbox/phone/business records | Deduplicate genuine inquiries privately. Offered service + workable location, with service/city and verified source when available. Tap/draft/duplicate is not a lead. |
| Confirmed bookings | Exact organic total unresolved; website label alone does not identify organic | Customer and owner agreed to a date or recurring arrangement; scheduled/unconfirmed conflict stays pending until reconciled. Deduplicate by actual job. |
| Revenue by verified source | No defensible organic revenue baseline supplied | Record collected revenue from confirmed business records linked to a verified source; track booked value separately. No inferred organic revenue from date/channel coincidence. |
| Unknown-source inquiries | Historic job extract: 42/67 blank sources (jobs, **not** an inquiry-rate baseline) | Separate count/share of unknown-source inquiries, bookings and revenue. Use unknown unless existing evidence or genuine customer report establishes source. |

Priority URL filters: `/screen-repair-hesperia.html`, `/screen-repair-victorville.html`, `/window-cleaning.html`, `/window-cleaning-apple-valley.html`, `/apple-valley.html`, `/commercial-window-cleaning-hesperia.html`, `/pigeon-proofing.html`, `/solar-panel-bird-mesh-cost.html`. Monitor historical HTTP and preferred HTTPS homepage reports separately. Record raw counts; low-volume changes do not establish causation or guaranteed ranking/AI visibility.

## Review and verification

- Reused the kit's content checker **unchanged** as `tests/verify_phase1_content.py`. Repeat with an untouched baseline checkout: `python tests/verify_phase1_content.py /path/to/baseline .`.
- Existing architecture remains static GitHub Pages; no build or new production dependency. `python -m unittest discover -s tests -p test_seo.py -v` runs offline crawl, retirement, FAQ and preservation checks. `python -m unittest discover -s tests -p test_requests.py -v` uses a local server at `http://127.0.0.1:8010` (override `TWC_TEST_URL`), Playwright, lxml and Chromium/WebKit. All remote services are intercepted; no real leads or analytics calls are sent.
- Source-level validation covers syntax, schema/visible-content consistency and local reachability; it is not a claim of rich-result eligibility or a fresh live Google validation after release.
- Keep this as one content release. Owner approves merge/release timing. Rollback is a revert of this release commit; it requires the same production authorization. First naturally occurring post-release inquiry can be checked privately against the existing intake, without a test customer submission.

Final results on November 20 (no production submissions):

| Check | Result |
| --- | --- |
| Existing `test_requests.py` | **17/17 PASS**, 107.326 s; includes Chromium/WebKit device emulation, consent, privacy, retry, receipt/failure/fallback and screen appointment flow. |
| `test_seo.py` | **5/5 PASS**, 1.772 s; 92-page graph/resources/canonicals/FAQ and preservation checks. |
| `test_priority_browser.py` | **3/3 PASS**, 99.530 s; nine priority pages across Chromium 320/390/1440px and WebKit 390px (36 renders), working menus, decoded photos, no overflow/page errors, service text without JS. |
| Unmodified kit `verify_phase1_content.py` | **PASS**: 93 baseline URLs vs 92 active RC; 367 JSON-LD blocks; both city examples/prices/minimum/two visits; active form/script markup and robots unchanged. SHA-256 of reused checker: `e9c93055609877339e2df3ab6977d1e0ff8cc165d350fa577341f801e29236c5`. |
| `git diff --check` | **PASS**. |
| Live baseline comparison | **93/93 HTTP200 and byte-identical** to audited main; redirect and unknown-404 behavior preserved. |

The first browser run had two environment-only WebKit launch errors (missing system libraries). Final runs passed using the standard Playwright browser plus local extracted libraries via `TWC_WEBKIT_EXECUTABLE=/workspace/evidence/run_webkit.sh`; no production dependency was added. Browser/device emulation does not test physical devices or native SMS/email app delivery. Nine mobile screenshots were captured; screen and Apple Valley layouts were visually reviewed. Raw logs/screenshots/live hashes remain outside this public repository in `/workspace/evidence/`.

### Exact changed-file manifest

33 files: 26 active HTML pages, one retired-offer HTML notice, sitemap, four test files and this record. No images, stylesheets or executable website scripts changed.


```text
all-weather-mesh.html
apple-valley.html
big-bear-lake.html
cajon-pass.html
commercial-window-cleaning-hesperia.html
contact.html
crestline.html
docs/seo-release-candidate.md
gallery.html
index.html
pigeon-proofing.html
pricing.html
reparacion-de-mosquiteros.html
running-springs.html
screen-repair-adelanto.html
screen-repair-apple-valley.html
screen-repair-hesperia.html
screen-repair-oak-hills.html
screen-repair-phelan.html
screen-repair-victorville.html
screen-repair.html
screen-replacement.html
sitemap.xml
sliding-door-screen-repair.html
solar-panel-bird-mesh-cost.html
spring-valley-lake.html
tests/test_priority_browser.py
tests/test_requests.py
tests/test_seo.py
tests/verify_phase1_content.py
window-cleaning-apple-valley.html
window-cleaning.html
wrightwood.html
```
