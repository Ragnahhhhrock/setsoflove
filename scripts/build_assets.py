#!/usr/bin/env python3
"""Build every SetsOfLove brand asset from tokens/tokens.json.

Assets are built only from token colours. The wordmark is converted to outlines
from Inter Bold so no SVG depends on an installed font. Rules: DESIGN_GUIDE.md.
Run scripts/check_conformance.py afterwards.
"""
import json
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
C = {name: v["hex"] for name, v in TOKENS["colour"].items()}
LOGO = ROOT / "assets" / "logo"
ICONS = ROOT / "assets" / "icons"
SOCIAL = ROOT / "assets" / "social"
FONTS = ROOT / "public" / "fonts"
LOGO.mkdir(parents=True, exist_ok=True)
ICONS.mkdir(parents=True, exist_ok=True)
SOCIAL.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
WORDMARK = "setsoflove"
ACCENT_FROM = WORDMARK.index("love")  # "love" is set in coral

NS = 'xmlns="http://www.w3.org/2000/svg"'


# --- the mark, on a 64 x 40 grid -------------------------------------------
def mark_shapes(body: str, heart: str) -> str:
    """Barbell (bar + four plates) in `body`, heart in `heart`. 64 x 40 grid."""
    return (
        f'<rect x="2" y="18" width="60" height="4" rx="2" fill="{body}"/>'
        f'<rect x="6" y="4" width="5" height="32" rx="2.5" fill="{body}"/>'
        f'<rect x="13" y="9" width="4" height="22" rx="2" fill="{body}"/>'
        f'<rect x="53" y="4" width="5" height="32" rx="2.5" fill="{body}"/>'
        f'<rect x="47" y="9" width="4" height="22" rx="2" fill="{body}"/>'
        f"{heart_path(heart)}"
    )


def heart_path(fill: str) -> str:
    return (
        '<path d="M32 34 C32 34 20 26 20 17 C20 12 24 9 28 9 C30 9 32 10.5 32 12.5 '
        f'C32 10.5 34 9 36 9 C40 9 44 12 44 17 C44 26 32 34 32 34 Z" fill="{fill}"/>'
    )


def svg(width, height, title, body, view_w=None, view_h=None) -> str:
    vw, vh = view_w or width, view_h or height
    return (
        f'<svg {NS} viewBox="0 0 {vw} {vh}" width="{width}" height="{height}" '
        f'role="img">\n<title>{title}</title>\n{body}\n</svg>\n'
    )


# --- wordmark as outlines --------------------------------------------------
def wordmark_paths(body: str, accent: str, x0: float, baseline: float):
    """Return (svg path elements, end x) for the wordmark.

    Scaled so the ascender of 'l' equals the plate height (32 units),
    letter-spacing -0.02em. No kerning is applied (GPOS ignored).
    """
    font = TTFont(FONT_PATH)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = 32 / 1490  # 'l' ascender is 1490 font units
    tracking = -0.02 * upm
    x = x0
    parts = []
    for i, ch in enumerate(WORDMARK):
        g = glyphs[cmap[ord(ch)]]
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        tp = TransformPen(pen, (scale, 0, 0, -scale, x, baseline))
        g.draw(tp)
        colour = accent if i >= ACCENT_FROM else body
        d = pen.getCommands()
        if d:
            parts.append(f'<path d="{d}" fill="{colour}"/>')
        x += (g.width + tracking) * scale
    return "\n".join(parts), x - tracking * scale


def build_logos():
    variants = {
        "": (C["ink"], C["ink"]),  # body, wordmark body
        "-reversed": (C["chalk"], C["chalk"]),
    }
    for suffix, (body, word) in variants.items():
        # mark alone
        (LOGO / f"logo-mark{suffix}.svg").write_text(
            svg(64, 40, "SetsOfLove logo", mark_shapes(body, C["coral"]))
        )
        # lockup: mark, 12-unit gap, wordmark; baseline sits on the plate bottom (y=36)
        words, end_x = wordmark_paths(word, C["coral"], x0=64 + 12, baseline=36)
        width = round(end_x, 2)
        inner = mark_shapes(body, C["coral"]) + "\n" + words
        (LOGO / f"logo-lockup{suffix}.svg").write_text(
            svg(width, 40, "SetsOfLove", inner)
        )


# --- icons -----------------------------------------------------------------
def app_icon_svg() -> str:
    s = (1024 * 0.60) / 60  # mark visible width (60 units) fills 60% of the canvas
    tx, ty = 512 - 32 * s, 512 - 20 * s  # centre the mark's centre (32, 20)
    body = (
        f'<rect width="1024" height="1024" fill="{C["ink"]}"/>\n'
        f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s:.5f})">'
        f'{mark_shapes(C["chalk"], C["coral"])}</g>'
    )
    return svg(1024, 1024, "SetsOfLove app icon", body)


def favicon_svg() -> str:
    s = 1.4  # small-size mark: coral heart centred on an ink tile, no plates
    tx, ty = 32 - 32 * s, 32 - 21.5 * s  # heart centre is (32, 21.5)
    body = (
        f'<rect width="64" height="64" rx="14" fill="{C["ink"]}"/>\n'
        f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s})">{heart_path(C["coral"])}</g>'
    )
    return svg(64, 64, "SetsOfLove", body)


def rasterise(jobs):
    """jobs: list of (svg_path, png_path, size). Rendered with headless Chromium."""
    import tempfile

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        for i, (svg_path, png_path, size) in enumerate(jobs):
            # file:// images are blocked from about:blank, so load a real local page
            html = Path(tmp) / f"render-{i}.html"
            html.write_text(
                f'<body style="margin:0;background:transparent">'
                f'<img id="i" src="{Path(svg_path).as_uri()}" width="{size}" height="{size}" '
                f'style="display:block"></body>'
            )
            page = browser.new_page(viewport={"width": size, "height": size})
            page.goto(html.as_uri())
            page.wait_for_function(
                "document.getElementById('i').complete && document.getElementById('i').naturalWidth > 0"
            )
            page.screenshot(path=str(png_path), omit_background=True)
            page.close()
        browser.close()


def build_icons():
    (ICONS / "app-icon.svg").write_text(app_icon_svg())
    (ICONS / "favicon.svg").write_text(favicon_svg())

    jobs = [
        (ICONS / "app-icon.svg", ICONS / "icon-1024.png", 1024),
        (ICONS / "app-icon.svg", ICONS / "icon-512.png", 512),
        (ICONS / "app-icon.svg", ICONS / "icon-192.png", 192),
        (ICONS / "app-icon.svg", ICONS / "apple-touch-icon.png", 180),
        (ICONS / "favicon.svg", ICONS / "favicon-256.tmp.png", 256),
    ]
    rasterise(jobs)

    tmp = ICONS / "favicon-256.tmp.png"
    Image.open(tmp).convert("RGBA").save(
        ICONS / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    tmp.unlink()

    # app icons must be opaque: flatten and re-save as RGB
    for name in ("icon-1024.png", "icon-512.png", "icon-192.png", "apple-touch-icon.png"):
        path = ICONS / name
        img = Image.open(path).convert("RGBA")
        bg = Image.new("RGB", img.size, C["ink"])
        bg.paste(img, mask=img.split()[3])
        bg.save(path, optimize=True)


# --- social images ---------------------------------------------------------
# Built at 2x the interface scale (DESIGN_GUIDE.md section 8).
HEADLINE = ("Find someone who gets", "the early alarm")
SUBLINE = "Profiles for single gym-goers"


def social_html(width, height, bg, headline, accent, body, lockup_svg) -> str:
    k = TOKENS["social"]["scale"]
    display = TOKENS["type"]["scale"]["display"]
    text = TOKENS["type"]["scale"]["body"]
    pad = TOKENS["space"][-1]  # 64: the largest spacing step
    gap = TOKENS["space"][3] * k // 2 * 2  # 32
    lockup_h = 40 * k  # lockup is 40 units tall
    faces = "".join(
        f"@font-face{{font-family:'Inter';font-weight:{w};src:url('{(FONTS / f'inter-latin-{w}-normal.woff2').as_uri()}') format('woff2')}}"
        for w in TOKENS["type"]["weights"]
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{faces}
html,body{{margin:0;width:{width}px;height:{height}px;background:{bg}}}
body{{box-sizing:border-box;padding:{pad}px;display:flex;flex-direction:column;justify-content:space-between;
font-family:'Inter',{TOKENS['type']['fallback']};color:{headline}}}
img{{display:block;align-self:flex-start;width:auto;height:{lockup_h}px}}
h1{{margin:0 0 {gap}px;font-size:{display['size'] * k}px;line-height:{display['line'] * k}px;font-weight:{display['weight']}}}
h1 span{{color:{accent}}}
p{{margin:0;font-size:{text['size'] * k}px;line-height:{text['line'] * k}px;font-weight:{text['weight']};color:{body}}}
</style></head><body>
<img src="{lockup_svg.as_uri()}" alt="SetsOfLove">
<div><h1>{HEADLINE[0]}<br><span>{HEADLINE[1]}</span></h1><p>{SUBLINE}</p></div>
</body></html>"""


def build_social():
    import tempfile

    from playwright.sync_api import sync_playwright

    jobs = [
        # file, size, background, headline, accent, body text, lockup
        ("og-image.png", TOKENS["social"]["og"], C["ink"], C["chalk"], C["coral"], C["chalk"], LOGO / "logo-lockup-reversed.svg"),
        ("twitter-card.png", TOKENS["social"]["twitter"], C["chalk"], C["ink"], C["coral"], C["iron"], LOGO / "logo-lockup.svg"),
    ]
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        for name, size, bg, head, accent, body, lockup in jobs:
            w, h = size["width"], size["height"]
            html = Path(tmp) / f"{name}.html"
            html.write_text(social_html(w, h, bg, head, accent, body, lockup))
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(html.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_function("document.querySelector('img').complete && document.fonts.status === 'loaded'")
            out = SOCIAL / name
            page.screenshot(path=str(out))
            page.close()
            # opaque RGB, flattened onto the background
            img = Image.open(out).convert("RGBA")
            flat = Image.new("RGB", img.size, bg)
            flat.paste(img, mask=img.split()[3])
            flat.save(out, optimize=True)
        browser.close()


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "logo"):
        build_logos()
    if only in ("all", "icons"):
        build_icons()
    if only in ("all", "social"):
        build_social()
    print("built:", only)
