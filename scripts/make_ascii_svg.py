"""
Convert a portrait photo into a CLEAN, monochrome ASCII-art SVG (Andrew6rant
style: one light-gray color, subject isolated on a dark background) that "types"
itself in like a terminal, then holds.

Monochrome is deliberate -- per-character rainbow color is what makes ASCII
portraits look noisy. One fill color + a good density ramp + high contrast (so a
busy background washes out to blank) reads as neat and legible.

GitHub renders SVGs embedded via <img> and runs their SMIL animations there (JS
does not run). Each row is revealed with a left-to-right clip wipe plus a small
block cursor riding the wipe edge, staggered top -> bottom, so the whole
portrait prints once and freezes.
"""
import html
import os
import sys

import png

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "avi-ascii.svg")

COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"

GAMMA = 1.18
WHITE_FLOOR = 0.80
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"
ROW_DUR = 0.11
STAGGER = 0.11


def read_grayscale_png(path):
    reader = png.Reader(filename=path)
    width, height, pixels, metadata = reader.read()
    rows = []
    greyscale = metadata.get("greyscale", False)
    alpha = metadata.get("alpha", False)

    if greyscale and not alpha:
        for row in pixels:
            rows.append([int(v) for v in row])
    elif greyscale and alpha:
        for row in pixels:
            row = list(row)
            row_out = []
            for i in range(0, len(row), 2):
                lum = int((row[i] * row[i+1] + 255 * (255 - row[i+1])) / 255.0 + 0.5)
                row_out.append(lum)
            rows.append(row_out)
    elif not greyscale and not alpha:
        for row in pixels:
            row = list(row)
            rows.append([int((0.299 * row[i] + 0.587 * row[i+1] + 0.114 * row[i+2]) + 0.5)
                         for i in range(0, len(row), 3)])
    else:
        for row in pixels:
            row = list(row)
            row_out = []
            for i in range(0, len(row), 4):
                alpha_val = row[i + 3] / 255.0
                r = row[i] * alpha_val + 255 * (1.0 - alpha_val)
                g = row[i+1] * alpha_val + 255 * (1.0 - alpha_val)
                b = row[i+2] * alpha_val + 255 * (1.0 - alpha_val)
                row_out.append(int((0.299 * r + 0.587 * g + 0.114 * b) + 0.5))
            rows.append(row_out)
    return width, height, rows


def resize_nn(pixels, src_w, src_h, dst_w, dst_h):
    out = []
    for y in range(dst_w if False else dst_h):
        src_y = min(src_h - 1, int(y * src_h / dst_h))
        row = pixels[src_y]
        out.append([row[min(src_w - 1, int(x * src_w / dst_w))] for x in range(dst_w)])
    return out


STATIC = bool(os.environ.get("STATIC"))

width, height, image = read_grayscale_png(SRC)
image = resize_nn(image, width, height, COLS, ROWS)
rows_txt = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        lum = image[y][x] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            line.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        line.append(RAMP[idx])
    rows_txt.append("".join(line))

art_top = TITLEBAR_H + PAD * 0.35
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    f'</linearGradient></defs>',
    f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">ibrahim@github: ~$ ./portrait.sh</text>')

for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{CELL_H * 0.86:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')
    if STATIC:
        parts.append(text)
        continue
    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'ibrahim@github:~$ whoami <tspan fill="{INK}">Ibrahim Naseef</tspan></text>')
parts.append(f'<rect x="{PAD+196}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')
parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
