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
LOGO.mkdir(parents=True, exist_ok=True)
ICONS.mkdir(parents=True, exist_ok=True)

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


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "logo"):
        build_logos()
    if only in ("all", "icons"):
        build_icons()
    print("built:", only)
