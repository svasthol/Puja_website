# Mana Guruji website — managuruji.in

Bilingual (English / Telugu) static website for Mana Guruji: puja listings with prices,
booking requests, and the policy pages required for Razorpay onboarding.

## Structure
- `*.html`, `styles.css`, `site.js`, `assets/` — the published site (served from the repo root).
- `_build/` — the generator. Business details, puja catalogue and prices live at the top of
  `_build/build.py`; page styles and scripts in `_build/src/`.

## Updating the site
1. Edit `_build/build.py` (e.g. `BIZ` contact details, prices) or `_build/src/*`.
2. Run `python3 _build/build.py` — it regenerates every page (including one page per puja, the sitemap and
   structured data) in the repo root. For minified CSS/JS first run `pip install rcssmin rjsmin`.
3. Commit and push. Netlify redeploys automatically if the site is linked to this repo.

## Hosting
Hosted on Netlify (publish directory: repo root). The domain managuruji.in stays registered at Wix,
with DNS pointing to Netlify (A `@` → 75.2.60.5, CNAME `www` → <site>.netlify.app).
Booking and contact forms use Netlify Forms. Caching and security headers are set in `netlify.toml`.
