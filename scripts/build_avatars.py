#!/usr/bin/env python3
"""Build the two landing-page character avatars into public/img/ (DESIGN_GUIDE.md section 12).

Colours come from tokens/tokens.json: the 11 brand colours plus the illustration tones.
Proportions follow a well-conditioned athletic build: shoulders about 1.6x the waist,
capped delts, trapezius slope, lat flare and a trim midsection.
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


def eye(cx, cy, lashes=False, side=1):
    out = (f'<ellipse cx="{cx}" cy="{cy}" rx="9" ry="8.5" fill="{WHITE}"/>'
           f'<circle cx="{cx}" cy="{cy+0.5}" r="5.6" fill="{HR}"/>'
           f'<circle cx="{cx}" cy="{cy+0.5}" r="2.8" fill="{INK}"/>'
           f'<circle cx="{cx+2}" cy="{cy-2}" r="1.8" fill="{WHITE}"/>'
           f'<path d="M{cx-10} {cy-1} Q{cx} {cy-11} {cx+10} {cy-1}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
           f'<path d="M{cx-9} {cy+8} Q{cx} {cy+14} {cx+9} {cy+8}" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>')
    if lashes:
        ox = cx + 10 * side
        out += (f'<path d="M{ox} {cy-2} L{ox+7*side} {cy-7} M{ox-1*side} {cy-5} L{ox+4*side} {cy-12}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>')
    return out


def mouth(lips=SKD):
    return f"""
  <path d="M172 192 Q200 199 228 192 Q224 224 200 224 Q176 224 172 192 Z" fill="{INK}" stroke="{lips}" stroke-width="3.5" stroke-linejoin="round"/>
  <path d="M175 194 Q200 200 225 194 Q222 206 200 207 Q178 206 175 194 Z" fill="{WHITE}"/>
  <path d="M187 220 Q200 210 213 220 Q200 227 187 220 Z" fill="{CORAL}"/>
  <path d="M168 188 Q164 195 169 201 M232 188 Q236 195 231 201" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>"""


def earbud(cx, cy, side):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="5.5" ry="7.5" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M{cx+side} {cy+5} L{cx+side*1.5} {cy+24}" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>')


def hand_fist(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="{SK}"/>'
            f'<path d="M{cx-14} {cy-4} L{cx+14} {cy-4} M{cx-14} {cy+5} L{cx+14} {cy+5} M{cx-12} {cy+14} L{cx+12} {cy+14}" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<ellipse cx="{cx-18}" cy="{cy+9}" rx="7" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>')


def man():
    face_shape = "M142 140 C142 100 168 90 200 90 C232 90 258 100 258 140 C258 190 240 224 200 232 C160 224 142 190 142 140 Z"
    hair_top = ("M140 138 C128 84 160 54 204 52 C246 50 274 86 260 138 C254 118 240 106 222 100 "
                "C204 108 178 108 160 120 C152 124 144 130 140 138 Z")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" role="img">
  <title>Smiling man holding a phone</title>
  <rect width="400" height="500" fill="{YEL}"/>
  <circle cx="200" cy="170" r="152" fill="{WHITE}"/>
  {dumbbell(58, 70, -24)}
  {heart(338, 62, 0.8)} {heart(40, 150, 0.55)}
  {star(310, 120, 0.9)} {star(96, 120, 0.6)}

  <g transform="translate(28 64) scale(0.86)">
  <!-- torso, neck, traps -->
  <path d="M96 296 C120 276 160 268 200 268 C240 268 280 276 304 296 L324 372 C318 420 310 460 306 560 L94 560 C90 460 82 420 76 372 Z" fill="{SK}"/>
  <path d="M170 212 L170 262 C170 278 230 278 230 262 L230 212 Z" fill="{SK}"/>
  <path d="M170 212 C180 242 220 242 230 212 L230 234 C220 254 180 254 170 234 Z" fill="{SKD}"/>
  <path d="M168 250 C150 268 112 274 84 292 L316 292 C288 274 250 268 232 250 C220 262 180 262 168 250 Z" fill="{SK}"/>
  <path d="M168 254 C146 272 118 280 94 290 M232 254 C254 272 282 280 306 290" fill="none" stroke="{SKD}" stroke-width="4" stroke-linecap="round"/>
  <path d="M156 276 C174 268 188 270 198 276 M244 276 C226 268 212 270 202 276" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>

  <!-- delts -->
  <ellipse cx="78" cy="322" rx="38" ry="44" fill="{SK}"/>
  <ellipse cx="322" cy="322" rx="38" ry="44" fill="{SK}"/>
  <path d="M62 298 C74 318 74 342 66 360 M338 298 C326 318 326 342 334 360" fill="none" stroke="{SKD}" stroke-width="4" stroke-linecap="round"/>
  <path d="M66 304 C78 300 92 304 100 314 M334 304 C322 300 308 304 300 314" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>

  <!-- phone arm (left) -->
  <path d="M44 334 C38 372 44 406 52 434 L92 434 C98 404 100 366 112 334 Z" fill="{SK}"/>
  <path d="M86 354 C90 382 88 406 80 426" fill="none" stroke="{SKD}" stroke-width="4" stroke-linecap="round"/>
  <path d="M54 352 C60 366 62 384 58 402" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>
  <path d="M70 432 L128 382" fill="none" stroke="{SK}" stroke-width="40" stroke-linecap="round"/>
  <path d="M66 424 L112 380" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <path d="M104 396 L120 382" stroke="{INK}" stroke-width="16"/>
  <circle cx="111" cy="389" r="5.5" fill="{WHITE}"/>

  <!-- flexing arm (right) -->
  <path d="M326 338 L394 358" fill="none" stroke="{SK}" stroke-width="44" stroke-linecap="round"/>
  <path d="M394 358 L386 280" fill="none" stroke="{SK}" stroke-width="34" stroke-linecap="round"/>
  <ellipse cx="362" cy="338" rx="32" ry="21" transform="rotate(-8 362 338)" fill="{SK}"/>
  <path d="M338 330 Q362 308 388 330" fill="none" stroke="{SKL}" stroke-width="5" stroke-linecap="round"/>
  <path d="M340 358 Q364 372 388 362" fill="none" stroke="{SKD}" stroke-width="4" stroke-linecap="round"/>
  <path d="M372 346 C364 352 360 360 362 368 M392 326 C388 312 388 300 390 290" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M378 322 L406 330" stroke="{YEL}" stroke-width="10"/>
  {hand_fist(384, 262)}

  <!-- tank top -->
  <path d="M120 280 L146 262 Q200 338 254 262 L280 280 C276 330 290 362 300 402 L318 560 L82 560 L100 402 C110 362 124 330 120 280 Z" fill="{CORAL}"/>
  <path d="M120 280 L146 262 Q200 338 254 262 L280 280 M120 280 C124 330 110 362 100 402 M280 280 C276 330 290 362 300 402" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M150 348 Q172 376 198 364 M250 348 Q228 376 202 364 M150 470 Q160 500 156 540 M250 470 Q240 500 244 540" fill="none" stroke="{CDEEP}" stroke-width="4" stroke-linecap="round"/>
  {heart(200, 410, 1.5, WHITE)}

  <!-- head -->
  <circle cx="143" cy="168" r="12" fill="{SK}"/><circle cx="257" cy="168" r="12" fill="{SK}"/>
  <ellipse cx="143" cy="168" rx="5" ry="7" fill="{SKD}"/><ellipse cx="257" cy="168" rx="5" ry="7" fill="{SKD}"/>
  {earbud(142, 168, -1)}
  <path d="{face_shape}" fill="{SK}"/>
  <ellipse cx="200" cy="112" rx="26" ry="7" fill="{SKL}"/>
  <path d="{hair_top}" fill="{HR}"/>
  <path d="M166 98 Q198 66 242 84 M182 80 Q208 62 238 72 M150 112 Q160 92 176 84" fill="none" stroke="{HRL}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M164 140 Q180 128 196 136 M204 136 Q220 128 236 140" fill="none" stroke="{HR}" stroke-width="7" stroke-linecap="round"/>
  {eye(180, 154)} {eye(220, 154)}
  <path d="M200 156 C198 170 192 178 192 182 Q200 189 208 182" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="160" cy="184" r="9" fill="{SKD}"/><circle cx="240" cy="184" r="9" fill="{SKD}"/>
  {mouth()}
  <path d="M248 116 Q254 126 248 132 Q242 126 248 116 Z" fill="{WHITE}" stroke="{SKD}" stroke-width="1.5"/>

  <!-- phone and hand -->
  {phone(158, 346, -12)}
  <ellipse cx="119" cy="324" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <ellipse cx="116" cy="344" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <ellipse cx="115" cy="364" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <circle cx="140" cy="394" r="22" fill="{SK}"/>
  <ellipse cx="190" cy="372" rx="10" ry="19" transform="rotate(-14 190 372)" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  </g>
</svg>
"""


def woman():
    face_shape = "M146 142 C146 102 170 92 200 92 C230 92 254 102 254 142 C254 192 232 226 200 234 C168 226 146 192 146 142 Z"
    cap = ("M148 152 C134 90 164 58 204 56 C246 54 270 88 254 144 C246 122 232 108 214 102 "
           "C196 124 168 138 148 152 Z")
    ponytail = ("M178 72 C132 38 82 58 72 112 C68 142 86 168 108 176 C100 148 112 118 142 100 "
                "C154 92 166 84 178 72 Z")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500" role="img">
  <title>Smiling woman holding a phone</title>
  <rect width="400" height="500" fill="{PLATE}"/>
  <circle cx="200" cy="170" r="152" fill="{WHITE}"/>
  {dumbbell(342, 66, 24)}
  {heart(344, 140, 0.8)} {heart(46, 214, 0.55)}
  {star(70, 300, 0.9)} {star(318, 214, 0.6)}

  <g transform="translate(28 64) scale(0.86)">
  <!-- ponytail (behind) -->
  <path d="{ponytail}" fill="{HRL}"/>
  <path d="M168 78 C128 52 90 70 82 116 M160 92 C124 78 100 100 100 132 M150 100 C122 100 110 126 114 156" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>

  <!-- torso, neck, traps -->
  <path d="M110 300 C132 284 164 276 200 276 C236 276 268 284 290 300 L306 372 C302 420 298 460 298 560 L102 560 C102 460 98 420 94 372 Z" fill="{SK}"/>
  <path d="M174 214 L174 268 C174 282 226 282 226 268 L226 214 Z" fill="{SK}"/>
  <path d="M174 214 C182 242 218 242 226 214 L226 236 C218 254 182 254 174 236 Z" fill="{SKD}"/>
  <path d="M172 258 C154 272 124 278 98 296 L302 296 C276 278 246 272 228 258 C218 268 182 268 172 258 Z" fill="{SK}"/>
  <path d="M172 262 C152 276 126 284 106 294 M228 262 C248 276 274 284 294 294" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M160 282 C176 274 188 276 198 281 M240 282 C224 274 212 276 202 281" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>

  <!-- delts -->
  <ellipse cx="90" cy="326" rx="32" ry="40" fill="{SK}"/>
  <ellipse cx="310" cy="326" rx="32" ry="40" fill="{SK}"/>
  <path d="M68 300 C80 320 80 346 72 364 M332 300 C320 320 320 346 328 364" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M74 304 C86 300 98 304 106 314 M326 304 C314 300 302 304 294 314" fill="none" stroke="{SKL}" stroke-width="4" stroke-linecap="round"/>

  <!-- waving arm (left) -->
  <path d="M60 338 C56 368 60 398 66 420 L98 420 C102 396 104 364 112 338 Z" fill="{SK}"/>
  <path d="M90 352 C94 378 92 400 86 416" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M72 424 L44 326" fill="none" stroke="{SK}" stroke-width="32" stroke-linecap="round"/>
  <path d="M58 392 Q54 360 50 336" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round"/>
  <path d="M46 342 L74 332" stroke="{YEL}" stroke-width="10"/>
  <circle cx="38" cy="296" r="22" fill="{SK}"/>
  <path d="M22 282 L16 252 M34 276 L30 244 M46 276 L48 246 M58 284 L66 256" fill="none" stroke="{SK}" stroke-width="12" stroke-linecap="round"/>
  <ellipse cx="62" cy="304" rx="7" ry="13" transform="rotate(-40 62 304)" fill="{SK}"/>
  <path d="M26 300 L50 300" fill="none" stroke="{SKD}" stroke-width="2.5" stroke-linecap="round"/>

  <!-- phone arm (right) -->
  <path d="M340 338 C344 368 340 398 334 420 L302 420 C298 396 296 364 288 338 Z" fill="{SK}"/>
  <path d="M310 352 C306 378 308 400 314 416" fill="none" stroke="{SKD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M330 426 L276 382" fill="none" stroke="{SK}" stroke-width="36" stroke-linecap="round"/>
  <path d="M290 392 L274 380" stroke="{YEL}" stroke-width="12"/>
  <circle cx="283" cy="386" r="5" fill="{INK}"/>

  <!-- sports top -->
  <path d="M130 288 L154 272 Q200 334 246 272 L270 288 C268 330 278 362 284 402 L294 560 L106 560 L116 402 C122 362 132 330 130 288 Z" fill="{INK}"/>
  <path d="M130 288 L154 272 Q200 334 246 272 L270 288" fill="none" stroke="{YEL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M130 288 C132 330 122 362 116 402 M270 288 C268 330 278 362 284 402" fill="none" stroke="{YEL}" stroke-width="4" stroke-linecap="round"/>
  <path d="M158 344 Q178 366 198 358 M242 344 Q222 366 202 358" fill="none" stroke="{IRON}" stroke-width="4" stroke-linecap="round"/>
  {heart(200, 408, 1.4, YEL)}

  <!-- head -->
  <circle cx="148" cy="168" r="11" fill="{SK}"/><circle cx="252" cy="168" r="11" fill="{SK}"/>
  <ellipse cx="148" cy="168" rx="4.5" ry="6.5" fill="{SKD}"/><ellipse cx="252" cy="168" rx="4.5" ry="6.5" fill="{SKD}"/>
  {earbud(148, 168, -1)}
  <path d="{face_shape}" fill="{SK}"/>
  <ellipse cx="206" cy="114" rx="24" ry="6.5" fill="{SKL}"/>
  <path d="{cap}" fill="{HRL}"/>
  <path d="M164 92 Q198 66 242 82 M176 78 Q206 62 236 70" fill="none" stroke="{HR}" stroke-width="3.5" stroke-linecap="round"/>
  <ellipse cx="172" cy="76" rx="9" ry="15" transform="rotate(-52 172 76)" fill="{YEL}" stroke="{SKD}" stroke-width="1.5"/>
  <path d="M166 140 Q180 130 196 138 M204 138 Q220 130 234 140" fill="none" stroke="{HR}" stroke-width="4.5" stroke-linecap="round"/>
  {eye(181, 154, True, -1)} {eye(219, 154, True, 1)}
  <path d="M200 158 C198 170 193 177 193 181 Q200 187 207 181" fill="none" stroke="{SKD}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="163" cy="184" r="9" fill="{SKD}"/><circle cx="237" cy="184" r="9" fill="{SKD}"/>
  {mouth(CDEEP)}

  <!-- phone and hand -->
  {phone(244, 346, 12)}
  <ellipse cx="281" cy="324" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <ellipse cx="284" cy="344" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <ellipse cx="285" cy="364" rx="9" ry="11" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  <circle cx="260" cy="394" r="21" fill="{SK}"/>
  <ellipse cx="210" cy="372" rx="10" ry="19" transform="rotate(14 210 372)" fill="{SK}" stroke="{SKD}" stroke-width="2"/>
  </g>
</svg>
"""


out = ROOT / "public" / "img"
out.mkdir(exist_ok=True)
(out / "avatar-man.svg").write_text(man())
(out / "avatar-woman.svg").write_text(woman())
print("wrote public/img/avatar-man.svg, public/img/avatar-woman.svg")
