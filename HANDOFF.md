# Palm Beach Neurology — Site Handoff & Operations

This folder is a **complete, self-contained website**. It has no dependency on the
First Rehabilitation site or its accounts — its own build script, assets, config, and
(email-only) form delivery. It can be lifted into its own Git repo and Vercel project
without touching anything else.

## Stack at a glance

| Layer | What it uses | Account needed |
|---|---|---|
| Source / build | `build.py` (Python 3, no dependencies) → static HTML | none (any machine with Python 3) |
| Version control | Git / GitHub | GitHub (practice-owned) |
| Hosting / CDN / SSL | Vercel (static, auto-deploys on every push) | Vercel (practice-owned) |
| Domain | palmbeachneurology.com | registrar (point DNS at Vercel) |
| Appointment / patient forms | FormSubmit → email (no database) | an inbox + one-time activation |
| Optional lead database | *not used today* | Supabase (only if DB-stored requests are wanted later) |
| Ongoing edits | Claude Code on the web ↔ GitHub | Claude account (practice-owned) |

**The site does not use Supabase.** Every form posts to FormSubmit and arrives as
email. A Supabase account is only needed if the practice later wants appointment
requests stored in a database/dashboard (the way the First Rehab intake works).

## Build workflow

1. Edit `build.py` — all copy, doctors, conditions, services, and FAQ content live here.
2. `python3 build.py` — regenerates every page in place.
3. Preview: `python3 -m http.server 8000` → http://localhost:8000
4. Commit & push → Vercel auto-deploys.

Never hand-edit the `.html` files; they are generated and will be overwritten.

## Before go-live — verify / replace

These are placeholders or interim values in the config block at the top of `build.py`:

- [ ] **`EMAIL`** — set to the real inbox that should receive appointment requests, then
      submit one test request and click FormSubmit's **activation email** (first send
      only; check spam). Until activated, forms will not deliver.
- [ ] **`PORTAL`** — currently points to the Patient Center page; replace with the real
      EMR / patient-portal login URL when one exists.
- [ ] **Doctor bios** — Dr. Sadowsky and Dr. Zuniga use accurate interim bios; swap in
      their official bios and photos when provided.
- [ ] **Old-URL redirects** — add 301s in `vercel.json` mapping the current
      palmbeachneurology.com (Wix) URLs to the new pages, so existing search rankings
      carry over. Get the old URL list from Google Search Console → Pages, or the Wix
      sitemap. Do this **before** the DNS cutover.
- [ ] **Google Business Profile** — after launch, update the website link and submit
      `sitemap.xml` in Google Search Console.

## Maintaining it with Claude Code

Connect the practice's GitHub repo to Claude Code on the web (claude.ai/code). Describe
a change in plain English ("add a new doctor", "update the office hours", "write a blog
post about migraine triggers") and it edits `build.py`, rebuilds, and opens a pull
request that Vercel previews before anything goes live — the same workflow that built
this site.
