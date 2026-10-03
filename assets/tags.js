/* =========================================================
   Tony's Window Cleaning : measurement tags

   This file is loaded on every page, after the content, so adding
   Google Analytics 4 or a Google Ads conversion tag is a one file
   change instead of editing fifty pages.

   HOW TO TURN ON GA4
   1. Create the GA4 property at analytics.google.com and copy the
      Measurement ID. It looks like G-XXXXXXXXXX.
   2. Paste it into GA4_ID below. Nothing else changes.

   HOW TO TURN ON GOOGLE ADS CONVERSION TRACKING
   1. In Google Ads: Goals > Conversions > New conversion action >
      Website. Create two actions: "Phone click" and "Quote form".
   2. Copy the conversion ID (AW-XXXXXXXXX) into ADS_ID and the two
      labels into the matching fields below.
   Phone clicks fire on every tel: link. The form event fires when a
   quote form is submitted, including the new quick quote tool.

   HOW TO TURN ON THE META PIXEL
   Events Manager > Connect data > Web > Meta Pixel. Paste the numeric
   Pixel ID into META_PIXEL_ID. The quick quote then reports Lead when a
   quote is sent, plus custom events like select_service and view_3d.

   HOW TO TURN ON MICROSOFT CLARITY
   clarity.microsoft.com > New project > copy the project ID from the
   setup code and paste it into CLARITY_ID.
   ========================================================= */
(function () {
  'use strict';
  var GA4_ID = 'G-F97LW93P0P';
  var ADS_ID = 'AW-17238956448';
  var ADS_LABEL_PHONE = 'JBCvCJ2-oeEaEKCzlpxA';
  var ADS_LABEL_FORM = '';    // e.g. 'KlMnOpQrSt'
  var META_PIXEL_ID = '';     // e.g. '1234567890123456'
  var CLARITY_ID = '';        // e.g. 'abcd1234ef'

  if (META_PIXEL_ID && !window.fbq) {
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', META_PIXEL_ID);
    window.fbq('track', 'PageView');
  }
  if (CLARITY_ID && !window.clarity) {
    (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,'clarity','script',CLARITY_ID);
  }

  if (!GA4_ID && !ADS_ID) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  if (typeof window.gtag !== 'function') window.gtag = gtag;

  // The base Google tag is in the <head> of every page so Google's detector sees it.
  // Only load and configure here if a page is somehow missing it.
  if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + (GA4_ID || ADS_ID);
    document.head.appendChild(s);
    gtag('js', new Date());
    if (GA4_ID) gtag('config', GA4_ID);
    if (ADS_ID) gtag('config', ADS_ID);
  }

  function conv(label) {
    if (ADS_ID && label) window.gtag('event', 'conversion', { send_to: ADS_ID + '/' + label });
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"]');
    if (!a) return;
    if (GA4_ID) window.gtag('event', 'phone_click', { link_url: a.getAttribute('href') });
    conv(ADS_LABEL_PHONE);
  });

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || !f.classList || !f.classList.contains('quote-form')) return;
    if (GA4_ID) window.gtag('event', 'generate_lead', { form_page: location.pathname });
    conv(ADS_LABEL_FORM);
  });

  // The quick quote tool sends its own GA4 event; this only adds the Ads conversion.
  document.addEventListener('tq:lead', function () { conv(ADS_LABEL_FORM); });
})();
