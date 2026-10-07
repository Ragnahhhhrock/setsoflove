# SetsOfLove Design Guide

The visual rules for everything SetsOfLove ships. Values come from `tokens/tokens.json`; if this guide and the tokens ever disagree, the tokens win and this guide gets fixed.

**Rule zero: nothing ships that does not conform.** Every asset must be built from the tokens below and pass `python3 scripts/check_conformance.py`. If something you need isn't covered here, update the guide first, then make the asset.

## 1. Brand in one line

A grown-up, friendly place for single gym-goers to be found by someone worth meeting. Warm, confident, a bit cheeky. Never sleazy, never frat.

The idea behind the mark: a barbell with a heart where the weight would be. Sets, then love.

## 2. Colour

Nine colours. No others, no tints, no gradients, no opacity tricks.

| Token | Hex | Use |
|---|---|---|
| ink | `#1B1F2A` | Primary text, dark surfaces, logo body |
| chalk | `#F7F3EC` | Default page background, reversed logo body |
| iron | `#4A5060` | Secondary text, icons |
| plate | `#E4DED3` | Borders, dividers, disabled fills. Never for text |
| coral | `#C8323A` | Brand accent, primary buttons, the heart |
| coral-deep | `#A32630` | Pressed state, error text and borders |
| white | `#FFFFFF` | Text on coral or ink, card surfaces |
| sage | `#2F6B4F` | Success only |
| amber | `#8A5A00` | Warning only |

### Approved pairings (WCAG 2.x contrast, calculated)

| Text / graphic | On | Ratio | Allowed for |
|---|---|---|---|
| ink | chalk | 14.88 | All text |
| ink | white | 16.46 | All text |
| iron | chalk | 7.28 | All text |
| iron | white | 8.05 | All text |
| white | coral | 5.29 | All text (buttons) |
| white | coral-deep | 7.30 | All text |
| chalk | ink | 14.88 | All text (dark mode, reversed logo) |
| coral | chalk | 4.78 | Text 14px and up, graphics |
| coral | white | 5.29 | Text 14px and up, graphics |
| coral-deep | chalk | 6.60 | All text, error messages |
| sage | white | 6.29 | Success text |
| amber | white | 5.93 | Warning text |
| coral | ink | 3.11 | **Graphics and large text (24px+) only.** Never body text |
| ink | plate | 12.29 | All text |
| coral | plate | 3.95 | Graphics only |

Any pairing not in this table is not allowed. Plate on chalk is 1.21:1, so plate is for borders and fills only.

Colour is never the only signal. Errors get an icon and a message as well as coral-deep.

## 3. Typography

One family: **Inter**, weights 400, 500, 600, 700. Fallback: `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`.

| Style | Size / line | Weight |
|---|---|---|
| display | 40 / 48 | 700 |
| h1 | 32 / 40 | 700 |
| h2 | 24 / 32 | 700 |
| h3 | 20 / 28 | 600 |
| body | 16 / 24 | 400 |
| label | 14 / 20 | 600 |
| small | 14 / 20 | 400 |
| caption | 12 / 16 | 500 |

- Minimum body text on mobile is 16px (stops iOS zooming into form fields).
- Sentence case everywhere, including buttons and headings. No all-caps.
- Left-aligned. Centre only for the logo lockup and empty states.
- Line length 45 to 75 characters.

## 4. Spacing, shape and layout

- 4px base grid. Allowed spacing steps: **4, 8, 12, 16, 24, 32, 48, 64**.
- Radii: 8 (inputs, chips), 12 (buttons, cards), 16 (large cards, images), full (avatars, pills).
- Mobile first. Design at 390px wide, scale up. Page gutter 16px on mobile, 24px on tablet and up. Content max width 640px for profile pages.
- Minimum touch target **44 x 44px**.
- No drop shadows, glows or blurs. Separation comes from `plate` borders (1px) and spacing.

## 5. Components (rules, not pictures)

- **Primary button:** coral fill, white label (label style), 12px radius, 48px high, full width on mobile. Pressed: coral-deep.
- **Secondary button:** white fill, 1px ink border, ink label.
- **Text input:** white fill, 1px plate border (ink on focus, 2px), 8px radius, 48px high, label above in label style. Error: coral-deep border, icon and message below.
- **Profile card:** white, 1px plate border, 16px radius, photo on top at 4:5, 16px padding.
- **Profile photos:** 4:5 portrait crop. At least one clear face photo. Photos are never filtered, tinted or overlaid by the app.

## 6. Logo

The mark is a heart on a barbell: a coral heart sitting on an ink bar, flanked by two weight plates either side.

Files in `assets/logo/`:

| File | Use |
|---|---|
| `logo-mark.svg` | Mark alone, on chalk or white |
| `logo-mark-reversed.svg` | Mark alone, on ink |
| `logo-lockup.svg` | Mark plus wordmark, on chalk or white |
| `logo-lockup-reversed.svg` | Mark plus wordmark, on ink |

Rules:

- Use only these files. Don't redraw, recolour, rotate, stretch, outline or add effects.
- Clear space on every side equals one quarter of the mark's height.
- Minimum size: mark 24px tall, lockup 32px tall. Below 32px use the small-size mark (heart on ink tile, section 7).
- Wordmark is "setsoflove", all lowercase, Inter Bold, set as outlines with the mark. Never retype it in a font.
- Place on chalk, white or ink only. Never on photos or coral.

## 7. App icon and favicon

Files in `assets/icons/`:

| File | Size | Notes |
|---|---|---|
| `app-icon.svg` | 1024 | Master. Ink square, chalk and coral mark |
| `icon-1024.png`, `icon-512.png`, `icon-192.png` | 1024, 512, 192 | Opaque, square, no rounded corners (the platform masks them) |
| `apple-touch-icon.png` | 180 | Opaque |
| `favicon.svg` | scalable | Small-size mark: coral heart on an ink tile, no plates |
| `favicon.ico` | 16, 32, 48 | Same small-size mark |

- The mark fills 60% of the icon canvas, centred, so it sits inside the 80% maskable safe zone.
- Icons are never transparent.

## 8. Imagery and iconography

- Icons: outline style, 2px stroke at 24px, round caps and joins, colour `iron` (or `ink` when active, `coral` for the primary action). Draw from one set only; don't mix styles.
- Photography guidance for profile content lives in `STYLE_GUIDE.md`.
- No stock photos, no illustrations of people, no emoji in the interface.

## 9. Accessibility

- All text meets the pairings in section 2.
- Visible focus ring on every interactive element: 2px ink outline with 2px offset.
- Every image has alt text. Profile photos get "Photo of [first name]".
- Respect reduced-motion. Motion is limited to 150ms to 200ms fades and slides. Nothing bounces, pulses or auto-plays.

## 10. Asset checklist

Before an asset is committed:

1. Built only from section 2 colours, section 3 type and section 4 spacing.
2. Listed in this guide (new asset types: add them here first).
3. `python3 scripts/check_conformance.py` passes.
4. Looked at, at actual size, on chalk and on ink where relevant.

## 11. Web pages

The Cloudflare Pages app (`public/`, `functions/`) is an asset type too. Legal pages are built from `content/*.html` by `python3 scripts/build_legal.py` into `public/terms/` and `public/privacy/`.

- Styles use only `tokens/tokens.css` variables. No hex colours, gradients or `box-shadow` in `public/app.css`.
- Every page links to the terms of use and privacy policy in the footer.
- Profile pages live at `/<stub>`, are `noindex`, and carry Open Graph preview tags and share buttons (Facebook, X, WhatsApp, email, plus Copy link and Share where the browser supports them).
- Share buttons are secondary buttons with text labels. They are plain links: no third-party scripts, logos or tracking.
- Sign-up requires the member to accept the terms and privacy policy and to confirm that their approved profile is visible to anyone with their link. The accepted version and time are stored (`lib/legal.js`, `users.terms_version`).
- Copy follows `STYLE_GUIDE.md`: no banned words, no exclamation marks, no emoji.
