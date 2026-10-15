#!/usr/bin/env python3
"""Generate the original chibi Ramakien character SVGs for the website.

All art is drawn here from simple shapes (no external or official game art).
Run:  python3 tools/ramakien_chars.py   -> website/assets/img/chars/*.svg
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "website" / "assets" / "img" / "chars"
INK = "#2b1b33"


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ra, rb))


def light(c: str, t: float) -> str:
    return mix(c, "#ffffff", t)


def dark(c: str, t: float) -> str:
    return mix(c, "#000000", t)


@dataclass
class Char:
    slug: str
    name: str
    side: str          # "rama" | "lanka"
    role: str
    blurb: str
    skin: str
    face: str          # deva | female | monkey | yaksha
    crown: str         # chada | monkey | yaksha | tossakan | flame | female
    outfit: str
    weapon: str = ""   # bow | trident | club | sword | spear | lotus | ""
    tail: str = ""     # monkey | fish | ""
    muzzle: str = ""
    eyes: str = "normal"   # normal | wink | happy | sleepy | side | angry
    mouth: str = "smile"   # smile | grin | smirk | tongue | o | laugh
    gag: str = ""          # zzz | sweat | sparkle | point | smoke | heart


CHARS: list[Char] = [
    Char("rama", "พระราม", "rama", "อวตารของพระนารายณ์",
         "เจ้าชายแห่งอยุธยา ยิงศรทีไรแม่นทุกดอก แต่ยิ้มมุมปากหล่อ ๆ ก่อนยิงทุกครั้ง",
         "#3f9a6a", "deva", "chada", "#c8343f", "bow", eyes="normal", mouth="smirk", gag="sparkle"),
    Char("lak", "พระลักษมณ์", "rama", "อนุชาผู้ซื่อสัตย์",
         "น้องชายพระรามที่ตามพี่ไปทุกที่ ยิ้มกว้างตลอดเวลา แม้จะโดนศรนาคบาศก็ยังยิ้ม",
         "#e9b949", "deva", "chada", "#2f6fb8", "bow", eyes="happy", mouth="grin"),
    Char("sida", "นางสีดา", "rama", "ชายาของพระราม",
         "หญิงงามใจมั่นคง ถูกลักพาไปลงกา แต่ไม่เคยหวั่น ขยิบตาให้ทศกัณฐ์แบบว่า ฝันไปเถอะ",
         "#f6dcc0", "female", "female", "#2aa58a", "lotus", eyes="wink", mouth="smile", gag="heart"),
    Char("hanuman", "หนุมาน", "rama", "ทหารเอกของพระราม",
         "วานรเผือกตัวแสบ หาวเป็นดาวเป็นเดือน เผาลงกาเล่นแล้วแลบลิ้นใส่ยักษ์ทั้งเมือง",
         "#f4f4fa", "monkey", "monkey", "#d33a45", "trident", "monkey", "#fde3ea", eyes="wink", mouth="tongue"),
    Char("sukrip", "สุครีพ", "rama", "เจ้าเมืองขีดขิน",
         "พญาวานรกายแดง หัวเราะเสียงดังที่สุดในกองทัพ ใครเล่ามุกอะไรก็ขำ",
         "#d94a3c", "monkey", "monkey", "#2a7a5a", "trident", "monkey", "#f7c2a8", eyes="happy", mouth="laugh"),
    Char("phali", "พาลี", "rama", "พญาวานรผู้ทรงพลัง",
         "พี่ชายสุครีพ แข็งแรงที่สุดในเมืองขีดขิน หน้าบึ้งเก่ง แต่บึ้งแล้วกลับดูน่ารัก",
         "#3f8f4c", "monkey", "monkey", "#b0263a", "club", "monkey", "#cfe8b8", eyes="angry", mouth="o"),
    Char("ongkhot", "องคต", "rama", "ทูตผู้กล้า",
         "ลูกพาลี อาสาเป็นทูตไปลงกา เอาหางขดเป็นบัลลังก์นั่งสูงกว่าทศกัณฐ์ให้ช้ำใจ",
         "#7cc46a", "monkey", "monkey", "#7a3fb0", "club", "monkey", "#e2f4d4", eyes="side", mouth="smirk"),
    Char("nilaphat", "นิลพัท", "rama", "วานรกายสีดำ",
         "วานรขนสีนิล ขี้เล่นตัวพ่อ คู่กัดของหนุมานที่แกล้งกันไปมาทั้งเรื่อง",
         "#3a3f63", "monkey", "monkey", "#e0a33a", "club", "monkey", "#b9bede", eyes="normal", mouth="tongue", gag="sweat"),
    Char("macchanu", "มัจฉานุ", "rama", "บุตรหนุมานกับสุพรรณมัจฉา",
         "ครึ่งลิงครึ่งปลา ว่ายน้ำเร็วกว่าเดิน เจอพ่อครั้งแรกก็ดีใจจนครีบกระดิก",
         "#f4f4fa", "monkey", "monkey", "#2a8fb8", "trident", "fish", "#fde3ea", eyes="happy", mouth="grin", gag="sparkle"),
    Char("sadayu", "สดายุ", "rama", "พญานกผู้กล้าหาญ",
         "พญานกที่บินเข้าขวางทศกัณฐ์เพื่อช่วยนางสีดา ตกใจง่ายแต่ใจสู้",
         "#f2a33a", "bird", "monkey", "#d33a45", "", "wings", eyes="normal", mouth="o", gag="sweat"),
    Char("phiphek", "พิเภก", "rama", "โหราจารย์แห่งลงกา",
         "ยักษ์สายดูดวง หลับตาทำนายแม่นทุกครั้ง ยกเว้นตอนทำนายว่าวันนี้ฝนจะไม่ตก",
         "#7ac05a", "yaksha", "yaksha", "#e6c24a", "lotus", eyes="happy", mouth="smile", gag="sparkle"),
    Char("ruesi", "พระฤาษี", "rama", "นักพรตผู้วิเศษ",
         "ฤาษีหนวดยาวสายเวทมนตร์ ชุบตัวคนได้ เสกของได้ แต่เสกแว่นตาหายของตัวเองไม่เจอทุกเช้า",
         "#e8b98a", "ruesi", "tiger", "#d9782a", "staff", eyes="wink", mouth="grin", gag="sparkle"),
    Char("phokae", "พ่อแก่", "rama", "บรมครูแห่งศิลปะ",
         "ครูของครูทั้งปวง ผู้ประสาทวิชาให้นักรำและนักผจญภัย ยิ้มใจดีเสมอ ใครมาไหว้ได้พรกลับไปทุกคน",
         "#d9a441", "ruesi", "tigergold", "#8c2a20", "staff", eyes="happy", mouth="smile", gag="sparkle"),
    Char("suphan", "สุพรรณมัจฉา", "lanka", "นางเงือกทองคำ",
         "ธิดาทศกัณฐ์ คุมฝูงปลาแอบขนหินทิ้งทะเล จนเจอหนุมานจับได้แล้วตกหลุมรัก",
         "#f8dfc4", "female", "female", "#e0a33a", "", "fish", eyes="wink", mouth="tongue", gag="heart"),
    Char("tossakan", "ทศกัณฐ์", "lanka", "เจ้ากรุงลงกา",
         "ยักษ์สิบหน้า สิบหน้านั้นยิ้มเจ้าเล่ห์พร้อมกันหมด ถอดหัวใจฝากไว้เพราะกลัวใจสลาย",
         "#2f8f5a", "yaksha", "tossakan", "#b0263a", "sword", eyes="side", mouth="grin"),
    Char("kumpakan", "กุมภกรรณ", "lanka", "อนุชาทศกัณฐ์",
         "ยักษ์นักหลับ นอนทีละหลายเดือน ปลุกยากที่สุดในสามโลก ถือหอกโมกขศักดิ์ไว้ละเมอ",
         "#5b5f72", "yaksha", "yaksha", "#3a7fb0", "spear", eyes="sleepy", mouth="o", gag="zzz"),
    Char("inthorachit", "อินทรชิต", "lanka", "โอรสทศกัณฐ์",
         "เจ้าของศรนาคบาศ ชอบแปลงเป็นพระอินทร์แล้วยิ้มมุมปากแบบรู้ทัน",
         "#3c9c76", "yaksha", "flame", "#d26a2a", "bow", eyes="angry", mouth="smirk"),
    Char("maiyarap", "ไมยราพ", "lanka", "เจ้าเมืองบาดาล",
         "ยักษ์นักสะกดทัพ เป่ากล้องยานอนให้ทุกคนหลับ แล้วแอบหัวเราะคิกคักอยู่คนเดียว",
         "#8a4fb0", "yaksha", "yaksha", "#2a8f7a", "", eyes="side", mouth="laugh", gag="smoke"),
    Char("nonthok", "นนทก", "lanka", "ยักษ์นิ้วเพชร",
         "ชี้นิ้วเพชรใส่ใครคนนั้นล้ม เลยชี้มั่วไปหมดจนต้องมีคนมาปราบ",
         "#4aa0a0", "yaksha", "yaksha", "#e05a8a", "", eyes="wink", mouth="grin", gag="point"),
    Char("benjakai", "นางเบญกาย", "lanka", "ธิดาพิเภก",
         "นางยักษ์สายแปลงร่าง เคยแปลงเป็นนางสีดาลอยน้ำมาหลอก เนียนจนตัวเองยังงง",
         "#f2d4c2", "female", "female", "#7a4fc0", "", eyes="side", mouth="smirk", gag="sparkle"),
    Char("montho", "นางมณโฑ", "lanka", "มเหสีทศกัณฐ์",
         "นางกบที่ฤๅษีชุบให้เป็นหญิงงาม อัครมเหสีแห่งลงกา ยิ้มหวานแต่ดุที่สุดในวัง",
         "#f6d9c4", "female", "female", "#c43a6a", "lotus", eyes="happy", mouth="smile", gag="heart"),
]


def defs(c: Char) -> str:
    sk = c.skin
    of = c.outfit
    return f"""<defs>
<radialGradient id="sk" cx=".36" cy=".3" r=".75"><stop offset="0" stop-color="{light(sk, .45)}"/><stop offset=".55" stop-color="{sk}"/><stop offset="1" stop-color="{dark(sk, .32)}"/></radialGradient>
<radialGradient id="mz" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="{light(c.muzzle or sk, .5)}"/><stop offset="1" stop-color="{dark(c.muzzle or sk, .12)}"/></radialGradient>
<linearGradient id="of" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{light(of, .3)}"/><stop offset=".55" stop-color="{of}"/><stop offset="1" stop-color="{dark(of, .38)}"/></linearGradient>
<linearGradient id="go" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3bf"/><stop offset=".45" stop-color="#f2c14e"/><stop offset="1" stop-color="#a8681a"/></linearGradient>
<linearGradient id="gh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b9781e"/><stop offset=".45" stop-color="#ffecaa"/><stop offset="1" stop-color="#b9781e"/></linearGradient>
<linearGradient id="si" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9aa6c0"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#aab6cc"/></linearGradient>
<linearGradient id="ft" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe9a6"/><stop offset=".5" stop-color="#e9a93a"/><stop offset="1" stop-color="#b8661c"/></linearGradient>
<radialGradient id="gem" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#ffd0d0"/><stop offset=".5" stop-color="#e8463a"/><stop offset="1" stop-color="#8c1a20"/></radialGradient>
<radialGradient id="gm2" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#d0fff0"/><stop offset=".5" stop-color="#2fc79a"/><stop offset="1" stop-color="#0f6b52"/></radialGradient>
<pattern id="lai" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M6 1 L9 6 L6 11 L3 6z" fill="none" stroke="#ffe08a" stroke-width="1" opacity=".55"/><circle cx="0" cy="0" r="1.3" fill="#ffe08a" opacity=".6"/><circle cx="12" cy="12" r="1.3" fill="#ffe08a" opacity=".6"/></pattern>
<linearGradient id="shd" x1="0" y1="0" x2="1" y2="0"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".32"/></linearGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="0"><stop offset=".6" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".35"/></linearGradient>
<radialGradient id="hl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
</defs>"""


# ---- parts -----------------------------------------------------------------

def weapon_back(c: Char) -> str:
    w = c.weapon
    art = _weapon(c)
    if not art:
        return ""
    if w == "bow":
        return f'<g transform="translate(-14 0)">{art}</g>'
    if c.gag == "zzz" or w == "lotus":
        return art
    return f'<g transform="translate(18 -2)">{art}</g>'


def _weapon(c: Char) -> str:
    w = c.weapon
    if w == "bow":
        return ('<path d="M44 66 Q14 140 44 214" fill="none" stroke="url(#go)" stroke-width="7"/>'
                '<path d="M44 66 Q14 140 44 214" fill="none" stroke="#7a4a12" stroke-width="1.4" opacity=".5"/>'
                '<path d="M44 66 L44 214" stroke="#f6efe0" stroke-width="1.4"/>'
                '<circle cx="44" cy="66" r="4" fill="url(#go)"/><circle cx="44" cy="214" r="4" fill="url(#go)"/>')
    if w == "trident":
        return ('<path d="M156 228 L156 70" stroke="#d9a23a" stroke-width="6"/>'
                '<path d="M156 74 L156 30 M141 70 Q140 48 146 40 M171 70 Q172 48 166 40" stroke="url(#si)" stroke-width="6" fill="none"/>'
                '<path d="M150 32 L156 18 L162 32z M141 44 L143 34 L149 42z M171 44 L169 34 L163 42z" fill="url(#si)"/>'
                '<rect x="138" y="68" width="36" height="9" rx="4" fill="url(#go)"/>')
    if w == "club":
        return ('<path d="M156 226 L156 96" stroke="#d9a23a" stroke-width="7"/>'
                '<ellipse cx="156" cy="80" rx="15" ry="22" fill="url(#go)"/>'
                '<path d="M144 72 Q156 64 168 72 M143 86 Q156 94 169 86" fill="none" stroke="#a8681a" stroke-width="2"/>'
                '<path d="M152 58 L156 46 L160 58z" fill="url(#go)"/>')
    if w == "sword":
        return ('<path d="M156 150 L156 40 L164 30 L170 40 L170 150z" fill="url(#si)"/>'
                '<path d="M163 44 L163 148" stroke="#c9d3e4" stroke-width="1.4"/>'
                '<rect x="146" y="148" width="34" height="9" rx="4" fill="url(#go)"/>'
                '<rect x="158" y="157" width="10" height="26" rx="4" fill="#7a2a1a"/>'
                '<circle cx="163" cy="186" r="6" fill="url(#go)"/>')
    if w == "staff":
        return ('<path d="M156 230 L156 60" stroke="#8a5a2a" stroke-width="7"/>'
                '<path d="M156 62 Q156 34 172 34 Q186 36 182 52" fill="none" stroke="#8a5a2a" stroke-width="7"/>'
                '<path d="M150 96 h12 v8 h-12z" fill="url(#go)"/>'
                '<ellipse cx="147" cy="118" rx="9" ry="12" fill="#e9b04a"/><ellipse cx="147" cy="104" rx="5" ry="6" fill="#e9b04a"/>'
                '<path d="M147 98 V92" stroke-width="2"/>')
    if w == "spear":
        return ('<path d="M156 228 L156 70" stroke="#d9a23a" stroke-width="6"/>'
                '<path d="M156 18 Q172 44 156 74 Q140 44 156 18z" fill="url(#si)"/>'
                '<path d="M156 26 L156 68" stroke="#9aa6c0" stroke-width="1.4"/>'
                '<path d="M146 80 Q156 92 166 80 L162 76 Q156 82 150 76z" fill="#d33a45"/>'
                '<rect x="146" y="70" width="20" height="8" rx="3" fill="url(#go)"/>')
    return ""


def lotus_front() -> str:
    return ('<path d="M150 214 Q146 176 156 150" fill="none" stroke="#3f8a4a" stroke-width="4"/>'
            '<path d="M156 150 Q140 136 146 120 Q156 128 156 150z" fill="#f59ab4"/>'
            '<path d="M156 150 Q172 136 166 120 Q156 128 156 150z" fill="#f59ab4"/>'
            '<path d="M156 150 Q146 126 156 106 Q166 126 156 150z" fill="#ffc6d6"/>'
            '<path d="M158 112 Q160 126 157 142" stroke="#fff" stroke-width="2" opacity=".6" fill="none"/>')


def tail(c: Char) -> str:
    if c.tail == "wings":
        return ('<path d="M66 172 Q20 150 18 104 Q34 122 44 118 Q36 140 52 146 Q44 160 70 168z" fill="url(#ft)"/>'
                '<path d="M134 172 Q180 150 182 104 Q166 122 156 118 Q164 140 148 146 Q156 160 130 168z" fill="url(#ft)"/>'
                '<path d="M30 116 Q40 136 60 156 M170 116 Q160 136 140 156" fill="none" stroke="#a8681a" stroke-width="1.6"/>')
    if c.tail != "monkey":
        return ""
    return (f'<path d="M136 206 Q186 210 182 160 Q180 136 166 140" fill="none" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M136 206 Q186 210 182 160 Q180 136 166 140" fill="none" stroke="{c.skin}" stroke-width="7"/>')


def body(c: Char) -> str:
    sk = "url(#sk)"
    parts = []
    # arms
    parts.append(f'<ellipse cx="62" cy="184" rx="12" ry="22" transform="rotate(18 62 184)" fill="{sk}"/>')
    parts.append(f'<ellipse cx="138" cy="184" rx="12" ry="22" transform="rotate(-18 138 184)" fill="{sk}"/>')
    parts.append('<path d="M52 196 h18 v8 h-18z M130 196 h18 v8 h-18z" fill="url(#go)" transform="translate(0 0)"/>')
    if c.tail == "fish":
        parts.append('<path d="M66 196 Q100 190 134 196 Q140 226 116 236 Q140 242 150 262 Q120 258 100 246 Q80 258 50 262 Q60 242 84 236 Q60 226 66 196z" fill="url(#ft)"/>')
        parts.append('<path d="M76 210 q8 6 16 0 q8 6 16 0 q8 6 16 0 M82 224 q6 5 12 0 q6 5 12 0 q6 5 12 0" fill="none" stroke="#a8681a" stroke-width="1.8"/>')
    else:
        parts.append('<path d="M74 214 h22 v26 q-11 6 -22 0z M104 214 h22 v26 q-11 6 -22 0z" fill="url(#of)"/>')
        parts.append('<path d="M74 214 h22 v26 q-11 6 -22 0z M104 214 h22 v26 q-11 6 -22 0z" fill="url(#lai)" stroke="none"/>')
        parts.append(f'<path d="M72 238 h26 v6 h-26z M102 238 h26 v6 h-26z" fill="url(#go)"/>')
        parts.append(f'<ellipse cx="85" cy="252" rx="14" ry="7" fill="{sk}"/><ellipse cx="115" cy="252" rx="14" ry="7" fill="{sk}"/>')
    # torso
    if c.face == "female":
        parts.append('<path d="M70 168 Q100 156 130 168 L134 220 Q100 230 66 220z" fill="url(#of)"/>')
        parts.append('<path d="M70 168 Q100 156 130 168 L134 220 Q100 230 66 220z" fill="url(#lai)" stroke="none"/>')
        parts.append('<path d="M70 168 Q100 156 130 168 L134 220 Q100 230 66 220z" fill="url(#shd)" stroke="none"/>')
        parts.append(f'<path d="M72 168 Q100 186 128 168 L128 176 Q100 196 72 176z" fill="{sk}"/>')
        parts.append('<path d="M70 176 Q100 196 130 176 L130 184 Q100 204 70 184z" fill="url(#go)"/>')
    else:
        parts.append('<path d="M66 166 Q100 152 134 166 L136 218 Q100 228 64 218z" fill="url(#of)"/>')
        parts.append('<path d="M66 166 Q100 152 134 166 L136 218 Q100 228 64 218z" fill="url(#lai)" stroke="none"/>')
        parts.append('<path d="M66 166 Q100 152 134 166 L136 218 Q100 228 64 218z" fill="url(#shd)" stroke="none"/>')
        # collar
        parts.append('<path d="M70 164 Q100 196 130 164 Q126 176 100 188 Q74 176 70 164z" fill="url(#go)"/>')
        # shoulder flares (Inthanu)
        parts.append('<path d="M64 166 Q50 158 46 146 Q58 150 66 158z M136 166 Q150 158 154 146 Q142 150 134 158z" fill="url(#go)"/>')
    parts.append('<path d="M66 208 Q100 218 134 208 L134 216 Q100 226 66 216z" fill="url(#gh)"/>')
    parts.append('<circle cx="100" cy="182" r="5.5" fill="url(#gem)"/>')
    parts.append('<path d="M92 216 L100 232 L108 216z" fill="url(#go)"/>')
    return f'<g stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">{"".join(parts)}</g>'


def head(c: Char) -> str:
    p = []
    # ear ornaments (kanjiak) behind head
    p.append('<path d="M50 112 C34 118 34 146 46 156 C46 142 50 132 56 126z" fill="url(#go)"/>')
    p.append('<path d="M150 112 C166 118 166 146 154 156 C154 142 150 132 144 126z" fill="url(#go)"/>')
    if c.face == "female":
        p.insert(0, '<path d="M54 110 Q40 150 58 186 Q66 172 66 150z M146 110 Q160 150 142 186 Q134 172 134 150z" fill="#2a1d2e"/>')
    p.append('<circle cx="100" cy="114" r="52" fill="url(#sk)"/>')
    if c.face in ("deva", "female"):
        p.append('<path d="M49 112 Q50 64 100 62 Q150 64 151 112 Q144 92 128 90 Q112 96 100 88 Q88 96 72 90 Q56 92 49 112z" fill="#2a1d2e" stroke-width="2.2"/>')
    if c.face == "monkey":
        p.append('<ellipse cx="100" cy="134" rx="32" ry="22" fill="url(#mz)" stroke-width="2.2"/>')
    return "".join(p)


def eyes(c: Char) -> str:
    """Eyes at (86,113) and (114,113); style picks the expression."""
    big = c.face in ("monkey", "yaksha", "bird")
    r = 9.5 if big else 6.5
    yak = c.face == "yaksha"
    white = "#fff6d8" if yak else "#fff"
    rim = 'stroke="#c8303c" stroke-width="2.4"' if yak else 'stroke-width="2.2"'
    lx, rx, y = 86, 114, 113

    def open_eye(x: float, dx: float = 0) -> str:
        return (f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r if big else r * .8:.1f}" fill="{white}" {rim}/>'
                f'<circle cx="{x + dx + 1}" cy="{y + 1}" r="{r * .5:.1f}" fill="#1d1424" stroke="none"/>'
                f'<circle cx="{x + dx + 2.6}" cy="{y - 1}" r="{r * .18:.1f}" fill="#fff" stroke="none"/>')

    def closed(x: float, up: bool = True) -> str:
        d = -6 if up else 4
        return f'<path d="M{x - r} {y + 2} Q{x} {y + d} {x + r} {y + 2}" fill="none" stroke-width="3"/>'

    e = c.eyes
    if e == "wink":
        out = open_eye(lx) + closed(rx)
    elif e == "happy":
        out = closed(lx) + closed(rx)
    elif e == "sleepy":
        out = (closed(lx, False) + closed(rx, False)
               + f'<path d="M{lx - r} {y - 3} H{lx + r} M{rx - r} {y - 3} H{rx + r}" stroke-width="2" opacity=".6"/>')
    elif e == "side":
        out = open_eye(lx, 3) + open_eye(rx, 3)
        out += f'<path d="M{lx - r} {y - r * .6:.1f} H{lx + r} M{rx - r} {y - r * .6:.1f} H{rx + r}" stroke-width="2.6"/>'
    else:
        out = open_eye(lx) + open_eye(rx)
    # brows
    if e == "angry":
        out += f'<path d="M{lx - 12} {y - 16} L{lx + 8} {y - 10} M{rx + 12} {y - 16} L{rx - 8} {y - 10}" stroke-width="4"/>'
    elif c.face in ("deva", "female"):
        lift = -4 if c.mouth == "smirk" else 0
        out += f'<path d="M{lx - 12} {y - 11} Q{lx} {y - 19} {lx + 11} {y - 12} M{rx - 11} {y - 12 + lift} Q{rx} {y - 19 + lift} {rx + 12} {y - 11 + lift}" fill="none" stroke-width="3"/>'
    elif c.face == "yaksha":
        out += f'<path d="M{lx - 16} {y - 12} Q{lx} {y - 26} {lx + 12} {y - 12} Q{lx} {y - 18} {lx - 16} {y - 12}z M{rx + 16} {y - 12} Q{rx} {y - 26} {rx - 12} {y - 12} Q{rx} {y - 18} {rx + 16} {y - 12}z" fill="#2b1b33" stroke-width="1.4"/>'
    elif c.face == "monkey":
        out += f'<path d="M{lx - 16} {y - 9} Q{lx - 6} {y - 21} {lx + 10} {y - 13} Q{lx - 2} {y - 15} {lx - 6} {y - 9}z M{rx + 16} {y - 9} Q{rx + 6} {y - 21} {rx - 10} {y - 13} Q{rx + 2} {y - 15} {rx + 6} {y - 9}z" fill="#e2558a" stroke-width="1.8"/>'
    if c.face == "female" and e not in ("happy",):
        out += f'<path d="M{lx - r} {y - 2} l-4 -4 M{lx - r + 1} {y + 1} l-5 -1" stroke-width="1.8"/>'
    return out


def mouth(c: Char) -> str:
    y = {"monkey": 136, "yaksha": 136, "ruesi": 144}.get(c.face, 134)
    m = c.mouth
    lip = "#d6455e" if c.face == "female" else "#c8303c"
    if m == "grin":
        out = f'<path d="M84 {y - 3} Q100 {y + 18} 116 {y - 3}z" fill="{lip}" stroke-width="2.2"/><path d="M86 {y - 2} H114" stroke="#fff" stroke-width="3"/>'
    elif m == "laugh":
        out = (f'<path d="M82 {y - 4} Q100 {y + 22} 118 {y - 4}z" fill="#8c1a2a" stroke-width="2.2"/>'
               f'<path d="M92 {y + 8} Q100 {y + 2} 108 {y + 8} Q100 {y + 14} 92 {y + 8}z" fill="#ff7a8a" stroke="none"/>')
    elif m == "smirk":
        out = f'<path d="M88 {y + 1} Q102 {y + 6} 114 {y - 5}" fill="none" stroke-width="2.8"/><path d="M113 {y - 7} l3 3" stroke-width="2"/>'
    elif m == "tongue":
        out = (f'<path d="M86 {y - 1} Q100 {y + 10} 114 {y - 1}" fill="none" stroke-width="2.6"/>'
               f'<path d="M98 {y + 3} Q99 {y + 16} 106 {y + 15} Q112 {y + 13} 110 {y + 2}" fill="#ff7a8a" stroke-width="2"/>'
               f'<path d="M104 {y + 5} V{y + 11}" stroke="#c8303c" stroke-width="1.4"/>')
    elif m == "o":
        out = f'<ellipse cx="100" cy="{y + 3}" rx="6" ry="7.5" fill="#8c1a2a" stroke-width="2.2"/>'
    else:
        out = f'<path d="M90 {y} Q100 {y + 8} 110 {y}" fill="none" stroke-width="2.6"/>'
    if c.face == "yaksha":
        out += f'<path d="M80 {y - 2} L83 {y - 14} L88 {y - 1}z M120 {y - 2} L117 {y - 14} L112 {y - 1}z" fill="#fff" stroke-width="1.6"/>'
    if c.face == "monkey" and m in ("grin", "laugh"):
        out += f'<path d="M90 {y - 2} L92 {y + 4} L94 {y - 1}z M106 {y - 1} L108 {y + 4} L110 {y - 2}z" fill="#fff" stroke-width="1.2"/>'
    return out


def face(c: Char) -> str:
    out = [eyes(c)]
    if c.face == "bird":
        out.append('<path d="M84 122 Q100 116 116 122 L100 150z" fill="#f2c14e" stroke-width="2.2"/>'
                   '<path d="M88 126 Q100 122 112 126" stroke="#a8681a" stroke-width="1.6" fill="none"/>')
        if c.mouth == "o":
            out.append('<path d="M94 136 L100 146 L106 136z" fill="#8c1a2a" stroke-width="1.4"/>')
    else:
        if c.face == "monkey":
            out.append('<ellipse cx="100" cy="127" rx="4" ry="2.6" fill="#2b1b33" stroke="none"/>')
        elif c.face == "yaksha":
            out.append('<path d="M95 121 Q100 130 105 121" fill="none" stroke-width="2"/>')
        out.append(mouth(c))
    if c.face == "ruesi":
        out.append('<path d="M60 124 Q64 176 100 196 Q136 176 140 124 Q128 142 112 140 Q100 146 88 140 Q72 142 60 124z" fill="#f7f4ee" stroke-width="2.4"/>'
                   '<path d="M80 150 Q84 168 96 180 M120 150 Q116 168 104 180 M100 152 V186" fill="none" stroke="#c9c2b6" stroke-width="1.8"/>'
                   '<path d="M78 134 Q90 126 100 132 Q110 126 122 134 Q112 140 100 136 Q88 140 78 134z" fill="#f7f4ee" stroke-width="2"/>'
                   '<path d="M70 100 Q84 90 98 100 Q84 96 70 104z M130 100 Q116 90 102 100 Q116 96 130 104z" fill="#f7f4ee" stroke-width="1.8"/>')
    if c.face not in ("yaksha",):
        out.append('<g fill="#ff8e9e" opacity=".55" stroke="none"><ellipse cx="70" cy="129" rx="7" ry="4"/><ellipse cx="130" cy="129" rx="7" ry="4"/></g>')
    if c.face in ("deva", "female"):
        out.append('<path d="M100 99 l-3 -5 l3 -5 l3 5z" fill="url(#gem)" stroke-width="1.2"/>')
    return "".join(out)


def gag(c: Char) -> str:
    g = c.gag
    if g == "zzz":
        return ('<g fill="#e8f0ff" stroke="#2b1b33" stroke-width=".9" font-family="Arial Black,Arial,sans-serif" font-weight="900">'
                '<text x="26" y="84" font-size="24">Z</text><text x="36" y="58" font-size="18">z</text><text x="30" y="36" font-size="13">z</text></g>'
                '<circle cx="128" cy="136" r="7" fill="#cfe9ff" stroke="#7aa6d8" stroke-width="1.4" opacity=".85"/>')
    if g == "sweat":
        return '<path d="M146 84 Q154 98 146 104 Q138 98 146 84z" fill="#9ad8ff" stroke="#2b1b33" stroke-width="1.8"/>'
    if g == "sparkle":
        return ('<g fill="#fff3bf" stroke="#a8681a" stroke-width="1.2">'
                '<path d="M40 70 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3z"/><path d="M160 96 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2z"/></g>')
    if g == "heart":
        return '<path d="M150 82 q-6 -8 -12 -2 q-5 6 12 18 q17 -12 12 -18 q-6 -6 -12 2z" fill="#ff5a7a" stroke="#2b1b33" stroke-width="1.8"/>'
    if g == "smoke":
        return ('<g stroke="#2b1b33" stroke-width="2"><path d="M118 140 L150 150" stroke="url(#go)" stroke-width="5"/>'
                '<circle cx="160" cy="146" r="7" fill="#d8c8f0"/><circle cx="170" cy="134" r="9" fill="#e6dcf6"/><circle cx="168" cy="116" r="7" fill="#f0eafa"/></g>')
    if g == "point":
        return ('<g stroke="#2b1b33" stroke-width="2.4" stroke-linejoin="round">'
                '<path d="M136 172 Q150 160 164 150 L170 156 Q156 168 142 182z" fill="url(#sk)"/>'
                '<path d="M166 146 L178 136 L182 144 L170 152z" fill="#bdf2ff"/></g>'
                '<g fill="#fff" stroke="#3ab0d0" stroke-width="1.4"><path d="M186 128 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2z"/></g>')
    return ""


def crown(c: Char) -> str:
    k = c.crown
    band = ('<path d="M48 96 Q100 64 152 96 L150 106 Q100 78 50 106z" fill="url(#go)"/>'
            '<path d="M60 92 Q100 72 140 92" fill="none" stroke="#a8681a" stroke-width="1.6"/>'
            '<circle cx="100" cy="82" r="5" fill="url(#gm2)" stroke-width="1.6"/>')
    if k == "chada":
        return band + (
            '<path d="M66 90 Q100 70 134 90 L120 52 Q100 44 80 52z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="56" rx="21" ry="6" fill="url(#gh)"/>'
            '<path d="M82 54 L92 22 Q100 18 108 22 L118 54z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="28" rx="10" ry="4" fill="url(#gh)"/>'
            '<path d="M93 26 L100 -16 L107 26z" fill="url(#go)"/>'
            '<circle cx="100" cy="-14" r="3" fill="url(#gem)" stroke-width="1.2"/>'
            '<circle cx="100" cy="40" r="3.4" fill="url(#gem)" stroke-width="1.2"/>'
            '<path d="M84 70 Q100 62 116 70" fill="none" stroke="#a8681a" stroke-width="1.6"/>')
    if k == "monkey":
        return band + (
            '<path d="M68 90 Q100 72 132 90 L118 56 Q100 50 82 56z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="58" rx="18" ry="5.5" fill="url(#gh)"/>'
            '<path d="M86 58 Q84 36 100 20 Q116 36 114 58z" fill="url(#go)"/>'
            '<path d="M100 20 Q110 10 104 2 Q98 12 100 20z" fill="url(#go)"/>'
            '<circle cx="100" cy="44" r="3.4" fill="url(#gem)" stroke-width="1.2"/>')
    if k == "yaksha":
        return band + (
            '<path d="M66 90 Q100 70 134 90 L122 50 Q100 42 78 50z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="52" rx="23" ry="6" fill="url(#gh)"/>'
            '<path d="M82 50 Q78 30 100 26 Q122 30 118 50z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="28" rx="13" ry="4" fill="url(#gh)"/>'
            '<path d="M92 28 Q90 12 100 4 Q110 12 108 28z" fill="url(#go)"/>'
            '<circle cx="100" cy="2" r="4" fill="url(#gem)" stroke-width="1.2"/>'
            '<path d="M78 70 l-6 -12 M122 70 l6 -12" stroke-width="2"/>'
            '<circle cx="100" cy="64" r="3.6" fill="url(#gem)" stroke-width="1.2"/>')
    if k == "flame":
        return band + (
            '<path d="M66 90 Q100 70 134 90 L120 52 Q100 44 80 52z" fill="url(#go)"/>'
            '<ellipse cx="100" cy="54" rx="21" ry="6" fill="url(#gh)"/>'
            '<path d="M84 54 Q70 30 92 14 Q88 30 100 34 Q98 14 112 2 Q108 22 118 30 Q124 42 116 54z" fill="#f08a2a"/>'
            '<path d="M90 52 Q86 36 98 28 Q98 40 106 42 Q108 30 114 26 Q118 42 110 52z" fill="#ffd36a" stroke-width="1.6"/>'
            '<circle cx="100" cy="66" r="3.6" fill="url(#gem)" stroke-width="1.2"/>')
    if k == "tossakan":
        sk = "url(#sk)"
        faces = []
        for cx, cy, r in [(76, 66, 9), (100, 60, 10), (124, 66, 9), (86, 40, 8), (114, 40, 8), (100, 20, 8)]:
            faces.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sk}" stroke-width="2"/>'
                f'<circle cx="{cx - r * .35:.1f}" cy="{cy - 1}" r="{r * .22:.1f}" fill="#fff6d8" stroke="#c8303c" stroke-width="1"/>'
                f'<circle cx="{cx + r * .35:.1f}" cy="{cy - 1}" r="{r * .22:.1f}" fill="#fff6d8" stroke="#c8303c" stroke-width="1"/>'
                f'<path d="M{cx - r * .45:.1f} {cy + r * .4:.1f} Q{cx} {cy + r * .75:.1f} {cx + r * .45:.1f} {cy + r * .4:.1f}" fill="#9c1f2e" stroke-width="1.2"/>'
                f'<path d="M{cx - r * .7:.1f} {cy - r * .55:.1f} Q{cx} {cy - r * 1.05:.1f} {cx + r * .7:.1f} {cy - r * .55:.1f}" fill="url(#go)" stroke-width="1.4"/>')
        return band + (
            '<path d="M62 92 Q100 70 138 92 L126 34 Q100 8 74 34z" fill="url(#go)"/>'
            + "".join(faces) +
            '<path d="M94 12 Q92 -6 100 -16 Q108 -6 106 12z" fill="url(#go)"/>'
            '<circle cx="100" cy="-16" r="3.4" fill="url(#gem)" stroke-width="1.2"/>')
    if k in ("tiger", "tigergold"):
        stripes = "".join(f'<path d="M{x} {y} q6 -4 12 0" fill="none" stroke="#2b1b33" stroke-width="3"/>'
                          for x, y in [(74, 80), (112, 80), (82, 58), (106, 58), (90, 36), (92, 16)])
        base = ('<path d="M52 100 Q50 60 72 34 Q96 -10 112 6 Q124 20 132 44 Q150 70 148 100 Q100 78 52 100z" fill="#f0a23a"/>'
                '<path d="M60 92 Q70 56 96 20 M140 92 Q132 60 112 18" fill="none" stroke="#ffd27a" stroke-width="3" opacity=".7"/>'
                + stripes +
                '<path d="M110 8 Q126 -4 130 10 Q120 6 114 14z" fill="#f0a23a"/>')
        if k == "tigergold":
            base += ('<path d="M50 102 Q100 76 150 102 L148 112 Q100 88 52 112z" fill="url(#go)"/>'
                     '<path d="M58 100 Q100 80 142 100" fill="none" stroke="#fff6cf" stroke-width="2.4" stroke-dasharray="0 6" stroke-linecap="round"/>'
                     '<circle cx="100" cy="88" r="5.5" fill="url(#gem)" stroke-width="1.6"/>')
        else:
            base += '<path d="M50 102 Q100 80 150 102 L148 110 Q100 90 52 110z" fill="#f7f4ee"/>'
        return base
    # female: crown with flower tassels
    return (
        '<path d="M50 102 Q100 66 150 102 L148 110 Q100 80 52 110z" fill="url(#go)"/>'
        '<path d="M70 90 Q100 72 130 90 L116 58 Q100 52 84 58z" fill="url(#go)"/>'
        '<ellipse cx="100" cy="60" rx="17" ry="5" fill="url(#gh)"/>'
        '<path d="M88 60 L96 26 Q100 22 104 26 L112 60z" fill="url(#go)"/>'
        '<path d="M96 28 L100 0 L104 28z" fill="url(#go)"/>'
        '<circle cx="100" cy="78" r="4.4" fill="url(#gem)" stroke-width="1.4"/>'
        '<g stroke-width="1.2"><circle cx="54" cy="116" r="4" fill="#fff"/><circle cx="52" cy="126" r="3.6" fill="#fff"/><circle cx="52" cy="136" r="3.2" fill="#fff"/><circle cx="53" cy="145" r="3" fill="#f59ab4"/>'
        '<circle cx="146" cy="116" r="4" fill="#fff"/><circle cx="148" cy="126" r="3.6" fill="#fff"/><circle cx="148" cy="136" r="3.2" fill="#fff"/><circle cx="147" cy="145" r="3" fill="#f59ab4"/></g>')


def ornaments(c: Char) -> str:
    """Rim light on the head, beaded crown band, krajang leaves and a tip glint."""
    out = ['<path d="M128 72 A52 52 0 0 1 128 156 A60 60 0 0 0 128 72z" fill="url(#rim)"/>'
           .replace("M128 72 A52 52 0 0 1 128 156 A60 60 0 0 0 128 72z",
                    "M118 66 A52 52 0 0 1 132 155 Q154 116 118 66z")]
    if c.crown not in ("female", "tiger", "tigergold"):
        leaves = []
        for i in range(7):
            t = .2 + i * .1
            x = 48 + 104 * t
            y = 96 - 64 * t * (1 - t)
            leaves.append(f'<path d="M{x - 5:.1f} {y:.1f} Q{x:.1f} {y - 13:.1f} {x + 5:.1f} {y:.1f} Q{x:.1f} {y - 4:.1f} {x - 5:.1f} {y:.1f}z" fill="url(#go)" stroke="{INK}" stroke-width="1.4"/>')
        out.append("".join(leaves))
        out.append('<path d="M54 99 Q100 71 146 99" fill="none" stroke="#fff6cf" stroke-width="2.6" stroke-dasharray="0 6.5" stroke-linecap="round"/>')
    tip = {"chada": -16, "tossakan": -16, "female": 0, "monkey": 4, "yaksha": 2, "flame": 4, "tiger": 4, "tigergold": 4}.get(c.crown, 0)
    out.append(f'<path transform="translate(104 {tip - 2})" d="M0 -7 l1.8 5.2 5.2 1.8 -5.2 1.8 -1.8 5.2 -1.8 -5.2 -5.2 -1.8 5.2 -1.8z" fill="#fff" opacity=".95"/>')
    return "".join(out)


def svg(c: Char) -> str:
    front_weapon = lotus_front() if c.weapon == "lotus" else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="8 -28 184 296" role="img" aria-labelledby="t"><title id="t">{c.name} ตัวละครการ์ตูนจากรามเกียรติ์</title>
{defs(c)}
<ellipse cx="100" cy="258" rx="54" ry="8" fill="#000" opacity=".28"/>
<g stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">
{weapon_back(c)}
{tail(c)}
</g>
{body(c)}
<g stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">
{head(c)}
{face(c)}
{crown(c)}
{front_weapon}
</g>
{ornaments(c)}
{gag(c)}
<ellipse cx="82" cy="88" rx="16" ry="9" fill="url(#hl)" transform="rotate(-25 82 88)"/>
</svg>
"""


PEDESTAL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" aria-hidden="true">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3bf"/><stop offset=".5" stop-color="#f2c14e"/><stop offset="1" stop-color="#8f5512"/></linearGradient>
<linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd6e2"/><stop offset="1" stop-color="#d9577e"/></linearGradient></defs>
<ellipse cx="100" cy="46" rx="92" ry="12" fill="#000" opacity=".3"/>
<g stroke="#2b1b33" stroke-width="2" stroke-linejoin="round">

""" + "".join(
    f'<path d="M{x} 34 Q{x + 7} 56 {x + 14} 34 Q{x + 7} 30 {x} 34z" fill="url(#p)"/>' for x in range(22, 168, 13)
) + """
<ellipse cx="100" cy="28" rx="80" ry="10" fill="url(#g)"/>
<path d="M30 28 Q100 40 170 28" fill="none" stroke="#fff6cf" stroke-width="2.2" stroke-dasharray="0 7" stroke-linecap="round"/>
</g></svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pedestal.svg").write_text(PEDESTAL, encoding="utf-8")
    for c in CHARS:
        (OUT / f"{c.slug}.svg").write_text(svg(c), encoding="utf-8")
    meta = [{"slug": c.slug, "name": c.name, "side": c.side, "role": c.role, "blurb": c.blurb} for c in CHARS]
    js = OUT.parent.parent / "characters.js"
    js.write_text("// Generated by tools/ramakien_chars.py. Do not edit by hand.\n"
                  "window.RAMAKIEN_CHARS = Object.freeze(" + json.dumps(meta, ensure_ascii=False, indent=1) + ");\n",
                  encoding="utf-8")
    print(f"wrote {len(CHARS)} characters to {OUT}")


if __name__ == "__main__":
    main()
