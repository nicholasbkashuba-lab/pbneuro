/* ============================================================
   PALM BEACH NEUROLOGY — Help Assistant
   A chat-style concierge that answers common questions from a
   curated, fact-checked set and routes appointment requests to
   the secure form / office line.

   By design it collects NO patient information in-chat — anything
   involving personal or health details is handed off to the
   appointment form or the front desk. General information only,
   never medical advice.
   ============================================================ */
(function () {
  'use strict';
  if (window.__pbnAssistant) return;
  window.__pbnAssistant = true;

  var CFG = {
    phone: '561-845-0500',
    phoneHref: 'tel:+15618450500',
    researchPhone: '561-851-9400',
    researchPhoneHref: 'tel:+15618519400',
    autoOpenDelay: 5200
  };
  var KEYS = { auto: 'pbn.assistant.auto.v1' };

  // Resolve asset/link base from this script's own URL so links resolve at any page depth.
  var base = '';
  var self = document.currentScript || (function () {
    var s = document.querySelectorAll('script[src]');
    for (var i = 0; i < s.length; i++) if (/assistant\.js/.test(s[i].src)) return s[i];
    return null;
  })();
  if (self && self.src) base = self.src.replace(/assets\/js\/assistant\.js.*$/, '');
  var apptUrl = base + 'appointments.html';
  var faqUrl = base + 'faq.html';

  function store() { try { return window.sessionStorage; } catch (e) { return null; } }
  function get(k) { var s = store(); if (!s) return null; try { return JSON.parse(s.getItem(k)); } catch (e) { return null; } }
  function set(k, v) { var s = store(); if (!s) return; try { s.setItem(k, JSON.stringify(v)); } catch (e) {} }

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var chatIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';
  var closeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  var sendIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>';

  // ---------- Curated, always-available answers grounded in real facts ----------
  // Each entry: q (button label), a (answer HTML), k (keywords for typed matching).
  var A_APPT = 'You can <a href="' + apptUrl + '">request an appointment online</a> in about a minute, or call our office at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a>. New patients are always welcome.';
  var FAQ = [
    { q: 'Where are you located & when are you open?',
      a: 'We’re at <strong>4631 N Congress Ave, West Palm Beach, FL 33407</strong>, serving the greater Palm Beaches — West Palm Beach, Palm Beach, Palm Beach Gardens, Wellington, Royal Palm Beach, Lake Worth, and Jupiter. Office hours are <strong>Monday–Thursday 8:00 AM–' +
        '5:00 PM</strong> and <strong>Friday 8:00 AM–4:30 PM</strong>.',
      k: ['where', 'located', 'location', 'address', 'directions', 'hours', 'open', 'time', 'parking', 'congress', 'map'] },
    { q: 'Do I need a referral to be seen?',
      a: 'It depends on your insurance plan. Many PPO plans let you self-refer, while some HMO and Medicare Advantage plans require a referral from your primary care physician. Call us at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a> and our team will help you check before your visit.',
      k: ['referral', 'refer', 'primary', 'pcp', 'need', 'self'] },
    { q: 'Do you accept my insurance?',
      a: 'We accept many major insurance plans, including Medicare. Because coverage varies by plan, the fastest way to confirm is to call us at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a> with your card handy and we’ll verify your benefits.',
      k: ['insurance', 'medicare', 'medicaid', 'coverage', 'plan', 'cost', 'price', 'pay', 'billing', 'copay', 'accept'] },
    { q: 'What should I bring to my first visit?',
      a: 'Please bring your <strong>photo ID</strong>, <strong>insurance card</strong>, a list of your current <strong>medications</strong>, any recent brain or spine imaging (MRI/CT) on disc or via your portal, and any relevant records or referral paperwork. A family member is welcome — especially for memory-related visits. You can also complete your <a href="' + base + 'patient-center.html">new-patient forms</a> ahead of time to save time.',
      k: ['bring', 'first', 'visit', 'appointment', 'prepare', 'paperwork', 'forms', 'new patient', 'expect', 'records'] },
    { q: 'What is the FREE Memory Screen?',
      a: 'It’s a <strong>no-cost, confidential 30-minute screening</strong> of memory and thinking — a simple first step if you or a loved one has noticed changes. It isn’t a diagnosis, but it helps us decide whether a fuller evaluation is worthwhile. Ask us to schedule one at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a>.',
      k: ['memory', 'screen', 'screening', 'free', 'alzheimer', 'dementia', 'forget', 'cognitive', 'thinking'] },
    { q: 'What conditions do you treat?',
      a: 'We care for the full range of neurologic conditions: <strong>headache &amp; migraine, epilepsy &amp; seizures, Parkinson’s &amp; movement disorders, memory loss &amp; Alzheimer’s, multiple sclerosis, stroke &amp; TIA, neuropathy, neuromuscular disorders, sleep problems,</strong> and spine-related nerve pain. See our <a href="' + base + 'conditions/index.html">conditions</a> for details.',
      k: ['condition', 'treat', 'headache', 'migraine', 'epilepsy', 'seizure', 'parkinson', 'movement', 'tremor', 'memory', 'alzheimer', 'ms', 'multiple sclerosis', 'stroke', 'tia', 'neuropathy', 'neuromuscular', 'sleep', 'back', 'neck', 'nerve'] },
    { q: 'Do you offer testing like EEG and EMG?',
      a: 'Yes. Our neurologists use tools such as <strong>EEG</strong> (for seizures) and <strong>EMG / nerve-conduction studies</strong> (for neuropathy and neuromuscular conditions) as part of the work-up. Ask our team about what your evaluation may involve.',
      k: ['test', 'testing', 'eeg', 'emg', 'nerve conduction', 'ncs', 'study', 'diagnostic', 'scan', 'workup'] },
    { q: 'What clinical trials & research are available?',
      a: 'Through our on-site <strong>Premiere Research Institute</strong>, we run carefully monitored clinical trials in areas such as Alzheimer’s, migraine, and multiple sclerosis — often at no cost to participants. Studies change over time; see <a href="' + base + 'clinical-research.html">clinical research</a> or call <a href="' + CFG.researchPhoneHref + '">' + CFG.researchPhone + '</a> to ask what’s enrolling.',
      k: ['research', 'trial', 'trials', 'study', 'studies', 'premiere', 'institute', 'enroll', 'experimental'] },
    { q: 'Who are your doctors?',
      a: 'Our team includes nine fellowship-trained neurologists and specialists led by <strong>Dr. Paul Winner</strong>. You can meet each of them — with their focus areas and credentials — on our <a href="' + base + 'our-doctors.html">Our Doctors</a> page.',
      k: ['doctor', 'doctors', 'physician', 'neurologist', 'winner', 'staff', 'team', 'provider', 'who'] },
    { q: 'How long is a new-patient appointment?',
      a: 'New-patient neurology visits are scheduled for about <strong>one hour</strong>, so your neurologist has time to review your history, examine you, and explain the plan.',
      k: ['long', 'how long', 'duration', 'appointment', 'time', 'wait', 'hour'] },
    { q: 'Are you accepting new patients?',
      a: 'Yes — we’re accepting new patients. ' + A_APPT,
      k: ['new patient', 'accepting', 'take', 'available', 'appointment'] }
  ];

  var EMERGENCY = 'If you’re having a medical emergency — sudden weakness or numbness on one side, face drooping, trouble speaking, sudden severe headache, sudden vision loss, or a first-time seizure that won’t stop — <strong>call 911 now.</strong> These can be signs of a stroke and shouldn’t wait.';
  var EMERGENCY_K = ['911', 'emergency', 'stroke', 'urgent', 'help now', 'chest', 'can\'t speak', 'drooping', 'numb', 'weak'];

  // ---------- widget DOM ----------
  var root = el('div', 'pbn-root');
  root.innerHTML =
    '<div class="pbn-teaser">' +
      '<button class="pbn-teaser-x" aria-label="Dismiss">&#10005;</button>' +
      '<button class="pbn-teaser-open">👋 <strong>Questions?</strong> I can help with visits, insurance, conditions, and appointments — ask me anything.</button>' +
    '</div>' +
    '<button class="pbn-launcher" aria-label="Chat with Palm Beach Neurology" aria-haspopup="dialog">' + chatIcon + '<span class="pbn-dot"></span></button>' +
    '<div class="pbn-panel" role="dialog" aria-modal="false" aria-label="Palm Beach Neurology help assistant">' +
      '<div class="pbn-head">' +
        '<img src="' + base + 'assets/media/brand-icon.png" alt="">' +
        '<div class="pbn-who">' +
          '<div class="pbn-title">Neurology Assistant</div>' +
          '<div class="pbn-sub">Answers instantly · front desk within one business day</div>' +
        '</div>' +
        '<button class="pbn-x" aria-label="Close chat">' + closeIcon + '</button>' +
      '</div>' +
      '<div class="pbn-log" aria-live="polite"></div>' +
      '<div class="pbn-bar">' +
        '<input class="pbn-input" type="text" maxlength="300" placeholder="Type your question…" aria-label="Type your question">' +
        '<button class="pbn-send" aria-label="Send">' + sendIcon + '</button>' +
      '</div>' +
      '<div class="pbn-privacy">General information, not medical advice. Please don’t share personal health details here.<br>Or call <a href="' + CFG.phoneHref + '" style="color:inherit;font-weight:600;">' + CFG.phone + '</a></div>' +
    '</div>';

  var teaser, launcher, panel, log, input, sendBtn;
  var busy = false, chipsEl = null, started = false;

  function scrollLog() { log.scrollTop = log.scrollHeight; }

  function addUser(text) { log.appendChild(el('div', 'pbn-msg user', esc(text))); scrollLog(); }

  function clearChips() { if (chipsEl) { chipsEl.remove(); chipsEl = null; } }

  function botSay(messages, done) {
    busy = true;
    clearChips();
    var i = 0;
    (function nextMsg() {
      if (i >= messages.length) { busy = false; if (done) done(); return; }
      var typing = el('div', 'pbn-msg bot pbn-typing', '<i></i><i></i><i></i>');
      log.appendChild(typing); scrollLog();
      var delay = Math.min(320 + messages[i].replace(/<[^>]+>/g, '').length * 6, 1050);
      setTimeout(function () {
        typing.remove();
        log.appendChild(el('div', 'pbn-msg bot', messages[i]));
        scrollLog();
        i++; nextMsg();
      }, delay);
    })();
  }

  function showChips(defs) {
    clearChips();
    if (!defs || !defs.length) return;
    chipsEl = el('div', 'pbn-chips');
    defs.forEach(function (c) {
      var b;
      if (c.href) {
        // Real links (appointment form, phone) — work on the live site and let
        // the preview bundle's router intercept .html navigation.
        b = el('a', 'pbn-chip' + (c.cls ? ' ' + c.cls : ''), esc(c.label));
        b.setAttribute('href', c.href);
      } else {
        b = el('button', 'pbn-chip' + (c.cls ? ' ' + c.cls : ''), esc(c.label));
        b.addEventListener('click', function () { onChip(c); });
      }
      chipsEl.appendChild(b);
    });
    log.appendChild(chipsEl);
    scrollLog();
  }

  // The main menu shown after each answer.
  function mainMenu() {
    var chips = [{ label: '📅 Request an appointment', value: 'appointment', cls: 'primary' }];
    FAQ.forEach(function (f, i) { chips.push({ label: f.q.replace(/&amp;/g, '&'), value: 'faq:' + i }); });
    chips.push({ label: '📞 Call the office', href: CFG.phoneHref });
    showChips(chips);
  }

  function greet() {
    botSay([
      '👋 Welcome to <strong>Palm Beach Neurology</strong>. I’m the practice’s virtual assistant.',
      'I can answer questions about visits, insurance, the conditions we treat, our doctors, and clinical research — or help you request an appointment. What can I help you with?'
    ], function () { mainMenu(); });
  }

  function answerFaq(i) {
    var f = FAQ[i];
    if (!f) return;
    addUser(f.q.replace(/&amp;/g, '&'));
    botSay([f.a, 'Anything else I can help with?'], function () { mainMenu(); });
  }

  function goAppointment() {
    addUser('Request an appointment');
    botSay([
      'Wonderful — I’ll take you to our appointment request form. It goes straight to our front desk, who’ll confirm a time that works for you.',
      A_APPT
    ], function () {
      showChips([
        { label: '📝 Open the appointment form', href: apptUrl, cls: 'primary' },
        { label: '📞 Call ' + CFG.phone, href: CFG.phoneHref },
        { label: '← Back to questions', value: 'menu' }
      ]);
    });
  }

  function onChip(c) {
    if (busy) return;
    var v = c.value;
    if (v.indexOf('faq:') === 0) { answerFaq(parseInt(v.slice(4), 10)); return; }
    if (v === 'appointment') { goAppointment(); return; }
    if (v === 'menu') { addUser('Back to questions'); botSay(['Sure — here’s what I can help with:'], function () { mainMenu(); }); return; }
  }

  // ---------- typed-question matching ----------
  function normalize(s) { return ' ' + String(s).toLowerCase().replace(/[^a-z0-9\s']/g, ' ').replace(/\s+/g, ' ') + ' '; }

  function matchFaq(text) {
    var t = normalize(text);
    var best = -1, bestScore = 0;
    for (var i = 0; i < FAQ.length; i++) {
      var score = 0, kws = FAQ[i].k;
      for (var j = 0; j < kws.length; j++) {
        if (t.indexOf(' ' + kws[j].toLowerCase() + ' ') > -1 || t.indexOf(' ' + kws[j].toLowerCase()) > -1) {
          score += kws[j].indexOf(' ') > -1 ? 3 : 2; // multi-word keywords weigh more
        }
      }
      if (score > bestScore) { bestScore = score; best = i; }
    }
    return bestScore >= 2 ? best : -1;
  }

  function handleTyped(vRaw) {
    var v = (vRaw || '').trim();
    if (!v || busy) return;
    addUser(v);
    var t = normalize(v);
    // Emergency safety net first.
    for (var e = 0; e < EMERGENCY_K.length; e++) {
      if (t.indexOf(' ' + EMERGENCY_K[e].toLowerCase()) > -1) {
        botSay([EMERGENCY, 'For non-urgent questions I’m happy to help — or reach our office at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a>.'], function () { mainMenu(); });
        return;
      }
    }
    if (/\b(appointment|appt|book|schedule|see (a|the) doctor|request)\b/.test(t)) { goAppointment(); return; }
    var idx = matchFaq(v);
    if (idx > -1) {
      botSay([FAQ[idx].a, 'Did that help? Ask me anything else, or pick a topic below.'], function () { mainMenu(); });
    } else {
      botSay([
        'That’s a great question — and one our team can answer best. You can reach our front desk at <a href="' + CFG.phoneHref + '">' + CFG.phone + '</a>, or browse our <a href="' + faqUrl + '">full FAQ</a>.',
        'Meanwhile, here are the things I can answer right away:'
      ], function () { mainMenu(); });
    }
  }

  // ---------- open / close ----------
  function openPanel(auto) {
    hideTeaser();
    root.classList.add('open');
    if (!started) { started = true; greet(); }
    if (!auto) input.focus();
  }
  function closePanel() { root.classList.remove('open'); }
  function hideTeaser() { teaser.classList.remove('show'); }

  function boot() {
    document.body.appendChild(root);
    teaser = root.querySelector('.pbn-teaser');
    launcher = root.querySelector('.pbn-launcher');
    panel = root.querySelector('.pbn-panel');
    log = root.querySelector('.pbn-log');
    input = root.querySelector('.pbn-input');
    sendBtn = root.querySelector('.pbn-send');

    launcher.addEventListener('click', function () { openPanel(false); });
    root.querySelector('.pbn-x').addEventListener('click', closePanel);
    root.querySelector('.pbn-teaser-open').addEventListener('click', function () { openPanel(false); });
    root.querySelector('.pbn-teaser-x').addEventListener('click', hideTeaser);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.classList.contains('open')) closePanel();
    });

    function sendInput() {
      var v = input.value.trim();
      if (!v || busy) return;
      input.value = '';
      handleTyped(v);
    }
    sendBtn.addEventListener('click', sendInput);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); sendInput(); }
    });

    // Gentle teaser once per browser session (never auto-opens the full panel).
    if (!get(KEYS.auto)) {
      setTimeout(function () {
        if (root.classList.contains('open')) return;
        set(KEYS.auto, 1);
        teaser.classList.add('show');
        setTimeout(hideTeaser, 13000);
      }, CFG.autoOpenDelay);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
