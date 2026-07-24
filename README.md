# Palm Beach Neurology & Premiere Research Institute — Website

Self-contained marketing site for Palm Beach Neurology (West Palm Beach, FL).
One Python script generates every page; deploy the folder to Vercel.

## Build & preview
- `python3 build.py` — regenerates all HTML in place (no dependencies).
- `python3 -m http.server 8000` → http://localhost:8000
- Deploy: import this repo in Vercel (Framework preset: **Other**; the HTML is
  prebuilt and committed, `vercel.json` handles clean URLs, caching, and headers).

## Structure
- `build.py` — single source of truth (copy, doctors, conditions, services, FAQ).
- `content/*.json` — generated city / service / condition / blog / About / insurance
  content consumed by `build.py`.
- `assets/` — self-hosted fonts, CSS, JS (incl. the help assistant), images.
- `vercel.json` — clean URLs, caching, and security headers.
- `HANDOFF.md` — full stack overview, pre-launch checklist, and maintenance guide.

Never hand-edit the generated `.html` files — edit `build.py` (or `content/*.json`)
and rebuild. See **HANDOFF.md** for the complete operations guide.
