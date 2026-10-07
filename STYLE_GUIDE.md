# SetsOfLove Style Guide

How SetsOfLove sounds and how its content is written. Pairs with `DESIGN_GUIDE.md`, which covers how it looks. Every piece of copy and every asset must conform to both.

## 1. Voice

SetsOfLove talks like a good gym regular: friendly, direct, a little dry. It treats members as capable adults.

| We are | We are not |
|---|---|
| Warm | Gushing |
| Confident | Pushy or salesy |
| Dry-humoured | Crude, suggestive or "bro" |
| Plain-spoken | Jargon-heavy or corporate |
| Respectful | Pickup-artist, thirsty or objectifying |

Gym puns are welcome in small doses, and only where they help (one per screen at most, never in errors or safety messages).

## 2. Language rules

- **Australian English:** colour, favourite, organise, centre, programme only for a TV programme (use "program" for software).
- **Sentence case** for everything: headings, buttons, labels, menu items. Proper nouns keep their capitals.
- **Product name:** SetsOfLove in running text (capital S, O, L). The wordmark in the logo is the only place it appears as "setsoflove".
- **Short:** sentences under 20 words. One idea per sentence. Active voice.
- **Plain words:** "Sign in", not "Authenticate". "Photo", not "Media asset".
- **Numbers:** numerals for everything except "one" in running prose. Dates as 7 Oct 2026. Times as 6:30 am.
- **Contractions** are fine ("you're", "we'll").
- **No emoji, no exclamation marks** in interface copy, except at most one exclamation mark on a success moment.
- **Punctuation:** no full stop on buttons, labels or single-sentence helper text. Use full stops in multi-sentence messages. Use the Oxford comma only when it prevents ambiguity.
- **Avoid:** "hot", "babe", "hunk", "swipe", "match" (there's no matching algorithm here), "bro", "thirst", innuendo about bodies or lifting.

## 3. Words we use

| Use | Instead of |
|---|---|
| Profile | Listing, ad |
| Member | User, customer |
| Sign in / Sign out | Log in / Log out |
| Create your profile | Register, onboard |
| Your link | URL stub, slug |
| Send for approval | Submit for moderation |
| Approved | Live, published |

## 4. UI copy patterns

**Buttons:** verb first, 1 to 3 words. "Create account", "Sign in", "Add photos", "Save profile", "Send for approval".

**Labels:** noun phrases, no colon. "First name", "About you", "What you do".

**Helper text:** one short line under the field. Say what's wanted, not what's wrong. "Use a clear photo of your face."

**Errors:** say what happened and what to do next, with no blame and no humour.

- Good: "That email or password doesn't match. Check them and try again."
- Bad: "Oops! Something went wrong!"

**Empty states:** one sentence plus one action. "No photos yet. Add your first one."

**Success:** short and specific. "Profile sent for approval. We'll let you know once it's live."

**Confirmations for destructive actions:** name the thing. "Delete your profile? This can't be undone." Buttons: "Delete profile" and "Keep profile".

## 5. Profile content

Profiles are reviewed and approved by the admin before they go live. Keep these standards visible to members when they create a profile.

**Photos**

- Clear, recent, well lit, and the member is easy to recognise.
- At least one photo where the face is clearly visible, with no sunglasses or hat shading it.
- Gym and workout photos are encouraged: training shots, gym kit, a post-session mirror pic. No nudity, nothing sexual, nothing obscene.
- Only photos the member has the right to share. No photos of other people without their consent.
- Not allowed: photos of other people as the main image, screenshots, memes, or images with overlaid text or logos.

**Written fields**

- Written in the member's own voice, in plain language.
- Positive framing: say what you're looking for, not what you can't stand.
- Not allowed: anything obscene, discriminatory, hateful, political rants, contact details such as phone numbers or social handles in public text fields, or anything controversial.

**Lifts**

- Optional. Bench press, squat, deadlift and overhead press, entered in kg or lb.
- Stored in kg and shown in both units, with the member's chosen unit first. Example: "100 kg (220 lb)".
- Real numbers only. The admin can ask for changes if a figure looks off.

**Link stubs (profile URLs)**

- Lowercase letters, numbers and hyphens only, 3 to 30 characters.
- First name and a number or initial work well: `sam-t`, `dave-42`.
- No full surnames, no phone numbers, nothing offensive. Reserved words (admin, login, signup, api and similar) are blocked.

**Tone of the member-facing guidance:** friendly and brief. "Keep it friendly and keep it clean. We approve every profile before it goes live."

## 6. Writing for the logo and assets

- The logo is never retyped. Use the supplied files.
- Alt text for the logo: "SetsOfLove". For the mark alone: "SetsOfLove logo".
- File names are lowercase, hyphen-separated, descriptive: `logo-lockup-reversed.svg`, `icon-512.png`.
- Every SVG carries a `<title>` matching its alt text.

## 7. Style checklist for new copy

1. Sentence case, Australian spelling.
2. Verb-first on buttons, nothing cheesy in errors.
3. No banned words from section 2.
4. Would a 40-year-old find it friendly rather than cringe?
5. Does it work out loud, read to a mate?
