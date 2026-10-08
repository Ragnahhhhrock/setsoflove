#!/usr/bin/env python3
"""Build every SetsOfLove brand asset from brand-src/ and tokens/tokens.json.

The mark is the red-heart emoji with the flexed-biceps emoji centred in it
(Microsoft Fluent Emoji 3D, MIT licence: brand-src/FLUENT-EMOJI-LICENSE.txt).
Rules: DESIGN_GUIDE.md. Run scripts/check_conformance.py afterwards.

    python3 scripts/build_assets.py [logo|icons|social|all]

Also copies the finished files into public/ (see README.md).
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
C = {name: v["hex"] for name, v in TOKENS["colour"].items()}
LG = TOKENS["logo"]
SRC = ROOT / "brand-src"
LOGO = ROOT / "assets" / "logo"
ICONS = ROOT / "assets" / "icons"
SOCIAL = ROOT / "assets" / "social"
PUBLIC = ROOT / "public"
FONTS = PUBLIC / "fonts"
for d in (LOGO, ICONS, SOCIAL):
    d.mkdir(parents=True, exist_ok=True)


def rgb(hex_):
    return tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))


def crop_to_content(img: Image.Image) -> Image.Image:
    return img.crop(img.getchannel("A").getbbox())


HEART = crop_to_content(Image.open(SRC / "heart.png").convert("RGBA"))
FLEX = crop_to_content(Image.open(SRC / "flex.png").convert("RGBA"))


def mark(canvas: int, flex_ratio: float) -> Image.Image:
    """Heart on a square transparent canvas with the flex centred as in the chosen layout.

    The flex sits a touch left of and above the heart's box centre, the way the
    emoji pair is drawn: offsets are fractions of the heart's own size.
    """
    hw = round(canvas * LG["heart_width_ratio"])
    hr = HEART.resize((hw, round(hw * HEART.height / HEART.width)), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    hx, hy = (canvas - hr.width) // 2, (canvas - hr.height) // 2
    out.alpha_composite(hr, (hx, hy))
    fw = round(hw * flex_ratio)
    fr = FLEX.resize((fw, round(fw * FLEX.height / FLEX.width)), Image.LANCZOS)
    cx = hx + hr.width / 2 - (4 / 584) * hr.width
    cy = hy + hr.height / 2 - (27 / 512) * hr.height
    out.alpha_composite(fr, (round(cx - fr.width / 2), round(cy - fr.height / 2)))
    return out


def build_logos():
    mark(512, LG["flex_width_ratio"]).save(LOGO / "logo-mark.png", optimize=True)
    mark(128, LG["flex_width_ratio_small"]).save(LOGO / "logo-mark-small.png", optimize=True)

    # lockups: tight-cropped mark (128px tall) + wordmark in Bricolage Grotesque 800
    from playwright.sync_api import sync_playwright

    h = LG["lockup_height"]
    font_px = round(h / 1.35)
    gap = round(font_px * 0.36)
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        crop_to_content(mark(1024, LG["flex_width_ratio"])).save(tmp / "mark.png")
        browser = p.chromium.launch()
        for name, ink in (("logo-lockup.png", C["ink"]), ("logo-lockup-reversed.png", C["chalk"])):
            html = tmp / "lockup.html"
            html.write_text(f"""<!doctype html><meta charset=utf-8>
<style>
@font-face{{font-family:BG;font-weight:800;src:url('{(FONTS / "bricolage-grotesque-latin-800-normal.woff2").as_uri()}')}}
html,body{{margin:0;background:transparent}}
#l{{display:inline-flex;align-items:center;gap:{gap}px}}
#l img{{height:{h}px;width:auto;display:block}}
#l span{{font:800 {font_px}px/1 BG,sans-serif;letter-spacing:-0.02em;color:{ink}}}
#l b{{color:{C["heart"]};font-weight:800}}
</style>
<div id=l><img src="mark.png"><span>SetsOf<b>Love</b></span></div>""")
            page = browser.new_page(viewport={"width": 1400, "height": 400})
            page.goto(html.as_uri())
            page.wait_for_function("document.fonts.status === 'loaded' && document.querySelector('img').complete")
            page.locator("#l").screenshot(path=str(LOGO / name), omit_background=True)
            page.close()
            img = Image.open(LOGO / name).convert("RGBA")
            img.save(LOGO / name, optimize=True)
        browser.close()


def build_icons():
    big = crop_to_content(mark(1024, LG["flex_width_ratio"]))
    scale = (1024 * TOKENS["icon"]["mark_width"]) / big.width
    big = big.resize((round(big.width * scale), round(big.height * scale)), Image.LANCZOS)
    icon = Image.new("RGBA", (1024, 1024), rgb(C["ink"]) + (255,))
    icon.alpha_composite(big, ((1024 - big.width) // 2, (1024 - big.height) // 2))
    icon = icon.convert("RGB")
    icon.save(ICONS / "icon-1024.png", optimize=True)
    for name, size in (("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180)):
        icon.resize((size, size), Image.LANCZOS).save(ICONS / name, optimize=True)

    # favicon: small-size mark (larger flex) filling most of an ink tile
    tile = Image.new("RGBA", (256, 256), rgb(C["ink"]) + (255,))
    sm = crop_to_content(mark(512, LG["flex_width_ratio_small"]))
    k = (256 * 0.84) / sm.width
    sm = sm.resize((round(sm.width * k), round(sm.height * k)), Image.LANCZOS)
    tile.alpha_composite(sm, ((256 - sm.width) // 2, (256 - sm.height) // 2))
    tile.convert("RGB").save(ICONS / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


# --- social images: built at 2x the interface scale (DESIGN_GUIDE.md section 8) ---------
HEADLINE = ("Find someone who gets", "the early alarm")
SUBLINE = "Profiles for single gym-goers"


def social_html(width, height, bg, headline, accent, body, lockup: Path) -> str:
    k = TOKENS["social"]["scale"]
    display = TOKENS["type"]["scale"]["display"]
    text = TOKENS["type"]["scale"]["body"]
    pad = TOKENS["space"][-1]
    gap = TOKENS["space"][3] * k // 2 * 2
    lockup_h = 40 * k
    faces = "".join(
        f"@font-face{{font-family:'DM Sans';font-weight:{w};src:url('{(FONTS / f'dm-sans-latin-{w}-normal.woff2').as_uri()}')}}"
        for w in TOKENS["type"]["weights"]["text"]
    ) + "".join(
        f"@font-face{{font-family:'Bricolage Grotesque';font-weight:{w};src:url('{(FONTS / f'bricolage-grotesque-latin-{w}-normal.woff2').as_uri()}')}}"
        for w in TOKENS["type"]["weights"]["display"]
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{faces}
html,body{{margin:0;width:{width}px;height:{height}px;background:{bg}}}
body{{box-sizing:border-box;padding:{pad}px;display:flex;flex-direction:column;justify-content:space-between;
font-family:'DM Sans',{TOKENS['type']['fallback']};color:{headline}}}
img{{display:block;align-self:flex-start;width:auto;height:{lockup_h}px}}
h1{{margin:0 0 {gap}px;font-family:'Bricolage Grotesque',{TOKENS['type']['fallback']};font-size:{display['size'] * k}px;line-height:{display['line'] * k}px;font-weight:{display['weight']};letter-spacing:-0.02em}}
h1 span{{color:{accent}}}
p{{margin:0;font-size:{text['size'] * k}px;line-height:{text['line'] * k}px;font-weight:{text['weight']};color:{body}}}
</style></head><body>
<img src="{lockup.as_uri()}" alt="SetsOfLove">
<div><h1>{HEADLINE[0]}<br><span>{HEADLINE[1]}</span></h1><p>{SUBLINE}</p></div>
</body></html>"""


def build_social():
    from playwright.sync_api import sync_playwright

    jobs = [
        ("og-image.png", TOKENS["social"]["og"], C["ink"], C["chalk"], C["heart"], C["chalk"], LOGO / "logo-lockup-reversed.png"),
        ("twitter-card.png", TOKENS["social"]["twitter"], C["chalk"], C["ink"], C["heart"], C["iron"], LOGO / "logo-lockup.png"),
    ]
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        for name, size, bg, head, accent, body, lockup in jobs:
            w, h = size["width"], size["height"]
            html = Path(tmp) / f"{name}.html"
            html.write_text(social_html(w, h, bg, head, accent, body, lockup))
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(html.as_uri())
            page.wait_for_function("document.querySelector('img').complete && document.fonts.status === 'loaded'")
            out = SOCIAL / name
            page.screenshot(path=str(out))
            page.close()
            img = Image.open(out).convert("RGBA")
            flat = Image.new("RGB", img.size, rgb(bg))
            flat.paste(img, mask=img.split()[3])
            flat.save(out, optimize=True)
        browser.close()


def copy_to_public():
    """public/ holds copies of the brand files (the site serves only public/)."""
    (PUBLIC / "brand").mkdir(exist_ok=True)
    for f in LOGO.glob("*.png"):
        shutil.copyfile(f, PUBLIC / "brand" / f.name)
    for name in ("icon-192.png", "icon-512.png", "apple-touch-icon.png", "favicon.ico"):
        shutil.copyfile(ICONS / name, PUBLIC / name)
    for name in ("og-image.png", "twitter-card.png"):
        shutil.copyfile(SOCIAL / name, PUBLIC / name)
    shutil.copyfile(ROOT / "tokens" / "tokens.css", PUBLIC / "tokens.css")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "logo"):
        build_logos()
    if only in ("all", "icons"):
        build_icons()
    if only in ("all", "social"):
        build_social()
    copy_to_public()
    print("built:", only)
