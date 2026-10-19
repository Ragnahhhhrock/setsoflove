#!/usr/bin/env python3
"""Build the SetsOfLove explainer video in landscape (1920x1080) and portrait (1080x1920).

Output goes to public/video/. Everything is drawn from the design tokens, the site
fonts and the logo files, so it follows DESIGN_GUIDE.md section 14.

Needs: Pillow, fonttools and brotli (to read the site's woff2 fonts), and ffmpeg.
Run: python3 scripts/build_video.py
"""
import json
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "video"
MUSIC = OUT / "setsoflove-explainer-music.m4a"   # from scripts/build_music.py; silent track if missing
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


# ---------------------------------------------------------------- scenes

def scene_mirror(L):
    sc = Scene("mirror", INK, 3.0)
    TRANSCRIPT.append("Mirror selfies welcome")
    if L.land:
        m = 400
        mx, my = L.x0, L.cy - m / 2
        lines = [("Mirror selfies", CHALK), ("welcome", HEART)]
        tx, ty = mx + m + SPACING[32], L.cy - len(lines) * HERO[2] / 2
    else:
        m = 360
        lines = [("Mirror", CHALK), ("selfies", CHALK), ("welcome", HEART)]
        total = m + SPACING[24] + len(lines) * HERO[2]
        mx, my = L.x0, L.cy - total / 2
        tx, ty = L.x0, my + m + SPACING[24]
    sc.add(0, lambda img, dy: paste_rgba(img, logo("mark", m), mx, my + dy))

    def draw(img, dy):
        for i, (ln, fill) in enumerate(lines):
            draw_text(img, tx, ty + dy + i * HERO[2], ln, HERO, fill)

    sc.add(0, draw)
    return sc


def scene_what(L):
    sc = Scene("what", CHALK, 4.0)
    stack(sc, L, [
        logo_item("lockup", 96),
        text_item(H1, "A profile app for single gym-goers", INK, L.w, gap=SPACING[32]),
        text_item(BODY, "Show off the work you put in. Share your link. Let people get to know you.", IRON, L.w, start=0.8, gap=SPACING[16]),
    ])
    return sc


def photo_card(img, x, y, w, h, name, label, caption, tall):
    rrect(img, x, y, w, h, SPACING[16], fill=WHITE, outline=PLATE, bw=3)
    if tall:   # 4:5 photo slot, icon on top and text at the bottom
        pad = SPACING[12]
        paste_rgba(img, icon(name, 144, IRON), x + pad, y + pad)
        cap_lines = wrap(spec_font(CAPTION), caption, w - 2 * pad)
        block = LABEL[2] + len(cap_lines) * CAPTION[2]
        by = y + h - pad - block
        draw_text(img, x + pad, by, label, LABEL, INK)
        draw_lines(img, x + pad, by + LABEL[2], cap_lines, CAPTION, IRON)
    else:      # full-width row: icon left, text right
        pad = SPACING[16]
        paste_rgba(img, icon(name, 120, IRON), x + pad, y + (h - 120) / 2)
        tx = x + pad + 120 + SPACING[16]
        by = y + (h - (LABEL[2] + CAPTION[2])) / 2
        draw_text(img, tx, by, label, LABEL, INK)
        draw_text(img, tx, by + LABEL[2], caption, CAPTION, IRON)


def scene_photos(L):
    sc = Scene("photos", CHALK, 4.5)
    cards = [("face", "Main photo", "Face clearly visible"), ("camera", "Gym selfie", "Encouraged"),
             ("dumbbell", "Workout", "Gym kit welcome"), ("phone", "Mirror pic", "After your session")]
    for _, label, caption in cards:
        TRANSCRIPT.append(f"{label}. {caption}")
    gap = SPACING[12] if L.land else SPACING[8]
    if L.land:
        cw = (L.w - 3 * gap) // 4
        ch = round(cw * 5 / 4)
        parts = [(0.4 + i * 0.35, lambda img, x, y, i=i, c=c: photo_card(img, x + i * (cw + gap), y, cw, ch, c[0], c[1], c[2], True))
                 for i, c in enumerate(cards)]
        row = Item(ch, SPACING[24], parts)
    else:
        rh = SPACING[64] + SPACING[8]   # 216
        parts = [(0.4 + i * 0.35, lambda img, x, y, i=i, c=c: photo_card(img, x, y + i * (rh + gap), L.w, rh, c[0], c[1], c[2], False))
                 for i, c in enumerate(cards)]
        row = Item(4 * rh + 3 * gap, SPACING[16], parts)
    stack(sc, L, [text_item(H2, "Your gym photos are the main event", INK, L.w), row])
    return sc


LIFTS = [("Bench press", "100 kg (220 lb)"), ("Squat", "140 kg (309 lb)"),
         ("Deadlift", "180 kg (397 lb)"), ("Overhead press", "60 kg (132 lb)")]


def lifts_card(L, width):
    pad, row_h = SPACING[16], SPACING[32] + SPACING[4]   # 48 and 108
    head = CAPTION[2] + SPACING[8]
    h = pad + head + len(LIFTS) * row_h + pad - SPACING[8]
    TRANSCRIPT.append("Example lifts. " + ". ".join(f"{a} {b}" for a, b in LIFTS))
    TRANSCRIPT.append("Optional and self-reported. Enter kg or lb and we show both.")

    def base(img, x, y):
        rrect(img, x, y, width, h, SPACING[16], fill=WHITE, outline=PLATE, bw=3)
        draw_text(img, x + pad, y + pad, "Example lifts", CAPTION, IRON)

    parts = [(0.3, base)]
    for i, (name, value) in enumerate(LIFTS):
        def row(img, x, y, i=i, name=name, value=value):
            ry = y + pad + head + i * row_h
            if i:
                rrect(img, x + pad, ry, width - 2 * pad, 3, 0, fill=PLATE)
            draw_text(img, x + pad, ry + (row_h - LABEL[2]) / 2, name, SMALL, IRON)
            vw = spec_font(LABEL).getlength(value)
            draw_text(img, x + width - pad - vw, ry + (row_h - LABEL[2]) / 2, value, LABEL, INK)
        parts.append((0.6 + i * 0.25, row))
    return Item(h, SPACING[24], parts), h


def scene_lifts(L):
    sc = Scene("lifts", INK, 4.5)
    if L.land:
        col = 640
        card_w = L.w - col - SPACING[32]
        card, ch = lifts_card(L, card_w)
        left = [text_item(H2, "Lifts sit right beside your photos", CHALK, col),
                text_item(BODY, "Optional and self-reported. Enter kg or lb and we show both.", CHALK, col, start=0.3, gap=SPACING[16])]
        stack(sc, L, left)
        stack(sc, L, [Item(card.h, 0, card.parts)], x=L.x0 + col + SPACING[32])
    else:
        card, ch = lifts_card(L, L.w)
        stack(sc, L, [
            text_item(H2, "Lifts sit right beside your photos", CHALK, L.w),
            text_item(BODY, "Optional and self-reported. Enter kg or lb and we show both.", CHALK, L.w, start=0.3, gap=SPACING[16]),
            Item(card.h, SPACING[24], card.parts),
        ])
    return sc


def step_row(img, x, y, w, h, n, title, desc_runs):
    rrect(img, x, y, w, h, SPACING[16], fill=WHITE, outline=PLATE, bw=3)
    b = 108
    by = y + (h - b) / 2
    rrect(img, x + SPACING[16], by, b, b, b // 2, fill=YELLOW)
    draw_text(img, x + SPACING[16] + b / 2, by + (b - H3[2]) / 2, str(n), H3, INK, anchor="m")
    tx = x + SPACING[16] + b + SPACING[16]
    block = H3[2] + SMALL[2] * len(desc_runs)
    ty = y + (h - block) / 2
    draw_text(img, tx, ty, title, H3, INK)
    for i, runs in enumerate(desc_runs):
        cx = tx
        for text, spec, fill in runs:
            draw_text(img, cx, ty + H3[2] + i * SMALL[2], text, spec, fill)
            cx += spec_font(spec).getlength(text)


def scene_how(L):
    sc = Scene("how", CHALK, 6.0)
    steps = [
        ("Create your profile", "Add a few photos and a few lines about you."),
        ("We approve it", "We check every profile before it goes live."),
        ("Share your link", "Your own link, like setsoflove.com/sam-t"),
    ]
    text_w = L.w - (SPACING[16] + 108 + SPACING[16]) - SPACING[16]
    rows = []
    for title, desc in steps:
        TRANSCRIPT.append(f"{title}. {desc}")
        if "sam-t" in desc:
            lead, link = "Your own link, like ", "setsoflove.com/sam-t"
            if spec_font(SMALL).getlength(lead) + spec_font(LABEL).getlength(link) <= text_w:
                runs = [[(lead, SMALL, IRON), (link, LABEL, CORAL)]]
            else:   # narrow frame: link on its own line
                runs = [[(lead.strip(), SMALL, IRON)], [(link, LABEL, CORAL)]]
        else:
            lines = wrap(spec_font(SMALL), desc, text_w)
            runs = [[(ln, SMALL, IRON)] for ln in lines]
        rows.append((title, runs))
    row_h = SPACING[8] * 3 + H3[2] + SMALL[2] * max(len(r) for _, r in rows) + SPACING[8] * 3
    gap = SPACING[8]
    parts = [(0.4 + i * 1.4, lambda img, x, y, i=i, t=t, r=r: step_row(img, x, y + i * (row_h + gap), L.w, row_h, i + 1, t, r))
             for i, (t, r) in enumerate(rows)]
    stack(sc, L, [text_item(H2, "How it works", INK, L.w),
                  Item(3 * row_h + 2 * gap, SPACING[16], parts)])
    return sc


def scene_rules(L):
    sc = Scene("rules", INK, 4.0)
    spec = DISPLAY
    lines = ["No messages", "No comments", "No algorithm"]
    bullet = SPACING[12]
    avail = L.w - bullet - SPACING[12]
    if any(spec_font(spec).getlength(ln) > avail for ln in lines):
        spec = H1   # narrow frame: drop to h1 size
    for ln in lines:
        assert spec_font(spec).getlength(ln) <= avail, f"'{ln}' too wide"
    TRANSCRIPT.append(". ".join(lines))
    items = []
    for i, ln in enumerate(lines):
        def draw(img, x, y, ln=ln):
            rrect(img, x, y + (spec[2] - bullet) / 2, bullet, bullet, SPACING[4], fill=YELLOW)
            draw_text(img, x + bullet + SPACING[12], y, ln, spec, CHALK)
        items.append(Item(spec[2], SPACING[8] if i else 0, [(i * 0.5, draw)]))
    items.append(text_item(BODY, "You choose where to share your link. Introductions happen through friends or at the gym.",
                           CHALK, L.w, start=1.8, gap=SPACING[24]))
    stack(sc, L, items)
    return sc


def scene_close(L):
    sc = Scene("close", CHALK, 4.5)
    url = "setsoflove.com"
    uf = font("t600", 54)
    pw, ph = round(uf.getlength(url)) + 2 * SPACING[24], SPACING[48]
    TRANSCRIPT.append(url)

    def pill(img, x, y):
        rrect(img, x, y, pw, ph, SPACING[12], fill=CORAL)
        draw_text(img, x + pw / 2, y + (ph - 72) / 2, url, ("t600", 54, 72), WHITE, anchor="m")

    stack(sc, L, [
        logo_item("lockup", 144),
        multi_item(DISPLAY, [("You put in the work.", INK), ("Show it off.", HEART)], L.w, gap=SPACING[32]),
        Item(ph, SPACING[24], [(0.5, pill)]),
        text_item(SMALL, "For single gym-goers aged 18+, of every gender", IRON, L.w, start=0.9, gap=SPACING[16]),
    ])
    return sc


SCENES = [scene_mirror, scene_what, scene_photos, scene_lifts, scene_how, scene_rules, scene_close]


# ---------------------------------------------------------------- encode

def render(name, size):
    W, H = size
    L = Layout(W, H)
    scenes = [fn(L) for fn in SCENES]
    out = OUT / f"setsoflove-explainer-{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           *(["-i", str(MUSIC)] if MUSIC.exists() else ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]),
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
        prepare_fonts(Path(tmp))
        render("landscape", (1920, 1080))
        landscape_text = list(TRANSCRIPT)
        TRANSCRIPT.clear()
        render("portrait", (1080, 1920))
        TRANSCRIPT[:] = landscape_text
        check_copy()
        print("\n".join(landscape_text))


if __name__ == "__main__":
    main()
