# SetsOfLove Design Guide

The visual rules for everything SetsOfLove ships. Values come from `tokens/tokens.json`; if this guide and the tokens ever disagree, the tokens win and this guide gets fixed.

**Rule zero: nothing ships that does not conform.** Every asset must be built from the tokens below and pass `python3 scripts/check_conformance.py`. If something you need isn't covered here, update the guide first, then make the asset.

## 1. Brand in one line

A grown-up, friendly place for single gym-goers to be found by someone worth meeting. Warm, confident, a bit cheeky. Never sleazy, never frat.

The idea behind the mark: a love heart with a flexed bicep inside it. Strength, then love.

## 2. Colour

Eleven colours. No others, no tints, no gradients, no opacity tricks in the interface. (The mark itself is the 3D emoji artwork, which carries its own shading.)

| Token | Hex | Use |
|---|---|---|
| ink | `#1B1D26` | Primary text, dark surfaces, app icon ground |
| chalk | `#FFF6EC` | Default page background, reversed wordmark |
| iron | `#4A4D5A` | Secondary text, icons |
| plate | `#E8DCCD` | Borders, dividers, disabled fills. Never for text |
| coral | `#CC233B` | Primary buttons, links and small red text |
| coral-deep | `#A3182C` | Pressed state, error text and borders |
| heart | `#FF2C4A` | The heart in the logo. Graphics and large text (24px+) only |
| yellow | `#FFC139` | The flex in the logo. Highlights and fills, never text |
| white | `#FFFFFF` | Text on coral or ink, card surfaces |
| sage | `#2F6B4F` | Success only |
| amber | `#8A5A00` | Warning only |

### Approved pairings (WCAG 2.x contrast, calculated)

| Text / graphic | On | Ratio | Allowed for |
|---|---|---|---|
| ink | chalk | 15.71 | All text |
| ink | white | 16.80 | All text |
| ink | yellow | 10.35 | All text |
| ink | plate | 12.44 | All text |
| iron | chalk | 7.86 | All text |
| iron | white | 8.40 | All text |
| white | coral | 5.42 | All text (buttons) |
| white | coral-deep | 7.71 | All text |
| chalk | ink | 15.71 | All text (dark surfaces, reversed wordmark) |
| coral | chalk | 5.08 | All text |
| coral | white | 5.42 | All text |
| coral-deep | chalk | 7.21 | All text, error messages |
| sage | white | 6.29 | Success text |
| amber | white | 5.93 | Warning text |
| amber | chalk | 5.54 | Warning text |
| heart | ink | 4.57 | Large text (24px+) and graphics only |
| heart | chalk | 3.44 | Graphics and large text (24px+) only |

Any pairing not in this table is not allowed. Plate on chalk is 1.21:1, so plate is for borders and fills only.

Colour is never the only signal. Errors get an icon and a message as well as coral-deep.

## 3. Typography

Two families, both self-hosted: **Bricolage Grotesque** (700, 800) for the wordmark, display and headings, and **DM Sans** (400, 500, 600) for everything else. Fallback: `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`.

| Style | Size / line | Weight |
|---|---|---|
| display | 40 / 48 | 800 |
| h1 | 32 / 40 | 700 |
| h2 | 24 / 32 | 700 |
| h3 | 20 / 28 | 700 |
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

The mark is the standard red love-heart emoji with the flexed-biceps emoji centred in it. Artwork: Microsoft Fluent Emoji 3D (MIT licence, `brand-src/FLUENT-EMOJI-LICENSE.txt`). Source glyphs are in `brand-src/`; every logo file is built from them by `scripts/build_assets.py`.

Files in `assets/logo/` (PNG with transparent background):

| File | Use |
|---|---|
| `logo-mark.png` | Mark alone, 512px, on any approved surface |
| `logo-mark-small.png` | Mark alone, 128px, larger flex for small sizes |
| `logo-lockup.png` | Mark plus wordmark, for chalk or white |
| `logo-lockup-reversed.png` | Mark plus wordmark, for ink |

Rules:

- Use only these files. Don't redraw, recolour, rotate, stretch, outline or add effects.
- Wordmark is "SetsOfLove" in Bricolage Grotesque 800, with "Love" in the heart colour. Never retype it in another font.
- Clear space on every side equals one quarter of the mark's height.
- Minimum size: mark 24px tall, lockup 32px tall. Below 48px use `logo-mark-small.png`.
- Place on chalk, white or ink only. Never on photos or coral.

## 7. App icon and favicon

Files in `assets/icons/`:

| File | Size | Notes |
|---|---|---|
| `icon-1024.png`, `icon-512.png`, `icon-192.png` | 1024, 512, 192 | Opaque, square, no rounded corners (the platform masks them) |
| `apple-touch-icon.png` | 180 | Opaque |
| `favicon.ico` | 16, 32, 48 | Small-size mark on an ink tile |

- The mark is 62% of the icon width on an ink ground, centred, inside the 80% maskable safe zone.
- Icons are never transparent.

## 8. Social images

Shown when a SetsOfLove link is shared in a message, feed or search result.

Files in `assets/social/`:

| File | Size | Notes |
|---|---|---|
| `og-image.png` | 1200 x 630 | Open Graph image. Ink background, reversed lockup |
| `twitter-card.png` | 1200 x 600 | Twitter (X) large summary card, 2:1. Chalk background, standard lockup |

- Built at 2x the interface scale (display 80 / 96, body 32 / 48, page padding 64), with Bricolage Grotesque for the headline and DM Sans for body text.
- Layout: lockup top left, headline in display style with the second line in the heart colour (large text), one line of body text under it. Left-aligned, sentence case.
- Opaque PNG, no photos, no member content. Profile pages use these same images, never a member's photo.
- Corner pixel must match the background colour (ink for `og-image.png`, chalk for `twitter-card.png`).

## 9. Imagery and iconography

- Icons: outline style, 2px stroke at 24px, round caps and joins, colour `iron` (or `ink` when active, `coral` for the primary action). Draw from one set only; don't mix styles.
- Photography guidance for profile content lives in `STYLE_GUIDE.md`.
- No stock photos, no illustrations of people, no emoji in the interface copy (the logo is the one exception).

## 10. Accessibility

- All text meets the pairings in section 2.
- Visible focus ring on every interactive element: 2px ink outline with 2px offset.
- Every image has alt text. Profile photos get "Photo of [first name]".
- Respect reduced-motion. Motion is limited to 150ms to 200ms fades and slides. Nothing bounces, pulses or auto-plays.

## 11. Asset checklist

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
