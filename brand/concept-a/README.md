# SetsOfLove brand: Concept A (exploration)

Not adopted. The live brand is still `DESIGN_GUIDE.md`, `STYLE_GUIDE.md` and `tokens/tokens.json`. This folder holds a proposed alternative: a flexed bicep inside a heart, coral and night ink, Bricolage Grotesque and DM Sans. Nothing here is wired into `assets/`, `public/` or the conformance check.

---

SetsOfLove is a dating-profile app for single men at one gym who are looking for women. Gym photos are the main event, not a side note, and the whole brand follows from that: warm, a little dry, built around one mark, a flexed bicep inside a heart.

## Content fundamentals

- Voice is friendly and dry. Put the humour in the product (button labels, empty states, notices), never in a member's own profile text.
- Write sentence case everywhere. The only uppercase is the `eyebrow` style.
- Speak to the member as "you". Keep "we" for the admin voice ("we'll check your edit").
- Use plain gym words: sets, lifts, training. Never body-shame, rank or score anyone.
- No emoji in the interface. The mark is the only heart and the only flex.
- The words we avoid live in `STYLE_GUIDE.md` in the repo. Follow it first; this guide does not replace it.
- Real labels from the app: "Send for approval", "Edit profile", "Report this profile". Status words: Pending approval, Live, Needs changes.
- A rejection or takedown always carries a note that tells the member what to change.

## Visual foundations

- **Colour.** `surface` is the page, `surface-raised` is a card, `ink` is text, `ink-muted` is secondary text. `brand` coral belongs to the mark and to large graphics. Use `brand-text` for small coral text and `action` for the primary button. `gold` is only the arrow, highlights and the pending status.
- **Contrast rules.** Never set body-size text on `brand`. Text on `action` is `on-action`. Text on `gold` is `on-gold`. Every status is a word plus an icon, never colour alone.
- **Type.** Bricolage Grotesque (`display-xl`, `display-l`, `heading`, `stat`) for the name, headlines and lift numbers. DM Sans (`body-l`, `body`, `body-s`, `label`, `eyebrow`) for everything else. Both load from Google Fonts.
- **Spacing and shape.** Use `space-1` to `space-8`. Cards are `radius-lg`, buttons and inputs `radius-md`, chips `radius-pill`, the app icon `radius-xl`.
- **Borders over shadows.** Separate cards with a 1px `line` on `surface-raised`. The system defines no shadows.
- **Focus.** A solid 2px `focus` ring with a 2px offset on every interactive element.
- **Imagery.** Photos are the hero: 1 to 4 per profile, the main one showing the member's face. Gym and workout shots are welcome. Photos sit in a 4:5 frame with `radius-lg` corners and no filters, borders or overlays on top.
- **Motion.** None is defined. Keep any transition to a quick fade.

## Logo

- The mark is a coral heart (`brand`) with a cream flexed bicep (`paper`) centred in it. Use the files in Logos; never redraw it.
- The wordmark is "SetsOfLove" in Bricolage Grotesque 800 with -0.02em tracking: "SetsOf" in `ink`, "Love" in `brand` (or `brand-text` below 24px).
- In the horizontal lockup the mark is about 1.6 times the wordmark's font size, with a gap of about 0.35 times it.
- Keep clear space of a quarter of the mark's width on every side.
- Below 32px, and for favicons, use `mark-simple.svg`, which drops the knuckle and crease lines.
- Put the mark on `paper`, `night` or `surface`. Never on `brand` or any coral ground, where the heart disappears.
- The app icon is `app-icon.svg`: the mark centred on `night` with `radius-xl` corners.

## Iconography

- There is no icon set yet. Draw interface icons as 24px outline icons, 2px stroke, round caps and joins, in `currentColor`.
- Check, clock and alert are the first three needed, for Live, Pending approval and Needs changes.
- Do not use emoji or filled hearts as icons.

## Using the tokens

- Page: `surface`. Card: `surface-raised` with a 1px `line`. Text: `ink`. Secondary text: `ink-muted`.
- Primary action: `action` fill, `on-action` text. Secondary action: `control-border` outline, `ink` text.
- Links and small coral text: `brand-text`.
- Inputs, chips and secondary buttons take a 1.5px `control-border`.
