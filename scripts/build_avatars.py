#!/usr/bin/env python3
"""Build the illustrated avatars for the sample profiles (DESIGN_GUIDE.md section 12).

Reads seed/sample-profiles.json and writes one 4:5 portrait per profile to public/img/avatars/<stub>.svg.
Also rewrites the "example members" strip on the landing page (between the examples markers in public/index.html).
Re-uses the character parts in scripts/build_hero.py. Colours come from tokens/tokens.json only.
"""
import html
import json
from pathlib import Path

import build_hero as H

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "seed" / "sample-profiles.json").read_text())["profiles"]
C = H.C
OL, S, INK, WHITE = H.OL, H.S, H.INK, H.WHITE

SKIN = {
    "peach": H.PEACH,
    "tan": H.TAN,
    "brown": (C["brown"], C["brown-light"], C["brown-deep"]),
    "umber": (C["umber"], C["umber-light"], C["umber-deep"]),
}
HAIR = {"black": INK, "hair": C["hair"], "brown": C["hair"], "hair-light": C["hair-light"], "yellow": C["yellow"], "orange": C["orange"], "iron": C["iron"]}
HILITE = {"black": C["iron"], "hair": C["hair-light"], "brown": C["hair-light"], "hair-light": C["hair"], "yellow": WHITE, "orange": C["yellow"], "iron": C["plate"]}
BROW = {"black": INK, "hair": C["hair"], "brown": C["hair"], "hair-light": C["hair"], "yellow": C["hair-light"], "orange": C["hair-light"], "iron": C["iron"]}
TOP = {k: C[k] for k in ("denim", "teal", "olive", "orange", "coral", "white", "sky")}
BG = {"plate": C["plate"], "yellow": C["yellow"], "mint-deep": C["mint-deep"], "sky": C["sky"], "chalk": C["chalk"], "mint": C["mint"]}
IRIS = {"hair": C["hair"], "hair-light": C["hair-light"], "sky": C["denim"], "teal": C["teal"]}


# ------------------------------------------------------------------ men (head frame 400 x 500, head centre 200,163)
def man_head(a):
    sk, skl, skd = SKIN[a["skin"]]
    hair, hi, brow = HAIR[a["hair"]], HILITE[a["hair"]], BROW[a["hair"]]
    style = a["style"]
    iris = IRIS[a.get("iris", "hair")]
    smile = 24 if style != "curly" else 26
    base, feats = H.man_features(sk, skl, skd, 0, iris, smile)
    brows = (f'<path d="M160 140 Q176 118 197 130 L197 138 Q178 130 162 148 Z M240 140 Q224 118 203 130 L203 138 Q222 130 238 148 Z" fill="{brow}"/>')
    back = front = ""
    if style == "quiff":
        front = (f'<path d="M142 140 C132 88 160 54 206 52 C252 50 276 86 260 140 C258 124 252 114 240 108 C218 98 186 98 166 108 C152 114 146 126 142 140 Z" fill="{hair}"/>'
                 f'<path d="M158 104 Q190 70 246 86 M176 86 Q206 66 240 74 M146 126 Q152 106 168 96" fill="none" stroke="{hi}" stroke-width="4" stroke-linecap="round"/>')
    elif style == "sidepart":
        front = (f'<path d="M142 140 C134 96 158 62 200 58 C246 54 268 86 260 140 C256 120 248 110 232 106 C212 100 182 100 164 108 C152 114 146 126 142 140 Z" fill="{hair}"/>'
                 f'<path d="M176 62 Q188 92 160 112 M204 60 Q236 62 252 88 M150 124 Q154 108 168 100" fill="none" stroke="{hi}" stroke-width="4" stroke-linecap="round"/>')
    elif style == "buzz":
        front = (f'<path d="M144 138 C140 100 160 88 200 88 C240 88 260 100 256 138 C252 118 244 108 232 104 C214 98 186 98 168 104 C156 108 148 118 144 138 Z" fill="{hair}"/>'
                 f'<path d="M150 112 Q172 94 200 92 Q228 94 250 112" fill="none" stroke="{hi}" stroke-width="3" stroke-linecap="round"/>')
    elif style == "curly":
        bumps = [(160, 94, 15), (180, 74, 17), (206, 68, 18), (232, 74, 17), (250, 94, 15), (150, 116, 12), (258, 118, 12)]
        front = (f'<path d="M144 140 C142 104 156 96 170 100 L200 100 L232 100 C246 96 258 104 256 140 C254 124 246 114 232 110 C214 104 186 104 168 110 C154 116 146 126 144 140 Z" fill="{hair}"/>'
                 + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hair}" stroke="{OL}" stroke-width="2.4"/>' for x, y, r in bumps)
                 + f'<path d="M146 134 L147 160 L154 146 L154 120 Z M254 134 L253 160 L246 146 L246 120 Z" fill="{hair}"/>'
                 + f'<path d="M170 82 Q182 68 198 66 M214 66 Q230 66 240 78" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>')
    elif style == "bun":
        front = (f'<circle cx="200" cy="56" r="22" fill="{hair}" stroke="{OL}" stroke-width="2.6"/>'
                 f'<path d="M142 140 C134 94 160 64 204 62 C250 60 270 90 260 140 C258 124 252 114 240 108 C218 98 186 98 166 108 C152 114 146 126 142 140 Z" fill="{hair}"/>')
    # style == "bald": no hair
    beard = mouth = ""
    if a.get("beard"):
        bc = hair if style != "bald" else C["hair"]
        beard = (f'<path d="M146 166 Q148 212 178 236 Q200 246 222 236 Q252 212 254 166 L246 178 Q244 202 222 216 Q200 224 178 216 Q156 202 154 178 Z" fill="{bc}"/>'
                 f'<path d="M176 194 Q200 184 224 194 Q200 198 176 194 Z" fill="{bc}"/>')
        mouth = H.mouth(200, 27, smile, skd, skd)
    return f"{back}{base}{front}{brows}{feats}{beard}{mouth}"


# ------------------------------------------------------------------ women
def woman_head(a):
    sk, skl, skd = SKIN[a["skin"]]
    hair, hi, brow = HAIR[a["hair"]], HILITE[a["hair"]], BROW[a["hair"]]
    style = a["style"]
    accent = TOP.get(a.get("accent", "coral"), C["coral"])
    iris = IRIS[a.get("iris", "hair")]
    st = f'stroke="{OL}" stroke-width="3" stroke-linejoin="round"'
    back = front = ""
    if style == "pony":
        back = (f'<path d="M170 70 C112 32 70 86 92 150 C98 176 118 196 140 196 C122 172 120 130 152 108 Z" fill="{hair}" {st}/>'
                f'<path d="M150 90 C118 86 104 120 112 156 M140 80 C108 74 90 112 98 146" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>')
        front = f'<ellipse cx="160" cy="76" rx="9" ry="14" transform="rotate(-40 160 76)" fill="{accent}" stroke="{OL}" stroke-width="2.5"/>'
    elif style == "curly":
        curls = [(138, 96, 36), (100, 126, 34), (110, 170, 32), (80, 162, 26), (148, 66, 30), (172, 50, 24), (122, 214, 28), (92, 112, 24), (96, 226, 24), (126, 250, 24), (82, 200, 22),
                 (264, 96, 34), (300, 128, 32), (290, 172, 30), (320, 164, 24), (252, 66, 28), (230, 50, 22), (278, 214, 26), (308, 114, 22), (304, 226, 22), (274, 250, 22), (318, 202, 20)]
        back = ("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hair}" stroke="{OL}" stroke-width="3"/>' for x, y, r in curls)
                + "".join(f'<path d="M{x-r*0.5} {y-r*0.2} Q{x} {y-r*0.8} {x+r*0.5} {y-r*0.1}" fill="none" stroke="{hi}" stroke-width="3" stroke-linecap="round"/>' for x, y, r in curls))
    elif style == "long":
        back = (f'<path d="M154 110 C122 144 120 224 138 276 L190 262 C170 232 160 190 158 150 Z" fill="{hair}" {st}/>'
                f'<path d="M246 110 C278 144 280 224 262 276 L210 262 C230 232 240 190 242 150 Z" fill="{hair}" {st}/>'
                f'<path d="M140 180 Q140 224 150 256 M260 180 Q260 224 250 256" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>')
    elif style == "bob":
        back = (f'<path d="M152 112 C128 150 132 208 158 226 C172 230 180 216 178 198 L170 120 Z" fill="{hair}" {st}/>'
                f'<path d="M248 112 C272 150 268 208 242 226 C228 230 220 216 222 198 L230 120 Z" fill="{hair}" {st}/>')
        front = f'<path d="M152 190 Q156 214 170 222 M248 190 Q244 214 230 222" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>'
    elif style == "bun":
        front = (f'<circle cx="206" cy="46" r="26" fill="{hair}" {st}/>'
                 f'<path d="M190 36 Q206 24 222 38" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M186 66 Q206 76 228 66" fill="none" stroke="{accent}" stroke-width="7" stroke-linecap="round"/>')
    elif style == "braid":
        links = [(254, 168), (260, 194), (264, 220), (264, 246), (262, 272)]
        back = ""
        front = ("".join(f'<ellipse cx="{x}" cy="{y}" rx="14" ry="15" fill="{hair}" stroke="{OL}" stroke-width="2.8"/>'
                         f'<path d="M{x-8} {y-6} Q{x} {y+4} {x+8} {y-6}" fill="none" stroke="{hi}" stroke-width="2.4" stroke-linecap="round"/>' for x, y in links)
                 + f'<rect x="250" y="284" width="26" height="8" rx="4" fill="{accent}" stroke="{OL}" stroke-width="2.4"/>')
    elif style == "pixie":
        front = f'<path d="M146 130 Q140 160 150 180 Q158 154 154 132 Z M254 130 Q260 160 250 180 Q242 154 246 132 Z" fill="{hair}" {st}/>'
    eyes = (H.eye_happy(180, 156, 12, -1) + H.eye_happy(220, 156, 12, 1) if a.get("eyes") == "happy"
            else H.eye_open(180, 154, 12, 11, 8.5, 2, iris, True, -1) + H.eye_open(220, 154, 12, 11, 8.5, 2, iris, True, 1))
    cap = (f'<path d="M148 140 C136 86 166 54 206 52 C248 50 270 86 254 140 C250 116 240 100 222 92 C204 112 174 128 148 140 Z" fill="{hair}" {st}/>'
           f'<path d="M162 96 Q196 64 246 82 M174 78 Q204 58 238 66" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>')
    if style == "curly":  # fuller crown
        cap = (f'<path d="M148 140 C136 86 166 54 206 52 C248 50 270 86 254 140 C250 116 240 100 222 92 C204 112 174 128 148 140 Z" fill="{hair}" {st}/>'
               f'<path d="M162 96 Q196 64 246 82 M174 78 Q204 58 238 66" fill="none" stroke="{hi}" stroke-width="3.5" stroke-linecap="round"/>')
    return f"""{back}
  <circle cx="150" cy="166" r="10" fill="{sk}" {H.FACE_S}/><circle cx="250" cy="166" r="10" fill="{sk}" {H.FACE_S}/>
  <ellipse cx="150" cy="166" rx="4" ry="6" fill="{skd}"/><ellipse cx="250" cy="166" rx="4" ry="6" fill="{skd}"/>
  <path d="{H.WOMAN_FACE}" fill="{sk}" {H.FACE_S}/>
  <path d="M246 134 C246 170 238 204 222 224 Q236 214 244 194 Q250 164 246 134 Z" fill="{skd}"/>
  <ellipse cx="204" cy="112" rx="22" ry="6" fill="{skl}"/>
  {cap}{front}
  <path d="M164 140 Q178 128 194 136 M206 136 Q222 128 236 140" fill="none" stroke="{brow}" stroke-width="3.8" stroke-linecap="round"/>
  {eyes}
  <path d="M199 172 Q195 180 200 182 Q205 182 205 178" fill="none" stroke="{skd}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="164" cy="186" r="8" fill="{skd}"/><circle cx="236" cy="186" r="8" fill="{skd}"/>
  {H.mouth(200, 24, 24, C['coral-deep'], skd)}"""


# ------------------------------------------------------------------ busts (200 x 250 portrait frame)
def sleeves(colour):
    return (f'<path d="M66 196 C44 192 26 204 22 228 L26 244 L58 240 C62 226 68 216 76 210 Z" fill="{colour}" {S}/>'
            f'<path d="M134 196 C156 192 174 204 178 228 L174 244 L142 240 C138 226 132 216 124 210 Z" fill="{colour}" {S}/>')


def bust(a, sk, skd):
    colour = TOP[a["top"]]
    kind = a.get("kind", "tank")
    arms = H.arm_down(-1, sk) + H.arm_down(1, sk)
    if kind == "curl":
        db = (f'<g transform="translate(30 168)"><rect x="-17" y="-3" width="34" height="6" rx="2" fill="{C["iron"]}"/>'
              f'<rect x="-25" y="-14" width="10" height="28" rx="4" fill="{INK}" stroke="{OL}" stroke-width="2"/><rect x="15" y="-14" width="10" height="28" rx="4" fill="{INK}" stroke="{OL}" stroke-width="2"/></g>')
        arms += H.limbs([(30, 250, 34, 190, 22)], sk) + f'<circle cx="31" cy="176" r="13" fill="{sk}" {S}/>' + db
    trim = OL if colour == WHITE else WHITE
    if a["gender"] == "woman":
        top = (f'<path d="M72 198 L82 184 Q100 210 118 184 L128 198 C130 216 128 232 130 250 L70 250 C72 232 70 216 72 198 Z" fill="{colour}" {S}/>'
               f'<path d="M82 184 Q100 210 118 184" fill="none" stroke="{trim}" stroke-width="3"/>')
    else:
        top = (f'<path d="M66 196 L78 182 Q100 214 122 182 L134 196 C138 214 134 232 136 250 L64 250 C66 232 62 214 66 196 Z" fill="{colour}" {S}/>'
               f'<path d="M78 182 Q100 214 122 182" fill="none" stroke="{trim}" stroke-width="3"/>')
    if kind == "tee":
        top += sleeves(colour)
    return H.shoulders(sk, skd, top, WHITE, arms)


def avatar_svg(p):
    a = dict(p["avatar"], gender=p["gender"])
    sk, skl, skd = SKIN[a["skin"]]
    head = man_head(a) if p["gender"] == "man" else woman_head(a)
    tilt = (-3, 3)[len(p["stub"]) % 2]
    body = bust(a, sk, skd)
    inner = H.portrait(0, BG[a["bg"]], head, body, tilt)
    title = f'Illustrated avatar of {p["first_name"]}, {p["look"]}'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 250" role="img">\n'
            f'  <title>{html.escape(title)}</title>\n  {inner}\n</svg>\n')


# ------------------------------------------------------------------ landing page strip
def examples_html():
    cards = []
    for p in DATA:
        alt = f'Illustrated avatar of {p["first_name"]}, {p["look"]}'
        place = f'{p["suburb"]}, {p["city"]}' if p["suburb"] != p["city"] else p["city"]
        cards.append(
            f'    <li class="example-card"><img src="/img/avatars/{p["stub"]}.svg" alt="{html.escape(alt)}" width="200" height="250" loading="lazy">'
            f'<p class="label">{html.escape(p["first_name"])}, {p["age"]}</p><p class="small muted">{html.escape(place)}</p></li>')
    return ("<!-- examples:start (generated by scripts/build_avatars.py) -->\n"
            '  <section class="section stack" aria-labelledby="examples-heading">\n'
            '    <h2 id="examples-heading">Meet some example members</h2>\n'
            f'    <p>These {len(DATA)} characters are made up to show how profiles look. They aren\'t real members.</p>\n'
            '    <ul class="example-scroll" role="list" tabindex="0" aria-label="Example profiles. Scroll sideways to see more.">\n'
            + "\n".join(cards) +
            "\n    </ul>\n  </section>\n  <!-- examples:end -->")


def main():
    out = ROOT / "public" / "img" / "avatars"
    out.mkdir(parents=True, exist_ok=True)
    keep = {f'{p["stub"]}.svg' for p in DATA}
    for old in out.glob("*.svg"):
        if old.name not in keep:
            old.unlink()
    for p in DATA:
        (out / f'{p["stub"]}.svg').write_text(avatar_svg(p))
    page = ROOT / "public" / "index.html"
    text = page.read_text()
    start, end = text.index("<!-- examples:start"), text.index("<!-- examples:end -->") + len("<!-- examples:end -->")
    page.write_text(text[:start] + examples_html() + text[end:])
    print(f"wrote {len(DATA)} avatars to public/img/avatars/ and updated public/index.html")


if __name__ == "__main__":
    main()
