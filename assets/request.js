/* Service requests: private callback capture and honest external draft handoffs.
   No customer details are put into analytics, page URLs or persistent storage. */
(function () {
  'use strict';
  const form = document.getElementById('service-request');
  if (!form) return;
  const section = document.getElementById('quote');
  const es = document.documentElement.lang.toLowerCase().startsWith('es');
  const tr = (en, sp) => es ? sp : en;
  const intake = 'https://srkzjhuwojfpnilvumid.supabase.co/functions/v1/website-intake';
  const formspree = 'https://formspree.io/f/mdkzdael';
  const $ = (id) => document.getElementById(id);
  const val = (name) => String(form.elements[name]?.value || '').trim();
  const names = {win:'Window cleaning',scr:'Screen repair or replacement',sol:'Solar panel cleaning',pig:'Solar panel pigeon-proofing',hw:'Hard water removal',roof:'Roof soft wash',pw:'Pressure washing',gut:'Gutter cleaning',com:'Commercial glass',pc:'Post-construction cleaning',ad:'Adhesive removal',gr:'Graffiti removal',tb:'Trash bin cleaning'};
  const checks = Array.from(form.querySelectorAll('input[name="services"]'));
  const selected = () => checks.filter((n) => n.checked).map((n) => n.value);
  const phone = () => val('phone').replace(/\D/g,'').replace(/^1(?=\d{10}$)/,'');
  const validPhone = () => /^\d{10}$/.test(phone());
  const validEmail = () => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val('email'));
  const event = (name, attrs = {}) => {
    // Only a fixed event name, selected service codes and channel enter analytics.
    if (typeof window.gtag === 'function') window.gtag('event',name,{...attrs,services:selected().join(','),form_page:location.pathname});
  };
  let touched = false, pending = false, requestId = null, payloadKey = '', hubReceived = false, hubFormReceived = false, formReceived = false;
  const recordedReceipts = new Set();
  const recordReceipt = (channel, attrs) => { if(recordedReceipts.has(requestId))return; recordedReceipts.add(requestId); event('inquiry_received',{channel,...attrs}); event('generate_lead',{method:channel,...attrs}); };
  const uuid = () => {
    if (window.crypto?.randomUUID) return crypto.randomUUID();
    return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g,c=>(Number(c)^crypto.getRandomValues(new Uint8Array(1))[0]&15>>Number(c)/4).toString(16));
  };
  const error = (text) => { $('rq-error').textContent = text; if (text) $('rq-error').focus(); };
  const status = (text) => { $('rq-status').textContent = text; };
  function focusField(node) { node.focus({preventScroll:true}); node.scrollIntoView({block:'center',behavior:'instant'}); }
  function localToday() { return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()); }
  const today = localToday();
  for (const n of form.querySelectorAll('input[type="date"]')) { n.min=today; const limit=new Date(today+'T12:00:00Z');limit.setUTCDate(limit.getUTCDate()+400);n.max=limit.toISOString().slice(0,10); }
  function collect() {
    const services = selected();
    const property = {};
    if (val('stories')) property.stories = Number(val('stories'));
    for (const key of ['windows','screens','panels']) {
      const relevant = key==='windows' ? services.some(s=>['win','com'].includes(s)) : key==='screens' ? services.includes('scr') : services.some(s=>['sol','pig'].includes(s));
      if (relevant && val(key)) property[key] = Number(val(key));
    }
    if (services.includes('scr') && val('screen_package')) property.screen_package = val('screen_package');
    const screenOnly = services.length===1 && services[0]==='scr';
    return {name:val('name'),phone:phone(),email:val('email'),address:val('address'),services,notes:val('notes'),details:val('notes'),requested_date:val('requested_date')||undefined,requested_part:val('requested_part'),secondary_date:val('secondary_date')||undefined,screen_return_mode:screenOnly ? val('screen_return_mode') : undefined,screen_return_date:screenOnly && val('screen_return_mode')==='request' ? val('screen_return_date')||undefined : undefined,screen_return_part:screenOnly && val('screen_return_mode')==='request' ? val('screen_return_part') : undefined,preferred_contact:val('preferred_contact'),property,consent_callback:$('rq-consent').checked,page:location.pathname,lang:es?'es':'en'};
  }
  function summary(p) {
    const out = [tr('SERVICE REQUEST — awaiting Tony’s confirmation','SOLICITUD DE SERVICIO — pendiente de confirmación de Tony'),'',tr('Services: ','Servicios: ')+p.services.map(s=>names[s]).join(', ')];
    for (const [title,key] of [['Name','name'],['Phone','phone'],['Email','email'],['Property','address'],['Project details','notes'],['Preferred date','requested_date'],['Preferred time','requested_part'],['Alternative date','secondary_date'],['Reply by','preferred_contact']]) if(p[key]) out.push(title+': '+p[key]);
    for(const [key,value] of Object.entries(p.property)) out.push(key.replace(/_/g,' ')+': '+value);
    if(p.screen_return_mode) out.push('Screen-only Visit 1: pickup and inspection. Visit 2: return, installation and agreed cleaning; '+(p.screen_return_date ? p.screen_return_date+' '+p.screen_return_part : 'Tony confirms after inspection')+'.');
    out.push('',tr('Requested dates are not confirmed. Please confirm the final scope, price and any deposit in writing.','Las fechas no están confirmadas. Confirma el trabajo, precio final y cualquier depósito por escrito.'));
    return out.join('\n');
  }
  function update() {
    const services = selected();
    for (const n of form.querySelectorAll('[data-for-service]')) n.hidden = !n.dataset.forService.split(' ').some(s=>services.includes(s));
    const screenOnly = services.length===1 && services[0]==='scr';
    $('rq-screen-return').hidden = !screenOnly;
    $('rq-return-fields').hidden = !screenOnly || val('screen_return_mode')!=='request';
    const minimum = val('requested_date') || today;
    $('rq-screen_return_date').min = minimum;
    $('rq-summary').textContent = summary(collect());
  }
  async function payload(kind) {
    const p = collect();
    const identity={...p};delete identity.page;delete identity.lang;
    const key = JSON.stringify(identity);
    if (!requestId || key!==payloadKey) {
      let previous, digest;
      try {
        // A one-way retry token and random reference retain idempotency across a refresh.
        // No entered customer details are stored.
        if (crypto.subtle) digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(key))),n=>n.toString(16).padStart(2,'0')).join('');
        previous=JSON.parse(sessionStorage.getItem('twc-request-retry'));
      }catch(_){}
      requestId=digest && previous?.digest===digest && Date.now()-previous.at<30*60*1000 && /^[0-9a-f-]{36}$/i.test(previous.ref) ? previous.ref : uuid();
      payloadKey=key;hubReceived=false;hubFormReceived=false;formReceived=false;
      if(digest)try{sessionStorage.setItem('twc-request-retry',JSON.stringify({ref:requestId,digest,at:Date.now()}));}catch(_){}
    }
    return {...p,kind,hub_ref:requestId,text_ref:requestId,message:summary(p),quote:p.services.map(s=>names[s]).join(', '),_subject:'Website service request',_replyto:p.email||undefined,_gotcha:val('_gotcha')};
  }
  function validate() {
    if (!selected().length) {error(tr('Choose at least one service.','Elige al menos un servicio.'));focusField(checks[0]);return false;}
    if (!val('name')) {error(tr('Please enter your name.','Escribe tu nombre.'));focusField($('rq-name'));return false;}
    if (!validPhone()) {error(tr('Please enter a 10-digit phone number.','Escribe un número de teléfono de 10 dígitos.'));focusField($('rq-phone'));return false;}
    if (!val('address')) {error(tr('Enter the property address, or city and ZIP.','Escribe la dirección, o ciudad y código postal.'));focusField($('rq-address'));return false;}
    if (val('email') && !validEmail()) {error(tr('Check your email address.','Revisa tu correo electrónico.'));focusField($('rq-email'));return false;}
    if (val('preferred_contact')==='email' && !validEmail()) {error(tr('Add an email address for an email reply.','Agrega un correo para recibir una respuesta por correo.'));focusField($('rq-email'));return false;}
    for (const n of form.querySelectorAll('input[type="number"],input[type="date"]')) {
      if (!n.closest('[hidden]') && n.value && !n.checkValidity()) {error(tr('Check the quantity or requested date. Dates must be today or later.','Revisa las cantidades y fechas. Las fechas deben ser de hoy en adelante.'));focusField(n);return false;}
    }
    if (!$('rq-screen-return').hidden && val('screen_return_mode')==='request' && (!val('screen_return_date') || !val('requested_date') || val('screen_return_date')<=val('requested_date'))) {error(tr('Choose a return date after pickup, or let Tony arrange the return after inspection.','Elige una devolución después de la recogida, o deja que Tony la organice tras la inspección.'));focusField($('rq-return-mode'));return false;}
    if (!$('rq-consent').checked) {error(tr('Please allow Tony to save this service request and contact you.','Permite que Tony guarde esta solicitud y te contacte.'));focusField($('rq-consent'));return false;}
    return true;
  }
  async function post(url,p) {
    const controller = new AbortController();
    const timer = setTimeout(()=>controller.abort(),10000);
    try {
      const response = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(p),signal:controller.signal,keepalive:true});
      if (!response.ok) return false;
      // A positive explicit receipt is required; an empty/malformed response is not proof.
      const body = await response.json();
      return !!body && !body.error && !(body.errors?.length) && (body.ok===true || body.success===true) && (url!==intake || (body.receipt_status==='received' && body.inquiry_id===p.hub_ref));
    } catch (_) { return false; } finally {clearTimeout(timer);}
  }
  function busy(on) {
    pending=on;
    for(const button of form.querySelectorAll('.request-actions button')) button.disabled=on;
    form.setAttribute('aria-busy',String(on));
  }
  form.addEventListener('submit',async function(e) {
    e.preventDefault();if(pending||val('_gotcha'))return;
    error('');if(!validate())return;
    busy(true);const p=await payload('form');status(tr('Sending your request…','Enviando tu solicitud…'));
    const receipt = await Promise.all([hubFormReceived ? true : post(intake,p),formReceived ? true : post(formspree,p)]);
    hubFormReceived=hubFormReceived||receipt[0];hubReceived=hubReceived||receipt[0];formReceived=formReceived||receipt[1];busy(false);
    if (!hubReceived && !formReceived) {status('');error(tr('Receipt could not be confirmed. Your details are still here. Try again, or call/text 714-559-0300.','No se pudo confirmar la recepción. Tus datos siguen aquí. Intenta de nuevo o llama al 714-559-0300.'));event('inquiry_delivery_failed',{channel:'form'});return;}
    recordReceipt('form',{hub_receipt:hubReceived,formspree_receipt:formReceived});
    // Store only receipt flags. Never put customer details in the confirmation URL.
    try {sessionStorage.setItem('twc-request-receipt',JSON.stringify({at:Date.now(),hub:hubReceived,formspree:formReceived}));}catch(_){}
    status(tr('Request received. Your appointment still needs Tony’s confirmation.','Solicitud recibida. Tony aún debe confirmar tu cita.')+(hubReceived?'':tr(' Office synchronization is pending.',' La sincronización de oficina está pendiente.'))+(formReceived?'':tr(' The email copy was not confirmed.',' No se confirmó la copia por correo.')));
    // Navigation is only possible after at least one genuine receipt.
    location.assign('request-received.html');
  });
  async function handoff(channel) {
    if(pending||val('_gotcha'))return;
    error('');$('rq-open-draft').hidden=true;
    busy(true);const p=await payload(channel==='sms'?'sms_handoff':'email_handoff');
    const body=p.message;
    const apple = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform==='MacIntel' && navigator.maxTouchPoints>1);
    const href=channel==='sms'?'sms:+17145590300'+(apple?'&':'?')+'body='+encodeURIComponent(body):'mailto:twindowclean@gmail.com?subject='+encodeURIComponent(tr('Service request','Solicitud de servicio'))+'&body='+encodeURIComponent(body);
    const callback=p.consent_callback && p.services.length>0 && (validPhone()||validEmail()) && (!p.email || validEmail());
    if(callback) {
      busy(true);status(tr('Saving your callback request before opening the draft…','Guardando tu solicitud antes de abrir el borrador…'));
      const received=await post(intake,p);busy(false);hubReceived=hubReceived||received;
      if(!received) {
        status('');error(tr('Your callback request was not confirmed. Try Send Request, or open the draft below and send it yourself.','No se confirmó tu solicitud. Intenta Enviar solicitud, o abre el borrador y envíalo tú.'));
        const fallback=$('rq-open-draft');fallback.href=href;fallback.hidden=false;
        fallback.onclick=()=>{event('handoff_initiated',{channel,callback_saved:false});status(tr('Opening the draft. You still need to send it.','Abriendo el borrador. Aún debes enviarlo.'));};
        return;
      }
      recordReceipt(channel,{hub_receipt:true,formspree_receipt:false});
    }
    if(!callback)busy(false);
    status(callback?tr('Callback request saved. Your draft is opening; you still need to send it.','Solicitud guardada. Se abre el borrador; aún debes enviarlo.'):tr('Opening a draft only. No callback request was saved. You still need to send the message.','Solo se abre un borrador. No se guardó una solicitud. Aún debes enviar el mensaje.'));
    event('handoff_initiated',{channel,callback_saved:callback});
    location.href=href;
    const fallback=$('rq-open-draft');fallback.href=href;fallback.textContent=tr('Open the draft again','Abrir el borrador de nuevo');fallback.hidden=false;
  }
  $('rq-text').addEventListener('click',()=>handoff('sms'));
  $('rq-email-action').addEventListener('click',()=>handoff('email'));
  form.addEventListener('input',()=>{
    if(!touched){touched=true;event('inquiry_started');}
    $('rq-open-draft').hidden=true;update();
  });
  form.addEventListener('change',update);
  const mobile = /Android|iPhone|iPod|iPad/.test(navigator.userAgent) || (navigator.platform==='MacIntel' && navigator.maxTouchPoints>1);
  const primary=$(mobile?'rq-text':'rq-send');primary.classList.add('request-primary');primary.style.order='-1';
  try {const defaults=JSON.parse(section.dataset.defaultServices);checks.forEach(n=>n.checked=defaults.includes(n.value));}catch(_){}
  document.querySelectorAll('[data-screen-package]').forEach(button=>button.addEventListener('click',()=>{
    checks.find(n=>n.value==='scr').checked=true;$('rq-screen-package').value=button.dataset.screenPackage;$('rq-details').open=true;update();section.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  }));
  if('IntersectionObserver' in window) {const observer=new IntersectionObserver(entries=>{if(entries.some(x=>x.isIntersecting)){event('inquiry_viewed');observer.disconnect();}});observer.observe(section);}
  update();
})();
