# SetsOfLove brand: Concept A, emoji mark (exploration)

Not adopted. The live brand is still `DESIGN_GUIDE.md`, `STYLE_GUIDE.md` and `tokens/tokens.json`. This folder proposes an alternative: the red-heart emoji with the flexed-biceps emoji centred in it (Microsoft Fluent Emoji 3D, MIT, see `logo/FLUENT-EMOJI-LICENSE.txt`), Bricolage Grotesque and DM Sans, heart red and night ink. Nothing here is wired into `assets/`, `public/` or the conformance check.

Differences from the live guides to settle before adopting: the wordmark is "SetsOfLove" in capitals (live guide: lowercase "setsoflove" in Inter), the type is Bricolage Grotesque and DM Sans (live: Inter), and the logo carries gradients and 3D shading (live guide: no gradients).

---

SetsOfLove is a dating-profile app for single men at one gym who are looking for women. Gym photos are the main event, and the brand follows from that: warm, a little dry, and built around one mark, the flexed-bicep emoji sitting inside a love heart.

## Content fundamentals

- Voice is friendly, direct and a little dry. Treat members as capable adults. Put any humour in the product, never in a member's own profile text, and never in errors or safety messages.
- Write in Australian English (colour, favourite, organise, centre) and sentence case everywhere. The only uppercase is the `eyebrow` style.
- Write "SetsOfLove" in running text. The wordmark in the logo is set in the exact same capitals.
- Speak to the member as "you". Keep "we" for the admin voice ("We'll let you know once it's approved").
- Use the member words: Profile, Member, Sign in, Create your profile, Your link, Send for approval, Approved. Never Listing, User, Log in, Register, Slug, Live or Published.
- Buttons are verb first, 1 to 3 words: "Create account", "Add photos", "Save profile", "Send for approval". Labels are noun phrases with no colon.
- Errors say what happened and what to do next, with no blame and no humour: "That email or password doesn't match. Check them and try again."
- No emoji and no exclamation marks in interface copy, apart from at most one exclamation mark on a success moment. The logo is the only emoji artwork in the product.
- Never use: hot, babe, hunk, swipe, match, bro, thirst, or innuendo about bodies or lifting.
- The full voice rules are `STYLE_GUIDE.md` in the repo. Follow it first; this book never overrides it.

## Visual foundations

- **Colour.** `surface` is the page, `surface-raised` is a card, `ink` is text, `ink-muted` is secondary text. `brand` heart red belongs to the mark, large graphics and the word Love at 24px or larger. Use `brand-text` for small red text and links, and `action` for the primary button. `yellow` is the pending status and highlights.
- **Contrast.** Never set body-size text on `brand` or `yellow`. Text on `action` is `on-action`. Text on `yellow` is `on-yellow`. Every status is a word plus an icon, never colour alone.
- **Type.** Bricolage Grotesque (`display-xl`, `display-l`, `heading`, `stat`) for the name, headlines and lift numbers. DM Sans (`body-l`, `body`, `body-s`, `label`, `eyebrow`) for everything else. Both ship as font files with the system.
- **Spacing and shape.** Use `space-1` to `space-8`. Cards are `radius-lg`, buttons and inputs `radius-md`, chips `radius-pill`.
- **Flat, except the mark.** The logo is the only place with gradients and 3D shading. Everything else is flat: no gradients, glows, blurs or drop shadows. Separate cards with a 1px `line` on `surface-raised`.
- **Focus.** A solid 2px `focus` ring with a 2px offset on every interactive element, and targets of at least 44px.
- **Imagery.** Photos are the hero: 1 to 4 per profile, the main one showing the member's face. Gym and workout shots are welcome. Photos sit in a 4:5 frame with `radius-lg` corners and no filters or overlays. No stock photos and no illustrations of people.
- **Motion.** 150ms to 200ms fades and slides only. Nothing bounces, pulses or auto-plays, and reduced-motion is respected.

## Logo

- The mark is the red-heart emoji with the flexed-biceps emoji centred in it, in Microsoft's Fluent Emoji 3D artwork, default yellow skin tone. Use the files in Logos; never rebuild or recolour it.
- The wordmark is "SetsOfLove" in Bricolage Grotesque 800 with -0.02em tracking. "SetsOf" is `ink` (or `paper` on a dark ground) and "Love" is `brand`. Below 24px set "Love" in `brand-text` instead.
- In the horizontal lockup the mark is about 1.35 times the wordmark's font size tall, with a gap of about 0.36 times the font size. Use the supplied lockup files rather than retyping it.
- Clear space is a quarter of the mark's width on every side.
- Minimum size: mark 32px wide, lockup 40px tall. Below 32px use `setsoflove-mark-small.png`, where the flex is larger relative to the heart.
- Put the logo on `paper`, `night` or `surface`. Never on `brand`, `brand-tint` or any pink or red ground, where the heart disappears, and never on photos.
- Don't change the emoji's skin tone, swap either glyph, flip, rotate, stretch, outline or add a shadow.
- The app icon is `setsoflove-app-icon.png`: the mark on a `night` square, filling 62% of the canvas so it sits inside the maskable safe zone. Opaque and square; the platform rounds the corners.
- The artwork is Microsoft's Fluent Emoji (MIT licence), so the mark is not exclusive to SetsOfLove. Keep `FLUENT-EMOJI-LICENSE.txt` with any redistributed copy.

## Iconography

- There is no icon set yet. Draw interface icons as 24px outline icons, 2px stroke, round caps and joins, in `currentColor`.
- Check, clock and alert are the first three needed, for Approved, Pending approval and Needs changes.
- Do not use emoji or filled hearts as interface icons.

## Using the tokens

- Page: `surface`. Card: `surface-raised` with a 1px `line`. Text: `ink`. Secondary text: `ink-muted`.
- Primary action: `action` fill, `on-action` text. Secondary action: 1.5px `control-border` outline, `ink` text.
- Links and small red text: `brand-text`.
- Inputs, chips and secondary buttons take a 1.5px `control-border`.
