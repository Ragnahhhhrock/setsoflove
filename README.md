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
