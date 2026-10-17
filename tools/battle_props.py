"""Generate the flying royal chariots (ราชรถ) for the home page battle scene.

Original artwork in the same chibi style as tools/ramakien_chars.py:
ink outline #2b1b33, soft gradients, cute and goofy faces.
Both chariots face right; the Lanka one is mirrored with CSS.

    python3 tools/battle_props.py
"""
from pathlib import Path

INK = "#2b1b33"
OUT = Path(__file__).resolve().parent.parent / "website" / "assets" / "img"

# Wheels spin, legs gallop, flags wave and clouds puff. The SVG is used as an
# <img>, so its own CSS runs inside it and respects reduced motion by itself.
STYLE = """<style>
.wheel{transform-origin:110px 186px;animation:spin .6s linear infinite}
.leg{transform-box:fill-box;transform-origin:50% 0;animation:gallop .5s ease-in-out infinite alternate}
.leg.b{animation-delay:-.25s}
.flag{transform-box:fill-box;transform-origin:0 50%;animation:wave .8s ease-in-out infinite alternate}
.puff{transform-box:fill-box;transform-origin:50% 50%;animation:puff 1.4s ease-in-out infinite alternate}
.puff.b{animation-delay:-.7s}
.wing{transform-box:fill-box;transform-origin:20% 90%;animation:flap .45s ease-in-out infinite alternate}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes gallop{from{transform:rotate(-24deg)}to{transform:rotate(22deg)}}
@keyframes wave{from{transform:skewY(-8deg) scaleX(.92)}to{transform:skewY(8deg) scaleX(1.05)}}
@keyframes puff{from{transform:scale(.9)}to{transform:scale(1.08)}}
@keyframes flap{from{transform:rotate(-16deg)}to{transform:rotate(12deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def defs(p):
    """Gradients for one palette. p: body, body_dark, trim, trim_dark, roof, gem."""
    return f"""<defs>
<linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p['body']}"/><stop offset="1" stop-color="{p['body_dark']}"/></linearGradient>
<linearGradient id="trim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3bf"/><stop offset=".45" stop-color="{p['trim']}"/><stop offset="1" stop-color="{p['trim_dark']}"/></linearGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p['roof']}"/><stop offset="1" stop-color="{p['body_dark']}"/></linearGradient>
<radialGradient id="gem" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="{p['gem']}"/><stop offset="1" stop-color="{INK}"/></radialGradient>
<radialGradient id="cloud" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#c9c3ff"/></radialGradient>
</defs>"""


def clouds():
    return f"""<g stroke="{INK}" stroke-width="3" fill="url(#cloud)">
<g class="puff"><circle cx="70" cy="214" r="20"/><circle cx="104" cy="222" r="24"/><circle cx="142" cy="216" r="20"/><circle cx="172" cy="222" r="14"/></g>
<g class="puff b"><circle cx="262" cy="206" r="16"/><circle cx="292" cy="212" r="20"/><circle cx="326" cy="206" r="16"/></g>
</g>"""


def chariot(p, flame):
    """Tiered Thai pavilion (บุษบก) on a curled naga-prow car with one big wheel."""
    top = (f'<path d="M110 2 C100 18 120 20 110 34 C124 24 118 10 110 2z" fill="#ff8a3a" stroke="{INK}" stroke-width="3"/>'
           if flame else
           f'<path d="M110 0 L104 30 L116 30z" fill="url(#trim)" stroke="{INK}" stroke-width="3"/><circle cx="110" cy="4" r="5" fill="url(#gem)" stroke="{INK}" stroke-width="2"/>')
    return f"""<g stroke="{INK}" stroke-width="3" stroke-linejoin="round">
<path class="flag" d="M30 26 h46 l-12 12 l12 12 h-46z" fill="{p['flag']}"/>
<path d="M30 20 V150" stroke-width="5" stroke-linecap="round"/>
<circle cx="30" cy="20" r="5" fill="url(#trim)"/>
<rect x="56" y="78" width="10" height="74" rx="3" fill="url(#trim)"/>
<rect x="154" y="78" width="10" height="74" rx="3" fill="url(#trim)"/>
<path d="M66 100 Q110 120 154 100 V150 H66z" fill="{p['body_dark']}" opacity=".55"/>
<path d="M36 82 Q110 60 184 82 L170 92 H50z" fill="url(#roof)"/>
<path d="M52 64 Q110 44 168 64 L156 72 H64z" fill="url(#roof)"/>
<path d="M68 46 Q110 30 152 46 L142 54 H78z" fill="url(#roof)"/>
<path d="M84 34 L110 20 L136 34z" fill="url(#trim)"/>
{top}
<path d="M36 82 q-8 -4 -10 -14 q8 2 14 10z M184 82 q8 -4 10 -14 q-8 2 -14 10z" fill="url(#trim)"/>
<path d="M14 150 H196 Q228 150 236 122 Q242 100 226 96 Q214 96 216 108 Q220 122 204 128 L196 176 H30 Q14 176 14 160z" fill="url(#body)"/>
<path d="M22 158 H192" stroke="url(#trim)" stroke-width="6" stroke-linecap="round"/>
<path d="M32 168 q8 -8 16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="{p['trim']}" stroke-width="2.5"/>
<circle cx="226" cy="106" r="5" fill="url(#gem)" stroke-width="2"/>
<g class="wheel">
<circle cx="110" cy="186" r="36" fill="url(#trim)"/>
<circle cx="110" cy="186" r="26" fill="{p['body_dark']}"/>
<path d="M110 160 V212 M84 186 H136 M92 168 L128 204 M128 168 L92 204" stroke="url(#trim)" stroke-width="5"/>
<circle cx="110" cy="186" r="8" fill="url(#gem)"/>
</g>
</g>"""


def horse():
    """Indra's sky horse: a chubby white pony with tiny wings and a gold crown."""
    return f"""<g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M204 128 Q240 120 262 136" fill="none" stroke="#e8b64c" stroke-width="3"/>
<rect class="leg" x="262" y="160" width="12" height="34" rx="6" fill="#f4f1ff"/>
<rect class="leg b" x="282" y="162" width="12" height="32" rx="6" fill="#dcd6f4"/>
<rect class="leg b" x="318" y="160" width="12" height="34" rx="6" fill="#f4f1ff"/>
<rect class="leg" x="336" y="162" width="12" height="32" rx="6" fill="#dcd6f4"/>
<path d="M254 150 q-26 -6 -30 18 q14 -8 30 -6z" fill="#7ad0ff"/>
<ellipse cx="302" cy="152" rx="52" ry="30" fill="#f4f1ff"/>
<path class="wing" d="M290 132 q-10 -40 22 -50 q-4 14 8 16 q-10 8 2 14 q-14 8 -10 20z" fill="#fff" />
<path d="M336 140 Q346 104 360 92 L380 118 Q368 132 350 154z" fill="#f4f1ff"/>
<ellipse cx="370" cy="98" rx="26" ry="20" fill="#f4f1ff" transform="rotate(18 370 98)"/>
<ellipse cx="386" cy="108" rx="12" ry="9" fill="#ffd6e0"/>
<circle cx="389" cy="106" r="1.8" fill="{INK}"/>
<path d="M346 92 q-6 20 -16 40 q10 -4 12 -10 q2 10 -6 22 q16 -10 22 -32 q-8 -6 -12 -20z" fill="#7ad0ff"/>
<path d="M356 70 L362 84 L370 68 L376 84 L384 72 L382 90 H358z" fill="#f2c14e"/>
<path d="M358 80 l-6 -14 l12 8z" fill="#f4f1ff"/>
<ellipse cx="370" cy="96" rx="4.5" ry="6" fill="{INK}"/><circle cx="372" cy="93" r="1.8" fill="#fff" stroke="none"/>
<path d="M378 116 q6 4 12 0" fill="none" stroke-width="2.5"/>
<circle cx="360" cy="106" r="5" fill="#ff9fb3" stroke="none" opacity=".7"/>
</g>"""


def lion():
    """Lanka's goofy green lion (ราชสีห์) with a fiery mane and a tongue out."""
    return f"""<g stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
<path d="M204 128 Q240 120 262 136" fill="none" stroke="#e8b64c" stroke-width="3"/>
<rect class="leg" x="262" y="160" width="14" height="34" rx="7" fill="#5cc48a"/>
<rect class="leg b" x="282" y="162" width="14" height="32" rx="7" fill="#3f9a6a"/>
<rect class="leg b" x="318" y="160" width="14" height="34" rx="7" fill="#5cc48a"/>
<rect class="leg" x="336" y="162" width="14" height="32" rx="7" fill="#3f9a6a"/>
<path d="M254 148 q-30 -20 -40 4 q12 -4 16 4 q-12 4 -8 14 q16 -12 32 -10z" fill="#ff8a3a"/>
<ellipse cx="302" cy="152" rx="52" ry="30" fill="#5cc48a"/>
<path d="M286 140 q8 -8 18 0 M306 146 q8 -8 18 0" fill="none" stroke="#2f7a52" stroke-width="3"/>
<g fill="#ff8a3a">
<circle cx="350" cy="80" r="16"/><circle cx="378" cy="72" r="16"/><circle cx="398" cy="92" r="14"/>
<circle cx="340" cy="106" r="16"/><circle cx="352" cy="130" r="14"/><circle cx="396" cy="120" r="12"/>
</g>
<circle cx="370" cy="104" r="28" fill="#5cc48a"/>
<path d="M352 84 l-4 -12 l12 6z M384 80 l6 -12 l4 14z" fill="#f2c14e"/>
<ellipse cx="360" cy="96" rx="7" ry="8" fill="#fff"/><ellipse cx="380" cy="94" rx="7" ry="8" fill="#fff"/>
<circle cx="362" cy="98" r="3.5" fill="{INK}"/><circle cx="378" cy="96" r="3.5" fill="{INK}"/>
<path d="M352 86 l14 4 M388 84 l-14 4" stroke-width="3.5"/>
<ellipse cx="372" cy="112" rx="14" ry="9" fill="#9ae6bb"/>
<path d="M362 118 q10 10 22 0" fill="#8c2a20"/>
<path d="M370 120 q4 14 10 0" fill="#ff7a9a"/>
<path d="M364 118 l3 6 l3 -6 M376 118 l3 6 l3 -6" fill="#fff" stroke-width="2"/>
</g>"""


RAMA = dict(body="#f2c14e", body_dark="#9c6418", trim="#f2c14e", trim_dark="#9c6418",
            roof="#3a6ad8", gem="#7ad0ff", flag="#f7f3e6")
LANKA = dict(body="#c22d45", body_dark="#4a1030", trim="#e8b64c", trim_dark="#8a5a18",
             roof="#2b2a4a", gem="#3fd08a", flag="#3fd08a")


def svg(p, steed, flame, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 250" role="img" aria-label="{label}">'
            f"{STYLE}{defs(p)}{clouds()}{chariot(p, flame)}{steed()}</svg>\n")


def main():
    (OUT / "chariot-rama.svg").write_text(svg(RAMA, horse, False, "ราชรถทองของพระราม"), encoding="utf-8")
    (OUT / "chariot-lanka.svg").write_text(svg(LANKA, lion, True, "ราชรถของทศกัณฐ์"), encoding="utf-8")
    print("wrote chariot-rama.svg, chariot-lanka.svg")


if __name__ == "__main__":
    main()
