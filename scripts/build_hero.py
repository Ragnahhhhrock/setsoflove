#!/usr/bin/env python3
"""Build the landing-page illustrations into public/img/ (DESIGN_GUIDE.md section 12).

hero-gym.svg      Two original characters high-fiving in a bright gym, a phone in each other hand.
members-strip.svg Three more regulars as 4:5 portraits.

Colours come from tokens/tokens.json: the 11 brand colours plus the illustration tones.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "tokens" / "tokens.json").read_text())
C = {k: v["hex"] for k, v in T["colour"].items()}
C.update({k: v["hex"] for k, v in T["illustration"].items()})
INK, WHITE, YEL, HEART, CORAL, CDEEP, PLATE, IRON, CHALK = (C[k] for k in ("ink", "white", "yellow", "heart", "coral", "coral-deep", "plate", "iron", "chalk"))
MINT, MINTD, TEAL, SKY, DENIM, OLIVE, ORANGE = (C[k] for k in ("mint", "mint-deep", "teal", "sky", "denim", "olive", "orange"))
HR, HRL = C["hair"], C["hair-light"]
OL = HR  # outline colour
PEACH = (C["skin"], C["skin-light"], C["skin-deep"])
TAN = (C["tan"], C["tan-light"], C["tan-deep"])

HEART_D = "M0 14 C-18 2 -16 -14 -6 -14 C-2 -14 0 -11 0 -9 C0 -11 2 -14 6 -14 C16 -14 18 2 0 14 Z"
STAR_D = "M0 -12 Q2 -2 12 0 Q2 2 0 12 Q-2 2 -12 0 Q-2 -2 0 -12 Z"
S = f'stroke="{OL}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'


def heart(x, y, s, fill=HEART):
    return f'<path d="{HEART_D}" transform="translate({x} {y}) scale({s})" fill="{fill}"/>'


def star(x, y, s, fill=WHITE):
    return f'<path d="{STAR_D}" transform="translate({x} {y}) scale({s})" fill="{fill}"/>'


def limbs(segs, sk, join=True):
    """Outlined limb made of round-capped segments (x1, y1, x2, y2, width): outlines first, then fills."""
    o = "".join(f'<path d="M{a} {b} L{c} {d}" fill="none" stroke="{OL}" stroke-width="{w+5.5}" stroke-linecap="round"/>' for a, b, c, d, w in segs)
    f = "".join(f'<path d="M{a} {b} L{c} {d}" fill="none" stroke="{sk}" stroke-width="{w}" stroke-linecap="round"/>' for a, b, c, d, w in segs)
    return o + f


# ---------------------------------------------------------------- phone
def phone_group():
    return f"""<rect x="-30" y="-52" width="60" height="104" rx="11" fill="{INK}"/>
    <rect x="-25" y="-45" width="50" height="90" rx="7" fill="{WHITE}"/>
    <rect x="-8" y="-43" width="16" height="4" rx="2" fill="{INK}"/>
    <rect x="-20" y="-33" width="40" height="30" rx="5" fill="{PLATE}"/>
    {heart(0, -18, 0.9)}
    <rect x="-20" y="2" width="26" height="5" rx="2.5" fill="{INK}"/>
    <rect x="-20" y="12" width="36" height="4" rx="2" fill="{PLATE}"/>
    <rect x="-20" y="21" width="30" height="4" rx="2" fill="{PLATE}"/>
    <rect x="-20" y="30" width="40" height="8" rx="4" fill="{CORAL}"/>"""


def phone_in_hand(x, y, rot, side, sk):
    fx = -30 if side == -1 else 30
    tx = 30 if side == -1 else -30
    fingers = "".join(f'<ellipse cx="{fx}" cy="{dy}" rx="8.5" ry="10" fill="{sk}" {S}/>' for dy in (-14, 4, 22))
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale(0.86)">{phone_group()}{fingers}'
            f'<circle cx="0" cy="46" r="20" fill="{sk}" {S}/>'
            f'<ellipse cx="{tx}" cy="28" rx="9.5" ry="17" fill="{sk}" {S}/></g>')


# ---------------------------------------------------------------- face parts (old 400 x 500 frame, head centre 200,163)
def eye_open(cx, cy, rx, ry, ir, look=0, iris=None, lashes=False, side=1):
    i = cx + look
    o = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{WHITE}"/>'
         f'<circle cx="{i}" cy="{cy+1}" r="{ir}" fill="{iris or HR}"/>'
         f'<circle cx="{i}" cy="{cy+1}" r="{ir*0.5}" fill="{INK}"/>'
         f'<circle cx="{i+ir*0.4}" cy="{cy-ir*0.35}" r="{ir*0.32}" fill="{WHITE}"/>'
         f'<path d="M{cx-rx-1} {cy+1} Q{cx} {cy-ry-5} {cx+rx+1} {cy+1}" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    if lashes:
        ox = cx + (rx + 1) * side
        o += f'<path d="M{ox} {cy+1} Q{ox+6*side} {cy-2} {ox+10*side} {cy-8} Q{ox+4*side} {cy-5} {ox-2*side} {cy-6} Z" fill="{INK}"/>'
    return o


def eye_happy(cx, cy, w, side):
    ox = cx + (w + 1) * side
    return (f'<path d="M{cx-w} {cy+4} Q{cx} {cy-10} {cx+w} {cy+4}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'
            f'<path d="M{ox} {cy+3} L{ox+8*side} {cy-3}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')


def mouth(cx, w, depth, lips, skd):
    l, r = cx - w, cx + w
    return f"""
  <path d="M{l} 199 Q{cx} 206 {r} 199 Q{r-4} {199+depth} {cx} {199+depth} Q{l+4} {199+depth} {l} 199 Z" fill="{INK}" stroke="{lips}" stroke-width="3.4" stroke-linejoin="round"/>
  <path d="M{l+3} 201 Q{cx} 207 {r-3} 201 Q{r-6} {201+depth*0.38} {cx} {201+depth*0.4} Q{l+6} {201+depth*0.38} {l+3} 201 Z" fill="{WHITE}"/>
  <path d="M{cx-w*0.45} {197+depth*0.92} Q{cx} {197+depth*0.5} {cx+w*0.45} {197+depth*0.92} Q{cx} {197+depth*1.05} {cx-w*0.45} {197+depth*0.92} Z" fill="{CORAL}"/>
  <path d="M{l-4} 193 Q{l-8} 201 {l-2} 207 M{r+4} 193 Q{r+8} 201 {r+2} 207" fill="none" stroke="{skd}" stroke-width="2.6" stroke-linecap="round"/>"""


MAN_FACE = ("M146 132 C146 98 170 86 200 86 C230 86 254 98 254 132 L254 176 Q252 200 236 218 L222 236 "
            "Q200 244 178 236 L164 218 Q148 200 146 176 Z")
WOMAN_FACE = ("M150 130 C150 98 172 86 200 86 C228 86 250 98 250 130 C250 170 240 206 222 226 "
              "Q200 246 178 226 C160 206 150 170 150 130 Z")
FACE_S = f'stroke="{OL}" stroke-width="3.6" stroke-linejoin="round"'


def man_features(sk, skl, skd, look=0, iris=None, smile=26):
    return f"""
  <circle cx="146" cy="164" r="12" fill="{sk}" {FACE_S}/><circle cx="254" cy="164" r="12" fill="{sk}" {FACE_S}/>
  <ellipse cx="146" cy="164" rx="4.5" ry="7" fill="{skd}"/><ellipse cx="254" cy="164" rx="4.5" ry="7" fill="{skd}"/>
  <path d="{MAN_FACE}" fill="{sk}" {FACE_S}/>
  <path d="M250 134 L254 176 Q252 200 236 218 L222 236 Q238 228 244 212 Q252 190 250 134 Z" fill="{skd}"/>
  <ellipse cx="196" cy="112" rx="24" ry="6" fill="{skl}"/>""", f"""
  {eye_open(178, 154, 11, 9, 7, look, iris)} {eye_open(222, 154, 11, 9, 7, look, iris)}
  <path d="M201 156 L200 180 M193 184 Q200 190 207 184" fill="none" stroke="{skd}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="162" cy="186" r="8" fill="{skd}"/><circle cx="238" cy="186" r="8" fill="{skd}"/>
  {mouth(200, 27, smile, skd, skd)}
  <path d="M200 232 L200 240" stroke="{skd}" stroke-width="3" stroke-linecap="round"/>"""


def head_man_fade(look):
    """Character 2: short fade with a curly top."""
    sk, skl, skd = TAN
    base, feats = man_features(sk, skl, skd, look)
    bumps = [(160, 94, 15), (180, 74, 17), (206, 68, 18), (232, 74, 17), (250, 94, 15), (150, 116, 12), (258, 118, 12)]
    top = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}" stroke="{OL}" stroke-width="2.4"/>' for x, y, r in bumps)
    return f"""{base}
  <path d="M144 140 C142 104 156 96 170 100 L200 100 L232 100 C246 96 258 104 256 140 C254 124 246 114 232 110 C214 104 186 104 168 110 C154 116 146 126 144 140 Z" fill="{INK}"/>
  {top}
  <path d="M146 134 L147 160 L154 146 L154 120 Z M254 134 L253 160 L246 146 L246 120 Z" fill="{INK}"/>
  <path d="M170 82 Q182 68 198 66 M214 66 Q230 66 240 78" fill="none" stroke="{IRON}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M160 140 Q176 118 197 130 L197 138 Q178 130 162 148 Z M240 140 Q224 118 203 130 L203 138 Q222 130 238 148 Z" fill="{INK}"/>
  {feats}"""


def head_man_quiff(hair, hi, brow, iris=None, look=0):
    sk, skl, skd = TAN if hair == INK else PEACH
    base, feats = man_features(sk, skl, skd, look, iris, 22)
    return f"""{base}
  <path d="M142 140 C132 88 160 54 206 52 C252 50 276 86 260 140 C258 124 252 114 240 108 C218 98 186 98 166 108 C152 114 146 126 142 140 Z" fill="{hair}"/>
  <path d="M158 104 Q190 70 246 86 M176 86 Q206 66 240 74 M146 126 Q152 106 168 96" fill="none" stroke="{hi}" stroke-width="4" stroke-linecap="round"/>
  <path d="M160 140 Q176 118 197 130 L197 138 Q178 130 162 148 Z M240 140 Q224 118 203 130 L203 138 Q222 130 238 148 Z" fill="{brow}"/>
  {feats}"""


def head_woman_curly():
    """Character 1: big curly ponytail, laughing with her eyes shut."""
    sk, skl, skd = PEACH
    curls = [(138, 96, 36), (100, 126, 34), (110, 170, 32), (80, 162, 26), (148, 66, 30), (172, 50, 24), (122, 214, 28), (92, 112, 24),
             (96, 226, 24), (126, 250, 24), (82, 200, 22)]
    back = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{HRL}" stroke="{OL}" stroke-width="3"/>' for x, y, r in curls)
    swirls = "".join(f'<path d="M{x-r*0.5} {y-r*0.2} Q{x} {y-r*0.8} {x+r*0.5} {y-r*0.1}" fill="none" stroke="{HR}" stroke-width="3" stroke-linecap="round"/>' for x, y, r in curls)
    return f"""
  {back}{swirls}
  <circle cx="150" cy="166" r="10" fill="{sk}" {FACE_S}/><ellipse cx="150" cy="166" rx="4" ry="6" fill="{skd}"/>
  <path d="{WOMAN_FACE}" fill="{sk}" {FACE_S}/>
  <path d="M246 134 C246 170 238 204 222 224 Q236 214 244 194 Q250 164 246 134 Z" fill="{skd}"/>
  <ellipse cx="204" cy="112" rx="22" ry="6" fill="{skl}"/>
  <path d="M148 136 C138 84 166 54 206 52 C246 50 268 84 254 138 C250 114 240 98 224 90 C206 112 176 126 148 136 Z" fill="{HRL}" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M160 98 Q196 64 246 82 M172 80 Q204 58 238 66 M150 124 Q158 100 178 88" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="162" cy="116" r="9" fill="{HRL}" stroke="{OL}" stroke-width="2.5"/><circle cx="152" cy="134" r="8" fill="{HRL}" stroke="{OL}" stroke-width="2.5"/>
  <ellipse cx="168" cy="66" rx="10" ry="16" transform="rotate(-50 168 66)" fill="{TEAL}" stroke="{OL}" stroke-width="2.5"/>
  <path d="M164 140 Q178 128 194 136 M206 136 Q222 128 236 140" fill="none" stroke="{HR}" stroke-width="3.8" stroke-linecap="round"/>
  {eye_happy(180, 156, 12, -1)} {eye_happy(220, 156, 12, 1)}
  <path d="M199 172 Q195 180 200 182 Q205 182 205 178" fill="none" stroke="{skd}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="164" cy="186" r="8" fill="{skd}"/><circle cx="236" cy="186" r="8" fill="{skd}"/>
  {mouth(200, 24, 26, CDEEP, skd)}"""


def head_woman_pony():
    """Character 5: swinging ponytail, big smile."""
    sk, skl, skd = PEACH
    return f"""
  <path d="M170 70 C112 32 70 86 92 150 C98 176 118 196 140 196 C122 172 120 130 152 108 Z" fill="{HRL}" stroke="{OL}" stroke-width="3"/>
  <path d="M150 90 C118 86 104 120 112 156 M140 80 C108 74 90 112 98 146" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="150" cy="166" r="10" fill="{sk}" {FACE_S}/><ellipse cx="150" cy="166" rx="4" ry="6" fill="{skd}"/>
  <path d="{WOMAN_FACE}" fill="{sk}" {FACE_S}/>
  <path d="M246 134 C246 170 238 204 222 224 Q236 214 244 194 Q250 164 246 134 Z" fill="{skd}"/>
  <ellipse cx="204" cy="112" rx="22" ry="6" fill="{skl}"/>
  <path d="M148 140 C136 86 166 54 206 52 C248 50 270 86 254 140 C250 116 240 100 222 92 C204 112 174 128 148 140 Z" fill="{HRL}" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M162 96 Q196 64 246 82 M174 78 Q204 58 238 66" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  <ellipse cx="160" cy="76" rx="9" ry="14" transform="rotate(-40 160 76)" fill="{ORANGE}" stroke="{OL}" stroke-width="2.5"/>
  <path d="M164 140 Q178 128 194 136 M206 136 Q222 128 236 140" fill="none" stroke="{HR}" stroke-width="3.8" stroke-linecap="round"/>
  {eye_open(180, 154, 12, 11, 8.5, 2, None, True, -1)} {eye_open(220, 154, 12, 11, 8.5, 2, None, True, 1)}
  <path d="M199 172 Q195 180 200 182 Q205 182 205 178" fill="none" stroke="{skd}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="164" cy="186" r="8" fill="{skd}"/><circle cx="236" cy="186" r="8" fill="{skd}"/>
  {mouth(200, 24, 22, CDEEP, skd)}"""


def place_head(inner, tilt, x=0, y=-364, k=0.44):
    return (f'<g transform="translate({x} {y}) scale({k}) translate(-200 -163)">'
            f'<g transform="rotate({tilt} 200 250)">{inner}</g></g>')


def hand_up(x, y, flip, sk):
    f = flip
    fl = [(x-9*f, y-8, x-13*f, y-36, 9), (x-1*f, y-10, x-2*f, y-43, 9), (x+7*f, y-8, x+9*f, y-39, 9), (x+14*f, y-4, x+19*f, y-29, 9)]
    th = [(x-12*f, y+6, x-27*f, y-6, 10)]
    return limbs(fl + th, sk) + f'<ellipse cx="{x}" cy="{y+2}" rx="17" ry="19" fill="{sk}" {S}/>'


# ---------------------------------------------------------------- hero characters (local frame: feet at 0,0)
def man_body():
    sk, skl, skd = TAN
    return f"""
  <ellipse cx="0" cy="2" rx="74" ry="9" fill="{PLATE}"/>
  <path d="M-44 -132 C-48 -96 -44 -66 -36 -44 L-34 -32 L-8 -32 L-8 -44 C-4 -74 -4 -104 -6 -132 Z" fill="{sk}" {S}/>
  <path d="M44 -132 C48 -96 44 -66 36 -44 L34 -32 L8 -32 L8 -44 C4 -74 4 -104 6 -132 Z" fill="{sk}" {S}/>
  <path d="M-32 -108 C-40 -92 -38 -72 -34 -58 M32 -108 C40 -92 38 -72 34 -58" fill="none" stroke="{skd}" stroke-width="3" stroke-linecap="round"/>
  <rect x="-35" y="-37" width="28" height="23" rx="4" fill="{WHITE}" {S}/><rect x="7" y="-37" width="28" height="23" rx="4" fill="{WHITE}" {S}/>
  <path d="M-44 -16 C-42 -28 -18 -30 -8 -22 L-4 -6 C-4 2 -8 6 -14 6 L-48 6 C-56 6 -54 -8 -44 -16 Z" fill="{INK}" {S}/>
  <path d="M44 -16 C42 -28 18 -30 8 -22 L4 -6 C4 2 8 6 14 6 L48 6 C56 6 54 -8 44 -16 Z" fill="{INK}" {S}/>
  <path d="M-52 1 L-6 1 M6 1 L52 1" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
  <path d="M-32 -22 L-16 -16 M32 -22 L16 -16" stroke="{CORAL}" stroke-width="4" stroke-linecap="round"/>
  <path d="M-48 -202 L48 -202 L58 -120 L6 -120 L0 -152 L-6 -120 L-58 -120 Z" fill="{INK}" {S}/>
  <path d="M-46 -198 L-55 -124 M46 -198 L55 -124" stroke="{IRON}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M-8 -200 L-10 -170 M8 -200 L10 -170" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M-15 -336 L-15 -304 C-15 -296 15 -296 15 -304 L15 -336 Z" fill="{sk}" {S}/>
  <path d="M-14 -334 C-8 -318 8 -318 14 -334 L14 -324 C8 -308 -8 -308 -14 -324 Z" fill="{skd}"/>
  {limbs([(58, -294, 86, -236, 32), (86, -236, 94, -254, 24)], sk)}
  <path d="M-30 -314 Q0 -294 30 -314 L62 -300 L84 -256 L60 -240 L46 -266 C48 -240 46 -218 44 -196 L-44 -196 C-46 -218 -48 -240 -46 -266 L-60 -240 L-84 -256 L-62 -300 Z" fill="{CORAL}" {S}/>
  <path d="M-30 -314 Q0 -294 30 -314" fill="none" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
  <path d="M-26 -264 Q-10 -246 0 -256 M26 -264 Q10 -246 0 -256 M-32 -214 Q-28 -204 -30 -196 M32 -214 Q28 -204 30 -196" fill="none" stroke="{CDEEP}" stroke-width="3.5" stroke-linecap="round"/>
  {heart(0, -222, 1.0, WHITE)}
  <path d="M-26 -320 L-40 -226 L-20 -220 L-8 -304 Z M26 -320 L40 -226 L20 -220 L8 -304 Z" fill="{WHITE}" {S}/>
  <path d="M-39 -240 L-21 -235 M39 -240 L21 -235" stroke="{IRON}" stroke-width="3"/>
  {limbs([(-58, -292, -114, -280, 36), (-114, -280, -131, -350, 28)], sk)}
  <path d="M-98 -300 Q-108 -284 -102 -266 M-126 -316 L-130 -336" fill="none" stroke="{skd}" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M-98 -304 Q-86 -312 -74 -304" fill="none" stroke="{skl}" stroke-width="3.5" stroke-linecap="round"/>
  {hand_up(-134, -372, -1, sk)}
  {phone_in_hand(96, -278, 8, -1, sk)}
  {heart(104, -350, 0.7)}
  {place_head(head_man_fade(-4), 5)}
"""


def woman_body():
    sk, skl, skd = PEACH
    return f"""
  <ellipse cx="0" cy="2" rx="68" ry="9" fill="{PLATE}"/>
  <path d="M-24 -90 L-24 -34 L-4 -34 L-4 -90 Z M4 -90 L4 -34 L24 -34 L24 -90 Z" fill="{sk}" {S}/>
  <path d="M-38 -202 C-42 -160 -34 -118 -28 -80 L-6 -80 C-2 -118 0 -160 0 -202 Z" fill="{INK}" {S}/>
  <path d="M38 -202 C42 -160 34 -118 28 -80 L6 -80 C2 -118 0 -160 0 -202 Z" fill="{INK}" {S}/>
  <path d="M-37 -192 C-40 -150 -34 -120 -28 -84 M37 -192 C40 -150 34 -120 28 -84" fill="none" stroke="{YEL}" stroke-width="3.4" stroke-linecap="round"/>
  <path d="M-32 -22 C-30 -34 -8 -36 -2 -26 L2 -8 C2 0 -2 6 -8 6 L-36 6 C-44 6 -42 -8 -32 -22 Z" fill="{TEAL}" {S}/>
  <path d="M32 -22 C30 -34 8 -36 2 -26 L-2 -8 C-2 0 2 6 8 6 L36 6 C44 6 42 -8 32 -22 Z" fill="{TEAL}" {S}/>
  <path d="M-40 3 L-2 3 M2 3 L40 3" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>
  <path d="M-26 -22 L-12 -18 M-24 -28 L-10 -24 M26 -22 L12 -18 M24 -28 L10 -24" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M-12 -336 L-12 -306 C-12 -298 12 -298 12 -306 L12 -336 Z" fill="{sk}" {S}/>
  <path d="M-11 -334 C-6 -320 6 -320 11 -334 L11 -326 C6 -312 -6 -312 -11 -326 Z" fill="{skd}"/>
  <path d="M-46 -300 Q0 -320 46 -300 L40 -250 L34 -196 L-34 -196 L-40 -250 Z" fill="{sk}" {S}/>
  {limbs([(-44, -294, -72, -236, 26), (-72, -236, -80, -254, 20)], sk)}
  <path d="M-30 -302 L-20 -318 Q0 -292 20 -318 L30 -302 C34 -282 40 -268 38 -250 C36 -230 30 -214 34 -194 L-34 -194 C-30 -214 -36 -230 -38 -250 C-40 -268 -34 -282 -30 -302 Z" fill="{TEAL}" {S}/>
  <path d="M-30 -302 L-20 -318 Q0 -292 20 -318 L30 -302" fill="none" stroke="{WHITE}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M-20 -262 Q-8 -248 0 -258 M20 -262 Q8 -248 0 -258" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>
  {heart(0, -224, 0.9, WHITE)}
  {limbs([(44, -294, 102, -284, 28), (102, -284, 124, -350, 23)], sk)}
  <path d="M60 -304 Q74 -312 86 -304" fill="none" stroke="{skl}" stroke-width="3" stroke-linecap="round"/>
  <path d="M104 -310 L118 -334" fill="none" stroke="{YEL}" stroke-width="8"/>
  {hand_up(128, -372, 1, sk)}
  {phone_in_hand(-82, -278, -8, 1, sk)}
  {heart(-88, -350, 0.7)}
  {place_head(head_woman_curly(), -5, 0, -362)}
"""


# ---------------------------------------------------------------- scene
def light(x):
    return (f'<path d="M{x+90} 0 L{x+90} 24 M{x+30} 0 L{x+30} 24" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x}" y="22" width="120" height="14" rx="7" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>')


def dumbbell_rack():
    rows = ""
    for y in (372, 406):
        for i in range(5):
            x = 626 + i * 31
            rows += (f'<g transform="translate({x} {y})"><rect x="-13" y="-3" width="26" height="6" rx="2" fill="{IRON}"/>'
                     f'<rect x="-14" y="-10" width="7" height="20" rx="3" fill="{INK}"/><rect x="7" y="-10" width="7" height="20" rx="3" fill="{INK}"/></g>')
    return (f'<rect x="610" y="384" width="6" height="64" fill="{IRON}"/><rect x="788" y="384" width="6" height="64" fill="{IRON}"/>'
            f'<rect x="606" y="386" width="190" height="8" rx="3" fill="{IRON}"/><rect x="606" y="420" width="190" height="8" rx="3" fill="{IRON}"/>' + rows)


def squat_rack():
    return (f'<rect x="676" y="130" width="14" height="262" fill="{IRON}"/><rect x="752" y="130" width="14" height="262" fill="{IRON}"/>'
            f'<rect x="672" y="126" width="98" height="12" rx="3" fill="{INK}"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="{PLATE}"/>' for x in (683, 759) for y in range(160, 380, 24)) +
            f'<rect x="652" y="206" width="136" height="6" rx="3" fill="{IRON}"/>'
            f'<rect x="646" y="186" width="10" height="46" rx="4" fill="{INK}"/><rect x="784" y="186" width="10" height="46" rx="4" fill="{INK}"/>')


def bench():
    return (f'<rect x="40" y="368" width="130" height="22" rx="8" fill="{CORAL}"/><rect x="40" y="384" width="130" height="6" fill="{CDEEP}"/>'
            f'<rect x="58" y="390" width="8" height="48" fill="{IRON}"/><rect x="146" y="390" width="8" height="48" fill="{IRON}"/>'
            f'<rect x="44" y="436" width="40" height="7" rx="3" fill="{IRON}"/><rect x="128" y="436" width="40" height="7" rx="3" fill="{IRON}"/>'
            f'<g transform="translate(112 468)"><rect x="-26" y="-6" width="52" height="12" rx="3" fill="{IRON}"/>'
            f'<rect x="-34" y="-20" width="12" height="40" rx="4" fill="{INK}"/><rect x="22" y="-20" width="12" height="40" rx="4" fill="{INK}"/></g>')


def hero():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" role="img">
  <title>Smiling man and woman high-fiving in a gym</title>
  <rect width="800" height="500" fill="{CHALK}"/>
  <rect width="800" height="392" fill="{MINT}"/>
  <rect width="800" height="34" fill="{MINTD}"/>
  {light(150)}{light(470)}
  <rect x="14" y="58" width="156" height="262" fill="{SKY}" stroke="{WHITE}" stroke-width="8"/>
  <path d="M66 58 L66 320 M118 58 L118 320 M14 190 L170 190" stroke="{WHITE}" stroke-width="6"/>
  <path d="M30 100 L62 80 M30 130 L86 96 M80 230 L108 212" stroke="{WHITE}" stroke-width="5" stroke-linecap="round"/>
  <rect x="600" y="70" width="190" height="290" fill="{MINTD}" stroke="{WHITE}" stroke-width="6"/>
  <path d="M640 360 L700 70 M700 360 L748 70" stroke="{SKY}" stroke-width="10"/>
  {squat_rack()}
  <rect y="388" width="800" height="112" fill="{CHALK}"/>
  <rect y="386" width="800" height="8" fill="{PLATE}"/>
  <path d="M0 440 L800 440 M0 480 L800 480" stroke="{PLATE}" stroke-width="2"/>
  {bench()}
  {dumbbell_rack()}
  <g transform="translate(262 488) scale(1.05)">{woman_body()}</g>
  <g transform="translate(540 488) scale(1.05)">{man_body()}</g>
  <path d="M398 44 L398 24 M376 54 L362 40 M420 54 L434 40 M366 74 L346 68 M430 74 L450 68" stroke="{YEL}" stroke-width="5" stroke-linecap="round"/>
  {star(398, 12, 0.9)} {heart(466, 40, 0.8)} {heart(334, 34, 0.6)} {star(500, 112, 0.7)} {star(292, 104, 0.7)}
</svg>
"""


# ---------------------------------------------------------------- members strip (three 200 x 250 portraits)
def portrait(x, bg, head, body, tilt=0):
    return (f'<g transform="translate({x} 0)"><rect width="200" height="250" fill="{bg}"/>'
            f'<circle cx="100" cy="118" r="86" fill="{WHITE}"/>'
            f'{body}'
            f'<g transform="translate(100 110) scale(0.6) translate(-200 -163)"><g transform="rotate({tilt} 200 250)">{head}</g></g>'
            f'</g>')


def shoulders(sk, skd, top, trim, arm_pose):
    neck = (f'<path d="M84 150 L84 190 C84 200 116 200 116 190 L116 150 Z" fill="{sk}" {S}/>'
            f'<path d="M85 152 C92 170 108 170 115 152 L115 166 C108 182 92 182 85 166 Z" fill="{skd}"/>')
    return neck + arm_pose + top


def arm_down(side, sk):
    """Deltoid and upper arm tapering down, side=-1 left, 1 right (centre 100)."""
    if side == -1:
        d = "M70 192 C46 188 26 200 22 226 C20 240 24 248 26 250 L68 250 C66 232 68 212 70 192 Z"
        cx = 44
    else:
        d = "M130 192 C154 188 174 200 178 226 C180 240 176 248 174 250 L132 250 C134 232 132 212 130 192 Z"
        cx = 156
    return (f'<path d="{d}" fill="{sk}" {S}/>'
            f'<path d="M{cx-14} 206 Q{cx} 198 {cx+14} 208" fill="none" stroke="{HR}" stroke-width="2.4" stroke-linecap="round"/>')


def bust3():
    sk, skl, skd = TAN
    arms = arm_down(-1, sk) + arm_down(1, sk)
    tank = (f'<path d="M66 196 L78 182 Q100 214 122 182 L134 196 C138 214 134 232 136 250 L64 250 C66 232 62 214 66 196 Z" fill="{DENIM}" {S}/>'
            f'<path d="M78 182 Q100 214 122 182" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    return shoulders(sk, skd, tank, WHITE, arms)


def bust4():
    sk, skl, skd = PEACH
    db = (f'<g transform="translate(30 168)"><rect x="-17" y="-3" width="34" height="6" rx="2" fill="{IRON}"/>'
          f'<rect x="-25" y="-14" width="10" height="28" rx="4" fill="{INK}" stroke="{OL}" stroke-width="2"/><rect x="15" y="-14" width="10" height="28" rx="4" fill="{INK}" stroke="{OL}" stroke-width="2"/></g>')
    arms = arm_down(-1, sk) + arm_down(1, sk) + limbs([(30, 250, 34, 190, 22)], sk) + f'<circle cx="31" cy="176" r="13" fill="{sk}" {S}/>' + db
    tank = (f'<path d="M66 196 L78 182 Q100 214 122 182 L134 196 C138 214 134 232 136 250 L64 250 C66 232 62 214 66 196 Z" fill="{OLIVE}" {S}/>'
            f'<path d="M78 182 Q100 214 122 182" fill="none" stroke="{OL}" stroke-width="3"/>')
    return shoulders(sk, skd, tank, WHITE, arms)


def bust5():
    sk, skl, skd = PEACH
    arms = arm_down(-1, sk) + arm_down(1, sk)
    top = (f'<path d="M72 198 L82 184 Q100 210 118 184 L128 198 C130 216 128 232 130 250 L70 250 C72 232 70 216 72 198 Z" fill="{ORANGE}" {S}/>'
           f'<path d="M82 184 Q100 210 118 184" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    return shoulders(sk, skd, top, WHITE, arms)


def members():
    h3 = head_man_quiff(HR, HRL, HR, look=0)
    h4 = head_man_quiff(YEL, WHITE, C["hair-light"], iris=SKY)
    h5 = head_woman_pony()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 250" role="img">
  <title>Three smiling gym regulars</title>
  {portrait(0, PLATE, h3, bust3(), 3)}
  {portrait(200, YEL, h4, bust4(), -3)}
  {portrait(400, MINTD, h5, bust5(), 4)}
</svg>
"""


out_dir = ROOT / "public" / "img"
out_dir.mkdir(exist_ok=True)
(out_dir / "hero-gym.svg").write_text(hero())
(out_dir / "members-strip.svg").write_text(members())
print("wrote public/img/hero-gym.svg, public/img/members-strip.svg")
