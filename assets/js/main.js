// First Rehabilitation — v2 interactions
(function () {
  // Hero video: attach exactly ONE rendition based on viewport width —
  // 720p below 768px, 1440p above — as mp4 (primary) + webm (codec
  // fallback; browsers only download the first source they support).
  // Then nudge playback: some browsers need an explicit play() after load,
  // and Low Power Mode pauses autoplay until the page is interacted with.
  const heroVideo = document.querySelector('.hero-media video');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (heroVideo && !reducedMotion && !heroVideo.querySelector('source') && heroVideo.dataset.mp4Full) {
    const mobile = window.matchMedia('(max-width: 767px)').matches;
    const files = [
      [mobile ? heroVideo.dataset.mp4Mobile : heroVideo.dataset.mp4Full, 'video/mp4'],
      [mobile ? heroVideo.dataset.webmMobile : heroVideo.dataset.webmFull, 'video/webm'],
    ];
    files.forEach(([src, type]) => {
      if (!src) return;
      const s = document.createElement('source');
      s.src = src;
      s.type = type;
      heroVideo.appendChild(s);
    });
    heroVideo.load();
  }
  if (heroVideo && !reducedMotion) {
    let userPaused = false;
    const tryPlay = () => { if (!userPaused) heroVideo.play().catch(() => {}); };
    tryPlay();
    heroVideo.addEventListener('canplay', tryPlay);
    document.addEventListener('touchstart', tryPlay, { once: true, passive: true });
    document.addEventListener('click', tryPlay, { once: true });
    document.addEventListener('visibilitychange', () => { if (!document.hidden) tryPlay(); });
    // Safety nets for browsers that break the loop attribute or pause without
    // user intent — but the visible pause button below always wins.
    heroVideo.addEventListener('ended', () => { if (!userPaused) { heroVideo.currentTime = 0; tryPlay(); } });
    heroVideo.addEventListener('pause', () => { if (!document.hidden && !userPaused) setTimeout(tryPlay, 300); });
    const pauseBtn = document.querySelector('.hero-pause');
    if (pauseBtn) {
      pauseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userPaused = !userPaused;
        if (userPaused) { heroVideo.pause(); pauseBtn.innerHTML = '&#9654;'; pauseBtn.setAttribute('aria-label', 'Play background video'); }
        else { heroVideo.play().catch(() => {}); pauseBtn.innerHTML = '&#10073;&#10073;'; pauseBtn.setAttribute('aria-label', 'Pause background video'); }
        pauseBtn.setAttribute('aria-pressed', String(userPaused));
      });
    }
  } else if (heroVideo && reducedMotion) {
    const pauseBtn = document.querySelector('.hero-pause');
    if (pauseBtn) pauseBtn.hidden = true;
  }

  const header = document.querySelector('.site-header');
  const onScroll = () => header && header.classList.toggle('scrolled', window.scrollY > 40);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile nav
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    const setOpen = (open) => {
      links.classList.toggle('open', open);
      toggle.classList.toggle('active', open);
      document.body.classList.toggle('nav-locked', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    toggle.addEventListener('click', () => setOpen(!links.classList.contains('open')));
    // Escape closes the menu and returns focus to the toggle
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && links.classList.contains('open')) {
        setOpen(false);
        toggle.focus();
      }
    });
    links.querySelectorAll('li').forEach((li) => {
      const item = li.querySelector(':scope > a.nav-item');
      const dd = li.querySelector(':scope > .dropdown');
      if (item && dd) {
        item.setAttribute('aria-haspopup', 'true');
        item.setAttribute('aria-expanded', 'false');
        item.addEventListener('click', (e) => {
          if (window.matchMedia('(max-width: 1260px)').matches) {
            e.preventDefault();
            const open = li.classList.toggle('open-sub');
            item.setAttribute('aria-expanded', String(open));
          }
        });
      }
    });
  }

  // Scroll reveals
  const io = new IntersectionObserver(
    (entries) => entries.forEach((en) => en.isIntersecting && en.target.classList.add('in')),
    { threshold: 0.12 }
  );
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  // Seamless marquees & tickers: tag alternating tilts BEFORE cloning so the
  // pattern stays identical across the loop seam even with an odd item count,
  // then duplicate the content once — the roll animation travels exactly -50%.
  document.querySelectorAll('.marquee, .ticker').forEach((track) => {
    Array.from(track.children).forEach((el, i) =>
      el.classList.add(i % 2 ? 'tilt-b' : 'tilt-a'));
    if (reducedMotion) return; // no animation → no clone → no duplicate content
    const originals = track.children.length;
    track.innerHTML += track.innerHTML;
    Array.from(track.children).slice(originals).forEach((el) => {
      el.setAttribute('aria-hidden', 'true');
      if (el.tabIndex !== undefined) el.tabIndex = -1;
      el.querySelectorAll('a, button').forEach((n) => { n.tabIndex = -1; });
    });
  });

  // Animated counters (instant for prefers-reduced-motion users)
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const runCounter = (el) => {
    const target = parseFloat(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      el.textContent = target.toLocaleString() + suffix;
      return;
    }
    const dur = 1600;
    const start = performance.now();
    const step = (now) => {
      const p = Math.min((now - start) / dur, 1);
      const val = Math.round(target * easeOut(p));
      el.textContent = val.toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const cio = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting && !en.target.dataset.done) {
        en.target.dataset.done = '1';
        runCounter(en.target);
      }
    });
  }, { threshold: 0.2 });
  // Counters ship with their real final values server-rendered (SEO/no-JS);
  // the count-up is a progressive enhancement that replays 0 -> target on view.
  document.querySelectorAll('[data-count]').forEach((el) => cio.observe(el));

  // Body map: sync hotspot + list hover
  const link = (key, on) => {
    document.querySelectorAll(`[data-bm="${key}"]`).forEach((el) => el.classList.toggle('hot', on));
  };
  document.querySelectorAll('[data-bm]').forEach((el) => {
    el.addEventListener('mouseenter', () => link(el.dataset.bm, true));
    el.addEventListener('mouseleave', () => link(el.dataset.bm, false));
    el.addEventListener('focus', () => link(el.dataset.bm, true));
    el.addEventListener('blur', () => link(el.dataset.bm, false));
  });
})();

// Body map: gentle attract cycle — one point glows at a time (with its
// label chip) until the visitor interacts, then it hands over control.
(function () {
  const fig = document.querySelector('#bodymap .bodymap-fig');
  const spots = Array.from(document.querySelectorAll('#bodymap .bm-spot'));
  if (!fig || !spots.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  let i = -1;
  const setHot = (key, on) =>
    document.querySelectorAll('[data-bm="' + key + '"]').forEach((el) => el.classList.toggle('hot', on));
  const clearAll = () => spots.forEach((s) => setHot(s.dataset.bm, false));
  const tick = () => {
    clearAll();
    i = (i + 1) % spots.length;
    setHot(spots[i].dataset.bm, true);
  };
  const timer = setInterval(tick, 2400);
  tick();
  const stop = () => { clearInterval(timer); clearAll(); };
  ['pointerdown', 'mouseenter', 'focusin', 'touchstart'].forEach((ev) =>
    fig.addEventListener(ev, stop, { once: true, passive: true }));
})();

// FAQ page: category bubbles + live search + expand/collapse.
// Filtering only toggles visibility — every Q&A stays in the HTML for
// crawlers and AI engines; the FAQPage schema always matches the source.
(function () {
  const bubbles = Array.from(document.querySelectorAll('.faq-bubble'));
  if (!bubbles.length) return;
  const items = Array.from(document.querySelectorAll('.faq-item[data-cat]'));
  const sections = Array.from(document.querySelectorAll('[data-cat-section]'));
  const live = document.getElementById('faq-live');
  const search = document.getElementById('faq-search');
  const empty = document.getElementById('faq-empty');
  let cat = 'all';

  function apply() {
    const q = search ? search.value.trim().toLowerCase() : '';
    let shown = 0;
    const perCat = {};
    items.forEach((d) => {
      const matches = !q || d.textContent.toLowerCase().indexOf(q) > -1;
      if (matches) perCat[d.dataset.cat] = (perCat[d.dataset.cat] || 0) + 1;
      const show = matches && (cat === 'all' || d.dataset.cat === cat);
      d.classList.toggle('faq-hidden', !show);
      if (show) shown++;
    });
    sections.forEach((s) => {
      const any = s.querySelector('.faq-item:not(.faq-hidden)');
      s.classList.toggle('faq-hidden', !any);
    });
    bubbles.forEach((b) => {
      const c = b.dataset.cat;
      let n = 0;
      if (c === 'all') { for (const k in perCat) n += perCat[k]; }
      else n = perCat[c] || 0;
      const el = b.querySelector('.fb-count');
      if (el) el.textContent = '(' + n + ')';
    });
    if (empty) empty.classList.toggle('faq-hidden', shown > 0);
    if (live) live.textContent = 'Showing ' + shown + ' question' + (shown === 1 ? '' : 's');
  }

  function activate(b) {
    cat = b.dataset.cat;
    bubbles.forEach((x) => {
      const on = x === b;
      x.classList.toggle('active', on);
      x.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (history.replaceState) {
      history.replaceState(null, '', cat === 'all' ? location.pathname : '#' + cat);
    }
    apply();
  }

  bubbles.forEach((b, i) => {
    b.addEventListener('click', () => activate(b));
    // Arrow keys move focus AND switch the active topic, so keyboard users
    // can flip through categories without pressing Enter each time.
    b.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        e.preventDefault();
        const next = bubbles[(i + (e.key === 'ArrowRight' ? 1 : bubbles.length - 1)) % bubbles.length];
        next.focus();
        activate(next);
        if (next.scrollIntoView) next.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      }
    });
  });

  if (search) {
    search.addEventListener('input', () => {
      // searching spans every category, so snap the filter back to All
      if (search.value && cat !== 'all') activate(bubbles[0]);
      else apply();
    });
  }
  const ex = document.getElementById('faq-expand');
  const co = document.getElementById('faq-collapse');
  if (ex) ex.addEventListener('click', () => items.forEach((d) => { if (!d.classList.contains('faq-hidden')) d.open = true; }));
  if (co) co.addEventListener('click', () => items.forEach((d) => { d.open = false; }));

  // Deep links: /faq.html#hand-therapy pre-selects that category —
  // both on load and on later hash-only navigation.
  function syncToHash(fallback) {
    const hh = location.hash.replace('#', '');
    const t = bubbles.filter((b) => b.dataset.cat === hh)[0];
    if (t) activate(t); else if (fallback) apply();
  }
  window.addEventListener('hashchange', () => syncToHash(false));
  syncToHash(true);
})();

// Neuro Explorer: rich detail panel + area filter
(function () {
  const section = document.getElementById('bodymap');
  const panel = document.getElementById('bm-panel');
  const dataEl = document.getElementById('bm-data');
  if (!section || !panel || !dataEl) return;
  const DATA = JSON.parse(dataEl.textContent);
  const svg = section.querySelector('.bm-svg');

  // Respect reduced motion — freeze the traveling signal pulses.
  if (svg && svg.pauseAnimations && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    try { svg.pauseAnimations(); } catch (e) {}
  }

  const show = (key) => {
    const d = DATA[key];
    if (!d) return;
    panel.classList.remove('flash');
    void panel.offsetWidth; // restart animation
    panel.classList.add('flash');
    panel.innerHTML =
      '<span class="cond-tag">' + d.tag + '</span>' +
      '<h3>' + d.name + '</h3>' +
      (d.area ? '<p class="bm-area"><i class="bm-area-ic" aria-hidden="true"></i>' + d.area + '</p>' : '') +
      '<p>' + d.lede + '</p>' +
      (d.treats && d.treats.length
        ? '<div class="bm-sub">Signs we look for</div><ul class="check-list">' +
          d.treats.map(t => '<li>' + t + '</li>').join('') + '</ul>' : '') +
      (d.approach ? '<div class="bm-sub">How we help</div><p class="bm-approach">' + d.approach + '</p>' : '') +
      '<a class="bm-cta" href="' + d.url + '">Explore this condition &rarr;</a>';
    section.querySelectorAll('[data-bm]').forEach(el =>
      el.classList.toggle('active', el.dataset.bm === key));
    if (window.matchMedia('(max-width: 880px)').matches) {
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };
  section.querySelectorAll('[data-bm]').forEach((el) => {
    el.addEventListener('click', (e) => { e.preventDefault(); show(el.dataset.bm); });
  });

  // Area filter — All / Brain / Spine / Nerves & Muscle
  const fbtns = Array.from(section.querySelectorAll('.bm-fbtn'));
  const applyFilter = (f) => {
    section.querySelectorAll('[data-group]').forEach(el =>
      el.classList.toggle('dim', !(f === 'all' || el.dataset.group === f)));
    fbtns.forEach(b => {
      const on = b.dataset.filter === f;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  };
  fbtns.forEach(b => b.addEventListener('click', () => applyFilter(b.dataset.filter)));
})();

  // Spotify embeds load only when the visitor asks for them (podcast page).
  document.querySelectorAll('.pod-facade').forEach((btn) => {
    btn.addEventListener('click', () => {
      const iframe = document.createElement('iframe');
      iframe.src = btn.dataset.embed;
      iframe.width = '100%';
      iframe.height = btn.dataset.height || '152';
      iframe.frameBorder = '0';
      iframe.style.borderRadius = '14px';
      iframe.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
      iframe.loading = 'lazy';
      iframe.title = btn.dataset.title || 'Spotify player';
      btn.replaceWith(iframe);
    });
  });

// Email-delivered forms — any <form data-endpoint="…"> (appointment request AND
// the electronic new-patient intake) validates with native HTML constraints,
// posts to its FormSubmit endpoint, then reveals its data-done panel. The front
// desk phone is always shown as a fallback if delivery fails.
(function () {
  document.querySelectorAll('form[data-endpoint]').forEach((form) => {
    const errEl = form.querySelector('.af-error');
    const doneEl = form.dataset.done ? document.getElementById(form.dataset.done) : null;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (errEl) errEl.style.display = 'none';
      const btn = form.querySelector('button[type="submit"]');
      const label = btn && btn.textContent;
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      let ok = true;
      try {
        const data = new FormData(form);
        data.append('_subject', form.dataset.subject || 'New submission — Palm Beach Neurology');
        data.append('_template', 'table');
        await fetch(form.dataset.endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
      } catch (_) { ok = false; }
      if (doneEl) {
        form.hidden = true;
        doneEl.hidden = false;
        doneEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else if (btn) {
        btn.textContent = ok ? 'Sent — thank you!' : label;
        btn.disabled = false;
      }
    });
  });
})();

// Hero neural signals — bright pulses fire along the synapse edges, so the hero
// feels alive without any image or video asset. Reduced-motion users see none.
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const net = document.querySelector('.hero .neuro-net');
  if (!net) return;
  const lines = Array.from(net.querySelectorAll('line'));
  if (!lines.length) return;
  const NS = 'http://www.w3.org/2000/svg';
  const fire = () => {
    const ln = lines[Math.floor(Math.random() * lines.length)];
    const x1 = +ln.getAttribute('x1'), y1 = +ln.getAttribute('y1');
    const x2 = +ln.getAttribute('x2'), y2 = +ln.getAttribute('y2');
    const c = document.createElementNS(NS, 'circle');
    c.setAttribute('r', '3.2');
    c.setAttribute('class', 'hero-spark');
    net.appendChild(c);
    const dur = 850 + Math.random() * 900;
    let start = null;
    const step = (t) => {
      if (!start) start = t;
      const p = Math.min((t - start) / dur, 1);
      c.setAttribute('cx', String(x1 + (x2 - x1) * p));
      c.setAttribute('cy', String(y1 + (y2 - y1) * p));
      c.setAttribute('opacity', String(Math.sin(p * Math.PI)));
      if (p < 1) requestAnimationFrame(step); else c.remove();
    };
    requestAnimationFrame(step);
  };
  setInterval(() => { fire(); if (Math.random() > 0.45) setTimeout(fire, 260); }, 1050);
})();

// Premium v2: scroll-progress hairline + gentle hero parallax + reduced-motion
// pause for the hero orb's SMIL signal pulses.
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // progress hairline
  var bar = document.createElement('div');
  bar.className = 'scroll-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  var ticking = false;
  function paint() {
    ticking = false;
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    bar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(paint); }
  }, { passive: true });
  paint();

  var art = document.querySelector('.hero-art');
  if (art && art.querySelector('svg')) {
    var svg = art.querySelector('svg');
    if (reduced && svg.pauseAnimations) { try { svg.pauseAnimations(); } catch (e) {} }
    if (!reduced) {
      var pTick = false;
      window.addEventListener('scroll', function () {
        if (pTick) return;
        pTick = true;
        requestAnimationFrame(function () {
          pTick = false;
          var y = window.scrollY;
          if (y < window.innerHeight * 1.2) art.style.translate = '0 ' + (y * 0.09) + 'px';
        });
      }, { passive: true });
    }
  }
})();
