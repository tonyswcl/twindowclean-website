/* =========================================================
   Tony's Window Cleaning — UI interactions
   Nav, scroll progress, reveals, tilt cards, counters,
   before/after sliders, FAQ. Vanilla JS, no dependencies.
   ========================================================= */
(function () {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Current year ---- */
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---- Navbar scrolled state + scroll progress ---- */
  const nav = $('#nav');
  const progress = $('#scrollProgress');
  function onScroll() {
    const y = window.scrollY;
    if (nav) nav.classList.toggle('scrolled', y > 40);
    if (progress) {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Mobile menu ---- */
  const toggle = $('#navToggle');
  const links = $('#navLinks');
  if (toggle && links) {
    const close = () => {
      links.classList.remove('open');
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    };
    toggle.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      toggle.classList.toggle('active', open);
      toggle.setAttribute('aria-expanded', String(open));
    });
    $$('a', links).forEach((a) => a.addEventListener('click', close));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    // a tap anywhere outside the open menu closes it, the way people expect on a phone
    document.addEventListener('click', (e) => {
      if (links.classList.contains('open') && !links.contains(e.target) && !toggle.contains(e.target)) close();
    });
  }

  /* ---- Reveal on scroll ---- */
  const reveals = $$('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    // threshold must stay 0: a block taller than ~8x the viewport can never
    // reach a fractional threshold, so it would stay at opacity 0 forever.
    }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('in'));
  }

  /* ---- 3D tilt on service cards (pointer, desktop only) ---- */
  if (!reduceMotion && window.matchMedia('(hover:hover) and (pointer:fine)').matches) {
    $$('[data-tilt]').forEach((card) => {
      const max = 9;
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform =
          `perspective(800px) rotateX(${-py * max}deg) rotateY(${px * max}deg) translateY(-6px)`;
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
  }

  /* ---- Animated counters ---- */
  const counters = $$('[data-count]');
  if (counters.length) {
    const animate = (el) => {
      const target = parseFloat(el.dataset.count);
      const dur = 1400;
      const start = performance.now();
      const step = (now) => {
        const p = Math.min((now - start) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toString();
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if ('IntersectionObserver' in window && !reduceMotion) {
      const cio = new IntersectionObserver((entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) { animate(en.target); cio.unobserve(en.target); }
        });
      }, { threshold: 0.5 });
      counters.forEach((c) => cio.observe(c));
    } else {
      counters.forEach((c) => (c.textContent = c.dataset.count));
    }
  }

  /* ---- Before / After sliders ---- */
  $$('[data-ba]').forEach((ba) => {
    const before = $('.ba-before', ba);
    const handle = $('.ba-handle', ba);
    const range = $('.ba-range', ba);
    const set = (val) => {
      const pct = Math.max(0, Math.min(100, val));
      // before layer clipped from the right so dragging reveals the "after"
      before.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
      handle.style.left = pct + '%';
    };
    if (range) {
      range.addEventListener('input', () => set(parseFloat(range.value)));
      set(parseFloat(range.value || 50));
    }
  });

  /* ---- Smooth anchor offset for fixed nav ---- */
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length <= 1) return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - 70;
      window.scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  });

  /* ---- Calls, texts and email inside the Facebook, Instagram and other app browsers ----
     Those browsers often block tel:, sms: and mailto: links, so a tap does nothing. There, the tap opens
     a small sheet instead: the number in big type, a Call button to try, a button to copy the number,
     and how to open the page in the phone's own browser. The first tap is not counted as a contact,
     only a tap on the Call or Text button in the sheet. Normal browsers are untouched. */
  const ua = navigator.userAgent || '';
  const iabApp = /Instagram/i.test(ua) ? 'Instagram'
    : /FBAN|FBAV|FB_IAB|FBIOS|FB4A|Messenger/i.test(ua) ? 'Facebook'
    : /Nextdoor/i.test(ua) ? 'Nextdoor'
    : /musical_ly|Bytedance|TikTok/i.test(ua) ? 'TikTok'
    : /Snapchat/i.test(ua) ? 'Snapchat'
    : /LinkedInApp/i.test(ua) ? 'LinkedIn'
    : /Pinterest/i.test(ua) ? 'Pinterest'
    : /\bLine\//.test(ua) ? 'LINE' : '';
  window.__iab = iabApp;
  if (iabApp) {
    document.documentElement.classList.add('iab');
    const es = /^es/i.test(document.documentElement.lang || '');
    const T = (en, sp) => (es ? sp : en);
    let sheet = null;
    let back = null;
    const hide = () => {
      if (!sheet || sheet.hidden) return;
      sheet.hidden = true;
      if (back && back.focus) back.focus({ preventScroll: true });
    };
    const build = () => {
      sheet = document.createElement('div');
      sheet.className = 'iab-sheet';
      sheet.id = 'iabSheet';
      sheet.hidden = true;
      sheet.innerHTML =
        '<div class="iab-dim" data-x></div>' +
        '<div class="iab-card" role="dialog" aria-modal="true" aria-labelledby="iabT">' +
        '<button type="button" class="iab-x" data-x aria-label="' + T('Close', 'Cerrar') + '">&times;</button>' +
        '<h2 id="iabT"></h2><p class="iab-num" id="iabN"></p>' +
        '<button type="button" class="iab-form" id="iabF" hidden></button>' +
        '<div class="iab-row"><a class="iab-go" id="iabGo" href="#"></a><button type="button" class="iab-cp" id="iabCp"></button></div>' +
        '<p class="iab-ok" id="iabOk" role="status"></p><p class="iab-tip" id="iabTip"></p></div>';
      document.body.appendChild(sheet);
      sheet.addEventListener('click', (e) => { if (e.target.closest('[data-x]')) hide(); });
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });
      $('#iabF', sheet).addEventListener('click', () => {
        hide();
        const f = $('#tq-send');
        if (!f) return;
        window.scrollTo({ top: f.getBoundingClientRect().top + window.scrollY - 70, behavior: 'auto' });
        const first = $$('#fname,#fphone', f).find((x) => !x.value) || $('#sendBtn');
        if (first) first.focus({ preventScroll: true });
      });
      $('#iabCp', sheet).addEventListener('click', () => {
        const num = $('#iabN', sheet);
        const ok = $('#iabOk', sheet);
        const mail = sheet.dataset.kind === 'mail';
        const done = () => { ok.textContent = mail ? T('Copied. Open your email and paste it in the To line.', 'Copiado. Abre tu correo y pégalo en Para.') : T('Copied. Open your Phone or Messages app and paste it.', 'Copiado. Abre tu app de Teléfono o Mensajes y pégalo.'); };
        const pick = () => {
          try {
            const r = document.createRange();
            r.selectNodeContents(num);
            const s = window.getSelection();
            s.removeAllRanges();
            s.addRange(r);
            if (document.execCommand && document.execCommand('copy')) { done(); return; }
          } catch (x) { /* falls through to the hint */ }
          ok.textContent = T('Hold your finger on it and tap Copy.', 'Mantén el dedo encima y toca Copiar.');
        };
        const text = num.textContent;
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, pick);
        else pick();
      });
    };
    const open = (a) => {
      if (!sheet) build();
      back = a;
      const href = a.getAttribute('href') || '';
      const kind = /^tel:/i.test(href) ? 'tel' : /^sms:/i.test(href) ? 'sms' : 'mail';
      let raw = href.replace(/^(tel|sms|mailto):/i, '').split(/[?&]/)[0];
      try { raw = decodeURIComponent(raw); } catch (x) { /* keep it as written */ }
      const d = raw.replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
      const shown = kind === 'mail' ? raw : d.length === 10 ? d.slice(0, 3) + '-' + d.slice(3, 6) + '-' + d.slice(6) : raw;
      const quote = a.id === 'smsA' || a.id === 'mailA';
      sheet.dataset.kind = kind;
      $('#iabT', sheet).textContent = kind === 'tel' ? T('Call Tony', 'Llama a Tony') : kind === 'sms' ? T('Text Tony', 'Mándale texto a Tony') : T('Email Tony', 'Escríbele a Tony');
      $('#iabN', sheet).textContent = shown;
      const go = $('#iabGo', sheet);
      go.href = href;
      go.setAttribute('data-from', a.id || '');
      go.textContent = kind === 'tel' ? T('Call', 'Llamar') : kind === 'sms' ? T('Open Messages', 'Abrir Mensajes') : T('Open email', 'Abrir correo');
      $('#iabCp', sheet).textContent = kind === 'mail' ? T('Copy the email', 'Copiar el correo') : T('Copy the number', 'Copiar el número');
      const form = $('#iabF', sheet);
      form.hidden = !(quote && $('#tq-send'));
      form.textContent = T('Send the form instead. It works right here.', 'Mejor manda el formulario. Funciona aquí mismo.');
      $('#iabOk', sheet).textContent = '';
      const what = kind === 'tel' ? T('calls', 'llamadas') : kind === 'sms' ? T('texts', 'textos') : T('email', 'el correo');
      $('#iabTip', sheet).textContent = T(
        'The ' + iabApp + ' browser sometimes blocks ' + what + '. If nothing happens, copy it, or tap ••• or ⋮ at the top of the screen and choose Open in browser.',
        'El navegador de ' + iabApp + ' a veces bloquea ' + what + '. Si no pasa nada, cópialo, o toca ••• o ⋮ arriba en la pantalla y elige Abrir en el navegador.');
      sheet.hidden = false;
      (form.hidden ? go : form).focus({ preventScroll: true });
    };
    document.addEventListener('click', (e) => {
      const a = e.target.closest && e.target.closest('a[href^="tel:"],a[href^="sms:"],a[href^="mailto:"]');
      if (!a || a.closest('#iabSheet')) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      open(a);
    }, true);
  }

  /* ---- Form: friendly submit feedback (Formspree handles delivery) ---- */
  const form = $('.quote-form');
  if (form) {
    form.addEventListener('submit', () => {
      const btn = $('button[type="submit"]', form);
      if (btn && !form.action.includes('YOUR_FORM_ID')) {
        btn.textContent = 'Sending…';
        btn.disabled = true;
      }
    });
  }
})();
