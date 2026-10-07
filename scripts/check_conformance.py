#!/usr/bin/env python3
"""Check that every asset in the repo conforms to DESIGN_GUIDE.md and STYLE_GUIDE.md.

Exit code 0 only if everything passes. Run before every commit.
"""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text())
PALETTE = {v["hex"].upper() for v in TOKENS["colour"].values()}
INK, CHALK, CORAL = (TOKENS["colour"][k]["hex"].upper() for k in ("ink", "chalk", "coral"))
ICON_SIZES = set(TOKENS["icon"]["sizes"])
SAFE = TOKENS["icon"]["maskable_safe_zone"]

SVG_NS = "{http://www.w3.org/2000/svg}"
ALLOWED_TAGS = {"svg", "title", "rect", "path", "g"}
ALLOWED_EXT = {".svg", ".png", ".ico"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z]+$")

EXPECTED_TITLES = {
    "logo-mark.svg": "SetsOfLove logo",
    "logo-mark-reversed.svg": "SetsOfLove logo",
    "logo-lockup.svg": "SetsOfLove",
    "logo-lockup-reversed.svg": "SetsOfLove",
    "app-icon.svg": "SetsOfLove app icon",
    "favicon.svg": "SetsOfLove",
}
EXPECTED_PNG = {
    "icon-1024.png": 1024,
    "icon-512.png": 512,
    "icon-192.png": 192,
    "apple-touch-icon.png": 180,
}

failures: list[str] = []
passes = 0


def check(ok: bool, msg: str):
    global passes
    if ok:
        passes += 1
    else:
        failures.append(msg)


def colours_in(el) -> set[str]:
    found = set()
    for node in el.iter():
        for attr in ("fill", "stroke", "stop-color"):
            v = node.get(attr)
            if v and v.lower() not in ("none",):
                found.add(v.upper())
    return found


def check_svg(path: Path):
    name = path.name
    rel = path.relative_to(ROOT)
    tree = ET.parse(path)
    root = tree.getroot()
    check(root.tag == f"{SVG_NS}svg", f"{rel}: root is not <svg>")

    tags = {el.tag.replace(SVG_NS, "") for el in root.iter()}
    check(tags <= ALLOWED_TAGS, f"{rel}: disallowed elements {sorted(tags - ALLOWED_TAGS)} (no text, gradients, filters, images)")

    for node in root.iter():
        for banned in ("style", "opacity", "fill-opacity", "stroke-opacity", "filter", "mask", "clip-path", "font-family"):
            check(banned not in node.attrib, f"{rel}: forbidden attribute '{banned}'")

    cols = colours_in(root)
    bad = cols - PALETTE
    check(not bad, f"{rel}: colours outside the palette: {sorted(bad)}")
    check(bool(cols), f"{rel}: no colours found")

    check(root.get("viewBox") is not None, f"{rel}: missing viewBox")
    check(root.get("role") == "img", f"{rel}: missing role=\"img\"")
    title = root.find(f"{SVG_NS}title")
    expected = EXPECTED_TITLES.get(name)
    check(title is not None and title.text == expected, f"{rel}: <title> should be '{expected}'")

    # per-asset rules from DESIGN_GUIDE.md sections 6 and 7
    if name.startswith("logo-"):
        reversed_ = name.endswith("-reversed.svg")
        wrong = INK if reversed_ else CHALK
        check(wrong not in cols, f"{rel}: wrong body colour for {'reversed' if reversed_ else 'standard'} logo")
        check(CORAL in cols, f"{rel}: the heart must be coral")
        check(cols <= {INK, CHALK, CORAL}, f"{rel}: logo may only use ink, chalk and coral")
        rects = root.findall(f".//{SVG_NS}rect")
        check(len(rects) == 5, f"{rel}: expected 5 rects (bar + 4 plates), found {len(rects)}")
        if "lockup" in name:
            check(len(root.findall(f".//{SVG_NS}path")) >= 11, f"{rel}: lockup must contain heart + wordmark outlines")
            vb = [float(x) for x in root.get("viewBox").split()]
            check(vb[3] == 40, f"{rel}: lockup height must be 40 units")
    if name == "app-icon.svg":
        first = root.find(f"{SVG_NS}rect")
        check(first is not None and first.get("fill", "").upper() == INK, f"{rel}: background must be an ink square")
        check(first is not None and "rx" not in first.attrib, f"{rel}: no rounded corners on app icon")
        check(root.get("viewBox") == "0 0 1024 1024", f"{rel}: must be 1024 x 1024")
    if name == "favicon.svg":
        check(len(root.findall(f".//{SVG_NS}rect")) == 1, f"{rel}: small-size mark has no plates (tile only)")
        check(cols == {INK, CORAL}, f"{rel}: favicon is coral heart on ink tile only")


def _rgb(hex_: str):
    return tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))


def is_blend_of(rgb, dominant, tolerance: float = 4.0) -> bool:
    """True if rgb is a convex mix of the image's own dominant palette colours.

    This is what anti-aliasing produces where shapes meet; anything else
    (an off-palette hue, a gradient, a shadow tint) is rejected.
    """
    import numpy as np

    cols = np.array([_rgb(h) for h in dominant], dtype=float)  # n x 3
    # solve cols.T @ w = rgb with sum(w) = 1 by appending a weighted constraint row
    A = np.vstack([cols.T, np.full((1, len(cols)), 100.0)])
    b = np.append(np.array(rgb, dtype=float), 100.0)
    w, *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = np.linalg.norm(cols.T @ w - np.array(rgb, dtype=float))
    return bool(resid <= tolerance and (w >= -0.03).all())


def check_png(path: Path):
    rel = path.relative_to(ROOT)
    name = path.name
    img = Image.open(path)
    size = EXPECTED_PNG.get(name)
    check(size is not None, f"{rel}: PNG not listed in the guide (add it to DESIGN_GUIDE.md section 7 and this checker)")
    if size is None:
        return
    check(img.size == (size, size), f"{rel}: expected {size}x{size}, got {img.size}")
    check(size in ICON_SIZES or size == 180, f"{rel}: size not in tokens")
    check(img.mode == "RGB", f"{rel}: must be opaque RGB, got {img.mode}")
    img = img.convert("RGB")
    check(img.getpixel((0, 0)) == tuple(int(INK[i:i + 2], 16) for i in (1, 3, 5)), f"{rel}: corner pixel must be ink")

    # dominant colours must be palette colours (anti-aliased edges are allowed)
    counts = img.getcolors(maxcolors=size * size) or []
    total = size * size
    hexof = lambda rgb: "#%02X%02X%02X" % rgb
    dominant = [hexof(rgb) for n, rgb in counts if hexof(rgb) in PALETTE and n / total >= 0.001]
    off = [(hexof(rgb), n) for n, rgb in counts if hexof(rgb) not in PALETTE and not is_blend_of(rgb, dominant)]
    check(not off, f"{rel}: colours that are neither palette colours nor anti-aliased blends of them: {off[:3]}")
    blended = sum(n for n, rgb in counts if hexof(rgb) not in PALETTE)
    check(blended / total < 0.08, f"{rel}: too many blended pixels ({blended / total:.1%}); expected only anti-aliased edges")

    # mark must fill ~60% width and sit inside the maskable safe zone
    ink_rgb = tuple(int(INK[i:i + 2], 16) for i in (1, 3, 5))
    px = img.load()
    xs, ys = [], []
    for y in range(size):
        for x in range(size):
            if px[x, y] != ink_rgb:
                xs.append(x)
                ys.append(y)
    if xs:
        w = (max(xs) - min(xs) + 1) / size
        check(0.56 <= w <= 0.64, f"{rel}: mark should fill about 60% of width, got {w:.0%}")
        lo, hi = (1 - SAFE) / 2 * size, (1 + SAFE) / 2 * size
        check(min(xs) >= lo and max(xs) <= hi and min(ys) >= lo and max(ys) <= hi, f"{rel}: mark outside the 80% safe zone")
    else:
        check(False, f"{rel}: image is blank")


def check_ico(path: Path):
    rel = path.relative_to(ROOT)
    img = Image.open(path)
    sizes = set(img.info.get("sizes", {img.size}))
    check({(16, 16), (32, 32), (48, 48)} <= sizes, f"{rel}: must contain 16, 32 and 48 px images, has {sorted(sizes)}")


def check_web():
    """DESIGN_GUIDE.md section 11: styles, copy and required legal links for the web pages."""
    css = (ROOT / "public" / "app.css").read_text()
    check(not re.search(r"#[0-9A-Fa-f]{3,8}\b", css), "public/app.css: use token variables, not hex colours")
    check(not re.search(r"box-shadow|gradient|filter:|opacity:", css), "public/app.css: no shadows, gradients, filters or opacity")
    banned = re.compile(r"\b(hot|babe|hunk|swipe|match(?:es|ing)?|bro|thirst)\b", re.I)
    emoji = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
    pages = [ROOT / "content" / "terms.html", ROOT / "content" / "privacy.html",
             ROOT / "public" / "terms" / "index.html", ROOT / "public" / "privacy" / "index.html"]
    for p in pages:
        rel = p.relative_to(ROOT)
        check(p.exists(), f"{rel} is missing (run scripts/build_legal.py)")
        if not p.exists():
            continue
        raw = p.read_text()
        text = re.sub(r"<[^>]+>", " ", raw)
        m = banned.search(text)
        check(not m, f"{rel}: contains a banned word ({m and m.group(0)})")
        check("!" not in text, f"{rel}: no exclamation marks")
        check(not emoji.search(text), f"{rel}: no emoji")
        check("style=" not in raw, f"{rel}: no inline styles")
        if rel.parts[0] == "public":
            check('href="/terms/"' in raw and 'href="/privacy/"' in raw, f"{rel}: footer must link to terms and privacy")
    # public legal pages must be current with their sources
    before = {p: p.read_text() for p in pages[2:] if p.exists()}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_legal.py")], check=True, capture_output=True)
    for p, old in before.items():
        check(p.read_text() == old, f"{p.relative_to(ROOT)} was out of date (regenerated; commit it)")
    for p in sorted((ROOT / "public").glob("*.html")):
        raw = p.read_text()
        check('href="/terms/"' in raw and 'href="/privacy/"' in raw, f"{p.relative_to(ROOT)}: footer must link to terms and privacy")
    signup = (ROOT / "public" / "signup.html").read_text()
    check('id="accept_terms"' in signup and 'id="consent_public"' in signup, "public/signup.html: needs terms and public-visibility consent boxes")
    stub = (ROOT / "functions" / "[stub].js").read_text()
    for needle in ("data-share-root", "og:title", "og:image", "/terms/", "/privacy/", "noindex", "data-share-copy"):
        check(needle in stub, f"functions/[stub].js: profile page must include {needle}")


def main():
    # 1. tokens.css is generated from tokens.json and must be current
    css = ROOT / "tokens" / "tokens.css"
    before = css.read_text() if css.exists() else ""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_tokens.py")], check=True, capture_output=True)
    check(css.read_text() == before, "tokens/tokens.css was out of date (it has now been regenerated; commit it)")

    # 2. guides use exactly the token palette
    guide = (ROOT / "DESIGN_GUIDE.md").read_text()
    guide_hex = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", guide)}
    check(guide_hex == PALETTE, f"DESIGN_GUIDE.md palette differs from tokens: {sorted(guide_hex ^ PALETTE)}")
    check((ROOT / "STYLE_GUIDE.md").exists(), "STYLE_GUIDE.md is missing")

    # 3. every asset is allowed, correctly named and documented in the design guide
    assets = sorted(p for p in (ROOT / "assets").rglob("*") if p.is_file())
    check(bool(assets), "no assets found")
    for p in assets:
        rel = p.relative_to(ROOT)
        check(p.suffix in ALLOWED_EXT, f"{rel}: file type not allowed")
        check(bool(NAME_RE.match(p.name)), f"{rel}: name must be lowercase and hyphen-separated")
        check(p.name in guide, f"{rel}: not documented in DESIGN_GUIDE.md")
        if p.suffix == ".svg":
            check_svg(p)
        elif p.suffix == ".png":
            check_png(p)
        elif p.suffix == ".ico":
            check_ico(p)

    # 4. everything the guide promises actually exists
    for name in re.findall(r"`((?:logo|icon|app-icon|apple-touch-icon|favicon)[a-z0-9.-]*\.(?:svg|png|ico))`", guide):
        check(any(p.name == name for p in assets), f"DESIGN_GUIDE.md lists {name} but the file does not exist")

    check_web()

    print(f"{passes} checks passed, {len(failures)} failed, {len(assets)} assets checked")
    for f in failures:
        print("FAIL:", f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
