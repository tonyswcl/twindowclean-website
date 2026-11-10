(function () {
  'use strict';
  let receipt;
  try {receipt=JSON.parse(sessionStorage.getItem('twc-request-receipt'));}catch(_){}
  if(!receipt || Date.now()-receipt.at>30*60*1000 || !(receipt.hub||receipt.formspree))return;
  document.getElementById('receipt-heading').textContent='Your request was received';
  document.getElementById('receipt-message').textContent='Thank you for contacting Tony’s Window Cleaning. Tony will review your service request and reply using your preferred contact method. Your appointment is awaiting confirmation.';
  document.getElementById('receipt-detail').textContent=receipt.hub && receipt.formspree ? 'Your request is saved with Tony’s office and the email submission was accepted.' : receipt.hub ? 'Your request is saved with Tony’s office. The separate email copy was not confirmed.' : 'Your email submission was accepted. Office synchronization has not been confirmed.';
})();
