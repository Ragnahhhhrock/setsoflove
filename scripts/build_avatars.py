#!/usr/bin/env python3
"""Build the two landing-page character avatars into public/img/ (DESIGN_GUIDE.md section 12).

Colours come from tokens/tokens.json: the 11 brand colours plus the illustration tones.
Original fairytale-animation style characters: a square-jawed, heroic young man and a slender,
large-eyed young woman. Athletic build, flat colour with soft outlines.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "tokens" / "tokens.json").read_text())
C = {k: v["hex"] for k, v in T["colour"].items()}
C.update({k: v["hex"] for k, v in T["illustration"].items()})
INK, WHITE, YEL, HEART, CORAL, CDEEP, PLATE, IRON = (C[k] for k in ("ink", "white", "yellow", "heart", "coral", "coral-deep", "plate", "iron"))
SK, SKL, SKD, HR, HRL = C["skin"], C["skin-light"], C["skin-deep"], C["hair"], C["hair-light"]

HEART_D = "M0 14 C-18 2 -16 -14 -6 -14 C-2 -14 0 -11 0 -9 C0 -11 2 -14 6 -14 C16 -14 18 2 0 14 Z"
STAR_D = "M0 -12 Q2 -2 12 0 Q2 2 0 12 Q-2 2 -12 0 Q-2 -2 0 -12 Z"


def heart(x, y, s, fill=HEART):
    return f'<path d="{HEART_D}" transform="translate({x} {y}) scale({s})" fill="{fill}"/>'


def star(x, y, s):
    return f'<path d="{STAR_D}" transform="translate({x} {y}) scale({s})" fill="{WHITE}"/>'


def dumbbell(x, y, rot):
    return (f'<g transform="translate({x} {y}) rotate({rot})">'
            f'<rect x="-22" y="-3.5" width="44" height="7" rx="3" fill="{IRON}"/>'
            f'<rect x="-32" y="-13" width="11" height="26" rx="4" fill="{INK}"/>'
            f'<rect x="-24" y="-9" width="7" height="18" rx="3" fill="{IRON}"/>'
            f'<rect x="21" y="-13" width="11" height="26" rx="4" fill="{INK}"/>'
            f'<rect x="17" y="-9" width="7" height="18" rx="3" fill="{IRON}"/></g>')


def phone(cx, cy, rot):
    return f"""<g transform="rotate({rot} {cx} {cy})">
    <rect x="{cx-35}" y="{cy-60}" width="70" height="120" rx="13" fill="{INK}"/>
    <rect x="{cx-29}" y="{cy-52}" width="58" height="102" rx="8" fill="{WHITE}"/>
    <rect x="{cx-9}" y="{cy-50}" width="18" height="5" rx="2.5" fill="{INK}"/>
    <rect x="{cx-23}" y="{cy-38}" width="46" height="34" rx="6" fill="{PLATE}"/>
    {heart(cx, cy-21, 1.0)}
    <rect x="{cx-23}" y="{cy+2}" width="30" height="6" rx="3" fill="{INK}"/>
    <rect x="{cx-23}" y="{cy+13}" width="42" height="5" rx="2.5" fill="{PLATE}"/>
    <rect x="{cx-23}" y="{cy+23}" width="36" height="5" rx="2.5" fill="{PLATE}"/>
    <rect x="{cx-23}" y="{cy+33}" width="46" height="9" rx="4.5" fill="{CORAL}"/>
  </g>"""


OUT = f'stroke="{SKD}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"'


def eye(cx, cy, rx, ry, ir, wing=0, lashes=False, side=1):
    o = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{WHITE}"/>'
         f'<circle cx="{cx}" cy="{cy+1}" r="{ir}" fill="{HR}"/>'
         f'<circle cx="{cx}" cy="{cy+1}" r="{ir*0.5}" fill="{INK}"/>'
         f'<circle cx="{cx+ir*0.4}" cy="{cy-ir*0.35}" r="{ir*0.32}" fill="{WHITE}"/>'
         f'<circle cx="{cx-ir*0.35}" cy="{cy+ir*0.45}" r="{ir*0.16}" fill="{WHITE}"/>'
         f'<path d="M{cx-rx-1} {cy+1} Q{cx} {cy-ry-5} {cx+rx+1} {cy+1}" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="round"/>')
    if lashes:
        ox = cx + (rx + 1) * side
        o += (f'<path d="M{ox} {cy+1} Q{ox+6*side} {cy-2} {ox+10*side} {cy-8} Q{ox+4*side} {cy-5} {ox-2*side} {cy-6} Z" fill="{INK}"/>'
              f'<path d="M{cx-rx} {cy+ry-1} Q{cx} {cy+ry+4} {cx+rx} {cy+ry-1}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>'
              f'<path d="M{cx-rx-2} {cy-ry-6} Q{cx} {cy-ry-12} {cx+rx+2} {cy-ry-6}" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>')
    return o


def mouth_smile(cx, w, depth, lips):
    l, r = cx - w, cx + w
    return f"""
  <path d="M{l} 199 Q{cx} 206 {r} 199 Q{r-4} {199+depth} {cx} {199+depth} Q{l+4} {199+depth} {l} 199 Z" fill="{INK}" stroke="{lips}" stroke-width="3.2" stroke-linejoin="round"/>
  <path d="M{l+3} 201 Q{cx} 207 {r-3} 201 Q{r-6} {201+depth*0.38} {cx} {201+depth*0.4} Q{l+6} {201+depth*0.38} {l+3} 201 Z" fill="{WHITE}"/>
  <path d="M{cx-w*0.45} {197+depth*0.92} Q{cx} {197+depth*0.5} {cx+w*0.45} {197+depth*0.92} Q{cx} {197+depth*1.05} {cx-w*0.45} {197+depth*0.92} Z" fill="{CORAL}"/>
  <path d="M{l-4} 193 Q{l-8} 201 {l-2} 207 M{r+4} 193 Q{r+8} 201 {r+2} 207" fill="none" stroke="{SKD}" stroke-width="2.4" stroke-linecap="round"/>"""


def earbud(cx, cy, side):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="5.5" ry="7.5" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M{cx+side} {cy+5} L{cx+side*1.5} {cy+24}" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>')


def hand_on_hip(cx, cy, flip=1):
    return (f'<g transform="translate({cx} {cy}) scale({flip} 1)">'
            f'<path d="M-4 -14 C10 -20 26 -12 26 0 C26 12 12 18 -4 14 Z" fill="{SK}" {OUT}/>'
            f'<path d="M-22 -10 L-4 -12 M-24 -1 L-4 -1 M-22 8 L-4 8" fill="none" stroke="{SK}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M-24 -1 L-6 -1 M-22 8 L-6 8" fill="none" stroke="{SKD}" stroke-width="1.8"/></g>')


def phone_hand(cx, cy, rot, side):
    """Phone with the hand gripping it. side=-1: thumb on the right of the phone, fingers on the left."""
    fx = cx - 36 * side * -1 if False else cx + (-36 if side == -1 else 36)
    tx = cx + (36 if side == -1 else -36)
    return (phone(cx, cy, rot) +
            f'<g transform="rotate({rot} {cx} {cy})">'
            + "".join(f'<ellipse cx="{fx}" cy="{cy+dy}" rx="9" ry="11" fill="{SK}" {OUT}/>' for dy in (-18, 2, 22)) +
            f'<circle cx="{cx}" cy="{cy+52}" r="22" fill="{SK}" {OUT}/>'
            f'<ellipse cx="{tx}" cy="{cy+30}" rx="10" ry="19" fill="{SK}" {OUT}/></g>')


def man():
    face = ("M146 132 C146 98 170 86 200 86 C230 86 254 98 254 132 L254 176 Q252 200 236 218 L222 236 "
            "Q200 244 178 236 L164 218 Q148 200 146 176 Z")
    hair = ("M142 134 C130 82 158 48 204 44 C252 42 280 80 262 134 C258 120 250 112 238 108 "
            "C218 98 186 98 166 108 C152 114 146 124 142 134 Z")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" role="img">
  <title>Smiling prince-style man holding a phone</title>
  <rect width="400" height="500" fill="{YEL}"/>
  <circle cx="200" cy="170" r="152" fill="{WHITE}"/>
  {dumbbell(344, 62, 24)}
  {heart(52, 86, 0.8)} {heart(354, 160, 0.55)}
  {star(318, 112, 0.9)} {star(60, 190, 0.6)}
  <g transform="translate(28 64) scale(0.86)">
  <!-- torso, neck, traps -->
  <path d="M96 296 C120 276 160 268 200 268 C240 268 280 276 304 296 L324 372 C318 420 310 460 306 560 L94 560 C90 460 82 420 76 372 Z" fill="{SK}" {OUT}/>
  <path d="M168 214 L168 266 C168 282 232 282 232 266 L232 214 Z" fill="{SK}"/>
  <path d="M168 214 C180 252 220 252 232 214 L232 240 C220 260 180 260 168 240 Z" fill="{SKD}"/>
  <path d="M166 252 C148 268 112 274 84 292 L316 292 C288 274 252 268 234 252 C220 264 180 264 166 252 Z" fill="{SK}"/>
  <path d="M166 256 C146 272 118 280 94 290 M234 256 C254 272 282 280 306 290 M156 278 C174 270 188 272 198 278 M244 278 C226 270 212 272 202 278" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>
  <ellipse cx="78" cy="322" rx="38" ry="44" fill="{SK}" {OUT}/>
  <path d="M66 304 C78 300 92 304 100 314" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>

  <!-- raised arm (left) -->
  <path d="M44 334 C38 372 44 410 56 440 L98 440 C102 406 102 366 112 334 Z" fill="{SK}" {OUT}/>
  <ellipse cx="86" cy="388" rx="24" ry="30" fill="{SK}" {OUT}/>
  <path d="M72 372 Q86 360 100 372" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>
  <path d="M78 410 Q88 418 98 410" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <path d="M74 442 L90 352" fill="none" stroke="{SKD}" stroke-width="42" stroke-linecap="round"/>
  <path d="M74 442 L90 352" fill="none" stroke="{SK}" stroke-width="37" stroke-linecap="round"/>
  <path d="M82 420 L88 380" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>

  <!-- tank top -->
  <path d="M120 280 L146 262 Q200 338 254 262 L280 280 C276 330 290 362 300 402 L318 560 L82 560 L100 402 C110 362 124 330 120 280 Z" fill="{CORAL}"/>
  <path d="M120 280 L146 262 Q200 338 254 262 L280 280 M120 280 C124 330 110 362 100 402 M280 280 C276 330 290 362 300 402" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M148 348 Q172 378 198 366 M252 348 Q228 378 202 366 M150 470 Q160 500 156 540 M250 470 Q240 500 244 540" fill="none" stroke="{CDEEP}" stroke-width="4" stroke-linecap="round"/>
  {heart(200, 412, 1.5, WHITE)}

  <!-- hand-on-hip arm (right) -->
  <path d="M332 338 L376 412" fill="none" stroke="{SKD}" stroke-width="48" stroke-linecap="round"/>
  <path d="M332 338 L376 412" fill="none" stroke="{SK}" stroke-width="43" stroke-linecap="round"/>
  <path d="M376 412 L326 462" fill="none" stroke="{SKD}" stroke-width="38" stroke-linecap="round"/>
  <path d="M376 412 L326 462" fill="none" stroke="{SK}" stroke-width="33" stroke-linecap="round"/>
  <path d="M338 352 Q352 372 356 392 M356 420 Q344 436 338 448" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <path d="M340 342 Q356 340 366 358" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>
  {hand_on_hip(318, 466, -1)}

  <!-- head -->
  <circle cx="146" cy="164" r="12" fill="{SK}" {OUT}/><circle cx="254" cy="164" r="12" fill="{SK}" {OUT}/>
  <ellipse cx="146" cy="164" rx="4.5" ry="7" fill="{SKD}"/><ellipse cx="254" cy="164" rx="4.5" ry="7" fill="{SKD}"/>
  {earbud(145, 165, -1)}
  <path d="{face}" fill="{SK}" {OUT}/>
  <path d="M250 134 L254 176 Q252 200 236 218 L222 236 Q238 228 244 212 Q252 190 250 134 Z" fill="{SKD}"/>
  <path d="M200 232 L200 240" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="196" cy="108" rx="26" ry="6.5" fill="{SKL}"/>
  <path d="M150 124 L150 158 Q148 150 146 140 Z M250 124 L250 158 Q252 150 254 140 Z" fill="{HR}"/>
  <path d="{hair}" fill="{HR}"/>
  <path d="M164 100 Q196 62 246 82 M182 78 Q210 58 240 68 M154 116 Q162 94 180 84 " fill="none" stroke="{HRL}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M160 140 Q176 118 197 130 L197 137 Q178 130 162 147 Z M240 140 Q224 118 203 130 L203 137 Q222 130 238 147 Z" fill="{HR}"/>
  {eye(178, 154, 11, 9, 7)} {eye(222, 154, 11, 9, 7)}
  <path d="M201 156 L200 180 M193 184 Q200 190 207 184" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M206 160 Q211 176 208 183" fill="none" stroke="{SKD}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="162" cy="186" r="8" fill="{SKD}"/><circle cx="238" cy="186" r="8" fill="{SKD}"/>
  {mouth_smile(200, 27, 24, SKD)}
  <path d="M190 232 Q200 236 210 232" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M246 112 Q252 122 246 128 Q240 122 246 112 Z" fill="{WHITE}" stroke="{SKD}" stroke-width="1.5"/>

  <!-- phone and hand -->
  {phone_hand(92, 296, -8, -1)}
  </g>
</svg>
"""


def woman():
    face = ("M150 130 C150 98 172 86 200 86 C228 86 250 98 250 130 C250 170 240 206 222 226 "
            "Q200 246 178 226 C160 206 150 170 150 130 Z")
    back = ("M150 112 C108 150 98 262 118 336 C128 366 152 356 160 332 L164 298 L236 298 L242 332 "
            "C250 356 274 366 284 336 C304 262 292 150 250 112 Z")
    front = ("M148 134 C138 82 166 50 206 48 C246 46 268 84 254 138 C250 114 240 98 224 90 "
             "C206 112 176 126 148 134 Z")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" role="img">
  <title>Smiling princess-style woman holding a phone</title>
  <rect width="400" height="500" fill="{PLATE}"/>
  <circle cx="200" cy="170" r="152" fill="{WHITE}"/>
  {dumbbell(60, 62, -24)}
  {heart(350, 92, 0.8)} {heart(46, 176, 0.55)}
  {star(82, 120, 0.9)} {star(336, 190, 0.6)}
  <g transform="translate(28 64) scale(0.86)">
  <!-- hair behind -->
  <path d="{back}" fill="{HRL}" {OUT}/>
  <path d="M130 200 C120 250 126 300 140 336 M270 200 C280 250 274 300 260 336 M146 150 C134 200 134 250 146 300 M254 150 C266 200 266 250 254 300" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>

  <!-- torso, neck, traps -->
  <path d="M118 304 C138 290 168 284 200 284 C232 284 262 290 282 304 L292 372 C290 420 286 460 286 560 L114 560 C114 460 110 420 108 372 Z" fill="{SK}" {OUT}/>
  <path d="M180 222 L180 278 C180 290 220 290 220 278 L220 222 Z" fill="{SK}"/>
  <path d="M180 222 C186 250 214 250 220 222 L220 240 C214 258 186 258 180 240 Z" fill="{SKD}"/>
  <path d="M178 266 C164 278 138 284 116 302 L284 302 C262 284 236 278 222 266 C214 274 186 274 178 266 Z" fill="{SK}"/>
  <path d="M178 270 C160 280 136 288 120 300 M222 270 C240 280 264 288 280 300 M164 286 C178 278 190 280 198 285 M236 286 C222 278 210 280 202 285" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="106" cy="326" rx="26" ry="29" fill="{SK}" {OUT}/>
  <ellipse cx="294" cy="326" rx="26" ry="29" fill="{SK}" {OUT}/>
  <path d="M98 308 C108 304 118 308 124 316 M302 308 C292 304 282 308 276 316" fill="none" stroke="{SKL}" stroke-width="3.5" stroke-linecap="round"/>

  <!-- raised arm (right) -->
  <path d="M274 340 C280 374 286 410 296 440 L338 440 C342 408 336 372 324 340 Z" fill="{SK}" {OUT}/>
  <path d="M312 440 L304 356" fill="none" stroke="{SKD}" stroke-width="36" stroke-linecap="round"/>
  <path d="M312 440 L304 356" fill="none" stroke="{SK}" stroke-width="31" stroke-linecap="round"/>
  <path d="M300 372 Q310 366 318 374" fill="none" stroke="{SKL}" stroke-width="3" stroke-linecap="round"/>

  <!-- sports top -->
  <path d="M134 296 L158 280 Q200 340 242 280 L266 296 C264 332 272 362 276 402 L282 560 L118 560 L124 402 C128 362 136 332 134 296 Z" fill="{YEL}"/>
  <path d="M134 296 L158 280 Q200 340 242 280 L266 296 M134 296 C136 332 128 362 124 402 M266 296 C264 332 272 362 276 402" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M162 350 Q180 370 198 362 M238 350 Q220 370 202 362" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  {heart(200, 412, 1.3, CORAL)}

  <!-- hand-on-hip arm (left) -->
  <path d="M98 344 L62 410" fill="none" stroke="{SKD}" stroke-width="40" stroke-linecap="round"/>
  <path d="M98 344 L62 410" fill="none" stroke="{SK}" stroke-width="35" stroke-linecap="round"/>
  <path d="M62 410 L112 462" fill="none" stroke="{SKD}" stroke-width="34" stroke-linecap="round"/>
  <path d="M62 410 L112 462" fill="none" stroke="{SK}" stroke-width="29" stroke-linecap="round"/>
  <path d="M92 356 Q80 374 78 394" fill="none" stroke="{SKL}" stroke-width="3" stroke-linecap="round"/>
  {hand_on_hip(122, 468, 1)}

  <!-- head (tilted) -->
  <g transform="rotate(-5 200 250)">
  <circle cx="150" cy="166" r="10" fill="{SK}" {OUT}/><ellipse cx="150" cy="166" rx="4" ry="6" fill="{SKD}"/>
  {earbud(149, 167, -1)}
  <path d="{face}" fill="{SK}" {OUT}/>
  <path d="M246 134 C246 170 238 204 222 224 Q236 214 244 194 Q250 164 246 134 Z" fill="{SKD}"/>
  <ellipse cx="202" cy="110" rx="22" ry="6" fill="{SKL}"/>
  <path d="M250 112 C268 148 268 190 252 228 C262 200 258 150 244 118 Z" fill="{HRL}" {OUT}/>
  <path d="{front}" fill="{HRL}"/>
  <path d="M160 96 Q196 62 246 80 M172 78 Q204 56 238 64 M150 124 Q158 100 178 88 M214 94 Q198 116 168 128" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M150 104 Q200 76 252 108" fill="none" stroke="{YEL}" stroke-width="8" stroke-linecap="round"/>
  {heart(200, 86, 0.55)}
  <path d="M164 138 Q178 124 194 134 M206 134 Q222 124 236 138" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  {eye(178, 154, 12, 11, 8.5, lashes=True, side=-1)} {eye(222, 154, 12, 11, 8.5, lashes=True, side=1)}
  <path d="M199 172 Q195 180 200 182 Q205 182 205 178" fill="none" stroke="{SKD}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="162" cy="186" r="8" fill="{SKD}"/><circle cx="238" cy="186" r="8" fill="{SKD}"/>
  {mouth_smile(200, 21, 19, CDEEP)}
  </g>

  <!-- phone and hand -->
  {phone_hand(308, 300, 8, 1)}
  </g>
</svg>
"""


out = ROOT / "public" / "img"
out.mkdir(exist_ok=True)
(out / "avatar-man.svg").write_text(man())
(out / "avatar-woman.svg").write_text(woman())
print("wrote public/img/avatar-man.svg, public/img/avatar-woman.svg")
