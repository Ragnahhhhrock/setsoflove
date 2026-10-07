# SetsOfLove

A simple dating-profile app for single gym-goers.

## Brand rules

Everything in this repo follows two guides. Nothing is added that doesn't conform to them.

- [`DESIGN_GUIDE.md`](DESIGN_GUIDE.md): colour, type, spacing, logo, icons
- [`STYLE_GUIDE.md`](STYLE_GUIDE.md): voice, copy, profile content rules
- [`tokens/tokens.json`](tokens/tokens.json): the single source of truth for the values in both guides

`python3 scripts/build_tokens.py` regenerates `tokens/tokens.css`.
`python3 scripts/check_conformance.py` verifies every asset against the guides.
