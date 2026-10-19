# SetsOfLove

A simple dating-profile app for single gym-goers.

## Brand rules

Everything in this repo follows two guides. Nothing is added that doesn't conform to them.

- [`DESIGN_GUIDE.md`](DESIGN_GUIDE.md): colour, type, spacing, logo, icons
- [`STYLE_GUIDE.md`](STYLE_GUIDE.md): voice, copy, profile content rules
- [`tokens/tokens.json`](tokens/tokens.json): the single source of truth for the values in both guides

`python3 scripts/build_tokens.py` regenerates `tokens/tokens.css`.
`python3 scripts/check_conformance.py` verifies every asset against the guides.

## Building and checking assets

Requires Python 3 with `pillow`, `fonttools`, `numpy` and `playwright` (Chromium).

```
python3 scripts/build_tokens.py        # tokens.json -> tokens.css
python3 scripts/build_assets.py        # logos and icons, built only from tokens
python3 scripts/check_conformance.py   # must pass before every commit
```

Assets live in `assets/logo/` and `assets/icons/`. A new asset type must be added to `DESIGN_GUIDE.md` and the checker first.

## The app

Cloudflare Pages (`public/` and `functions/`) with D1 and R2. See [`DEPLOY.md`](DEPLOY.md) for setup. Brand files in `public/` (`tokens.css`, `brand/`, icons) are copies of `tokens/` and `assets/`; recopy them after rebuilding assets.

## Legal pages and sharing

- Legal copy lives in `content/terms.html` and `content/privacy.html`. After editing, run `python3 scripts/build_legal.py` and commit `public/terms/` and `public/privacy/`. Change the date at the top and `TERMS_VERSION` in `lib/legal.js` when the change is material.
- `CONTACT_EMAIL` in `wrangler.toml` is `contact@setsoflove.com`. It appears in the footer of every page and in the "Report this profile" link.
- Run `npx wrangler d1 migrations apply setsoflove --remote` to add the terms-acceptance columns (migration 0002), the contact messages table (0003) the lift stat columns (0004) the city and country columns (0005) and the gender, interested-in and seeking columns (0006).
- The contact form lives at `/contact` and posts to `/api/contact`. See `DEPLOY.md` for email setup.
- Search lives at `/search` and `/api/search`. It needs a signed-in member and only returns approved profiles, alphabetically.
- Each approved profile page (`/<stub>`) has preview tags for social sharing and share buttons.
- The sign-up form must send `accept_terms: true` and `consent_public: true` to `/api/signup`.

## Analytics and homepage stats

- Google Analytics 4 is wired in through `public/analytics.js`. The Measurement ID is `G-FJKNFMW5NN`, set in `GA_MEASUREMENT_ID`. The Google tag gateway is built in: the tag and hits go through `/metrics` (`functions/metrics/[[path]].js`). Don't also switch on Cloudflare's own Google tag gateway. Event names and the privacy rules are in `DESIGN_GUIDE.md` section 13.
- The homepage strip reads `/api/stats` (anonymous totals, cached for 5 minutes). It stays hidden until sign-ups reach `STATS_MIN_SIGNUPS` in `wrangler.toml`.

## Blog

Posts, plan and publishing schedule are described in [`BLOG.md`](BLOG.md). `python3 scripts/build_blog.py` builds the posts that are due, and a GitHub Action (`.github/workflows/publish-blog.yml`) runs it every 15 minutes and commits the result. Writing rules are in `content/blog/BRIEF.md`; `python3 scripts/check_blog.py` checks every post.
