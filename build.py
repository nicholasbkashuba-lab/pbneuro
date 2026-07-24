#!/usr/bin/env python3
"""
Palm Beach Neurology & Premiere Research Institute — static site generator.
Run `python3 build.py`; every page regenerates in place.

Engineered on the First Rehabilitation of North Palm Beach design system
(same editorial luxury: Playfair Display + Inter, film grain, scroll
choreography, interactive anatomy map) and re-themed to the Palm Beach
Neurology brand — beachy warm sand + deep coastal teal + sea-green, with a
synapse field replacing the lighthouse beam and a brain/nervous-system map
replacing the body map.

------------------------------------------------------------------------------
PENDING OWNER VERIFICATION (facts gathered from Google/Healthgrades because the
live site blocks automated access — CONFIRM before pointing the real domain here):
  * Provider roster & exact credentials/titles (see DOCTORS below)
  * "Premier" vs "Premiere" Research Institute spelling (their title tag uses
    "Premiere"; standard English is "Premier") -> set BRAND_SUB accordingly
  * Office hours (shown as "Call for hours" until confirmed)
  * In-house diagnostics offered (EMG/EEG/Ees, infusions, imaging)
  * Patient Portal login URL (PORTAL placeholder below)
  * Fax number, email, social links
  * Exact appointment offerings (FREE Memory Screen 30min + New Patient 1hr are
    confirmed from their live Appointments page screenshot)
------------------------------------------------------------------------------
"""
import os, html, hashlib as _hashlib, json as _json, re as _re

ROOT = os.path.dirname(os.path.abspath(__file__))

BRAND = "Palm Beach Neurology"
BRAND_SUB = "& Premiere Research Institute"
LEGAL = "Palm Beach Neurology & Premiere Research Institute"
TAGLINE = "Stay Sharp. Stay in Control."
PHONE = "561-845-0500"
PHONE_TEL = "+15618450500"
EMAIL = "info@palmbeachneurology.com"             # VERIFY
FAX = "561-845-0587"
RESEARCH_PHONE = "561-851-9400"
ADDR_STREET = "4631 N Congress Ave"
ADDR_CITY = "West Palm Beach"
ADDR_STATE = "FL"
ADDR_ZIP = "33407"
RESEARCH_URL = "https://www.premiereresearchinstitute.com/"
FORMS_PDF = "assets/forms/new-patient-paperwork.pdf"
PORTAL = "patient-center.html"                     # interim -> replace with real EMR portal login URL
BASE = "https://www.palmbeachneurology.com"
THEME_COLOR = "#0F3A46"
MAPS_EMBED = ("https://www.google.com/maps?q=4631+N+Congress+Ave+West+Palm+Beach+FL+33407&output=embed")
MAPS_LINK = ("https://www.google.com/maps/search/?api=1&query=4631+N+Congress+Ave+West+Palm+Beach+FL+33407")

# ----------------------------------------------------------------------------
# ASSET CACHE-BUSTING
# ----------------------------------------------------------------------------
def _v(path):
    with open(path, "rb") as f:
        return _hashlib.sha256(f.read()).hexdigest()[:8]
ASSET_V = {}
def asset_v(path):
    if path not in ASSET_V:
        try:
            ASSET_V[path] = _v(os.path.join(ROOT, path))
        except FileNotFoundError:
            ASSET_V[path] = "1"
    return ASSET_V[path]

FAVICON_V = "2"

# ----------------------------------------------------------------------------
# ORG SCHEMA + <head>
# ----------------------------------------------------------------------------
ORG_ID = f"{BASE}/#organization"
ORG_REF = {"@id": ORG_ID}

def _org_schema_str():
    data = {
        "@context": "https://schema.org",
        "@type": ["MedicalClinic", "Physician", "MedicalBusiness"],
        "@id": ORG_ID,
        "name": LEGAL,
        "alternateName": ["Palm Beach Neurology", "Premiere Research Institute", "PBN"],
        "description": ("Comprehensive neurology practice in West Palm Beach, Florida — one of the "
                        "most experienced neurological practices in the United States, with 25+ years "
                        "caring for the brain, spine, and nervous system, plus an on-site clinical-"
                        "research institute. We treat the patient, not just the disease."),
        "url": BASE + "/",
        "logo": f"{BASE}/assets/media/logo.png",
        "image": f"{BASE}/assets/media/og-cover.jpg",
        "telephone": "+1-" + PHONE,
        "faxNumber": "+1-" + FAX,
        "email": EMAIL,
        "medicalSpecialty": ["Neurologic"],
        "priceRange": "$$",
        "isAcceptingNewPatients": True,
        "slogan": "Treating the patient, not just the disease.",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"],
             "opens": "08:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Friday"], "opens": "08:00", "closes": "16:30"},
        ],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ADDR_STREET,
            "addressLocality": ADDR_CITY,
            "addressRegion": ADDR_STATE,
            "postalCode": ADDR_ZIP,
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 26.7717, "longitude": -80.0925},
        "hasMap": MAPS_LINK,
        "areaServed": [{"@type": "City", "name": c} for c in [
            "West Palm Beach", "Palm Beach", "Palm Beach Gardens", "Wellington",
            "Royal Palm Beach", "Lake Worth", "Boynton Beach", "Jupiter",
            "North Palm Beach", "Greenacres"]],
        "sameAs": [RESEARCH_URL],
    }
    data.pop("@context", None)
    website = {"@type": "WebSite", "@id": f"{BASE}/#website", "url": BASE + "/",
               "name": BRAND, "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}
    graph = {"@context": "https://schema.org", "@graph": [data, website]}
    return '<script type="application/ld+json">' + _json.dumps(graph, ensure_ascii=False) + "</script>"

def head(title, desc, depth=0, canonical="", og_image="assets/media/og-cover.jpg",
         page_type="website", extra_schema="", noindex=False):
    p = "../" * depth
    canon = f"{BASE}/{canonical}" if canonical else BASE + "/"
    canon_tag = "" if noindex else f'<link rel="canonical" href="{canon}">\n'
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{canon_tag}<meta name="robots" content="{robots}">
<meta name="author" content="{html.escape(LEGAL)}">
<meta name="geo.region" content="US-FL">
<meta name="geo.placename" content="West Palm Beach">
<meta property="og:type" content="{page_type}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{html.escape(BRAND)}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{BASE}/{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{BASE}/{og_image}">
<meta name="theme-color" content="{THEME_COLOR}">
<link rel="icon" href="{p}assets/icons/favicon.ico?v={FAVICON_V}" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/icons/icon-32.png?v={FAVICON_V}">
<link rel="icon" type="image/png" sizes="16x16" href="{p}assets/icons/icon-16.png?v={FAVICON_V}">
<link rel="apple-touch-icon" sizes="180x180" href="{p}assets/icons/apple-touch-icon.png?v={FAVICON_V}">
<link rel="manifest" href="{p}site.webmanifest">
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/playfair-display-latin-700-normal.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/inter-latin-400-normal.woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/styles.css?v={asset_v('assets/css/styles.css')}">
<link rel="stylesheet" href="{p}assets/css/assistant.css?v={asset_v('assets/css/assistant.css')}">
{_org_schema_str()}
{extra_schema}</head>
<body>
"""

# ----------------------------------------------------------------------------
# NAV / FOOTER / SHARED
# ----------------------------------------------------------------------------
def nav(depth=0, solid=False):
    p = "../" * depth
    cls = "site-header solid" if solid else "site-header"
    cond_links = "".join(
        f'<a href="{p}conditions/{slug}.html">{c["nav"]}</a>' for slug, c in CONDITIONS.items())
    # Services: dropdown of dedicated service pages when present, else a plain link.
    if SERVICES_DATA:
        svc_dd = (f'<a href="{p}services.html">All Services</a>'
                  + "".join(f'<a href="{p}services/{s["slug"]}.html">{s["name"]}</a>' for s in SERVICES_DATA))
        services_li = (f'<li><a class="nav-item" href="{p}services.html">Services</a>'
                       f'<div class="dropdown"><div class="dd-cols">{svc_dd}</div></div></li>')
    else:
        services_li = f'<li><a class="nav-item" href="{p}services.html">Services</a></li>'
    about_li = f'<li><a class="nav-item" href="{p}about.html">About</a></li>' if ABOUT_DATA else ''
    patients_extra = (f'<a href="{p}locations/index.html">Areas We Serve</a>' if LOCATIONS_DATA else '') + \
                     (f'<a href="{p}insurance-billing.html">Insurance &amp; Billing</a>' if INSURANCE_DATA else '')
    return f"""
<header class="{cls}">
  <a class="skip-link" href="#main">Skip to main content</a>
  <div class="wrap nav-bar">
    <a class="brand" href="{p}index.html" aria-label="{html.escape(BRAND)} home">
      <img class="brand-logo brand-logo-light" src="{p}assets/media/logo-light.png" alt="{html.escape(BRAND)}" width="204" height="55">
      <img class="brand-logo brand-logo-dark" src="{p}assets/media/logo.png" alt="{html.escape(BRAND)}" width="204" height="55">
    </a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav-el" aria-label="Main menu">
    <ul class="nav-links">
      <li><a class="nav-item" href="{p}index.html">Home</a></li>
      <li>
        <a class="nav-item" href="{p}conditions/index.html">Conditions</a>
        <div class="dropdown"><div class="dd-cols">{cond_links}</div></div>
      </li>
      {services_li}
      <li><a class="nav-item" href="{p}our-doctors.html">Our Doctors</a></li>
      <li><a class="nav-item" href="{p}clinical-research.html">Research</a></li>
      {about_li}
      <li>
        <a class="nav-item" href="{p}appointments.html">Patients</a>
        <div class="dropdown">
          <a href="{p}appointments.html">Appointments</a>
          <a href="{p}patient-center.html">Patient Center &amp; Forms</a>
          {patients_extra}
          <a href="{p}blog/index.html">Articles &amp; Insights</a>
          <a href="{p}faq.html">FAQ</a>
        </div>
      </li>
      <li><a class="nav-item" href="{p}contact.html">Contact</a></li>
      <li class="nav-menu-cta"><a class="btn btn-coral" href="{p}appointments.html">Request Appointment</a></li>
    </ul>
    </nav>
    <a class="btn btn-coral nav-cta-btn" href="{p}appointments.html">Request Appointment</a>
  </div>
</header>
"""

def footer(depth=0):
    p = "../" * depth
    cond_links = "".join(
        f'<li><a href="{p}conditions/{slug}.html">{c["nav"]}</a></li>'
        for slug, c in list(CONDITIONS.items())[:7])
    if LOCATIONS_DATA:
        area_links = "".join(f'<li><a href="{p}locations/{l["slug"]}.html">{l["city"]}</a></li>' for l in LOCATIONS_DATA)
    else:
        areas = ["West Palm Beach", "Palm Beach", "Palm Beach Gardens", "Wellington",
                 "Royal Palm Beach", "Lake Worth", "Jupiter", "Boynton Beach"]
        area_links = "".join(f"<li>{a}</li>" for a in areas)
    practice_extra = (f'<li><a href="{p}about.html">About Us</a></li>' if ABOUT_DATA else '') + \
                     (f'<li><a href="{p}insurance-billing.html">Insurance &amp; Billing</a></li>' if INSURANCE_DATA else '')
    return f"""
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="f-brand">
        <img class="f-logo" src="{p}assets/media/logo-light.png" alt="{html.escape(BRAND)}" width="216" height="58" loading="lazy">
        <div class="brand-tag">Treating the patient, not just the disease.</div>
        <p>Board-certified neurology and on-site clinical research in West Palm Beach —
        advanced, compassionate care for the brain, spine, and nervous system for more than 25 years.</p>
      </div>
      <div>
        <h2 class="f-head">Conditions</h2>
        <ul>{cond_links}<li><a href="{p}conditions/index.html">All Conditions &rarr;</a></li></ul>
      </div>
      <div>
        <h2 class="f-head">Practice</h2>
        <ul>
          {practice_extra}
          <li><a href="{p}services.html">Services</a></li>
          <li><a href="{p}our-doctors.html">Our Doctors</a></li>
          <li><a href="{p}clinical-research.html">Clinical Research</a></li>
          <li><a href="{p}appointments.html">Appointments</a></li>
          <li><a href="{p}patient-center.html">Patient Center</a></li>
          <li><a href="{p}blog/index.html">Blog</a></li>
          <li><a href="{p}faq.html">FAQ</a></li>
        </ul>
      </div>
      <div>
        <h2 class="f-head">Areas We Serve</h2>
        <ul class="f-areas">{area_links}</ul>
      </div>
      <div>
        <h2 class="f-head">Visit Us</h2>
        <ul class="f-contact">
          <li>{ADDR_STREET}<br>{ADDR_CITY}, {ADDR_STATE} {ADDR_ZIP}</li>
          <li>Phone: <a href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <span>&copy; 2026 {html.escape(LEGAL)}. All rights reserved.</span>
      <span>Board-certified neurology &middot; West Palm Beach, FL</span>
    </div>
  </div>
</footer>
<nav class="mobile-call-nav" aria-label="Call the office">
  <a class="mobile-call" href="tel:{PHONE_TEL}" aria-label="Call {html.escape(BRAND)} now at {PHONE}"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.4 21 3 13.6 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.6.1.4 0 .8-.3 1l-2.2 2.2z"/></svg><span>Call Now</span></a>
</nav>
<script src="{p}assets/js/main.js?v={asset_v('assets/js/main.js')}"></script>
<script src="{p}assets/js/assistant.js?v={asset_v('assets/js/assistant.js')}" defer></script>
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments);}};</script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""

def brand_mark(variant="nav"):
    """Inline SVG brain-flower mark (no external logo file needed). Two-tone
    teal/sea-green petals forming a brain, echoing the practice's logo."""
    cls = {"nav": "brand-mark", "footer": "brand-mark f-mark", "hero": "brand-mark hero-mark"}[variant]
    petals = ""
    import math
    for i in range(6):
        ang = math.radians(i * 60 - 90)
        cx = 32 + 15 * math.cos(ang)
        cy = 32 + 15 * math.sin(ang)
        fill = "var(--sea)" if i % 2 == 0 else "var(--leaf)"
        petals += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11.5" fill="{fill}" opacity="0.9"/>'
    return (f'<svg class="{cls}" viewBox="0 0 64 64" role="img" aria-label="{html.escape(BRAND)} logo" '
            f'width="52" height="52">{petals}'
            f'<circle cx="32" cy="32" r="12" fill="var(--ink)"/>'
            f'<path d="M27 27c-2 0-3.4 1.4-3.4 3.2 0 .5.1 1 .3 1.4-1 .5-1.6 1.5-1.6 2.6 0 1.7 1.4 3 3.2 3 '
            f'M37 27c2 0 3.4 1.4 3.4 3.2 0 .5-.1 1-.3 1.4 1 .5 1.6 1.5 1.6 2.6 0 1.7-1.4 3-3.2 3 '
            f'M32 24.5v15" fill="none" stroke="var(--cream)" stroke-width="1.5" stroke-linecap="round"/>'
            f'</svg>')

def cta_band(depth=0,
             heading='Clarity for the mind starts with <em>one conversation.</em>',
             sub="Request an appointment today — new patients are welcome, and our team will help verify your insurance and find a time that works."):
    p = "../" * depth
    return f"""
<section class="cta-band">
  <div class="hero-fallback"></div>
  {neuro_field(0.6)}
  <div class="wrap cta-inner reveal">
    <h2>{heading}</h2>
    <p>{sub}</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a class="btn btn-coral" href="{p}appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
      <a class="btn btn-ghost" href="tel:{PHONE_TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>
"""

def wave_divider(variant="cream"):
    """Signature EEG-trace section divider (a neurology-specific motif)."""
    path = ("M0 20 H470 L494 20 L508 9 L520 31 L534 3 L548 33 L562 12 L576 20 "
            "L600 20 L636 20 H1200")
    return (f'<div class="wave-divider wave-{variant}" aria-hidden="true">'
            f'<svg viewBox="0 0 1200 40"><path d="{path}"/>'
            f'<circle class="wave-spark" cx="534" cy="3" r="4"/></svg></div>')

def hero_orb():
    """Hero artwork: a luminous neural constellation — brain silhouette, slow-turning
    orbital rings, glowing nodes and traveling signal pulses. Purely decorative."""
    N = [(260,150),(200,180),(320,180),(170,240),(350,240),(220,230),(300,230),
         (260,210),(190,300),(330,300),(240,290),(280,290),(260,340),(210,350),(310,350)]
    E = [(0,1),(0,2),(1,3),(2,4),(1,5),(2,6),(5,7),(6,7),(3,8),(4,9),(5,10),(6,11),
         (10,12),(11,12),(8,13),(9,14),(12,13),(12,14),(7,10),(7,11)]
    edges = "".join(
        f'<path id="orbE{i}" class="orb-axon" d="M{N[a][0]},{N[a][1]} L{N[b][0]},{N[b][1]}"/>'
        for i, (a, b) in enumerate(E))
    nodes = "".join(f'<circle class="orb-node" cx="{x}" cy="{y}" r="3"/>' for x, y in N)
    pulses = "".join(
        f'<circle class="orb-signal" r="3.2"><animateMotion dur="{d}s" repeatCount="indefinite" '
        f'begin="{i*0.9}s"><mpath href="#orbE{e}"/></animateMotion></circle>'
        for i, (e, d) in enumerate([(0,3.2),(4,4.1),(9,3.6),(13,4.4),(17,3.9)]))
    # satellites riding the outer rings
    sats = "".join(
        f'<circle class="orb-sat" cx="{x}" cy="{y}" r="4"/>'
        for x, y in [(260,40),(455,320),(80,160),(430,120),(110,370)])
    sil = ('<g transform="translate(90,62)">'
           '<path class="orb-sil" d="M170,44 C210,44 244,60 260,92 C276,122 274,146 268,164 '
           'C282,178 286,204 272,224 C285,242 281,272 258,286 C246,300 224,306 200,302 '
           'C190,314 150,314 140,302 C116,306 94,300 82,286 C59,272 55,242 68,224 '
           'C54,204 58,178 72,164 C66,146 64,122 80,92 C96,60 130,44 170,44 Z"/>'
           '<path class="orb-fissure" d="M170,50 C177,96 163,132 170,172 C177,210 165,252 170,300"/></g>')
    return (
        '<div class="orb-glow"></div>'
        '<svg viewBox="0 0 520 520" aria-hidden="true" focusable="false">'
        '<g class="orb-rings"><circle class="orb-ring" cx="260" cy="250" r="238"/>'
        '<circle class="orb-ring r2" cx="260" cy="250" r="196"/></g>'
        '<g class="orb-rings rev"><circle class="orb-ring r2" cx="260" cy="250" r="160"/></g>'
        f'{sil}<g class="orb-net">{edges}{nodes}{pulses}</g>{sats}</svg>')

def page_hero(eyebrow, title, lede, crumbs_html=""):
    return f"""
<section class="page-hero">
  <div class="hero-fallback"></div>
  {neuro_field(0.5)}
  <div class="wrap">
    {crumbs_html}
    <span class="eyebrow">{eyebrow}</span>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>
"""

# ----------------------------------------------------------------------------
# SIGNATURE MOTIF: synapse field (aura + neural constellation)
# ----------------------------------------------------------------------------
def neuro_field(opacity=0.6):
    import random
    rng = random.Random(7)          # fixed seed -> deterministic, reproducible build
    W, H = 1200, 620
    nodes = []
    # loose grid with jitter so the constellation feels organic but even
    for gx in range(6):
        for gy in range(3):
            x = 90 + gx * 205 + rng.randint(-45, 45)
            y = 90 + gy * 210 + rng.randint(-45, 45)
            nodes.append((x, y))
    edges = []
    for i, (x1, y1) in enumerate(nodes):
        d = sorted(range(len(nodes)),
                   key=lambda j: (nodes[j][0]-x1)**2 + (nodes[j][1]-y1)**2)
        for j in d[1:3]:
            if (min(i, j), max(i, j)) not in edges:
                edges.append((min(i, j), max(i, j)))
    def _edge(k, a, b):
        cls = ' class="edge-lit"' if k % 5 == 0 else ''
        return f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"{cls}/>'
    lines = "".join(_edge(k, a, b) for k, (a, b) in enumerate(edges))
    circ = ""
    for k, (x, y) in enumerate(nodes):
        cls = "node"
        if k % 3 == 0:
            cls += " pulse"
        if k % 4 == 0:
            cls += " lit"
        dur = 3.6 + (k % 5) * 0.6
        r = 2.6 if k % 3 else 3.6
        circ += f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}" style="--pulse-dur:{dur}s"/>'
    return (f'<div class="neuro-field" aria-hidden="true" style="opacity:{opacity}">'
            f'<div class="neuro-aura"></div>'
            f'<svg class="neuro-net" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
            f'{lines}{circ}</svg></div>')

# ----------------------------------------------------------------------------
# BRAIN / NERVOUS-SYSTEM MAP (interactive)
# ----------------------------------------------------------------------------
# Which anatomical structure each hotspot belongs to (drives the Brain/Spine/Nerves filter).
BM_GROUP = {
    "migraine": "brain", "memory": "brain", "epilepsy": "brain", "movement": "brain",
    "stroke": "brain", "ms": "brain", "sleep": "brain",
    "spine": "spine", "neuropathy": "nerves", "neuromuscular": "nerves",
}
BM_LINKS = {
    "migraine": "conditions/headaches-migraine.html",
    "memory": "conditions/memory-alzheimers.html",
    "epilepsy": "conditions/epilepsy-seizures.html",
    "movement": "conditions/parkinsons-movement.html",
    "stroke": "conditions/stroke.html",
    "ms": "conditions/multiple-sclerosis.html",
    "sleep": "conditions/sleep-disorders.html",
    "spine": "conditions/back-neck-pain.html",
    "neuropathy": "conditions/neuropathy.html",
    "neuromuscular": "conditions/neuromuscular.html",
}

def brainmap_svg():
    """Interactive Neuro Explorer: an anatomical top-down brain + brainstem, spinal
    cord and peripheral nerves, overlaid with a living neural network (traveling
    signal pulses), labeled regions, and 10 condition hotspots. Brain-local
    coordinates are centred on x=170 and shifted right inside a 480-wide viewBox."""
    # (key, x, y, label) over the figure — brain-local coords (centre x=170)
    spots = [
        ("migraine",   170,  82, "Headache &amp; Migraine"),
        ("ms",         232, 118, "Multiple Sclerosis"),
        ("memory",     110, 150, "Memory &amp; Alzheimer's"),
        ("epilepsy",   230, 160, "Epilepsy &amp; Seizures"),
        ("stroke",     106, 212, "Stroke &amp; TIA"),
        ("movement",   170, 196, "Parkinson's &amp; Movement"),
        ("sleep",      170, 300, "Sleep Disorders"),
        ("spine",      170, 396, "Neck &amp; Back Pain"),
        ("neuropathy", 116, 556, "Neuropathy"),
        ("neuromuscular", 224, 560, "Neuromuscular"),
    ]

    def _chip(x, y, lbl):
        plain = html.unescape(lbl)
        w = round(len(plain) * 6.5 + 20)
        rx = x + 18 if x <= 170 else x - 18 - w
        rx = max(-56, min(rx, 404 - w))
        ry = y - 11
        return (f'<g class="bm-chip"><rect x="{rx}" y="{ry}" width="{w}" height="22" rx="11"/>'
                f'<text x="{rx + w/2}" y="{ry + 15}" text-anchor="middle">{lbl}</text></g>')

    spots_svg = "".join(
        f'''<a href="{BM_LINKS[k]}" class="bm-spot" data-bm="{k}" data-group="{BM_GROUP[k]}" aria-label="{lbl}">
        <circle class="hit" cx="{x}" cy="{y}" r="19" fill="#000" fill-opacity="0" pointer-events="all"/>
        <circle class="halo" cx="{x}" cy="{y}" r="10"/>
        <circle class="core" cx="{x}" cy="{y}" r="6"/>
        {_chip(x, y, lbl)}
        <title>{lbl}</title></a>''' for k, x, y, lbl in spots
    )

    # --- Top-down cerebrum: hemispheres, fissure, richer gyri ---
    brain = """
    <path class="bm-silhouette" d="M170,44
      C210,44 244,60 260,92 C276,122 274,146 268,164
      C282,178 286,204 272,224 C285,242 281,272 258,286
      C246,300 224,306 200,302 C190,314 150,314 140,302
      C116,306 94,300 82,286 C59,272 55,242 68,224
      C54,204 58,178 72,164 C66,146 64,122 80,92
      C96,60 130,44 170,44 Z"/>
    <path class="bm-fissure" d="M170,50 C177,96 163,132 170,172 C177,210 165,252 170,300"/>
    """
    gyri = "".join(f'<path class="bm-gyrus" d="{d}"/>' for d in [
        "M120,86 C108,104 122,116 110,134", "M148,74 C138,96 152,110 142,132",
        "M220,86 C232,104 218,116 230,134", "M192,74 C202,96 188,110 198,132",
        "M100,150 C92,168 106,180 96,198", "M240,150 C248,168 234,180 244,198",
        "M132,196 C124,214 140,224 130,244", "M208,196 C216,214 200,224 210,244",
        "M96,120 C90,132 100,140 94,152", "M244,120 C250,132 240,140 246,152",
        "M150,250 C144,262 156,270 150,282", "M190,250 C196,262 184,270 190,282",
    ])

    # --- Living neural network overlay (nodes, axons, traveling signal pulses) ---
    N = [(170,80),(128,104),(212,104),(150,132),(190,132),(104,150),(236,150),
         (132,176),(208,176),(170,158),(120,206),(220,206),(156,224),(184,224),(170,252)]
    E = [(0,1),(0,2),(1,3),(2,4),(3,9),(4,9),(1,5),(2,6),(3,7),(4,8),(5,7),(6,8),
         (7,10),(8,11),(9,12),(9,13),(12,10),(13,11),(12,14),(13,14),(10,14),(11,14),(5,10),(6,11)]
    axons = "".join(
        f'<path id="bmE{i}" class="bm-axon" d="M{N[a][0]},{N[a][1]} L{N[b][0]},{N[b][1]}"/>'
        for i, (a, b) in enumerate(E))
    nodes = "".join(f'<circle class="bm-node" cx="{x}" cy="{y}" r="2.3"/>' for x, y in N)
    # A handful of pulses ride the axons (paused for reduced-motion via JS).
    pulse_edges = [(0, 3.4), (5, 4.1), (11, 3.0), (17, 4.6), (20, 3.7), (2, 5.0)]
    signals = "".join(
        f'<circle class="bm-signal" r="2.7"><animateMotion dur="{d}s" repeatCount="indefinite" '
        f'begin="{i*0.6}s"><mpath href="#bmE{ei}"/></animateMotion></circle>'
        for i, (ei, d) in enumerate(pulse_edges))

    # --- Anatomical region annotations (educational depth; leader line + label) ---
    def _region(lx, ly, tx, ty, anchor, label):
        return (f'<g class="bm-region"><line x1="{lx}" y1="{ly}" x2="{tx}" y2="{ty}"/>'
                f'<circle cx="{tx}" cy="{ty}" r="2"/>'
                f'<text x="{lx}" y="{ly}" text-anchor="{anchor}">{label}</text></g>')
    regions = "".join([
        _region(170, 26, 170, 52, "middle", "Frontal lobe"),
        _region(20, 132, 82, 138, "start", "Temporal lobe"),
        _region(322, 128, 258, 138, "end", "Parietal lobe"),
        _region(322, 250, 244, 250, "end", "Occipital lobe"),
        _region(322, 322, 188, 322, "end", "Brainstem"),
        _region(322, 430, 184, 430, "end", "Spinal cord"),
        _region(322, 542, 214, 552, "end", "Peripheral nerves"),
    ])

    # --- Brainstem, spinal cord (vertebrae), peripheral nerve fan ---
    stem = '<path class="bm-spine" d="M170,300 C170,320 168,336 170,352"/>'
    verts = "".join(
        f'<rect class="bm-vert" x="159" y="{y}" width="22" height="15" rx="6"/>'
        for y in range(356, 520, 22))
    nerve = "".join(f'<path class="bm-nerve" d="{d}"/>' for d in [
        "M170,470 C150,486 128,500 112,548", "M170,486 C190,502 210,516 226,560",
        "M170,452 C154,462 140,470 126,500", "M170,468 C186,478 200,486 214,516",
        "M170,506 C158,520 150,532 142,566", "M170,506 C182,520 190,532 198,566",
    ])

    defs = ('<defs>'
            '<linearGradient id="bmFig" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%" stop-color="rgba(243,236,220,0.22)"/>'
            '<stop offset="100%" stop-color="rgba(243,236,220,0.05)"/></linearGradient>'
            '<radialGradient id="bmHalo" cx="50%" cy="50%" r="50%">'
            '<stop offset="0%" stop-color="rgba(46,156,142,0.55)"/>'
            '<stop offset="100%" stop-color="rgba(46,156,142,0)"/></radialGradient>'
            '<filter id="bmGlow" x="-60%" y="-60%" width="220%" height="220%">'
            '<feGaussianBlur stdDeviation="2.4" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '</defs>')
    inner = (f'{brain}{gyri}{regions}<g class="bm-network">{axons}{nodes}{signals}</g>'
             f'{stem}{verts}{nerve}{spots_svg}')
    return (f'<svg class="bm-svg" viewBox="0 0 480 620" role="group" '
            f'aria-label="Interactive brain and nervous-system map — choose an area of concern">'
            f'{defs}<g transform="translate(70,0)">{inner}</g></svg>')

# ----------------------------------------------------------------------------
# UTIL
# ----------------------------------------------------------------------------
def _plain(s):
    return _re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&rsquo;", "'").replace("&ldquo;", '"').replace("&rdquo;", '"')

def linkify_phone(html_out):
    """Turn visible mentions of the phone number into tap-to-call links WITHOUT
    touching the <head> (meta/title/schema) or the insides of any tag/attribute —
    we only rewrite text nodes in the body, and never nest inside an existing link."""
    idx = html_out.find("</head>")
    head_part, rest = (html_out[:idx + 7], html_out[idx + 7:]) if idx != -1 else ("", html_out)
    protected = []
    def _protect(m):
        protected.append(m.group(0))
        return f"\x00{len(protected) - 1}\x00"
    # Protect existing anchors/scripts wholesale, then every remaining tag, so the
    # phone replacement can only land in real text between tags.
    rest = _re.sub(r"<(a|script)\b[^>]*>.*?</\1>", _protect, rest, flags=_re.S)
    rest = _re.sub(r"<[^>]+>", _protect, rest)
    rest = rest.replace(PHONE, f'<a href="tel:{PHONE_TEL}">{PHONE}</a>')
    rest = _re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], rest)
    return head_part + rest

# Correct condition-slug guesses that appear in generated copy (applied to every page).
_SLUG_FIX = {
    "conditions/concussion.html": "conditions/concussion-tbi.html",
    "conditions/epilepsy.html": "conditions/epilepsy-seizures.html",
    "conditions/headache-migraine.html": "conditions/headaches-migraine.html",
    "conditions/headaches-and-migraine.html": "conditions/headaches-migraine.html",
    "conditions/memory-loss-alzheimers.html": "conditions/memory-alzheimers.html",
    "conditions/memory-alzheimers-disease.html": "conditions/memory-alzheimers.html",
    "conditions/parkinsons-disease.html": "conditions/parkinsons-movement.html",
    "conditions/parkinsons.html": "conditions/parkinsons-movement.html",
    "conditions/multiple-sclerosis-ms.html": "conditions/multiple-sclerosis.html",
    "conditions/stroke-tia.html": "conditions/stroke.html",
    "conditions/neck-back-pain.html": "conditions/back-neck-pain.html",
    "conditions/neck-and-back-pain.html": "conditions/back-neck-pain.html",
    "conditions/sleep.html": "conditions/sleep-disorders.html",
}

def write(path, content):
    if path.endswith(".html"):
        content = linkify_phone(content)
        for _a, _b in _SLUG_FIX.items():
            content = content.replace(_a, _b)
        content = content.replace("<main>", '<main id="main">', 1)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("wrote", path)

def breadcrumb_schema(items):
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": _plain(n),
                 "item": (BASE + "/" + u) if u else BASE + "/"}
                for i, (n, u) in enumerate(items)]}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

# ============================================================================
# CONTENT — CONDITIONS
# ============================================================================
CONDITIONS = {
    "headaches-migraine": {
        "name": "Headache &amp; Migraine",
        "nav": "Headache &amp; Migraine",
        "tag": "Headache Medicine",
        "lede": "Chronic migraine, tension headache, cluster headache, and post-traumatic "
                "headache — evaluated and managed by neurologists who take head pain seriously.",
        "intro": "Recurring headaches are not something to simply live with. Our neurologists "
                 "distinguish migraine from tension-type, cluster, and secondary headaches, then "
                 "build a plan that may combine trigger management, acute and preventive "
                 "medications, and the newer CGRP-targeted therapies and Botox for chronic migraine.",
        "symptoms": ["Throbbing or one-sided head pain", "Aura, light &amp; sound sensitivity",
                     "Nausea with headaches", "Headaches 15+ days a month", "\"Worst headache of my life\""],
        "approach": [
            ("Careful diagnosis", "We separate primary headache disorders from secondary causes and order imaging only when it will change the plan."),
            ("Preventive strategy", "Daily preventives, CGRP monoclonal antibodies, and Botox for chronic migraine — matched to your pattern."),
            ("Acute relief", "A rescue plan that actually works, so an attack doesn't cost you a day."),
        ],
    },
    "epilepsy-seizures": {
        "name": "Epilepsy &amp; Seizures",
        "nav": "Epilepsy &amp; Seizures",
        "tag": "Epilepsy",
        "lede": "Seizures and epilepsy diagnosed with EEG and imaging, then managed toward the "
                "goal every patient shares — no seizures, no side effects.",
        "intro": "A first seizure, or seizures that keep breaking through, deserve a neurologist's "
                 "evaluation. We use EEG and MRI to characterize seizure type, then tailor "
                 "anti-seizure medication and lifestyle guidance — and coordinate advanced options "
                 "for seizures that remain difficult to control.",
        "symptoms": ["Convulsions or staring spells", "Sudden confusion or déjà vu",
                     "Loss of awareness", "Unexplained falls", "Recurrent unusual sensations"],
        "approach": [
            ("Characterize the seizures", "EEG and high-resolution MRI to define seizure type and, when possible, the source."),
            ("Medication that fits your life", "Effective seizure control with the fewest side effects and drug interactions."),
            ("Safety &amp; driving guidance", "Clear counseling on triggers, safety, and Florida driving rules."),
        ],
    },
    "parkinsons-movement": {
        "name": "Parkinson's &amp; Movement Disorders",
        "nav": "Parkinson's &amp; Movement",
        "tag": "Movement Disorders",
        "lede": "Parkinson's disease, essential tremor, dystonia, and other movement disorders — "
                "diagnosed early and managed to keep you steady and independent.",
        "intro": "Tremor, stiffness, and slowness can have many causes. Our neurologists "
                 "distinguish Parkinson's disease from essential tremor and related conditions, "
                 "and manage them with medication, Botox for dystonia and tremor, and coordinated "
                 "therapy — helping you stay active and independent for as long as possible.",
        "symptoms": ["Resting tremor", "Stiffness or slow movement", "Shuffling or balance changes",
                     "Cramping or twisting postures", "Handwriting getting smaller"],
        "approach": [
            ("Precise diagnosis", "Sorting Parkinson's from essential tremor and mimics — the diagnosis drives everything."),
            ("Medication optimization", "Fine-tuned dopaminergic and symptomatic therapy as needs change over time."),
            ("Botox &amp; procedures", "Targeted injections for dystonia and tremor, and referral pathways for advanced therapies."),
        ],
    },
    "memory-alzheimers": {
        "name": "Memory Loss, Alzheimer's &amp; Dementia",
        "nav": "Memory &amp; Alzheimer's",
        "tag": "Cognitive Neurology",
        "lede": "Memory concerns evaluated thoroughly — because treatable causes are common, and "
                "early answers open the most doors, including new disease-modifying therapies.",
        "intro": "Not all memory loss is Alzheimer's, and not all of it is permanent. We evaluate "
                 "cognition carefully, screen for reversible contributors, and — when appropriate — "
                 "discuss the latest disease-modifying treatments and clinical-trial options through "
                 "our on-site research institute.",
        "symptoms": ["Forgetfulness affecting daily life", "Repeating questions", "Word-finding trouble",
                     "Getting lost in familiar places", "Personality or mood changes"],
        "approach": [
            ("Thorough cognitive work-up", "Testing plus a search for reversible causes — medications, thyroid, B12, sleep, mood."),
            ("A clear plan for the family", "Diagnosis, expectations, safety, and support — explained without jargon."),
            ("Access to new therapies", "Disease-modifying options and clinical trials via our Premiere Research Institute."),
        ],
    },
    "multiple-sclerosis": {
        "name": "Multiple Sclerosis",
        "nav": "Multiple Sclerosis",
        "tag": "Neuroimmunology",
        "lede": "MS and related conditions managed with modern disease-modifying therapy and a "
                "long-term partnership focused on protecting function.",
        "intro": "Multiple sclerosis care has changed dramatically. We diagnose MS with MRI and "
                 "clinical evaluation, then match you to a modern disease-modifying therapy, manage "
                 "relapses and symptoms, and monitor over time — with access to MS clinical trials "
                 "through our research institute.",
        "symptoms": ["Numbness or tingling", "Vision changes in one eye", "Weakness or imbalance",
                     "Fatigue", "Heat-sensitive symptoms"],
        "approach": [
            ("Confident diagnosis", "MRI and clinical criteria to diagnose MS and rule out mimics."),
            ("Modern DMTs", "Selecting and monitoring disease-modifying therapy to reduce relapses and protect the brain."),
            ("Symptom &amp; relapse care", "Practical management of fatigue, spasticity, and flares."),
        ],
    },
    "stroke": {
        "name": "Stroke &amp; TIA",
        "nav": "Stroke &amp; TIA",
        "tag": "Vascular Neurology",
        "lede": "Stroke and TIA (\"mini-stroke\") follow-up and prevention — finding the cause and "
                "lowering the risk of the next one.",
        "intro": "After a stroke or TIA, the priority is preventing the next event. Our neurologists "
                 "investigate the underlying cause — blood pressure, heart rhythm, carotid disease, "
                 "and more — and build a prevention plan, while coordinating rehabilitation to help "
                 "you recover function.",
        "symptoms": ["Sudden weakness or numbness", "Face drooping", "Trouble speaking",
                     "Sudden vision loss", "Sudden severe dizziness"],
        "note": "A stroke is an emergency — call 911 immediately if symptoms are happening now.",
        "approach": [
            ("Find the cause", "Targeted testing of vessels, heart rhythm, and risk factors to explain why it happened."),
            ("Prevent the next one", "Medication and risk-factor management proven to lower recurrence."),
            ("Support recovery", "Coordinated referrals for rehabilitation and ongoing neurologic follow-up."),
        ],
    },
    "neuropathy": {
        "name": "Neuropathy &amp; Nerve Pain",
        "nav": "Neuropathy",
        "tag": "Peripheral Nerve",
        "lede": "Numbness, tingling, and burning in the hands and feet — diagnosed with EMG/nerve "
                "testing and managed to protect sensation and relieve pain.",
        "intro": "Peripheral neuropathy has dozens of causes, from diabetes to vitamin deficiencies "
                 "to nerve compression. We use nerve-conduction studies and EMG to characterize it, "
                 "search for the treatable cause, and manage nerve pain so it stops running your day.",
        "symptoms": ["Numbness or tingling in feet/hands", "Burning or electric pain",
                     "Weakness or balance trouble", "Sensitivity to touch", "Symptoms worse at night"],
        "approach": [
            ("Nerve testing", "EMG and nerve-conduction studies to define the type and severity."),
            ("Find the cause", "A focused search for reversible contributors so we treat the source, not just the symptom."),
            ("Pain relief", "Evidence-based medications and strategies to calm nerve pain."),
        ],
    },
    "neuromuscular": {
        "name": "Neuromuscular Disorders",
        "nav": "Neuromuscular",
        "tag": "Neuromuscular",
        "lede": "Muscle weakness, myasthenia gravis, ALS, and related neuromuscular conditions — "
                "diagnosed precisely and managed with expertise.",
        "intro": "Weakness that doesn't add up deserves a neuromuscular evaluation. Using EMG and "
                 "targeted testing, we diagnose conditions affecting the nerves and muscles — from "
                 "myasthenia gravis to inflammatory myopathies — and manage them with the newest "
                 "available therapies.",
        "symptoms": ["Muscle weakness or wasting", "Drooping eyelids or double vision",
                     "Difficulty swallowing", "Muscle cramps or twitching", "Fatigable weakness"],
        "approach": [
            ("EMG &amp; diagnosis", "Electrodiagnostic testing to localize and characterize the problem."),
            ("Targeted treatment", "Immune and symptomatic therapies matched to the specific diagnosis."),
            ("Ongoing partnership", "Close monitoring as we adjust care over time."),
        ],
    },
    "sleep-disorders": {
        "name": "Sleep Disorders",
        "nav": "Sleep Disorders",
        "tag": "Sleep Neurology",
        "lede": "Insomnia, restless legs, and sleep problems tied to neurologic conditions — "
                "because the brain heals when you sleep.",
        "intro": "Sleep and neurology are deeply connected. We evaluate insomnia, restless legs "
                 "syndrome, and sleep disturbances that accompany migraine, Parkinson's, and memory "
                 "disorders — and coordinate sleep studies when they're needed.",
        "symptoms": ["Trouble falling or staying asleep", "Restless, crawling leg sensations",
                     "Excessive daytime sleepiness", "Acting out dreams", "Unrefreshing sleep"],
        "approach": [
            ("Understand the sleep problem", "Sorting primary sleep disorders from neurologic causes."),
            ("Coordinated testing", "Referral for sleep studies when the history points to it."),
            ("Restorative plan", "Behavioral and medical strategies to rebuild healthy sleep."),
        ],
    },
    "back-neck-pain": {
        "name": "Neck &amp; Back Pain, Radiculopathy",
        "nav": "Neck &amp; Back Pain",
        "tag": "Spine Neurology",
        "lede": "Pinched nerves, sciatica, and spine-related pain evaluated from the neurologic "
                "angle — nerve, not just joint.",
        "intro": "When neck or back pain comes with numbness, tingling, or weakness, the nerves are "
                 "involved. We evaluate radiculopathy and spine-related nerve problems with exam and "
                 "EMG, clarify what's compressing the nerve, and guide you to the right treatment — "
                 "medical or surgical.",
        "symptoms": ["Pain radiating down an arm or leg", "Numbness or tingling", "Weakness in a limb",
                     "Sciatica", "Pain with certain positions"],
        "approach": [
            ("Localize the nerve", "Exam and EMG to pinpoint which nerve root is involved."),
            ("Clarify the cause", "Correlating imaging with your symptoms — so the plan targets the real problem."),
            ("Right-size the treatment", "From conservative care to the right specialist referral when needed."),
        ],
    },
}
# Extra list-only entries for the home map sidebar
BM_EXTRA = [("sleep-disorders", "Sleep Disorders"), ("neuromuscular", "Neuromuscular")]

def condition_schema(slug, c):
    data = {"@context": "https://schema.org", "@type": "MedicalCondition",
            "name": _plain(c["name"]),
            "description": _plain(c["lede"]),
            "possibleTreatment": {"@type": "MedicalTherapy", "name": "Neurologic evaluation and management",
                                  "provider": ORG_REF}}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def build_conditions():
    slugs = list(CONDITIONS.items())
    # ---- Hub ----
    cards = "".join(
        f'''<a class="cond-card reveal d{i%3+1}" href="{slug}.html">
          <span class="cond-tag">{c["tag"]}</span>
          <h3>{c["name"]}</h3>
          <p>{_plain(c["lede"])[:120]}…</p>
        </a>''' for i, (slug, c) in enumerate(slugs))
    body = f"""
<main>
{page_hero("What We Treat", "Conditions We <em class='accent'>Care For</em>",
  "From migraine and memory loss to epilepsy, Parkinson's, MS, stroke, and neuropathy — "
  "comprehensive neurologic care for the brain, spine, and nervous system, all in West Palm Beach.",
  '<div class="crumbs"><a href="../index.html">Home</a> / Conditions</div>')}
<section class="section">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">Comprehensive Neurology</span>
      <h2>Choose a <em class="accent">Condition</em></h2>
      <p class="lede">Every pathway begins with a thorough evaluation by a board-certified neurologist.</p>
    </div>
    <div class="cond-grid">{cards}</div>
  </div>
</section>
{cta_band(1)}
</main>
"""
    write("conditions/index.html",
          head("Neurology Conditions | Palm Beach Neurology",
               "Neurologic conditions treated at Palm Beach Neurology in West Palm Beach: migraine, "
               "epilepsy, Parkinson's, Alzheimer's, MS, stroke, neuropathy, and more.",
               depth=1, canonical="conditions/index.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Conditions", "conditions/index.html")]))
          + nav(1) + body + footer(1))

    # ---- Individual pages ----
    for i, (slug, c) in enumerate(slugs):
        symptoms = "".join(f"<li>{s}</li>" for s in c["symptoms"])
        approach = "".join(
            f'<div class="svc-feature reveal d{j%3+1}"><span class="svc-feature-num">{j+1:02d}</span>'
            f'<div><h3>{t}</h3><p>{d}</p></div></div>'
            for j, (t, d) in enumerate(c["approach"]))
        others = [(s2, c2) for s2, c2 in slugs if s2 != slug][:5]
        related = "".join(f'<a href="{s2}.html">{c2["nav"]}</a> ' for s2, c2 in others)
        note = (f'<p class="af-note" style="background:var(--cream);border:1px solid var(--line-gold);'
                f'border-radius:14px;padding:1rem 1.2rem;color:var(--ink);font-weight:600;">'
                f'⚠ {c["note"]}</p>') if c.get("note") else ""
        body = f"""
<main>
{page_hero(c["tag"], c["name"].replace("&amp;", "&amp;"), c["lede"],
  f'<div class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Conditions</a> / {c["nav"]}</div>')}
<section class="section">
  <div class="wrap two-col">
    <div class="prose reveal">
      <h2>Understanding {c["name"]}</h2>
      <p>{c["intro"]}</p>
      {note}
      <h2>Signs it's time to see a neurologist</h2>
      <ul class="check-list">{symptoms}</ul>
      <p style="margin-top:1.4rem;">If these sound familiar, a focused neurologic evaluation is the
      fastest route to answers. <a class="text-link" href="../appointments.html">Request an appointment &rarr;</a></p>
    </div>
    <aside class="side-card reveal d2">
      <h3>Start here</h3>
      <p>New patients are welcome. Our team will help verify your insurance and get you scheduled.</p>
      <a class="btn btn-coral" href="../appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
      <div class="side-meta">
        <p style="margin-bottom:0.4rem;">Prefer to call?</p>
        <a href="tel:{PHONE_TEL}">{PHONE}</a>
      </div>
    </aside>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Our Approach</span>
      <h2>How We Treat <em class="accent">{c["nav"]}</em></h2>
    </div>
    <div class="svc-feature-grid">{approach}</div>
    <div class="related-links reveal" style="margin-top:2.4rem;">
      <strong>Related conditions:</strong><br>{related}
    </div>
  </div>
</section>
{cta_band(1)}
</main>
"""
        write(f"conditions/{slug}.html",
              head(f"{_plain(c['nav'])} | Neurologists in West Palm Beach, FL",
                   (_plain(c['lede'])[:104].rsplit(' ', 1)[0] + " — Palm Beach Neurology, West Palm Beach FL."),
                   depth=1, canonical=f"conditions/{slug}.html", page_type="article",
                   extra_schema=condition_schema(slug, c) + breadcrumb_schema(
                       [("Home", ""), ("Conditions", "conditions/index.html"), (_plain(c["nav"]), f"conditions/{slug}.html")]))
              + nav(1) + body + footer(1))

# ============================================================================
# CONTENT — DOCTORS  (roster PENDING OWNER VERIFICATION — see header note)
# ============================================================================
# Authoritative roster + bios pulled verbatim from the practice's own About pages.
# Photo files live in assets/team/<slug>.jpg where slug = _doc_slug(name).
# (Sadowsky/Zuniga bios are concise interim summaries pending their verbatim About text.)
DOCTORS = [
    {"name": "Paul Winner", "creds": "DO, FAAN, FAHS",
     "focus": ["Headache &amp; Migraine", "Clinical Research"],
     "bio": "Dr. Paul Winner is President of the Florida Association for the Study of Headache and "
            "Neurologic Disorders, Past-President of the Florida Society of Neurology, and Past-President "
            "of the American Headache Society. An active member of the American Medical Association, "
            "American Osteopathic Association, American Academy of Neurology, and American Headache "
            "Society, he has published numerous journal articles and multiple textbooks for both the "
            "medical community and the general public, and is a national speaker and educator."},
    {"name": "Reed Stone", "creds": "MD, FAAN",
     "focus": ["Nerve &amp; Muscle", "EMG / NCV", "Spine"],
     "bio": "Board-certified in Neurology, Dr. Reed Stone has been part of Palm Beach Neurology for over "
            "38 years. A graduate of Brooklyn College (Biology, Magna Cum Laude), he earned his medical "
            "degree with honors from Universidad Central Del Este and completed his neurology residency "
            "at SUNY Downstate Medical Center, where he served as Chief Resident. He specializes in the "
            "diagnosis and treatment of spine, nerve, and muscle disorders, with expertise in EMG-NCV "
            "testing, and has extensive experience in medical-legal neurology including workers' "
            "compensation and personal injury."},
    {"name": "Arnaldo Da Silva", "creds": "MD, FAHS",
     "focus": ["Headache &amp; Migraine", "Neuromodulation"],
     "bio": "Dr. Arnaldo Neves Da Silva is Co-Director of the Palm Beach Headache Center and is "
            "board-certified in both Neurology and Headache Medicine, and a Fellow of the American "
            "Headache Society. Originally from Brazil, he began his career as a neurosurgeon before "
            "completing fellowships in Neuro-oncology and Radiosurgery at the University of Virginia, a "
            "Neurology residency at the University of Chicago, and a headache fellowship at the Cleveland "
            "Clinic. His special interests include cell therapies for migraine, interventional pain "
            "procedures, and neuromodulation. He is fluent in English, Portuguese, and Spanish."},
    {"name": "Tara Becker", "creds": "MD",
     "focus": ["Epilepsy &amp; Seizures", "EEG"],
     "bio": "Dr. Tara Becker is dual board-certified in Neurology and Epilepsy. She earned her medical "
            "degree from the Florida State University College of Medicine, completed her neurology "
            "residency at the Mayo Clinic in Jacksonville, and pursued fellowship training in Epilepsy "
            "at the University of Pennsylvania. She specializes in the diagnosis and management of adults "
            "with epilepsy and seizures, with advanced expertise in EEG including ambulatory continuous "
            "video EEG monitoring, evaluation for epilepsy surgery, and neuromodulation devices such as "
            "vagus nerve stimulation (VNS)."},
    {"name": "Robert Coppola", "creds": "DO",
     "focus": ["Multiple Sclerosis", "Neuro-immunology"],
     "bio": "Born and raised in Ft. Lauderdale, Dr. Robert Coppola earned his Bachelor of Science in "
            "Biology with honors and his medical degree from Nova Southeastern University, then completed "
            "his neurology residency at Larkin Community Hospital in Miami, where he served as Chief "
            "Resident. He specializes in the diagnosis and management of neurological disorders in "
            "adults, with a subspecialty focus on multiple sclerosis and related neuro-immunological "
            "conditions, and completed fellowship training at the University of Miami."},
    {"name": "Manisha Korb", "creds": "MD",
     "focus": ["Neuromuscular", "ALS", "EMG"],
     "bio": "Dr. Manisha Korb is a neuromuscular neurologist, board-certified in both Neurology and "
            "Electrodiagnostic Medicine. She earned her medical degree from the University of Virginia, "
            "completed her residency and a neuromuscular electrophysiology fellowship at the University "
            "of Chicago (where she served as Chief Resident), and spent seven years at UC Irvine as an "
            "associate clinical professor in a designated MDA and ALS Center. Her interests include SMA, "
            "neuropathy, GBS, CIDP, ALS, myasthenia gravis, and muscular dystrophy; she performs NCS/EMG, "
            "Botox for spasticity, skin biopsies, and intrathecal medication administration."},
    {"name": "Michael Alosilla", "creds": "MD",
     "focus": ["Movement Disorders", "Parkinson's &amp; DBS"],
     "bio": "Dr. Michael Alosilla is a fellowship-trained neurologist subspecializing in Movement "
            "Disorders. He earned his medical degree from Universidad Peruana Cayetano Heredia in Lima, "
            "Peru, and completed his fellowship at MedStar Georgetown University Hospital, with advanced "
            "training in Parkinson's disease, atypical parkinsonian syndromes, dystonia, tremor, and "
            "ataxia. His interests include movement disorders and neurodegenerative conditions such as "
            "Lewy body and frontotemporal dementia. He is skilled in botulinum toxin injections, deep "
            "brain stimulation (DBS) programming, and emerging infusion therapies, and is fluent in "
            "English and Spanish."},
    {"name": "Carl Sadowsky", "creds": "MD, FAAN",
     "focus": ["Memory &amp; Alzheimer's", "Clinical Research"],
     "bio": "A Fellow of the American Academy of Neurology, Dr. Carl Sadowsky focuses on memory and "
            "cognitive disorders, including Alzheimer's disease, and is actively involved in clinical "
            "research advancing new treatments for memory loss."},
    {"name": "Jose Zuniga", "creds": "MD",
     "focus": ["General Neurology"],
     "bio": "Dr. Jose Zuniga is a board-certified neurologist who cares for the full range of "
            "neurologic conditions, treating every patient and family with respect, empathy, and "
            "professionalism."},
]

def _doc_slug(name):
    return _plain(name).lower().replace(",", "").replace(".", "").replace(" ", "-")

def person_schema():
    people = []
    for d in DOCTORS:
        people.append({
            "@type": "Physician",
            "@id": f"{BASE}/our-doctors.html#{_doc_slug(d['name'])}",
            "name": "Dr. " + _plain(d["name"]),
            "honorificPrefix": "Dr.",
            "honorificSuffix": _plain(d["creds"]),
            "jobTitle": "Neurologist",
            "medicalSpecialty": "Neurologic",
            "description": _plain(d["bio"]),
            "worksFor": ORG_REF,
        })
    data = {"@context": "https://schema.org", "@graph": people}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def build_doctors():
    cards = ""
    for i, d in enumerate(DOCTORS):
        slug = _doc_slug(d['name'])
        focus = "".join(f"<span>{f}</span>" for f in d["focus"])
        cards += f'''
        <article class="team-card reveal d{i%3+1}" id="{slug}">
          <a class="team-photo" href="doctors/{slug}.html" aria-label="Dr. {_plain(d['name'])} — full profile"><img src="assets/team/{slug}.jpg" alt="Dr. {_plain(d['name'])}, {_plain(d['creds'])}" width="640" height="640" loading="lazy" decoding="async"></a>
          <h3><a href="doctors/{slug}.html">Dr. {d["name"]}</a></h3>
          <div class="role">{d["creds"]}</div>
          <div class="pw-tags" style="justify-content:center;margin-top:0.7rem;">{focus}</div>
          <p>{d["bio"]}</p>
          <a class="text-link" href="doctors/{slug}.html">View full profile &rarr;</a>
        </article>'''
    body = f"""
<main>
{page_hero("Meet the Team", "Our <em class='accent'>Doctors</em>",
  "Board-certified neurologists caring for the brain, spine, and nervous system for more than "
  "25 years — right here in West Palm Beach.",
  '<div class="crumbs"><a href="index.html">Home</a> / Our Doctors</div>')}
<section class="section" style="padding-bottom:0;">
  <div class="wrap"><div class="team-banner reveal"><img src="assets/media/team-group.jpg" alt="The Palm Beach Neurology care team" loading="lazy"></div></div>
</section>"""
    body += f"""
<section class="section">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">Clinical Neuroscience Professionals</span>
      <h2>Expertise You Can <em class="accent">Trust</em></h2>
      <p class="lede">Our clinical neuroscience professionals are board-certified neurologists trained
      to diagnose and treat diseases and conditions of the nervous system — focused on diagnosis,
      treatment, prevention, rehabilitation, and education for you and your family.</p>
    </div>
    <div class="team-grid">{cards}</div>
  </div>
</section>
<section class="section on-ink">
  {neuro_field(0.5)}
  <div class="wrap" style="position:relative;z-index:1;">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow on-dark">More Than a Clinic</span>
        <h2>A research institute <em class="accent">under the same roof</em></h2>
        <p style="margin-top:1.2rem;">Our physicians are active in clinical research through the
        Premiere Research Institute — giving our patients access to tomorrow's therapies for
        Alzheimer's, migraine, and MS, today.</p>
        <div class="mt-2"><a class="btn btn-ghost" href="clinical-research.html">Explore Clinical Research <span class="arr">&rarr;</span></a></div>
      </div>
      <div class="reveal d2">
        <div class="stat-row">
          <div><strong data-count="25" data-suffix="+">25+</strong><span>Years of Expertise</span></div>
          <div><strong>Board</strong><span>Certified Neurologists</span></div>
          <div><strong>On-site</strong><span>Clinical Research</span></div>
          <div><strong>New</strong><span>Patients Welcome</span></div>
        </div>
      </div>
    </div>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("our-doctors.html",
          head("Our Doctors | Palm Beach Neurology, West Palm Beach",
               "Meet the board-certified neurologists of Palm Beach Neurology in West Palm Beach, FL — "
               "25+ years caring for the brain, spine, and nervous system.",
               canonical="our-doctors.html",
               extra_schema=person_schema() + breadcrumb_schema([("Home", ""), ("Our Doctors", "our-doctors.html")]))
          + nav(0) + body + footer(0))

# Map a physician's focus/bio keywords to the conditions they most treat (for cross-links).
_FOCUS_COND = [
    ("headache", "headaches-migraine"), ("migraine", "headaches-migraine"),
    ("epilepsy", "epilepsy-seizures"), ("seizure", "epilepsy-seizures"), ("eeg", "epilepsy-seizures"),
    ("multiple sclerosis", "multiple-sclerosis"), ("immunolog", "multiple-sclerosis"),
    ("movement", "parkinsons-movement"), ("parkinson", "parkinsons-movement"), ("dbs", "parkinsons-movement"),
    ("tremor", "parkinsons-movement"),
    ("memory", "memory-alzheimers"), ("alzheimer", "memory-alzheimers"), ("cognit", "memory-alzheimers"),
    ("neuromuscular", "neuromuscular"), ("als", "neuromuscular"), ("myasthenia", "neuromuscular"),
    ("emg", "neuropathy"), ("nerve", "neuropathy"), ("neuropathy", "neuropathy"),
    ("spine", "back-neck-pain"), ("stroke", "stroke"), ("sleep", "sleep-disorders"),
]

def _doctor_conditions(d):
    hay = (" ".join(d["focus"]) + " " + d["bio"]).lower()
    slugs = []
    for kw, slug in _FOCUS_COND:
        if kw in hay and slug in CONDITIONS and slug not in slugs:
            slugs.append(slug)
    return slugs[:6]

def build_doctor_pages():
    for d in DOCTORS:
        slug = _doc_slug(d["name"])
        name = _plain(d["name"])
        creds = _plain(d["creds"])
        focus_chips = "".join(f"<span>{f}</span>" for f in d["focus"])
        conds = _doctor_conditions(d)
        cond_links = "".join(
            f'<a class="cond-card reveal d{i%3+1}" href="../conditions/{s}.html">'
            f'<span class="cond-tag">{CONDITIONS[s]["tag"]}</span><h3>{CONDITIONS[s]["nav"]}</h3></a>'
            for i, s in enumerate(conds))
        conds_section = f"""
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Areas of Focus</span>
      <h2>Conditions Dr. {name.split()[-1]} <em class="accent">Treats</em></h2>
    </div>
    <div class="cond-grid">{cond_links}</div>
  </div>
</section>""" if cond_links else ""
        lede = f"{creds} · " + ", ".join(_plain(f) for f in d["focus"])
        physician = {
            "@context": "https://schema.org", "@type": "Physician",
            "@id": f"{BASE}/doctors/{slug}.html#physician",
            "name": "Dr. " + name, "honorificPrefix": "Dr.", "honorificSuffix": creds,
            "jobTitle": "Neurologist", "medicalSpecialty": "Neurologic",
            "description": _plain(d["bio"]), "image": f"{BASE}/assets/team/{slug}.jpg",
            "url": f"{BASE}/doctors/{slug}.html", "worksFor": ORG_REF,
            "sameAs": f"{BASE}/our-doctors.html#{slug}",
        }
        physician_schema = ('<script type="application/ld+json">'
                            + _json.dumps(physician, ensure_ascii=False) + "</script>\n")
        body = f"""
<main>
{page_hero("Neurologist", f"Dr. {name}", lede,
  f'<div class="crumbs"><a href="../index.html">Home</a> / <a href="../our-doctors.html">Our Doctors</a> / Dr. {name}</div>')}
<section class="section">
  <div class="wrap two-col">
    <div class="prose reveal">
      <h2>About Dr. {name}</h2>
      <p>{d["bio"]}</p>
      <div class="pw-tags" style="margin:1.6rem 0 0.4rem;">{focus_chips}</div>
      <p style="margin-top:1.4rem;">New patients are welcome. To see Dr. {name.split()[-1]},
      <a class="text-link" href="../appointments.html">request an appointment &rarr;</a> or call
      <a class="text-link" href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
    </div>
    <aside class="side-card reveal d2">
      <div class="team-photo" style="margin-bottom:1.2rem;"><img src="../assets/team/{slug}.jpg" alt="Dr. {name}, {creds}" width="640" height="640" loading="lazy" decoding="async"></div>
      <h3>Dr. {name}</h3>
      <div class="role" style="color:var(--coral-text);font-weight:700;margin-bottom:0.4rem;">{creds}</div>
      <a class="btn btn-coral" href="../appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
      <div class="side-meta">
        <p style="margin-bottom:0.4rem;">Prefer to call?</p>
        <a href="tel:{PHONE_TEL}">{PHONE}</a>
      </div>
    </aside>
  </div>
</section>
{conds_section}
{cta_band(1)}
</main>
"""
        write(f"doctors/{slug}.html",
              head(f"Dr. {name}, {creds} | Palm Beach Neurology",
                   (f"Dr. {name}, {creds} — " + ", ".join(_plain(f) for f in d["focus"])
                    + ". Board-certified neurologic care at Palm Beach Neurology in West Palm Beach, FL; new patients welcome.")[:160],
                   depth=1, canonical=f"doctors/{slug}.html", page_type="article",
                   extra_schema=physician_schema + breadcrumb_schema(
                       [("Home", ""), ("Our Doctors", "our-doctors.html"), ("Dr. " + name, f"doctors/{slug}.html")]))
              + nav(1) + body + footer(1))

# ============================================================================
# CLINICAL RESEARCH
# ============================================================================
def build_research():
    trials = [
        ("Alzheimer's &amp; Memory", "Studies of investigational treatments aimed at slowing memory "
         "loss — including options for people with early symptoms and those at risk."),
        ("Migraine", "Trials of new approaches to prevent and treat migraine for people who haven't "
         "found lasting relief."),
        ("Multiple Sclerosis", "Research into next-generation therapies to reduce relapses and "
         "protect long-term function in MS."),
    ]
    trial_cards = "".join(
        f'<div class="svc-feature reveal d{i%3+1}"><span class="svc-feature-num">{i+1:02d}</span>'
        f'<div><h3>{t}</h3><p>{d}</p></div></div>' for i, (t, d) in enumerate(trials))
    steps = [("Screen", "A no-cost screening visit to see whether a study is a fit for you."),
             ("Enroll", "If you qualify and choose to join, our team walks you through informed consent."),
             ("Participate", "Study visits with close monitoring by our physicians and research staff."),
             ("Contribute", "You help advance care for the next generation of patients — and may access tomorrow's therapies today.")]
    steps_html = "".join(
        f'<div class="svc-step reveal d{i%4+1}"><div class="svc-step-dot">{i+1}</div>'
        f'<h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(steps))
    body = f"""
<main>
{page_hero("Premiere Research Institute", "Clinical <em class='accent'>Research</em>",
  "Our on-site research institute gives Palm Beach patients access to carefully monitored clinical "
  "trials — tomorrow's therapies for Alzheimer's, migraine, and MS, available today.",
  '<div class="crumbs"><a href="index.html">Home</a> / Clinical Research</div>')}
<section class="section">
  <div class="wrap">
    <div class="center reveal" style="margin-bottom:2rem;">
      <a href="{RESEARCH_URL}" target="_blank" rel="noopener" aria-label="Visit the Premiere Research Institute">
        <img class="prem-logo" src="assets/media/premiere-research.png" alt="Premiere Research Institute" style="margin:0 auto;" width="230" height="200"></a>
    </div>
    <div class="section-head reveal">
      <span class="eyebrow">Why It Matters</span>
      <h2>Advancing Neurology, <em class="accent">Right Here</em></h2>
      <p class="lede">Clinical trials are how every treatment we use today came to be. Participating
      can give you access to investigational therapies and expert oversight — at no cost to you.
      To reach the research team directly, call {RESEARCH_PHONE}.</p>
    </div>
    <div class="svc-feature-grid">{trial_cards}</div>
    <p style="max-width:70ch;margin-top:1.6rem;">Participants receive ongoing expert care throughout
    every study. Eligibility and available trials change over time, and participation is always
    voluntary — talk with our team to learn what is currently enrolling and whether it may be right for you.</p>
    <div class="mt-2"><a class="text-link" href="{RESEARCH_URL}" target="_blank" rel="noopener">Visit the Premiere Research Institute &rarr;</a></div>
  </div>
</section>
<section class="section on-ink">
  {neuro_field(0.55)}
  <div class="wrap" style="position:relative;z-index:1;">
    <div class="section-head center reveal">
      <span class="eyebrow on-dark">How It Works</span>
      <h2>From Screening to <em class="accent">Contribution</em></h2>
    </div>
    <div class="svc-process">{steps_html}</div>
    <div class="center mt-3 reveal">
      <a class="btn btn-coral" href="appointments.html">Ask About Research <span class="arr">&rarr;</span></a>
    </div>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("clinical-research.html",
          head("Clinical Research & Trials | Palm Beach Neurology",
               "The Premiere Research Institute at Palm Beach Neurology runs clinical trials in "
               "Alzheimer's, migraine, and MS in West Palm Beach, FL. Learn how to participate.",
               canonical="clinical-research.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Clinical Research", "clinical-research.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# APPOINTMENTS  (their real offerings: FREE Memory Screen + New Patient)
# ============================================================================
def build_appointments():
    options = [
        ("FREE Memory Screen", "30 min",
         "A brief, no-cost screening designed to assess memory and cognitive function and identify "
         "potential memory problems or early signs of conditions like mild cognitive impairment (MCI) "
         "or dementia — simple, structured tests of memory, attention, and thinking skills.", "Free · 30 min"),
        ("New Patient Appointment", "1 hour",
         "A comprehensive first visit to develop a complete medical profile, identify any risk "
         "factors, and create a personalized care plan. Please bring a list of current medications, "
         "past medical records, previous test results, and insurance information.", "New patients welcome"),
    ]
    opt_cards = "".join(
        f'''<div class="cond-card reveal d{i+1}" style="padding:2rem 1.9rem;">
          <span class="cond-tag">{badge}</span>
          <h3>{t}</h3>
          <p style="margin-top:0.5rem;">{d}</p>
          <p style="margin-top:1rem;font-weight:700;color:var(--ink);">⏱ {dur}</p>
        </div>''' for i, (t, dur, d, badge) in enumerate(options))
    body = f"""
<main>
{page_hero("Get Started", "Request an <em class='accent'>Appointment</em>",
  "New patients are welcome. Choose a free memory screen or a full new-patient visit, then send "
  "the request below — our front desk will call you back to confirm and verify insurance.",
  '<div class="crumbs"><a href="index.html">Home</a> / Appointments</div>')}
<section class="section">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">Appointment Options</span>
      <h2>Two Ways to <em class="accent">Begin</em></h2>
    </div>
    <div class="cond-grid" style="max-width:820px;margin:0 auto;grid-template-columns:1fr 1fr;">{opt_cards}</div>
    <div class="cht-callout reveal" style="margin:2.6rem auto 0;text-align:center;">
      <h3>Save time — complete your new-patient forms first</h3>
      <p style="margin:0 auto;">Fill out your new patient paperwork before your appointment to save
      time in the waiting room. Questions about any of the forms? Call our office at {PHONE}.</p>
      <div class="mt-2"><a class="btn btn-ink" href="{FORMS_PDF}" download>Download New Patient Paperwork (PDF)</a></div>
    </div>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap contact-grid">
    <div class="appt-form-card reveal">
      <h2 class="h3-size">Request an Appointment</h2>
      <p class="af-sub">Tell us a little about what you need and our front desk will call you back to confirm.</p>
      <form class="appt-form" id="appt-form" data-endpoint="https://formsubmit.co/ajax/{EMAIL}" data-done="af-done" data-subject="New appointment request — Palm Beach Neurology" novalidate>
        <div class="af-field">
          <label for="af-name">Full name *</label>
          <input id="af-name" name="name" type="text" autocomplete="name" required maxlength="200">
        </div>
        <div class="af-two">
          <div class="af-field">
            <label for="af-phone">Phone *</label>
            <input id="af-phone" name="phone" type="tel" autocomplete="tel" required maxlength="40" placeholder="Your phone number">
          </div>
          <div class="af-field">
            <label for="af-email">Email</label>
            <input id="af-email" name="email" type="email" autocomplete="email" maxlength="200">
          </div>
        </div>
        <div class="af-field">
          <label for="af-type">Appointment type</label>
          <select id="af-type" name="type">
            <option>New Patient Appointment</option>
            <option>FREE Memory Screen</option>
            <option>Follow-up</option>
            <option>Clinical research inquiry</option>
          </select>
        </div>
        <div class="af-field">
          <label for="af-reason">Reason for visit *</label>
          <textarea id="af-reason" name="reason" required maxlength="2000" placeholder="e.g. frequent migraines, memory concerns, numbness in the feet…"></textarea>
        </div>
        <div class="af-field">
          <label style="display:flex;gap:0.6rem;align-items:flex-start;font-size:0.92rem;font-weight:500;text-transform:none;letter-spacing:0;color:var(--text);cursor:pointer;">
            <input type="checkbox" name="trials" value="yes" style="margin-top:0.2rem;width:18px;height:18px;accent-color:var(--coral);flex-shrink:0;">
            <span>Yes! I'd also like to learn more about clinical trials.</span>
          </label>
        </div>
        <p class="af-note">This is a contact request, not a medical record — please don't include
        detailed health history or sensitive information here. We only need the basics to call you back.</p>
        <p class="af-error" id="af-error" role="alert"></p>
        <button class="btn btn-coral" type="submit">Send Request <span class="arr">&rarr;</span></button>
      </form>
      <div class="af-done" id="af-done" hidden>
        <div class="af-check">&#10003;</div>
        <h3>Request received!</h3>
        <p id="af-done-msg">Thank you — our front desk will call you back to confirm. If you haven't
        heard from us within 48 hours, please call <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
      </div>
    </div>
    <div class="reveal d2">
      <div class="contact-card" style="margin-bottom:1.5rem;">
        <h3>Palm Beach Neurology</h3>
        <div class="c-row"><span class="c-label">Address</span><span>{ADDR_STREET}<br>{ADDR_CITY}, {ADDR_STATE} {ADDR_ZIP}</span></div>
        <div class="c-row"><span class="c-label">Phone</span><a href="tel:{PHONE_TEL}">{PHONE}</a></div>
        <div class="c-row"><span class="c-label">Hours</span><span>Monday – Thursday, 8:00 AM – 5:00 PM<br>Friday, 8:00 AM – 4:30 PM</span></div>
        <div class="c-row"><span class="c-label">Portal</span><a href="{PORTAL}">Patient Portal &rarr;</a></div>
        <a class="btn btn-coral mt-2" href="tel:{PHONE_TEL}">Call to Book <span class="arr">&rarr;</span></a>
      </div>
      <iframe class="map-frame" src="{MAPS_EMBED}" title="Map to Palm Beach Neurology" loading="lazy" referrerpolicy="no-referrer-when-downgrade" style="min-height:300px;"></iframe>
    </div>
  </div>
</section>
</main>
"""
    write("appointments.html",
          head("Request an Appointment | Palm Beach Neurology",
               "Request a neurology appointment in West Palm Beach — free memory screen or new-patient "
               "visit. Call 561-845-0500 or send a request online. New patients welcome.",
               canonical="appointments.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Appointments", "appointments.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# CONTACT
# ============================================================================
def build_contact():
    body = f"""
<main>
{page_hero("We're Here to Help", "Contact <em class='accent'>Palm Beach Neurology</em>",
  "Call, request an appointment, or stop by our West Palm Beach office. Our team is glad to help "
  "you get scheduled and verify your insurance.",
  '<div class="crumbs"><a href="index.html">Home</a> / Contact</div>')}
<section class="section">
  <div class="wrap contact-grid">
    <div class="reveal">
      <div class="contact-card">
        <h2 class="h3-size">Palm Beach Neurology &amp; Premiere Research Institute</h2>
        <div class="c-row"><span class="c-label">Address</span><span>{ADDR_STREET}<br>{ADDR_CITY}, {ADDR_STATE} {ADDR_ZIP}</span></div>
        <div class="c-row"><span class="c-label">Phone</span><a href="tel:{PHONE_TEL}">{PHONE}</a></div>
        <div class="c-row"><span class="c-label">Research</span><span><a href="tel:+15618519400">{RESEARCH_PHONE}</a> · clinical trials</span></div>
        <div class="c-row"><span class="c-label">Fax</span><span>{FAX}</span></div>
        <div class="c-row"><span class="c-label">Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
        <div class="c-row"><span class="c-label">Hours</span><span>Monday – Thursday, 8 AM – 5 PM · Friday, 8 AM – 4:30 PM</span></div>
        <div class="hero-ctas" style="margin-top:1.6rem;">
          <a class="btn btn-coral" href="appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
          <a class="btn btn-ink" href="tel:{PHONE_TEL}">Call Now</a>
        </div>
      </div>
    </div>
    <div class="reveal d2">
      <iframe class="map-frame" src="{MAPS_EMBED}" title="Map to Palm Beach Neurology" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("contact.html",
          head("Contact | Palm Beach Neurology, West Palm Beach FL",
               f"Contact Palm Beach Neurology: {ADDR_STREET}, {ADDR_CITY}, {ADDR_STATE} {ADDR_ZIP}. "
               f"Call {PHONE} to schedule with a board-certified neurologist.",
               canonical="contact.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Contact", "contact.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# FAQ
# ============================================================================
FAQ_CATEGORIES = [
    ("visit", "Your Visit", [
        ("Do I need a referral to see a neurologist?",
         "It depends on your insurance plan. Many PPO plans let you self-refer, while some HMO and "
         "Medicare Advantage plans require a referral from your primary care physician. Call us at "
         f"{PHONE} and our team will help you check before your visit."),
        ("What should I bring to my first appointment?",
         "Please bring your photo ID, insurance card, a list of your current medications, any recent "
         "brain or spine imaging (MRI/CT) on disc or through your portal, and any relevant records or "
         "referral paperwork. A family member is welcome — especially for memory-related visits."),
        ("How long is a new-patient appointment?",
         "New-patient neurology visits are scheduled for about one hour so your neurologist has time "
         "to review your history, examine you, and explain the plan."),
        ("What is the FREE Memory Screen?",
         "It's a no-cost, confidential 30-minute screening of memory and thinking — a simple first "
         "step if you or a loved one has noticed changes. It isn't a diagnosis, but it helps us decide "
         "whether a fuller evaluation is worthwhile."),
    ]),
    ("insurance", "Insurance &amp; Billing", [
        ("Which insurance plans do you accept?",
         "We accept many major insurance plans, including Medicare. Because coverage varies by plan, "
         f"the fastest way to confirm is to call us at {PHONE} with your card handy and we'll verify "
         "your benefits."),
        ("Do you see new patients?",
         "Yes — we are accepting new patients. You can request an appointment online or call the office."),
        ("How much will my visit cost?",
         "Your cost depends on your specific insurance plan, deductible, and the services provided. "
         "Our front desk will help you understand your coverage before your visit whenever possible."),
    ]),
    ("care", "Our Care", [
        ("What conditions do you treat?",
         "We care for the full range of neurologic conditions — headache and migraine, epilepsy and "
         "seizures, Parkinson's and movement disorders, Alzheimer's and memory loss, multiple "
         "sclerosis, stroke and TIA, neuropathy, neuromuscular disorders, sleep problems, and "
         "spine-related nerve pain."),
        ("Do you offer testing like EEG and EMG?",
         "Our neurologists use tools such as EEG (for seizures) and EMG/nerve-conduction studies "
         "(for neuropathy and neuromuscular conditions) as part of the work-up. Ask our team about "
         "what's available and what your evaluation may involve."),
        ("What clinical trials are available?",
         "Through our on-site Premiere Research Institute, we run carefully monitored trials in areas "
         "such as Alzheimer's, migraine, and MS. Available studies change over time — ask us what's "
         "currently enrolling."),
    ]),
    ("urgent", "Urgent Symptoms", [
        ("When is a symptom an emergency?",
         "Call 911 immediately for sudden weakness or numbness on one side, face drooping, trouble "
         "speaking, sudden severe headache, sudden vision loss, or a first-time seizure that won't "
         "stop. These can be signs of a stroke or other emergency and shouldn't wait for an office visit."),
        ("I had a mini-stroke (TIA) — how soon should I be seen?",
         "A TIA is a warning sign and should be evaluated promptly. Call your physician or seek "
         "emergency care right away, and let us help you with prompt neurologic follow-up and "
         "prevention planning."),
    ]),
]
FAQS = [qa for _s, _t, pairs in FAQ_CATEGORIES for qa in pairs]

def faq_schema(pairs):
    data = {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": _plain(q),
                 "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}}
                for q, a in pairs]}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def build_faq():
    total = len(FAQS)
    bubbles = (f'<button type="button" class="faq-bubble active" data-cat="all" aria-pressed="true">'
               f'All Questions <span class="fb-count">({total})</span></button>')
    bubbles += "".join(
        f'<button type="button" class="faq-bubble" data-cat="{sid}" aria-pressed="false">{title} <span class="fb-count">({len(pairs)})</span></button>'
        for sid, title, pairs in FAQ_CATEGORIES)
    sections = ""
    for sid, title, pairs in FAQ_CATEGORIES:
        items = "".join(
            f'<details class="faq-item reveal" data-cat="{sid}"><summary>{q}</summary><div class="faq-a">{a}</div></details>'
            for q, a in pairs)
        sections += f'''
  <section class="faq-cat" id="{sid}" aria-labelledby="{sid}-h" data-cat-section="{sid}">
    <div class="faq-cat-head"><h2 id="{sid}-h">{title}</h2><span class="faq-count">{len(pairs)} answers</span></div>
    <div class="faq-list">{items}</div>
  </section>'''
    body = f"""
<main>
{page_hero("Questions, Answered", "Frequently Asked <em class='accent'>Questions</em>",
  f"{total} straight answers about referrals, insurance, what to expect, and when a symptom is urgent — "
  "filter by topic or search below.",
  '<div class="crumbs"><a href="index.html">Home</a> / FAQ</div>')}
<div class="faq-jump-bar">
  <div class="faq-jump" role="group" aria-label="Filter FAQs by category">{bubbles}</div>
</div>
<section class="section">
  <div class="wrap">
    <div class="faq-toolbar reveal">
      <label class="sr-only" for="faq-search">Search the FAQs</label>
      <input type="search" id="faq-search" class="faq-search" placeholder="Search questions… (e.g. referral, Medicare, memory)" autocomplete="off">
      <div class="faq-tools">
        <button type="button" class="faq-tool" id="faq-expand">Expand all</button>
        <button type="button" class="faq-tool" id="faq-collapse">Collapse all</button>
      </div>
    </div>
    <p class="sr-only" aria-live="polite" id="faq-live"></p>
    <p class="faq-empty faq-hidden" id="faq-empty">No questions match your search — try a different word, or call <a href="tel:{PHONE_TEL}">{PHONE}</a> and ask us directly.</p>
    {sections}
    <div class="center mt-3 reveal"><p class="lede" style="margin:0 auto 1.2rem;">Still have a question?</p>
    <a class="btn btn-ink" href="contact.html">Contact Us <span class="arr">&rarr;</span></a></div>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("faq.html",
          head("Neurology FAQ | Palm Beach Neurology, West Palm Beach",
               "Answers about referrals, insurance, first visits, testing, and urgent symptoms at "
               "Palm Beach Neurology in West Palm Beach, FL.",
               canonical="faq.html",
               extra_schema=faq_schema(FAQS) + breadcrumb_schema([("Home", ""), ("FAQ", "faq.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# HOME
# ============================================================================
def build_home():
    # --- Neuro Explorer data (all 10 conditions, keyed to figure hotspots) ---
    key_to_slug = {"migraine": "headaches-migraine", "memory": "memory-alzheimers",
                   "epilepsy": "epilepsy-seizures", "movement": "parkinsons-movement",
                   "stroke": "stroke", "ms": "multiple-sclerosis", "sleep": "sleep-disorders",
                   "spine": "back-neck-pain", "neuropathy": "neuropathy", "neuromuscular": "neuromuscular"}
    bm_area = {
        "migraine": "Cerebrum · pain &amp; vascular pathways",
        "memory": "Temporal lobe · memory networks",
        "epilepsy": "Cerebral cortex · electrical activity",
        "movement": "Basal ganglia · movement circuits",
        "stroke": "Cerebrum · blood supply",
        "ms": "Brain &amp; spinal cord · myelin",
        "sleep": "Brainstem · sleep–wake regulation",
        "spine": "Spinal cord · nerve roots",
        "neuropathy": "Peripheral nerves",
        "neuromuscular": "Nerves &amp; muscle",
    }

    def _bm_item(key):
        slug = key_to_slug[key]; c = CONDITIONS[slug]
        return (f'<a class="bm-item" data-bm="{key}" data-group="{BM_GROUP[key]}" href="conditions/{slug}.html">'
                f'<span class="bm-item-dot"></span>'
                f'<span class="bm-item-name">{c["nav"]}</span>'
                f'<span class="bm-tag">{c["tag"]}</span></a>')
    bm_order = ["migraine", "memory", "epilepsy", "movement", "ms",
                "stroke", "sleep", "spine", "neuropathy", "neuromuscular"]
    bm_list_html = "".join(_bm_item(k) for k in bm_order)

    bm_data = {}
    for key, slug in key_to_slug.items():
        c = CONDITIONS[slug]
        appr = c.get("approach", [])
        bm_data[key] = {
            "name": _plain(c["name"]), "tag": _plain(c["tag"]),
            "area": _plain(bm_area.get(key, "")), "group": BM_GROUP[key],
            "lede": _plain(c["lede"]),
            "treats": [_plain(s) for s in c["symptoms"][:4]],
            "approach": (_plain(appr[0][0]) + " — " + _plain(appr[0][1])) if appr else "",
            "url": f"conditions/{slug}.html",
        }
    bm_json = _json.dumps(bm_data)

    ticker = "".join(f"<span>{s}</span>" for s in
        ["Headache &amp; Migraine", "Epilepsy", "Parkinson's", "Memory &amp; Alzheimer's",
         "Multiple Sclerosis", "Stroke", "Neuropathy", "Neuromuscular", "Sleep", "Clinical Research"])

    pathways = [
        ("01", "Comprehensive Neurology", "The whole nervous system, one practice.",
         "Board-certified neurologists evaluating and managing conditions of the brain, spine, "
         "and peripheral nerves — with the time to get the diagnosis right.",
         ["Headache", "Epilepsy", "Movement", "Neuropathy"], "conditions/index.html", ""),
        ("02", "Memory &amp; Cognitive Care", "Answers when memory changes.",
         "Thorough evaluation of memory and thinking — including a free memory screen — with access "
         "to the newest disease-modifying therapies.",
         ["Free Memory Screen", "Alzheimer's", "Dementia"], "conditions/memory-alzheimers.html", ""),
        ("03", "Clinical Research", "Tomorrow's therapies, today.",
         "Our on-site Premiere Research Institute offers carefully monitored trials in Alzheimer's, "
         "migraine, and MS — expert oversight, at no cost to participants.",
         ["Alzheimer's", "Migraine", "MS"], "clinical-research.html",
         '<span class="badge-inline">On-site</span>'),
    ]
    pathways_html = "".join(
        f'''<a class="pathway reveal" href="{url}">
          <span class="pw-num">{num}</span>
          <div><h3>{title}{badge}</h3><span class="pw-kicker">{kick}</span></div>
          <div class="pw-body"><p>{desc}</p>
            <div class="pw-tags">{"".join(f"<span>{t}</span>" for t in tags)}</div></div>
          <span class="pw-go">&rarr;</span>
        </a>''' for num, title, kick, desc, tags, url, badge in pathways)

    # Featured physicians for the homepage strip (name-matched into DOCTORS).
    featured = ["Paul Winner", "Carl Sadowsky", "Tara Becker", "Michael Alosilla", "Manisha Korb"]
    by_name = {d["name"]: d for d in DOCTORS}
    spec_cards = "".join(
        f'''<a class="spec-card reveal d{i%3+1}" href="doctors/{_doc_slug(n)}.html">
          <span class="spec-photo"><img src="assets/team/{_doc_slug(n)}.jpg" alt="Dr. {_plain(n)}, {_plain(by_name[n]["creds"])}" width="320" height="320" loading="lazy" decoding="async"></span>
          <span class="spec-name">Dr. {by_name[n]["name"].split()[-1]}</span>
          <span class="spec-role">{by_name[n]["focus"][0]}</span>
        </a>''' for i, n in enumerate(featured)) + '''
        <a class="spec-card spec-all reveal d3" href="our-doctors.html">
          <span class="spec-all-num">9</span>
          <span class="spec-name">All Our Physicians</span>
          <span class="spec-role">Meet the full team &rarr;</span>
        </a>'''

    body = f"""
<main>
<section class="hero">
  <div class="hero-media">
    <div class="hero-fallback"></div>
    {neuro_field(1)}
  </div>
  <div class="hero-scrim"></div>
  <div class="wrap hero-inner">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="eyebrow on-dark">Compassionate Neurological Care · South Florida</span>
        <h1>
          <span class="line"><span>Clarity</span></span>
          <span class="line"><span>for the</span></span>
          <span class="line"><span><em class="accent">mind.</em></span></span>
        </h1>
        <p class="hero-tag">&ldquo;Treating the patient, not just the disease.&rdquo;</p>
        <p class="hero-sub">Board-certified neurologists caring for the brain, spine, and nervous
        system for more than 25 years — with an on-site research institute bringing tomorrow's
        therapies to the Palm Beaches today.</p>
        <div class="hero-ctas">
          <a class="btn btn-coral" href="appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
          <a class="btn btn-ghost" href="#bodymap">Explore Conditions</a>
        </div>
        <div class="hero-meta">
          <div><strong data-count="25" data-suffix="+">25+</strong><span>Years of Expertise</span></div>
          <div><strong>Board</strong><span>Certified Neurologists</span></div>
          <div><strong>On-site</strong><span>Clinical Research</span></div>
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">{hero_orb()}</div>
    </div>
  </div>
  <div class="scroll-hint"><span></span></div>
</section>

<div class="ins-strip"><div class="ticker">{ticker}</div></div>

<section class="section on-paper manifesto">
  <div class="wrap manifesto-grid">
    <div class="reveal">
      <span class="eyebrow">{TAGLINE}</span>
      <h2 class="manifesto-line">Treating the <em class="accent">patient</em>,<br>not just the disease.</h2>
    </div>
    <div class="reveal d2 manifesto-body">
      <p>Palm Beach Neurology is a comprehensive neurological practice committed to preventing and
      treating every element of neurological disease. As one of the most experienced neurological
      practices in the United States, our physicians and staff stay on the cutting edge of research
      and patient care — treating every patient with respect, empathy, and professionalism.</p>
      <a class="text-link" href="about.html">Our story &rarr;</a>
    </div>
  </div>
</section>

{wave_divider("cream")}
<section class="section" id="pathways">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">What We Do</span>
      <h2>Neurology in <em class="accent">West Palm Beach</em></h2>
      <p class="lede">Advanced, compassionate care for the nervous system — plus a research institute
      under the same roof.</p>
    </div>
    <div class="pathways">{pathways_html}</div>
  </div>
</section>

<section class="section on-ink" id="bodymap">
  {neuro_field(0.6)}
  <div class="wrap" style="position:relative;z-index:1;">
    <div class="section-head reveal">
      <span class="eyebrow on-dark">Where Does It Start?</span>
      <h2>Explore the <em class="accent">Nervous System</em></h2>
      <p class="lede">Hover or tap the brain, spine, or nerves — or any condition — to see the area
      involved, what it does, and how we treat it. Every pathway begins with a thorough evaluation.</p>
    </div>
    <div class="bm-filter reveal" role="group" aria-label="Filter conditions by area of the nervous system">
      <button type="button" class="bm-fbtn is-active" data-filter="all" aria-pressed="true">All areas</button>
      <button type="button" class="bm-fbtn" data-filter="brain" aria-pressed="false">Brain</button>
      <button type="button" class="bm-fbtn" data-filter="spine" aria-pressed="false">Spine</button>
      <button type="button" class="bm-fbtn" data-filter="nerves" aria-pressed="false">Nerves &amp; Muscle</button>
    </div>
    <div class="bodymap-grid three">
      <div class="bodymap-fig reveal">{brainmap_svg()}</div>
      <div class="bm-list reveal d2">{bm_list_html}</div>
      <aside class="bm-panel reveal d3" id="bm-panel" aria-live="polite">
        <div class="bm-panel-default">
          <span class="eyebrow on-dark">Your Guide</span>
          <h3>Select a glowing point</h3>
          <p>Tap any point on the figure — or any condition in the list — and we'll show you the
          area involved, what it does, and how our neurologists approach it.</p>
          <div class="bm-legend">
            <span><i class="lg-signal"></i> Neural signal</span>
            <span><i class="lg-spot"></i> A condition we treat</span>
          </div>
        </div>
      </aside>
    </div>
  </div>
  <script type="application/json" id="bm-data">{bm_json}</script>
</section>

<section class="section" id="specialists">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Meet Your Specialists</span>
      <h2>Subspecialty experts, <em class="accent">one&nbsp;team</em></h2>
      <p class="lede">Neurology is too broad for one doctor to master it all — so each of our
      physicians concentrates on the conditions they know most deeply.</p>
    </div>
    <div class="spec-strip">{spec_cards}</div>
  </div>
</section>

<section class="section on-cream">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Our Story</span>
      <h2>25 Years of Neurologic <em class="accent">Excellence</em></h2>
      <p style="margin-top:1.2rem;">For more than 25 years, Palm Beach Neurology has combined
      state-of-the-art techniques with a personal approach — treating the patient, not just the
      disease. Our board-certified neurologists take the time to reach the right diagnosis and build
      a plan around your life.</p>
      <p>Because we house the Premiere Research Institute under the same roof, our patients can reach
      tomorrow's therapies today — through carefully monitored clinical trials in Alzheimer's,
      migraine, and MS.</p>
      <div class="stat-row">
        <div><strong data-count="25" data-suffix="+">25+</strong><span>Years of Expertise</span></div>
        <div><strong>Board</strong><span>Certified Neurologists</span></div>
        <div><strong>On-site</strong><span>Research Institute</span></div>
        <div><strong>Personal</strong><span>Patient-First Care</span></div>
      </div>
      <div class="mt-2"><a class="text-link" href="our-doctors.html">Meet our doctors &rarr;</a></div>
    </div>
    <div class="reveal d2">
      <div class="eeg-console" role="img" aria-label="Illustration: a live EEG recording drawing five brainwave channels — delta, theta, alpha, beta, and gamma — the kind of neurodiagnostic testing performed in our office.">
        <div class="eeg-inner" aria-hidden="true">
          <div class="eeg-head">
            <span class="eeg-title">Neurodiagnostic Suite &middot; Live EEG</span>
            <span class="eeg-status"><i></i>Monitoring <b class="eeg-clock">00:00</b></span>
          </div>
          <div class="eeg-screen">
            <canvas class="eeg-canvas"></canvas>
            <div class="eeg-labels">
              <span><b>&delta;</b> Delta</span>
              <span><b>&theta;</b> Theta</span>
              <span><b>&alpha;</b> Alpha</span>
              <span><b>&beta;</b> Beta</span>
              <span><b>&gamma;</b> Gamma</span>
            </div>
            <div class="eeg-event"></div>
          </div>
          <div class="eeg-foot"><span>256 samples/sec</span><span>5 channels</span><span>Recorded on-site</span></div>
        </div>
      </div>
      <p class="eeg-caption">A glimpse of our on-site neurodiagnostics —
      <a class="text-link" href="services/eeg.html">explore EEG &amp; seizure testing &rarr;</a></p>
    </div>
  </div>
</section>

<section class="section on-paper">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">Getting Started Is Simple</span>
      <h2>Your First <em class="accent">Visit</em></h2>
    </div>
    <div class="svc-process">
      <div class="svc-step reveal d1"><div class="svc-step-dot">1</div><h3>Reach Out</h3><p>Request an appointment online or call — new patients are welcome.</p></div>
      <div class="svc-step reveal d2"><div class="svc-step-dot">2</div><h3>We Verify</h3><p>Our team confirms your insurance and helps gather any records.</p></div>
      <div class="svc-step reveal d3"><div class="svc-step-dot">3</div><h3>Comprehensive Visit</h3><p>A full hour with a neurologist to examine you and explain the plan.</p></div>
      <div class="svc-step reveal d4"><div class="svc-step-dot">4</div><h3>A Clear Plan</h3><p>Diagnosis, next steps, and follow-up — in plain language.</p></div>
    </div>
    <div class="center mt-3 reveal"><a class="btn btn-coral" href="appointments.html">Request Appointment <span class="arr">&rarr;</span></a></div>
  </div>
</section>

{cta_band(0)}
</main>
"""
    write("index.html",
          head("Neurologist in West Palm Beach | Palm Beach Neurology",
               "Board-certified neurology & clinical research in West Palm Beach, FL — migraine, "
               "epilepsy, Parkinson's, MS, stroke & neuropathy. New patients welcome.",
               canonical="", og_image="assets/media/og-cover.jpg")
          + nav(0) + body + footer(0))

# ============================================================================
# SERVICES  (their site lacks a services list — built from their 5 care pillars)
# ============================================================================
def build_services():
    pillars = [
        ("Diagnosis", "Accurate answers start here. Detailed neurologic examination plus testing "
         "such as EEG, EMG/nerve-conduction studies, cognitive evaluation, and imaging review to "
         "pinpoint what's really going on."),
        ("Treatment", "Personalized, state-of-the-art treatment matched to your diagnosis — including "
         "expert medication management and, where appropriate, Botox and infusion therapies."),
        ("Prevention", "Stopping the next event before it happens — stroke-risk reduction, migraine "
         "prevention, and proactive brain-health strategies."),
        ("Rehabilitation", "Restoring function after stroke, injury, or a new diagnosis, coordinated "
         "with the right therapists and specialists."),
        ("Education", "You and your family, fully informed. We explain your condition and your plan "
         "in plain language so you can make confident decisions."),
    ]
    pillar_html = "".join(
        f'<div class="svc-feature reveal d{i%3+1}"><span class="svc-feature-num">{i+1:02d}</span>'
        f'<div><h3>{t}</h3><p>{d}</p></div></div>' for i, (t, d) in enumerate(pillars))
    care = [(c["nav"], c["tag"], f"conditions/{slug}.html") for slug, c in CONDITIONS.items()]
    care += [("Clinical Trials", "Premiere Research Institute", "clinical-research.html"),
             ("Free Memory Screen", "No-cost cognitive screen", "appointments.html")]
    care_html = "".join(
        f'''<a class="cond-card reveal d{i%3+1}" href="{url}">
          <span class="cond-tag">{tag}</span><h3>{name}</h3></a>''' for i, (name, tag, url) in enumerate(care))
    body = f"""
<main>
{page_hero("Comprehensive Neurologic Care", "Our <em class='accent'>Services</em>",
  "From diagnosis to treatment, prevention, rehabilitation, and education — complete care for the "
  "brain, spine, and nervous system, all under one roof in West Palm Beach.",
  '<div class="crumbs"><a href="index.html">Home</a> / Services</div>')}
<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Five Pillars of Care</span>
      <h2>How We <em class="accent">Help</em></h2>
      <p class="lede">Our physicians focus on providing the highest quality of healthcare services
      across every stage of your neurologic care.</p>
    </div>
    <div class="svc-feature-grid pillars">{pillar_html}</div>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">Areas of Care</span>
      <h2>What We <em class="accent">Treat</em></h2>
      <p class="lede">Comprehensive neurology — choose an area to learn more.</p>
    </div>
    <div class="cond-grid">{care_html}</div>
    <p class="af-note" style="max-width:72ch;margin:2rem auto 0;text-align:center;">Testing and
    procedures available as part of your evaluation may include EEG, EMG and nerve-conduction studies,
    cognitive testing, and coordinated imaging. Ask our team what your work-up will involve.</p>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("services.html",
          head("Neurology Services in West Palm Beach | Palm Beach Neurology",
               "Comprehensive neurology in West Palm Beach: diagnosis, treatment, prevention, "
               "rehabilitation & education for headache, epilepsy, Parkinson's, MS & stroke.",
               canonical="services.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Services", "services.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# PATIENT CENTER  (new-patient info, forms download, portal, what to bring)
# ============================================================================
def build_patient_center():
    bring = ["Photo ID and insurance card(s)", "A list of your current medications and dosages",
             "Past medical records and previous test results", "Any brain or spine imaging (MRI/CT) on disc",
             "A referral, if your plan requires one", "A written list of your questions and concerns",
             "A family member or caregiver — especially for memory-related visits"]
    bring_html = "".join(f"<li>{b}</li>" for b in bring)
    body = f"""
<main>
{page_hero("Patient Center", "New <em class='accent'>Patients</em>",
  "Everything you need for a smooth first visit — your paperwork, what to bring, and how to reach "
  "the patient portal. We're glad you're here.",
  '<div class="crumbs"><a href="index.html">Home</a> / Patient Center</div>')}
<section class="section">
  <div class="wrap two-col">
    <div class="prose reveal">
      <h2>Your first visit</h2>
      <p>The purpose of a new-patient appointment is to develop a complete medical profile, identify
      any risk factors, and create a personalized care plan. This foundational visit helps build a
      relationship between you and your physician and ensures your ongoing care is tailored to your
      unique needs.</p>
      <h2>What to bring</h2>
      <ul class="check-list">{bring_html}</ul>
      <h2>New patient paperwork</h2>
      <p>To help your visit go smoothly, you can complete your new-patient paperwork before you arrive —
      it saves time in the waiting room. If you have questions about any of the forms, call our office
      at {PHONE}.</p>
      <p><a class="btn btn-coral" href="{FORMS_PDF}" download>Download New Patient Paperwork (PDF)</a></p>
    </div>
    <aside class="side-card reveal d2">
      <h3>Patient Portal</h3>
      <p>Access your information and manage your care online.</p>
      <span class="btn btn-ink" style="opacity:0.55;cursor:default;pointer-events:none;" aria-disabled="true">Portal Login — Coming Soon</span>
      <div class="side-meta">
        <p style="margin-bottom:0.4rem;">Ready to schedule?</p>
        <a href="appointments.html" class="text-link">Request an appointment &rarr;</a>
      </div>
      <div class="side-meta">
        <p style="margin-bottom:0.4rem;">Insurance</p>
        <p style="font-size:0.9rem;color:var(--muted);">We accept many major plans, including Medicare.
        Call <a href="tel:{PHONE_TEL}">{PHONE}</a> to verify your coverage.</p>
      </div>
    </aside>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("patient-center.html",
          head("Patient Center & New Patient Forms | Palm Beach Neurology",
               "New patient information, downloadable paperwork, patient portal, and what to bring "
               "to your first neurology visit at Palm Beach Neurology in West Palm Beach, FL.",
               canonical="patient-center.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Patient Center", "patient-center.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# ELECTRONIC NEW-PATIENT INTAKE FORM
# ============================================================================
def build_new_patient_form():
    hx = ["High blood pressure", "Diabetes", "High cholesterol", "Stroke or TIA", "Seizures / epilepsy",
          "Migraines / headaches", "Thyroid disease", "Heart disease", "Cancer", "Depression / anxiety",
          "Sleep disorder", "Head injury / concussion", "Parkinson's", "Multiple sclerosis"]
    sx = ["Headaches", "Memory changes", "Dizziness / vertigo", "Numbness or tingling", "Weakness",
          "Seizures", "Tremor", "Trouble walking / balance", "Vision changes", "Sleep problems",
          "Neck or back pain", "Speech difficulty"]
    hx_html = "".join(
        f'<label class="np-check"><input type="checkbox" name="History: {html.escape(_plain(h))}" value="Yes"> {h}</label>'
        for h in hx)
    sx_html = "".join(
        f'<label class="np-check"><input type="checkbox" name="Symptom: {html.escape(_plain(s))}" value="Yes"> {s}</label>'
        for s in sx)
    body = f"""
<main>
{page_hero("New Patient Intake", "New Patient <em class='accent'>Form</em>",
  "Complete your intake online before your visit — it saves time in the waiting room and helps your "
  "neurologist prepare. Prefer paper? You can download the packet instead.",
  '<div class="crumbs"><a href="index.html">Home</a> / <a href="patient-center.html">Patient Center</a> / New Patient Form</div>')}
<section class="section">
  <div class="wrap">
    <form class="np-form appt-form" id="np-form"
          data-endpoint="https://formsubmit.co/ajax/{EMAIL}"
          data-done="np-done"
          data-subject="New Patient Intake — Palm Beach Neurology" novalidate>
      <div class="np-privacy">
        <strong>Before you begin:</strong> please share only what you're comfortable submitting online.
        This form is emailed securely to our office to help prepare for your visit — you can always finish
        any details in person. <strong>Do not use this form for a medical emergency — call 911.</strong>
        Questions? Call us at {PHONE}. Prefer paper? <a href="{FORMS_PDF}" download>Download the PDF packet</a>.
      </div>

      <div class="np-section">
        <h3><span class="np-num">01</span> Patient Information</h3>
        <div class="np-grid">
          <div class="af-field"><label for="np-first">First name *</label><input id="np-first" name="First name" type="text" required maxlength="80"></div>
          <div class="af-field"><label for="np-last">Last name *</label><input id="np-last" name="Last name" type="text" required maxlength="80"></div>
          <div class="af-field"><label for="np-dob">Date of birth *</label><input id="np-dob" name="Date of birth" type="date" required></div>
          <div class="af-field"><label for="np-sex">Sex</label><select id="np-sex" name="Sex"><option value="">Select…</option><option>Female</option><option>Male</option><option>Prefer not to say</option></select></div>
          <div class="af-field full"><label for="np-addr">Street address</label><input id="np-addr" name="Address" type="text" autocomplete="street-address" maxlength="160"></div>
          <div class="af-field"><label for="np-city">City</label><input id="np-city" name="City" type="text" maxlength="80"></div>
          <div class="af-field"><label for="np-zip">State / ZIP</label><input id="np-zip" name="State and ZIP" type="text" maxlength="40"></div>
          <div class="af-field"><label for="np-phone">Cell phone *</label><input id="np-phone" name="Cell phone" type="tel" required autocomplete="tel" maxlength="40" placeholder="Your phone number"></div>
          <div class="af-field"><label for="np-email">Email *</label><input id="np-email" name="Email" type="email" required autocomplete="email" maxlength="160"></div>
        </div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">02</span> Emergency Contact</h3>
        <div class="np-grid">
          <div class="af-field"><label for="np-ec">Name</label><input id="np-ec" name="Emergency contact name" type="text" maxlength="120"></div>
          <div class="af-field"><label for="np-ecr">Relationship</label><input id="np-ecr" name="Emergency contact relationship" type="text" maxlength="80"></div>
          <div class="af-field full"><label for="np-ecp">Phone</label><input id="np-ecp" name="Emergency contact phone" type="tel" maxlength="40"></div>
        </div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">03</span> Insurance</h3>
        <div class="np-grid">
          <div class="af-field"><label for="np-ins">Insurance carrier</label><input id="np-ins" name="Insurance carrier" type="text" maxlength="120"></div>
          <div class="af-field"><label for="np-mem">Member ID</label><input id="np-mem" name="Member ID" type="text" maxlength="80"></div>
          <div class="af-field"><label for="np-grp">Group number</label><input id="np-grp" name="Group number" type="text" maxlength="80"></div>
          <div class="af-field"><label for="np-holder">Policy holder (if not you)</label><input id="np-holder" name="Policy holder" type="text" maxlength="120"></div>
        </div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">04</span> Physicians &amp; Pharmacy</h3>
        <div class="np-grid">
          <div class="af-field"><label for="np-ref">Referring / primary care physician</label><input id="np-ref" name="Referring physician" type="text" maxlength="120"></div>
          <div class="af-field"><label for="np-refp">Physician phone</label><input id="np-refp" name="Referring physician phone" type="tel" maxlength="40"></div>
          <div class="af-field full"><label for="np-rx">Preferred pharmacy (name &amp; location)</label><input id="np-rx" name="Pharmacy" type="text" maxlength="160"></div>
        </div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">05</span> Reason for Visit</h3>
        <div class="af-field"><label for="np-reason">What brings you in? *</label><textarea id="np-reason" name="Reason for visit" required maxlength="1500" placeholder="Describe your main concern and when it started…"></textarea></div>
        <label style="display:block;font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-soft);margin:0.6rem 0 0.7rem;">Symptoms you're experiencing</label>
        <div class="np-checks">{sx_html}</div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">06</span> Medications &amp; Allergies</h3>
        <div class="af-field"><label for="np-meds">Current medications &amp; dosages</label><textarea id="np-meds" name="Current medications" maxlength="1500" placeholder="List names and doses, or write &quot;none&quot;…"></textarea></div>
        <div class="af-field"><label for="np-allerg">Allergies</label><textarea id="np-allerg" name="Allergies" maxlength="800" placeholder="Medication or other allergies, or &quot;none&quot;…"></textarea></div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">07</span> Medical History</h3>
        <label style="display:block;font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:0.7rem;">Have you had any of the following?</label>
        <div class="np-checks">{hx_html}</div>
        <div class="af-field full" style="margin-top:1.1rem;"><label for="np-surg">Past surgeries</label><textarea id="np-surg" name="Past surgeries" maxlength="1000" placeholder="Type and approximate year…"></textarea></div>
        <div class="af-field full"><label for="np-fam">Family medical history</label><textarea id="np-fam" name="Family history" maxlength="1000" placeholder="Relevant conditions in close relatives…"></textarea></div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">08</span> Social History</h3>
        <div class="np-grid">
          <div class="af-field"><label for="np-tob">Tobacco use</label><select id="np-tob" name="Tobacco use"><option value="">Select…</option><option>Never</option><option>Former</option><option>Current</option></select></div>
          <div class="af-field"><label for="np-alc">Alcohol use</label><select id="np-alc" name="Alcohol use"><option value="">Select…</option><option>None</option><option>Occasional</option><option>Regular</option></select></div>
          <div class="af-field full"><label for="np-occ">Occupation</label><input id="np-occ" name="Occupation" type="text" maxlength="120"></div>
        </div>
      </div>

      <div class="np-section">
        <h3><span class="np-num">09</span> Consent &amp; Signature</h3>
        <label class="np-consent"><input type="checkbox" name="Consent" value="I certify the information is accurate" required> I certify that the information above is accurate to the best of my knowledge. *</label>
        <div class="np-grid">
          <div class="af-field"><label for="np-sig">Type your full name (signature) *</label><input id="np-sig" name="Signature" type="text" required maxlength="120"></div>
          <div class="af-field"><label for="np-date">Date *</label><input id="np-date" name="Date" type="date" required></div>
        </div>
        <p class="af-error" role="alert"></p>
        <button class="btn btn-coral" type="submit">Submit Intake Form <span class="arr">&rarr;</span></button>
      </div>
    </form>
    <div class="af-done np-section" id="np-done" hidden style="text-align:center;">
      <div class="af-check">&#10003;</div>
      <h3>Thank you — your intake was submitted.</h3>
      <p style="color:var(--muted);max-width:46ch;margin:0.5rem auto 0;">Our team will review it before your visit.
      If you don't hear from us within 48 hours, please call <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
    </div>
  </div>
</section>
{cta_band(0)}
</main>
"""
    write("new-patient-form.html",
          head("New Patient Form (Online Intake) | Palm Beach Neurology",
               "Complete your Palm Beach Neurology new-patient intake online before your visit in West "
               "Palm Beach, FL. Fast, secure, and mobile-friendly — or download the PDF packet.",
               canonical="new-patient-form.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Patient Center", "patient-center.html"),
                                               ("New Patient Form", "new-patient-form.html")]))
          + nav(0) + body + footer(0))

# ============================================================================
# META (sitemap / robots / llms / manifest / 404)
# ============================================================================
# ============================================================================
# CONTENT — BLOG  (plain-English articles, physician-reviewed; facts only)
# ============================================================================
BLOG_POSTS = {
    "first-neurology-visit": {
        "title": "What to Expect at Your First Neurology Visit",
        "date": "July 2026", "iso": "2026-07-22",
        "tag": "Getting Started",
        "teaser": "A neurology appointment can feel intimidating. Here is exactly how the first "
                  "visit works at Palm Beach Neurology — what to bring, what happens, and how to prepare.",
        "body": """
<p>If you have never seen a neurologist, the first appointment can feel like a mystery. Neurology covers the brain, spine, and nervous system, and the evaluation is a bit different from a typical office visit. Here is an honest walkthrough so you can arrive relaxed and ready.</p>
<h2>It begins with your story</h2>
<p>Before any testing, your neurologist wants to understand what is happening in your own words. When did the symptoms start? What makes them better or worse? How are they affecting your day — your work, your sleep, your independence? For memory concerns, a family member's perspective is invaluable, so a loved one is always welcome to join you. The history you share shapes everything that follows, which is why a new-patient visit is scheduled for about an hour.</p>
<h2>The neurologic exam</h2>
<p>Next comes a hands-on examination of how your nervous system is working: strength, reflexes, sensation, coordination, balance, and often your memory and thinking. None of it is painful. Each part helps your neurologist localize where a problem might be coming from — the brain, the spinal cord, the nerves, or the muscles.</p>
<h2>Testing, only when it will change the plan</h2>
<p>Depending on what your exam suggests, your neurologist may recommend further testing — an <a href="../conditions/epilepsy-seizures.html">EEG</a> for spells or seizures, an <a href="../conditions/neuropathy.html">EMG and nerve-conduction study</a> for numbness or weakness, or brain and spine imaging. We order tests when the result will genuinely guide your care, not by default.</p>
<h2>What to bring</h2>
<p>Please bring your <strong>photo ID</strong>, <strong>insurance card</strong>, a current <strong>medication list</strong>, and any prior imaging (MRI or CT) on disc or through a portal, along with any referral paperwork. Completing your <a href="../patient-center.html">new-patient forms</a> ahead of time saves you paperwork in the waiting room.</p>
<h2>Leaving with a plan</h2>
<p>By the end of the visit, the goal is that you understand what is being considered, what the next step is, and how to reach us with questions. If you would like to get started, you can <a href="../appointments.html">request an appointment online</a> — new patients are always welcome.</p>
""",
    },
    "free-memory-screen": {
        "title": "The Free Memory Screen: A Simple First Step",
        "date": "July 2026", "iso": "2026-07-21",
        "tag": "Memory & Aging",
        "teaser": "Noticed changes in memory — your own or a loved one's? Our no-cost, 30-minute "
                  "memory screen is a low-pressure way to know whether a fuller look is worthwhile.",
        "body": """
<p>Forgetting a name or misplacing keys happens to everyone. But when memory changes start to worry you or the people who know you best, it is hard to know whether it is normal aging or something worth checking. That uncertainty is exactly what a memory screen is designed to ease.</p>
<h2>What the screen is</h2>
<p>The Free Memory Screen at Palm Beach Neurology is a <strong>no-cost, confidential, roughly 30-minute check</strong> of memory and thinking. It uses brief, well-established questions and tasks to get a snapshot of how you are doing. It is comfortable, low-pressure, and there is nothing to study for.</p>
<h2>What it is not</h2>
<p>A screen is not a diagnosis. A single check cannot, by itself, tell anyone they do or do not have a condition like <a href="../conditions/memory-alzheimers.html">Alzheimer's disease</a>. What it can do is help decide whether a fuller evaluation — with a physician, and sometimes additional testing — is worthwhile. Think of it as a helpful first step, not a final answer.</p>
<h2>Why earlier is better</h2>
<p>Many things that affect memory are treatable — from thyroid and vitamin issues to sleep problems, medication side effects, and mood. Sorting out what is going on sooner opens more options, supports better planning, and often brings real peace of mind, whatever the result.</p>
<h2>Who might consider one</h2>
<p>Anyone noticing more frequent forgetfulness, trouble following conversations or handling familiar tasks, or a nagging sense that "something has changed" — and any family member who has quietly wondered the same about someone they love. If that is you, call us at <strong>561-845-0500</strong> to ask about scheduling a screen, or <a href="../appointments.html">request an appointment</a>.</p>
""",
    },
    "migraine-beyond-headache": {
        "title": "Migraine Is More Than a Headache",
        "date": "July 2026", "iso": "2026-07-20",
        "tag": "Headache & Migraine",
        "teaser": "Migraine is a neurologic condition, not just a bad headache — and today's "
                  "treatments have come a long way. Here is what modern migraine care can look like.",
        "body": """
<p>Migraine is one of the most common reasons people see a neurologist, and one of the most misunderstood. It is not simply a strong headache. It is a neurologic condition that can involve throbbing pain, nausea, sensitivity to light and sound, and — for some — visual aura, and it can cost a person entire days. The encouraging news is that migraine care has advanced dramatically.</p>
<h2>Getting the diagnosis right first</h2>
<p>Effective treatment starts with a careful diagnosis. Our neurologists distinguish migraine from tension-type, cluster, and secondary headaches, because the plan depends entirely on which one you have. Imaging is ordered when it will change management — not automatically. You can read more on our <a href="../conditions/headaches-migraine.html">headache and migraine page</a>.</p>
<h2>Two halves of a good plan</h2>
<p>Most migraine plans have two parts. The first is <strong>acute (rescue) treatment</strong> — a plan that reliably stops an attack so it does not cost you a day. The second is <strong>preventive treatment</strong> for people with frequent or disabling attacks, aimed at making them less frequent and less severe in the first place.</p>
<h2>Newer, migraine-specific options</h2>
<p>Treatment is no longer one-size-fits-all. In addition to established medications, there are now therapies developed specifically for migraine — including <strong>CGRP-targeted treatments</strong> and, for chronic migraine, <strong>Botox</strong>. Matching the right option to your pattern is exactly the kind of decision a neurologist is trained to make with you.</p>
<h2>The everyday levers still matter</h2>
<p>Identifying triggers, protecting sleep, staying hydrated, managing stress, and avoiding overuse of over-the-counter pain relievers all remain part of good migraine care. They work best alongside — not instead of — a medical plan.</p>
<h2>When head pain needs urgent care</h2>
<p>A sudden "worst headache of your life," or a headache with fever, confusion, vision loss, weakness, numbness, or trouble speaking, is an emergency — call 911. For the recurring, disabling headaches that keep circling back, a neurologist can help you get ahead of them. <a href="../appointments.html">Request an appointment</a> to start.</p>
""",
    },
    "clinical-trials-explained": {
        "title": "Clinical Trials, Explained",
        "date": "July 2026", "iso": "2026-07-19",
        "tag": "Research",
        "teaser": "What is a clinical trial, and why does our practice have a research institute? "
                  "A plain-English look at how neurology research works — and how it helps patients.",
        "body": """
<p>Palm Beach Neurology is home to an on-site research institute, <strong>Premiere Research Institute</strong>, and patients often ask what that actually means for them. Here is a clear, jargon-free explanation of clinical trials and the role they play in advancing neurologic care.</p>
<h2>What a clinical trial is</h2>
<p>A clinical trial is a carefully designed, closely monitored study that tests whether a new treatment is safe and helpful. Trials follow strict protocols and oversight to protect participants at every step. They are how promising ideas become tomorrow's approved treatments — which means today's therapies exist because past patients had the option to take part.</p>
<h2>Why an on-site institute matters</h2>
<p>Having research under the same roof as clinical care means our physicians stay at the leading edge of neurology, and it can give appropriate patients access to studied therapies that are not yet widely available. We run monitored trials in areas such as <a href="../conditions/memory-alzheimers.html">Alzheimer's disease</a>, <a href="../conditions/headaches-migraine.html">migraine</a>, and <a href="../conditions/multiple-sclerosis.html">multiple sclerosis</a>. You can learn more on our <a href="../clinical-research.html">clinical research page</a>.</p>
<h2>Is participation right for everyone?</h2>
<p>Not necessarily — and that is the point of the process. Every study has specific criteria for who can join, designed with safety and good science in mind. Participation is always voluntary, you can ask any question you like, and you may leave a study at any time. Trials also frequently involve close monitoring and study-related care.</p>
<h2>How to ask what is enrolling</h2>
<p>Available studies change over time. If you are curious whether a current trial might fit your situation, ask your neurologist, call our research line at <strong>561-851-9400</strong>, or explore <a href="../clinical-research.html">our research program</a>. It costs nothing to ask, and the answer might open a door.</p>
""",
    },
}

def blogpost_schema(slug, p):
    iso = p.get("iso", "2026-07-01")
    data = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": _plain(p["title"]),
        "description": _plain(p["teaser"]),
        "datePublished": iso, "dateModified": iso,
        "author": {"@type": "MedicalOrganization", "@id": BASE + "/#organization", "name": LEGAL},
        "reviewedBy": {"@type": "Physician", "@id": BASE + "/our-doctors.html#paul-winner",
                       "name": "Paul Winner, DO, FAAN, FAHS"},
        "publisher": {"@id": BASE + "/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": BASE + "/blog/" + slug + ".html"},
        "url": BASE + "/blog/" + slug + ".html",
        "image": BASE + "/assets/media/og-cover.jpg",
        "articleSection": _plain(p["tag"]), "inLanguage": "en-US", "isAccessibleForFree": True,
    }
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def build_blog():
    posts = list(BLOG_POSTS.items())
    # ---- Hub ----
    cards = "".join(
        f'''<a class="cond-card reveal d{i%3+1}" href="{slug}.html">
          <span class="cond-tag">{p["tag"]} &middot; {p["date"]}</span>
          <h3>{p["title"]}</h3>
          <p>{_plain(p["teaser"])[:150]}…</p>
        </a>''' for i, (slug, p) in enumerate(posts))
    body = f"""
<main>
{page_hero("Insights", "Neurology <em class='accent'>Articles</em>",
  "Plain-English guidance on brain, spine, and nervous-system health from the team at "
  "Palm Beach Neurology — every article reviewed by our physicians.",
  '<div class="crumbs"><a href="../index.html">Home</a> / Blog</div>')}
<section class="section">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow">From Our Team</span>
      <h2>Latest <em class="accent">Articles</em></h2>
      <p class="lede">Clear, trustworthy information — reviewed by board-certified neurologists.
      Helpful background, never a substitute for a visit.</p>
    </div>
    <div class="cond-grid">{cards}</div>
  </div>
</section>
{cta_band(1)}
</main>
"""
    write("blog/index.html",
          head("Neurology Articles &amp; Insights | Palm Beach Neurology",
               "Plain-English neurology articles from Palm Beach Neurology, West Palm Beach — first "
               "visits, memory screens, migraine care, and clinical research, reviewed by our physicians.",
               depth=1, canonical="blog/index.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Blog", "blog/index.html")]))
          + nav(1) + body + footer(1))

    # ---- Individual posts ----
    for i, (slug, p) in enumerate(posts):
        others = [(s2, p2) for s2, p2 in posts if s2 != slug][:3]
        related = "".join(
            f'''<a class="cond-card reveal d{j%3+1}" href="{s2}.html">
              <span class="cond-tag">{p2["tag"]}</span><h3>{p2["title"]}</h3></a>'''
            for j, (s2, p2) in enumerate(others))
        post_body = f"""
<main>
{page_hero(p["tag"], p["title"], p["teaser"],
  f'<div class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Blog</a> / {p["tag"]}</div>')}
<section class="section">
  <div class="wrap prose-wrap">
    <article class="prose reveal">
      <p class="post-byline">By the Palm Beach Neurology team &middot; {p["date"]} &middot; <em>Medically reviewed by Dr. Paul Winner, DO, FAAN</em></p>
      {p["body"]}
      <p class="post-disclaimer">This article is general information, not medical advice. Every
      situation is different — please consult a qualified neurologist about yours. In an emergency, call 911.</p>
      <p style="margin-top:1.6rem;"><a class="btn btn-coral" href="../appointments.html">Request an Appointment <span class="arr">&rarr;</span></a></p>
    </article>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head center reveal"><span class="eyebrow">Keep Reading</span>
      <h2>More <em class="accent">Articles</em></h2></div>
    <div class="cond-grid">{related}</div>
  </div>
</section>
{cta_band(1)}
</main>
"""
        write(f"blog/{slug}.html",
              head(f"{_plain(p['title'])} | Palm Beach Neurology",
                   _plain(p["teaser"])[:155],
                   depth=1, canonical=f"blog/{slug}.html", page_type="article",
                   extra_schema=blogpost_schema(slug, p) + breadcrumb_schema(
                       [("Home", ""), ("Blog", "blog/index.html"), (_plain(p["title"]), f"blog/{slug}.html")]))
              + nav(1) + post_body + footer(1))

# ============================================================================
# EXPANSION — content loaded from content/*.json (generated + fact-verified),
# consumed here into location, service, About and insurance pages, plus extra
# conditions/blog posts merged into the existing dicts. Guarded so the build is
# valid whether or not the content files are present.
# ============================================================================
def _load_content(name):
    try:
        with open(os.path.join(ROOT, "content", name), encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return None

def mini_faq(faqs):
    if not faqs:
        return ""
    items = "".join(
        f'<details class="mfq"><summary>{f["q"]}</summary><div class="mfq-a"><p>{f["a"]}</p></div></details>'
        for f in faqs)
    return f'<div class="mini-faq">{items}</div>'

def service_schema(s):
    data = {"@context": "https://schema.org", "@type": s.get("schema_type", "MedicalProcedure"),
            "name": _plain(s["name"]), "description": _plain(s["desc"]),
            "url": f"{BASE}/services/{s['slug']}.html"}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def _service_city_schema(city, slug):
    data = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Neurology",
            "name": f"Neurology for {city}", "provider": ORG_REF,
            "areaServed": {"@type": "City", "name": city},
            "url": f"{BASE}/locations/{slug}.html"}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>\n"

def build_locations():
    if not LOCATIONS_DATA:
        return
    cards = "".join(
        f'''<a class="cond-card reveal d{i%3+1}" href="{l["slug"]}.html">
          <span class="cond-tag">Areas We Serve</span><h3>{l["city"]}</h3>
          <p>Board-certified neurology for {l["city"]} residents, from our West Palm Beach office.</p></a>'''
        for i, l in enumerate(LOCATIONS_DATA))
    hub = f"""
<main>
{page_hero("Areas We Serve", "Neurology Across the <em class='accent'>Palm Beaches</em>",
  "Board-certified neurologic care for communities across Palm Beach County — all delivered from our "
  "West Palm Beach office.", '<div class="crumbs"><a href="../index.html">Home</a> / Areas We Serve</div>')}
<section class="section"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Palm Beach County</span>
    <h2>Communities We <em class="accent">Serve</em></h2>
    <p class="lede">Board-certified brain, spine, and nerve care for the whole region — all delivered from our West Palm Beach office.</p></div>
  <div class="cond-grid">{cards}</div>
</div></section>
{cta_band(1)}
</main>"""
    write("locations/index.html",
          head("Areas We Serve | Palm Beach Neurology, West Palm Beach",
               "Neurology for West Palm Beach, Palm Beach, Palm Beach Gardens, Jupiter, Wellington & "
               "more — expert brain, spine & nerve care from Palm Beach Neurology.",
               depth=1, canonical="locations/index.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Areas We Serve", "locations/index.html")]))
          + nav(1) + hub + footer(1))
    cg = "".join(
        f'<a class="cond-card reveal d{i%3+1}" href="../conditions/{s}.html"><span class="cond-tag">{CONDITIONS[s]["tag"]}</span><h3>{CONDITIONS[s]["nav"]}</h3></a>'
        for i, s in enumerate(list(CONDITIONS)[:8]))
    for l in LOCATIONS_DATA:
        faqs = mini_faq(l.get("faqs", []))
        body = f"""
<main>
{page_hero(l.get("eyebrow", "Areas We Serve"), l["h1"], l["lede"],
  f'<div class="crumbs"><a href="../index.html">Home</a> / <a href="index.html">Areas We Serve</a> / {l["city"]}</div>')}
<section class="section">
  <div class="wrap two-col">
    <div class="prose reveal">
      {l["intro_html"]}
      <h2>Caring for {l["city"]}</h2>
      {l["who_html"]}
      <h2>Getting to our office</h2>
      {l["access_html"]}
    </div>
    <aside class="side-card reveal d2">
      <h3>Request an appointment</h3>
      <p>New patients from {l["city"]} are welcome. We'll help verify your insurance and find a time that works.</p>
      <a class="btn btn-coral" href="../appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
      <div class="side-meta"><p style="margin-bottom:0.4rem;">Prefer to call?</p><a href="tel:{PHONE_TEL}">{PHONE}</a></div>
    </aside>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">What We Treat</span>
      <h2>Conditions We <em class="accent">Care For</em></h2></div>
    <div class="cond-grid">{cg}</div>
    {('<div style="max-width:760px;margin:2.6rem auto 0;">' + faqs + '</div>') if faqs else ''}
  </div>
</section>
{cta_band(1)}
</main>"""
        write(f"locations/{l['slug']}.html",
              head(l["title"], l["desc"], depth=1, canonical=f"locations/{l['slug']}.html",
                   extra_schema=_service_city_schema(l["city"], l["slug"]) + breadcrumb_schema(
                       [("Home", ""), ("Areas We Serve", "locations/index.html"), (l["city"], f"locations/{l['slug']}.html")]))
              + nav(1) + body + footer(1))

def build_service_pages():
    if not SERVICES_DATA:
        return
    for s in SERVICES_DATA:
        expect = "".join(
            f'<div class="svc-step reveal d{i%4+1}"><div class="svc-step-dot">{i+1}</div><h3>{e["title"]}</h3><p>{e["desc"]}</p></div>'
            for i, e in enumerate(s["expect"]))
        approach = "".join(
            f'<div class="svc-feature reveal d{i%3+1}"><span class="svc-feature-num">{i+1:02d}</span><div><h3>{a["title"]}</h3><p>{a["desc"]}</p></div></div>'
            for i, a in enumerate(s["approach"]))
        faqs = mini_faq(s.get("faqs", []))
        who = s.get("who_html", "")
        body = f"""
<main>
{page_hero(s.get("eyebrow", "Our Services"), s["h1"], s["lede"],
  f'<div class="crumbs"><a href="../index.html">Home</a> / <a href="../services.html">Services</a> / {s["name"]}</div>')}
<section class="section">
  <div class="wrap two-col">
    <div class="prose reveal">
      {s["intro_html"]}
      <h2>What it is</h2>
      {s["what_html"]}
      {('<h2>Who it helps</h2>' + who) if who else ''}
    </div>
    <aside class="side-card reveal d2">
      <h3>Ask about {s["name"]}</h3>
      <p>Our team will explain whether this is right for you and help coordinate scheduling.</p>
      <a class="btn btn-coral" href="../appointments.html">Request Appointment <span class="arr">&rarr;</span></a>
      <div class="side-meta"><p style="margin-bottom:0.4rem;">Questions?</p><a href="tel:{PHONE_TEL}">{PHONE}</a></div>
    </aside>
  </div>
</section>
<section class="section on-ink">
  {neuro_field(0.5)}
  <div class="wrap" style="position:relative;z-index:1;">
    <div class="section-head reveal"><span class="eyebrow on-dark">What to Expect</span>
      <h2>Your <em class="accent">Experience</em></h2></div>
    <div class="svc-process">{expect}</div>
  </div>
</section>
<section class="section on-cream">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Our Approach</span>
      <h2>How We <em class="accent">Do It Well</em></h2></div>
    <div class="svc-feature-grid">{approach}</div>
    {('<div style="max-width:760px;margin:2.6rem auto 0;">' + faqs + '</div>') if faqs else ''}
  </div>
</section>
{cta_band(1)}
</main>"""
        write(f"services/{s['slug']}.html",
              head(s["title"], s["desc"], depth=1, canonical=f"services/{s['slug']}.html", page_type="article",
                   extra_schema=service_schema(s) + breadcrumb_schema(
                       [("Home", ""), ("Services", "services.html"), (s["name"], f"services/{s['slug']}.html")]))
              + nav(1) + body + footer(1))

def build_about():
    if not ABOUT_DATA:
        return
    a = ABOUT_DATA
    values = "".join(
        f'<div class="svc-feature reveal d{i%3+1}"><span class="svc-feature-num">{i+1:02d}</span><div><h3>{v["title"]}</h3><p>{v["desc"]}</p></div></div>'
        for i, v in enumerate(a.get("values", [])))
    why = "".join(
        f'<div class="svc-feature reveal d{i%3+1}"><span class="svc-feature-num">{i+1:02d}</span><div><h3>{w["title"]}</h3><p>{w["desc"]}</p></div></div>'
        for i, w in enumerate(a.get("why", [])))
    body = f"""
<main>
{page_hero("About Us", "Our <em class='accent'>Story</em>",
  "Decades of compassionate neurologic care and research in the Palm Beaches.",
  '<div class="crumbs"><a href="index.html">Home</a> / About</div>')}
<section class="section"><div class="wrap prose-wrap"><div class="prose reveal">{a["story_html"]}
  <p style="margin-top:1.6rem;font-style:italic;color:var(--coral-text);font-size:1.1rem;">{a.get("mission", "")}</p></div></div></section>
<section class="section on-cream"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What Guides Us</span><h2>Our <em class="accent">Values</em></h2></div>
  <div class="svc-feature-grid">{values}</div></div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Why Palm Beach Neurology</span><h2>Care You Can <em class="accent">Trust</em></h2></div>
  <div class="svc-feature-grid">{why}</div>
  <div style="text-align:center;margin-top:2.8rem;"><a class="btn btn-coral" href="our-doctors.html">Meet Our Doctors <span class="arr">&rarr;</span></a></div>
</div></section>
{cta_band(0)}
</main>"""
    body = body.replace('href="../', 'href="')  # About is root-level; content was drafted one folder deep
    write("about.html",
          head(a["title"], a["desc"], canonical="about.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("About", "about.html")]))
          + nav(0) + body + footer(0))

def build_insurance():
    if not INSURANCE_DATA:
        return
    ins = INSURANCE_DATA
    secs = "".join(
        f'<div class="reveal" style="margin-bottom:2rem;"><h2>{sx["heading"]}</h2>{sx["body_html"]}</div>'
        for sx in ins.get("sections", []))
    faqs = mini_faq(ins.get("faqs", []))
    body = f"""
<main>
{page_hero("Patients", "Insurance &amp; <em class='accent'>Billing</em>",
  "Straightforward answers about coverage, referrals, and costs — with a front-desk team happy to help.",
  '<div class="crumbs"><a href="index.html">Home</a> / Insurance &amp; Billing</div>')}
<section class="section"><div class="wrap prose-wrap">
  <div class="prose reveal">{ins["intro_html"]}</div>
  <div style="max-width:760px;margin:2.4rem auto 0;">{secs}{faqs}</div>
</div></section>
{cta_band(0)}
</main>"""
    body = body.replace('href="../', 'href="')  # root-level page; content was drafted one folder deep
    write("insurance-billing.html",
          head(ins["title"], ins["desc"], canonical="insurance-billing.html",
               extra_schema=breadcrumb_schema([("Home", ""), ("Insurance &amp; Billing", "insurance-billing.html")]))
          + nav(0) + body + footer(0))

# ---- Load generated content + merge extra conditions/blog posts ----
LOCATIONS_DATA = _load_content("locations.json") or []
SERVICES_DATA = _load_content("services.json") or []
ABOUT_DATA = _load_content("about.json")
INSURANCE_DATA = _load_content("insurance.json")

for _c in (_load_content("conditions_extra.json") or []):
    _slug = _c.pop("slug")
    _c["approach"] = [(_a["title"], _a["desc"]) for _a in _c.get("approach", [])]
    CONDITIONS[_slug] = _c
for _p in (_load_content("blog_extra.json") or []):
    BLOG_POSTS[_p["slug"]] = {"title": _p["title"], "date": _p.get("date", "July 2026"),
                              "iso": _p.get("iso", "2026-07-18"), "tag": _p["tag"],
                              "teaser": _p["teaser"], "body": _p["body_html"]}

def build_meta():
    write("site.webmanifest", _json.dumps({
        "name": LEGAL, "short_name": "PB Neurology",
        "description": "Board-certified neurology & clinical research in West Palm Beach, FL.",
        "start_url": "/", "display": "standalone",
        "background_color": "#F3ECDC", "theme_color": THEME_COLOR,
        "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }, indent=2) + "\n")

    pages = ["", "services.html", "our-doctors.html", "clinical-research.html", "appointments.html",
             "patient-center.html", "contact.html", "faq.html", "conditions/index.html", "blog/index.html"]
    pages += [f"conditions/{s}.html" for s in CONDITIONS]
    pages += [f"blog/{s}.html" for s in BLOG_POSTS]
    pages += [f"doctors/{_doc_slug(d['name'])}.html" for d in DOCTORS]
    if SERVICES_DATA:
        pages += [f"services/{s['slug']}.html" for s in SERVICES_DATA]
    if LOCATIONS_DATA:
        pages += ["locations/index.html"] + [f"locations/{l['slug']}.html" for l in LOCATIONS_DATA]
    if ABOUT_DATA:
        pages += ["about.html"]
    if INSURANCE_DATA:
        pages += ["insurance-billing.html"]
    from datetime import date as _date
    lastmod = _date.today().isoformat()
    def _prio(p):
        if p == "":                                   return ("1.0", "weekly")
        if p.startswith("conditions/") and p != "conditions/index.html": return ("0.8", "monthly")
        if p in ("services.html", "our-doctors.html", "clinical-research.html", "appointments.html"): return ("0.8", "monthly")
        return ("0.6", "monthly")
    urls = ""
    for p in pages:
        pr, cf = _prio(p)
        urls += (f"  <url><loc>{BASE}/{p}</loc><lastmod>{lastmod}</lastmod>"
                 f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>\n")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")

    ai_crawlers = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot",
                   "Claude-User", "Google-Extended", "Bingbot", "Applebot", "meta-externalagent"]
    ai_blocks = "".join(f"User-agent: {ua}\nAllow: /\n\n" for ua in ai_crawlers)
    write("robots.txt",
          "# All crawlers welcome, including AI/answer-engine bots.\n"
          "User-agent: *\nAllow: /\n\n" + ai_blocks + f"Sitemap: {BASE}/sitemap.xml\n")

    cond_lines = "\n".join(f"- {_plain(c['name'])}: {BASE}/conditions/{slug}.html" for slug, c in CONDITIONS.items())
    doc_lines = "; ".join(_plain(d["name"]) for d in DOCTORS)
    write("llms.txt", f"""# {LEGAL}

> Board-certified neurology practice in West Palm Beach, Florida, with 25+ years caring for the
> brain, spine, and nervous system, plus an on-site clinical-research institute (Premiere Research
> Institute). We treat the patient, not just the disease.

## Key facts
- Address: {ADDR_STREET}, {ADDR_CITY}, {ADDR_STATE} {ADDR_ZIP}
- Phone: {PHONE} · Fax: {FAX} · Research (clinical trials): {RESEARCH_PHONE}
- Hours: Monday-Thursday 8:00 AM-5:00 PM; Friday 8:00 AM-4:30 PM
- Accepting new patients; free memory screens available
- Website: {BASE}/

## Doctors
{doc_lines}
Our Doctors: {BASE}/our-doctors.html

## Services & conditions treated (dedicated pages)
Full services: {BASE}/services.html
{cond_lines}

## Clinical research
Premiere Research Institute — trials in Alzheimer's, migraine, and MS: {BASE}/clinical-research.html
Institute website: {RESEARCH_URL}

## Appointments & new patients
Free Memory Screen (30 min) and New Patient Appointment (1 hr): {BASE}/appointments.html
Patient Center & new-patient forms: {BASE}/patient-center.html

## Common questions
{BASE}/faq.html
""")

    body = f"""
<main>
{page_hero("404", "This Page Took a <em class='accent'>Wrong Turn</em>",
  "The page you're looking for isn't here — but our team is a click away.")}
<section class="section center">
  <div class="wrap">
    <a class="btn btn-coral" href="/index.html">Back to Home <span class="arr">&rarr;</span></a>
  </div>
</section>
</main>
"""
    write("404.html",
          head("Page Not Found | Palm Beach Neurology",
               "That page took a wrong turn. Find neurology care at Palm Beach Neurology in West Palm Beach, FL.",
               noindex=True) + nav(0, solid=True) + body + footer(0))

if __name__ == "__main__":
    build_home()
    build_conditions()
    build_services()
    build_doctors()
    build_doctor_pages()
    build_research()
    build_appointments()
    build_patient_center()
    build_contact()
    build_faq()
    build_blog()
    build_service_pages()
    build_locations()
    build_about()
    build_insurance()
    build_meta()
    print("\nDone. Open index.html or deploy the folder to Vercel.")
