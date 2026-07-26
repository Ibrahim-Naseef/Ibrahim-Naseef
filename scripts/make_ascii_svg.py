"""
make_ascii_svg.py
Converts source-prepped.png into avi-ascii.svg: a monochrome ASCII portrait
that "types" itself in row by row via SMIL clip-path animation.

Usage:
    python scripts/make_ascii_svg.py
"""

import numpy as np
from PIL import Image

SRC = "source-prepped.png"
OUT = "avi-ascii.svg"

COLS = 100
ROWS = 53

# bright (sparse) -> dark (dense); leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL = "#8b949e"          # single light-gray fill, no rainbow-per-char
BG = "transparent"
ROW_DELAY = 0.045          # stagger between rows, seconds
WIPE_DUR = 0.5             # how long each row's wipe takes


def image_to_ascii(path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("L").resize((cols, rows))
    arr = np.array(img, dtype=np.float32) / 255.0  # 0=black,1=white
    lines = []
    ramp_len = len(RAMP) - 1
    for y in range(rows):
        row_chars = []
        for x in range(cols):
            brightness = arr[y, x]
            idx = int((1 - brightness) * ramp_len)  # bright -> low idx (space)
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(lines: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    total_dur = ROWS * ROW_DELAY + WIPE_DUR

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')

    for i, line in enumerate(lines):
        y = (i + 1) * CHAR_H
        begin = round(i * ROW_DELAY, 3)
        clip_id = f"clip{i}"
        text_esc = escape(line)

        # clip rect wipes left -> right over WIPE_DUR, then freezes full width
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{y - CHAR_H:.1f}" width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{width:.0f}" '
            f'begin="{begin}s" dur="{WIPE_DUR}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0 0.2 1"/>'
            f"</rect>"
        )
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'<text x="0" y="{y:.1f}" fill="{FILL}" xml:space="preserve">{text_esc}</text>'
        )
        # small block cursor riding the wipe edge, fades out once the row is done
        parts.append(
            f'<rect x="0" y="{y - CHAR_H:.1f}" width="{CHAR_W:.1f}" height="{CHAR_H:.1f}" '
            f'fill="{FILL}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.05;0.9;1" begin="{begin}s" dur="{WIPE_DUR}s" fill="freeze"/>'
            f'<animateMotion path="M0,0 H{width:.0f}" begin="{begin}s" '
            f'dur="{WIPE_DUR}s" fill="freeze"/>'
            f"</rect>"
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    lines = image_to_ascii(SRC, COLS, ROWS)
    svg = build_svg(lines)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({COLS}x{ROWS} chars, total animation ~{ROWS*ROW_DELAY+WIPE_DUR:.1f}s)")
