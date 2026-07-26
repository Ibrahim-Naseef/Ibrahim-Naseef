"""
make_info_card.py
Hand-authored neofetch-style SVG panel: title bar + colored key/value rows,
each fading/sliding in on a stagger. Set STATIC=1 to emit a frozen frame
(useful for local Quick Look previews / thumbnails).

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
"""

import os

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

WIDTH = 490
ROW_H = 26
TITLE_H = 34
PAD_X = 20

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BG = "#161b22"
DOT_RED, DOT_YEL, DOT_GRN = "#ff5f56", "#ffbd2e", "#27c93f"
KEY_COLOR = "#39d353"      # green, like a shell prompt var
VAL_COLOR = "#c9d1d9"
LABEL_COLOR = "#8b949e"
FONT = "Consolas, Menlo, monospace"

# (label, value) rows — this is the part that tells the story the
# contribution graph can't: current focus, what's next, stack, highlights.
ROWS = [
    ("user", "ibrahim@dev ~ %"),
    ("Now", "Dental X-Ray Age Prediction (Deep Learning)"),
    ("Next", "Learning MERN stack"),
    ("Help wanted", "Java Fullstack"),
    ("Stack", "Java · Python · JS · React · Django"),
    ("ML/Data", "TensorFlow · Keras · NumPy · Pandas"),
    ("Fun fact", "Bugs are part of life."),
]

HEIGHT = TITLE_H + len(ROWS) * ROW_H + 20


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}" font-size="13">'
    )

    # window chrome
    parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1"/>'
    )
    parts.append(
        f'<rect x="0" y="0" width="{WIDTH}" height="{TITLE_H}" rx="8" fill="{TITLE_BG}"/>'
    )
    parts.append(f'<rect x="0" y="{TITLE_H-8}" width="{WIDTH}" height="8" fill="{TITLE_BG}"/>')
    for i, color in enumerate([DOT_RED, DOT_YEL, DOT_GRN]):
        parts.append(f'<circle cx="{18 + i*18}" cy="{TITLE_H/2:.0f}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH/2:.0f}" y="{TITLE_H/2+4:.0f}" text-anchor="middle" '
        f'fill="{LABEL_COLOR}" font-size="12">neofetch</text>'
    )

    fade_dur = 0.35
    stagger = 0.12

    for i, (label, value) in enumerate(ROWS):
        y = TITLE_H + 20 + i * ROW_H
        begin = round(i * stagger, 3)
        label_esc = escape(label)
        value_esc = escape(value)

        group_attrs = ""
        anim = ""
        if not STATIC:
            group_attrs = 'opacity="0"'
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}s" dur="{fade_dur}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-12,0" to="0,0" begin="{begin}s" dur="{fade_dur}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>'
            )

        parts.append(f'<g {group_attrs}>')
        parts.append(anim)
        if i == 0:
            # first row styled like a shell prompt line, not a key/value pair
            parts.append(
                f'<text x="{PAD_X}" y="{y}" fill="{KEY_COLOR}">{value_esc}</text>'
            )
        else:
            parts.append(
                f'<text x="{PAD_X}" y="{y}" fill="{KEY_COLOR}">{label_esc}</text>'
            )
            parts.append(
                f'<text x="{PAD_X + 118}" y="{y}" fill="{VAL_COLOR}">{value_esc}</text>'
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({'static' if STATIC else 'animated'})")
