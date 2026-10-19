#!/usr/bin/env python3
"""Build the SetsOfLove explainer video in landscape (1920x1080) and portrait (1080x1920).

Output goes to public/video/. Everything is drawn from the design tokens, the site
fonts and the logo files, so it follows DESIGN_GUIDE.md section 14. The sound is three
cuts from the band track in brand-src/music/, and the profile shown is the owner's own
(setsoflove.com/malgordon), with its photos fetched from the live site at build time.

Needs: Pillow, fonttools and brotli (to read the site's woff2 fonts), and ffmpeg.
Run: python3 scripts/build_video.py
"""
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "video"
SONG = ROOT / "brand-src" / "music" / "sets-of-love-anthem.mp3"
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
C = {k: tuple(int(v["hex"][i:i + 2], 16) for i in (1, 3, 5)) for k, v in TOKENS["colour"].items()}
INK, CHALK, IRON, PLATE = C["ink"], C["chalk"], C["iron"], C["plate"]
CORAL, HEART, YELLOW, WHITE = C["coral"], C["heart"], C["yellow"], C["white"]

S = 3            # interface scale: the video is drawn at 3x the token sizes
FPS = 30
FADE = 0.2       # DESIGN_GUIDE.md section 10: fades and slides of 150 to 200 ms
SS = 4           # supersampling for shapes

SPACING = {s: s * S for s in (4, 8, 12, 16, 24, 32, 48, 64)}

# (font key, size, line height). Interface scale x3, plus one hero size (4x display).
FONT_FILES = {
    "d800": "bricolage-grotesque-latin-800-normal",
    "d700": "bricolage-grotesque-latin-700-normal",
    "t400": "dm-sans-latin-400-normal",
    "t500": "dm-sans-latin-500-normal",
    "t600": "dm-sans-latin-600-normal",
}
HERO = ("d800", 160, 176)
DISPLAY = ("d800", 120, 144)
H1 = ("d700", 96, 120)
H2 = ("d700", 72, 96)
H3 = ("d700", 60, 84)
BODY = ("t400", 48, 72)
SMALL = ("t400", 42, 60)
LABEL = ("t600", 42, 60)
CAPTION = ("t500", 36, 48)

_font_dir: Path | None = None
TRANSCRIPT: list[str] = []


def prepare_fonts(tmp: Path):
    """Convert the site's woff2 fonts to ttf so Pillow can read them."""
    global _font_dir
    from fontTools.ttLib import TTFont
    for stem in FONT_FILES.values():
        f = TTFont(ROOT / "public" / "fonts" / f"{stem}.woff2")
        f.flavor = None
        f.save(tmp / f"{stem}.ttf")
    _font_dir = tmp


@lru_cache(maxsize=None)
def font(key: str, size: int):
    return ImageFont.truetype(str(_font_dir / f"{FONT_FILES[key]}.ttf"), size)


def spec_font(spec):
    return font(spec[0], spec[1])


# ---------------------------------------------------------------- text

def wrap(f, text: str, width: float):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def draw_text(img, x, y, s, spec, fill, anchor="l"):
    f = spec_font(spec)
    asc, desc = f.getmetrics()
    base = y + (spec[2] - (asc + desc)) / 2 + asc
    ImageDraw.Draw(img).text((x, base), s, font=f, fill=fill, anchor=anchor + "s")


def draw_lines(img, x, y, lines, spec, fill):
    for i, line in enumerate(lines):
        draw_text(img, x, y + i * spec[2], line, spec, fill)


# ---------------------------------------------------------------- shapes

_masks: dict = {}


def _mask(w, h, r):
    key = (w, h, r)
    if key not in _masks:
        m = Image.new("L", (w * SS, h * SS), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), radius=min(r, w // 2, h // 2) * SS, fill=255)
        _masks[key] = m.resize((w, h), Image.LANCZOS)
    return _masks[key]


def rrect(img, x, y, w, h, r, fill=None, outline=None, bw=0):
    x, y, w, h, r = (round(v) for v in (x, y, w, h, r))
    if outline is not None and bw:
        img.paste(outline, (x, y), _mask(w, h, r))
        if fill is not None:
            img.paste(fill, (x + bw, y + bw), _mask(w - 2 * bw, h - 2 * bw, max(r - bw, 0)))
    elif fill is not None:
        img.paste(fill, (x, y), _mask(w, h, r))


@lru_cache(maxsize=None)
def icon(name: str, size: int, colour: tuple):
    """Outline icon, 2px stroke at 24px, round caps and joins (DESIGN_GUIDE.md section 9)."""
    u = size * SS / 24
    sw = round(2 * u)
    m = Image.new("L", (size * SS, size * SS), 0)
    d = ImageDraw.Draw(m)

    def P(px, py):
        return (px * u, py * u)

    def cap(px, py):
        cx, cy = P(px, py)
        d.ellipse((cx - sw / 2, cy - sw / 2, cx + sw / 2, cy + sw / 2), fill=255)

    def line(*pts):
        d.line([P(*p) for p in pts], fill=255, width=sw, joint="curve")
        cap(*pts[0])
        cap(*pts[-1])

    def rr(x0, y0, x1, y1, r):
        d.rounded_rectangle((*P(x0, y0), *P(x1, y1)), radius=r * u, outline=255, width=sw)

    def ring(cx, cy, r):
        d.ellipse((*P(cx - r, cy - r), *P(cx + r, cy + r)), outline=255, width=sw)

    if name == "face":
        ring(12, 8, 4)
        d.arc((*P(4, 15), *P(20, 31)), 180, 360, fill=255, width=sw)
        cap(4, 23)
        cap(20, 23)
    elif name == "camera":
        rr(3, 7, 21, 20, 3)
        ring(12, 13.5, 3.5)
        line((8, 7), (9.5, 4.5), (14.5, 4.5), (16, 7))
    elif name == "dumbbell":
        line((7, 12), (17, 12))
        rr(4.5, 8, 7, 16, 1.2)
        rr(17, 8, 19.5, 16, 1.2)
        line((2, 10.5), (2, 13.5))
        line((22, 10.5), (22, 13.5))
    elif name == "check":
        line((5, 12.5), (10, 17.5), (19, 7))
    elif name == "phone":
        rr(7, 2, 17, 22, 2.5)
        line((10.5, 18.5), (13.5, 18.5))
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), colour)
    out.putalpha(m)
    return out


@lru_cache(maxsize=None)
def logo(kind: str, height: int):
    name = {"mark": "logo-mark", "lockup": "logo-lockup", "lockup-rev": "logo-lockup-reversed"}[kind]
    im = Image.open(ROOT / "public" / "brand" / f"{name}.png").convert("RGBA")
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def paste_rgba(img, im, x, y):
    img.paste(im, (round(x), round(y)), im)


# ---------------------------------------------------------------- scene machinery

def ease(p):
    return 1 - (1 - p) ** 3


class Scene:
    def __init__(self, name, bg, dur):
        self.name, self.bg, self.dur, self.parts = name, bg, dur, []

    def add(self, start, fn):
        self.parts.append((start, fn))

    @property
    def settle(self):
        return max((s for s, _ in self.parts), default=0) + FADE

    def render(self, t, size):
        img = Image.new("RGB", size, self.bg)
        for start, fn in self.parts:
            if start <= 0:
                fn(img, 0)
                continue
            p = ease(min(max((t - start) / FADE, 0), 1))
            if p <= 0:
                continue
            if p >= 1:
                fn(img, 0)
            else:
                before = img.copy()
                fn(img, round((1 - p) * SPACING[8]))
                img = Image.blend(before, img, p)
        return img


class Layout:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.land = W > H
        self.pad = SPACING[48] if self.land else SPACING[32]
        self.x0, self.w = self.pad, W - 2 * self.pad
        # Portrait keeps clear of the top and bottom bars that Shorts, Reels and TikTok draw over a video.
        self.top, self.bot = (108, H - 108) if self.land else (240, H - 480)
        self.cy = (self.top + self.bot) / 2


class Item:
    """A vertical block: height, gap above it, and timed parts drawn relative to its top left."""

    def __init__(self, h, gap=0, parts=()):
        self.h, self.gap, self.parts = h, gap, list(parts)


def stack(sc: Scene, L: Layout, items, x=None):
    x = L.x0 if x is None else x
    total = sum(i.h for i in items) + sum(i.gap for i in items[1:])
    y = L.cy - total / 2
    for n, item in enumerate(items):
        if n:
            y += item.gap
        for start, fn in item.parts:
            sc.add(start, lambda img, dy, fn=fn, y=y: fn(img, x, y + dy))
        y += item.h
    return total


def logo_item(kind, height, start=0, gap=0):
    return Item(height, gap, [(start, lambda img, x, y: paste_rgba(img, logo(kind, height), x, y))])


def text_item(spec, text, fill, width, start=0, gap=0):
    TRANSCRIPT.append(text)
    lines = wrap(spec_font(spec), text, width)
    return Item(len(lines) * spec[2], gap, [(start, lambda img, x, y: draw_lines(img, x, y, lines, spec, fill))])


def multi_item(spec, rows, width, start=0, gap=0):
    """Several lines of different colours as one block. rows: list of (text, colour)."""
    lines = []
    for text, fill in rows:
        TRANSCRIPT.append(text)
        lines += [(ln, fill) for ln in wrap(spec_font(spec), text, width)]

    def draw(img, x, y):
        for i, (ln, fill) in enumerate(lines):
            draw_text(img, x, y + i * spec[2], ln, spec, fill)

    return Item(len(lines) * spec[2], gap, [(start, draw)])


# ---------------------------------------------------------------- profile (the owner's own, setsoflove.com/malgordon)

PROFILE = {"name": "Malcolm, 48", "place": "St James, Perth", "lift": "Bench press", "kg": "125 kg", "lb": "(276 lb)",
           "link": "setsoflove.com/malgordon"}
PHOTO_URLS = [  # main photo, mirror selfie, close-up: the three photos on the live profile, in that order
    "https://setsoflove.com/api/photos/57462357-4f8e-479d-9e50-38595c687411",
    "https://setsoflove.com/api/photos/09a89ac8-8211-4bd9-aecc-df0e8158783e",
    "https://setsoflove.com/api/photos/2c2be823-7c45-4e7d-9e28-e8c30e6b60db",
]
PHOTOS: list[Image.Image] = []


def load_photos(tmp: Path):
    for i, url in enumerate(PHOTO_URLS):
        dst = tmp / f"photo{i}.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})   # the site refuses the default Python agent
        with urllib.request.urlopen(req, timeout=60) as r:
            dst.write_bytes(r.read())
        PHOTOS.append(Image.open(dst).convert("RGB"))


@lru_cache(maxsize=None)
def _photo(i, w, h):
    im = PHOTOS[i]
    scale = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((left, top, left + w, top + h))


def draw_photo(img, i, x, y, w, h, r=SPACING[16]):
    """Photo exactly as uploaded (cropped to its 4:5 frame), with the plate border. Never filtered or overlaid."""
    x, y, w, h = (round(v) for v in (x, y, w, h))
    rrect(img, x, y, w, h, r, fill=PLATE)
    img.paste(_photo(i, w - 6, h - 6), (x + 3, y + 3), _mask(w - 6, h - 6, r - 3))


def pill(img, x, y, text, size, fill=CORAL):
    f = font("t600", size)
    w, h = round(f.getlength(text)) + 2 * SPACING[24], SPACING[48]
    rrect(img, x, y, w, h, SPACING[12], fill=fill)
    draw_text(img, x + w / 2, y + (h - 72) / 2, text, ("t600", size, 72), WHITE, anchor="m")
    return w


# ---------------------------------------------------------------- scenes, timed to the song

def scene_hook(L):
    """'Mirror selfies welcome, you put in the work, now show it off.'"""
    sc = Scene("hook", INK, 6.2)
    TRANSCRIPT.append("Mirror selfies welcome. You put in the work. Show it off.")
    if L.land:
        ph = 800
        pw = ph * 4 // 5
        py = L.cy - ph / 2
        tx = L.x0 + pw + SPACING[32]
        sc.add(0, lambda img, dy: draw_photo(img, 1, L.x0, py + dy, pw, ph))
        lines = [("Mirror selfies", CHALK), ("welcome", HEART)]
        total = len(lines) * DISPLAY[2] + SPACING[16] + BODY[2]
        ty = L.cy - total / 2

        def head(img, dy):
            for i, (ln, fill) in enumerate(lines):
                draw_text(img, tx, ty + dy + i * DISPLAY[2], ln, DISPLAY, fill)

        sc.add(0, head)
        sc.add(3.2, lambda img, dy: draw_text(img, tx, ty + dy + len(lines) * DISPLAY[2] + SPACING[16],
                                              "You put in the work. Show it off.", BODY, CHALK))
    else:
        ph, pw = 700, 560
        lines = [("Mirror selfies", CHALK), ("welcome", HEART)]
        total = ph + SPACING[16] + len(lines) * DISPLAY[2] + SPACING[8] + BODY[2]
        y0 = L.cy - total / 2
        sc.add(0, lambda img, dy: draw_photo(img, 1, L.x0, y0 + dy, pw, ph))
        ty = y0 + ph + SPACING[16]

        def head(img, dy):
            for i, (ln, fill) in enumerate(lines):
                draw_text(img, L.x0, ty + dy + i * DISPLAY[2], ln, DISPLAY, fill)

        sc.add(0, head)
        sc.add(3.2, lambda img, dy: draw_text(img, L.x0, ty + dy + len(lines) * DISPLAY[2] + SPACING[8],
                                              "You put in the work. Show it off.", BODY, CHALK))
    return sc


def scene_profile(L):
    """'Sets of Love, let the whole room know. Show your lifts, stand tall and proud. Sing it out loud.'"""
    sc = Scene("profile", CHALK, 7.3)
    TRANSCRIPT.append(f"{PROFILE['name']}, {PROFILE['place']}. {PROFILE['lift']} {PROFILE['kg']} {PROFILE['lb']}. {PROFILE['link']}")
    ph = 460 if L.land else 450
    pw = ph * 4 // 5
    pad = SPACING[16]
    card_h = ph + 2 * pad
    cap_h = CAPTION[2]
    total = card_h + SPACING[12] + cap_h + SPACING[4] + SPACING[48]
    y0 = L.cy - total / 2
    tx = L.x0 + pad + pw + pad
    name_spec = H2 if L.land else H3

    def card(img, dy):
        y = y0 + dy
        rrect(img, L.x0, y, L.w, card_h, SPACING[16], fill=WHITE, outline=PLATE, bw=3)
        draw_photo(img, 0, L.x0 + pad, y + pad, pw, ph)
        draw_text(img, tx, y + pad, PROFILE["name"], name_spec, INK)
        draw_text(img, tx, y + pad + name_spec[2], PROFILE["place"], SMALL, IRON)

    def lifts(img, dy):
        y = y0 + dy + card_h - pad
        draw_text(img, tx, y - (SMALL[2] + H1[2] if L.land else SMALL[2] + H2[2] + SMALL[2]), PROFILE["lift"], SMALL, IRON)
        if L.land:
            vy = y - H1[2]
            draw_text(img, tx, vy, PROFILE["kg"], H1, INK)
            draw_text(img, tx + spec_font(H1).getlength(PROFILE["kg"]) + SPACING[8], vy + (H1[2] - SMALL[2]) / 2 + SPACING[4],
                      PROFILE["lb"], SMALL, IRON)
        else:
            draw_text(img, tx, y - H2[2] - SMALL[2], PROFILE["kg"], H2, INK)
            draw_text(img, tx, y - SMALL[2], PROFILE["lb"], SMALL, IRON)

    def link(img, dy):
        y = y0 + dy + card_h + SPACING[12]
        draw_text(img, L.x0, y, "Your own link", CAPTION, IRON)
        pill(img, L.x0, y + cap_h + SPACING[4], PROFILE["link"], 54)

    sc.add(0, card)
    sc.add(1.7, lifts)
    sc.add(4.0, link)
    return sc


def scene_rules(L):
    """'No messages, no comments, no algorithm in the way.'"""
    sc = Scene("rules", INK, 5.7)
    spec = DISPLAY
    lines = ["No messages", "No comments", "No algorithm"]
    bullet = SPACING[12]
    avail = L.w - bullet - SPACING[12]
    if any(spec_font(spec).getlength(ln) > avail for ln in lines):
        spec = H1
    TRANSCRIPT.append(". ".join(lines))
    items = []
    for ln, start in zip(lines, (0, 1.4, 2.2)):
        def draw(img, x, y, ln=ln):
            rrect(img, x, y + (spec[2] - bullet) / 2, bullet, bullet, SPACING[4], fill=YELLOW)
            draw_text(img, x + bullet + SPACING[12], y, ln, spec, CHALK)
        items.append(Item(spec[2], SPACING[8] if start else 0, [(start, draw)]))
    items.append(text_item(BODY, "You choose where to share your link. Introductions happen through friends or at the gym.",
                           CHALK, L.w, start=3.6, gap=SPACING[24]))
    stack(sc, L, items)
    return sc


def scene_name(L):
    """'Sets of Love' held, then 'your profile, your say'."""
    sc = Scene("name", CHALK, 4.76)
    stack(sc, L, [
        logo_item("lockup", 144),
        multi_item(DISPLAY, [("Your profile.", INK), ("Your say.", HEART)], L.w, start=0.8, gap=SPACING[32]),
    ])
    return sc


def scene_age(L):
    """'Eighteen plus, come as you are.'"""
    sc = Scene("age", INK, 4.07)
    badge_w, badge_h = 264, 168
    TRANSCRIPT.append("18+")

    def badge(img, x, y):
        rrect(img, x, y, badge_w, badge_h, SPACING[16], fill=YELLOW)
        draw_text(img, x + badge_w / 2, y + (badge_h - DISPLAY[2]) / 2, "18+", DISPLAY, INK, anchor="m")

    stack(sc, L, [
        Item(badge_h, 0, [(0, badge)]),
        text_item(H1, "Come as you are", CHALK, L.w, start=0.3, gap=SPACING[24]),
        text_item(BODY, "For single gym-goers. Men, women and non-binary members are all welcome.", CHALK, L.w, start=1.3, gap=SPACING[12]),
    ])
    return sc


def scene_approved(L):
    """'Every profile cleared to start.'"""
    sc = Scene("approved", CHALK, 3.4)
    d = 168

    def tick(img, x, y):
        rrect(img, x, y, d, d, d // 2, fill=YELLOW)
        paste_rgba(img, icon("check", 96, INK), x + (d - 96) / 2, y + (d - 96) / 2)

    stack(sc, L, [
        Item(d, 0, [(0, tick)]),
        text_item(H1, "We approve every profile", INK, L.w, start=0.3, gap=SPACING[24]),
        text_item(BODY, "A person checks each one before it goes live.", IRON, L.w, start=1.1, gap=SPACING[12]),
    ])
    return sc


def scene_link(L):
    """'Your own link, your name, your proof.'"""
    sc = Scene("link", INK, 2.9)
    size = 72 if L.land else 54
    f = font("t600", size)
    pw = round(f.getlength(PROFILE["link"])) + 2 * SPACING[24]
    TRANSCRIPT.append(PROFILE["link"])
    stack(sc, L, [
        text_item(H2, "Your own link", CHALK, L.w),
        Item(SPACING[48], SPACING[16], [(0.4, lambda img, x, y: pill(img, x, y, PROFILE["link"], size))]),
        text_item(SMALL, "Send it to whoever you like", CHALK, L.w, start=1.2, gap=SPACING[16]),
    ])
    return sc


def scene_photos(L):
    """'Take what you've built and let it move.'"""
    sc = Scene("photos", CHALK, 5.23)
    order = [0, 1, 2]
    if L.land:
        gap, pw = SPACING[16], 480
    else:
        gap = SPACING[8]
        pw = (L.w - 2 * gap) // 3
    ph = pw * 5 // 4
    parts = [(0.2 + n * 0.5, lambda img, x, y, n=n, i=i: draw_photo(img, i, x + n * (pw + gap), y, pw, ph))
             for n, i in enumerate(order)]
    stack(sc, L, [
        text_item(H2, "Show what you've built", INK, L.w),
        Item(ph, SPACING[8], parts),
        text_item(SMALL, "Up to 4 photos. Gym selfies encouraged.", IRON, L.w, start=1.8, gap=SPACING[8]),
    ])
    return sc


def scene_close(L):
    """'Sets of Love' held, then 'dot com'."""
    sc = Scene("close", CHALK, 8.95)
    url = "setsoflove.com"
    uf = font("t600", 54)
    pw, ph = round(uf.getlength(url)) + 2 * SPACING[24], SPACING[48]
    TRANSCRIPT.append(url)

    def pill_url(img, x, y):
        rrect(img, x, y, pw, ph, SPACING[12], fill=CORAL)
        draw_text(img, x + pw / 2, y + (ph - 72) / 2, url, ("t600", 54, 72), WHITE, anchor="m")

    stack(sc, L, [
        logo_item("lockup", 144),
        multi_item(DISPLAY, [("You put in the work.", INK), ("Show it off.", HEART)], L.w, gap=SPACING[32]),
        Item(ph, SPACING[24], [(6.15, pill_url)]),
        text_item(SMALL, "For single gym-goers aged 18+, of every gender", IRON, L.w, start=6.6, gap=SPACING[16]),
    ])
    return sc


SCENES = [scene_hook, scene_profile, scene_rules, scene_name, scene_age, scene_approved, scene_link, scene_photos, scene_close]


# ---------------------------------------------------------------- sound: three cuts from the band track

# (start, end) in seconds in the song, all cut on the beat (143.5 BPM): the chorus, the pre-chorus that leads
# to the second chorus, and the closing "Sets of Love dot com". Joined with 0.3 s crossfades.
CUTS = [(74.82, 99.08), (127.13, 143.03), (257.95, 266.90)]
XFADE = 0.3


def build_audio(dst: Path):
    total = sum(b - a for a, b in CUTS) - XFADE * (len(CUTS) - 1)
    parts = ";".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]" for i, (a, b) in enumerate(CUTS))
    chain = "[a0]"
    for i in range(1, len(CUTS)):
        chain += f"[a{i}]acrossfade=d={XFADE}:c1=qsin:c2=qsin" + (f"[x{i}];[x{i}]" if i < len(CUTS) - 1 else "[mix]")
    fx = f"[mix]afade=t=in:d=0.04,afade=t=out:st={total - 0.35:.2f}:d=0.35,loudnorm=I=-14:TP=-1.5:LRA=9[out]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SONG),
                    "-filter_complex", f"{parts};{chain};{fx}", "-map", "[out]", "-ar", "48000", str(dst)], check=True)
    return total


# ---------------------------------------------------------------- encode

def render(name, size, audio):
    W, H = size
    L = Layout(W, H)
    scenes = [fn(L) for fn in SCENES]
    out = OUT / f"setsoflove-explainer-{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(audio),
           "-map", "0:v", "-map", "1:a", "-shortest",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-r", str(FPS),
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "192k",
           "-metadata", "title=SetsOfLove explainer", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev = None
    frames = 0
    for n, sc in enumerate(scenes):
        cached = None
        for i in range(round(sc.dur * FPS)):
            t = i / FPS
            if cached is not None and t >= sc.settle:
                data = cached
            else:
                img = sc.render(t, size)
                if prev is not None and t < FADE:
                    img = Image.blend(prev, img, ease(t / FADE))
                data = img.tobytes()
                if t >= sc.settle:
                    cached = data
            proc.stdin.write(data)
            frames += 1
        prev = sc.render(sc.dur + 10, size)
        if n == 0:
            poster = prev.resize((W // 2, H // 2), Image.LANCZOS)
            poster.save(OUT / f"setsoflove-explainer-{name}-poster.png", optimize=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit(f"ffmpeg failed for {name}")
    print(f"{out.relative_to(ROOT)}: {frames} frames, {frames / FPS:.1f} s, {out.stat().st_size / 1e6:.1f} MB")


def check_copy():
    text = " ".join(TRANSCRIPT)
    assert "!" not in text, "no exclamation marks"
    banned = re.compile(r"\b(hot|babe|hunk|swipe|match(?:es|ing)?|bro|thirst)\b", re.I)
    assert not banned.search(text), "banned word in video copy"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        prepare_fonts(tmp)
        load_photos(tmp)
        wav = tmp / "audio.wav"
        audio_len = build_audio(wav)
        video_len = None
        for name, size in (("landscape", (1920, 1080)), ("portrait", (1080, 1920))):
            _photo.cache_clear()
            render(name, size, wav)
            if video_len is None:
                video_len = sum(fn(Layout(*size)).dur for fn in SCENES)
        print(f"audio {audio_len:.2f} s, scenes {video_len:.2f} s")
        check_copy()


if __name__ == "__main__":
    main()
