"""
make_ascii_svg.py — turn source-prepped.png into a self-typing ASCII SVG.

Usage:
    python scripts/make_ascii_svg.py

Produces: ibrahim-ascii.svg
"""

import numpy as np
from PIL import Image

SRC = "source-prepped.png"
OUT = "ibrahim-ascii.svg"

COLS = 100
ROWS = 53
FONT_SIZE = 9
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL = "#8b949e"  # single light-gray tone — no per-char rainbow

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing


def image_to_grid(path: str, cols: int, rows: int) -> list[str]:
    img = Image.open(path).convert("L").resize((cols, rows))
    arr = np.array(img)
    n = len(RAMP) - 1
    lines = []
    for row in arr:
        line = "".join(RAMP[int((255 - px) / 255 * n)] for px in row)
        lines.append(line)
    return lines


def escape(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(lines: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">',
        "<style>",
        ".row { }",
        ".cursor { fill: #58a6ff; }",
        "</style>",
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="transparent"/>',
    ]

    stagger = 0.018  # seconds between row starts
    row_dur = 0.55    # seconds for a row to fully wipe in

    for r, line in enumerate(lines):
        y = (r + 1) * CHAR_H
        start = r * stagger
        row_id = f"row{r}"
        text_content = "".join(escape(c) for c in line)

        # clip-path that wipes left -> right over the row's duration
        clip_id = f"clip{r}"
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{y - CHAR_H:.1f}" '
            f'width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{width:.0f}" '
            f'begin="{start:.3f}s" dur="{row_dur}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f"</rect></clipPath>"
        )
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y:.1f}" fill="{FILL}" xml:space="preserve">{text_content}</text>'
            f"</g>"
        )
        # small cursor block riding the wipe edge
        parts.append(
            f'<rect class="cursor" y="{y - CHAR_H:.1f}" width="{CHAR_W:.1f}" height="{CHAR_H:.1f}" '
            f'opacity="0">'
            f'<animate attributeName="x" from="0" to="{width - CHAR_W:.0f}" '
            f'begin="{start:.3f}s" dur="{row_dur}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.9;1" '
            f'begin="{start:.3f}s" dur="{row_dur}s" fill="freeze"/>'
            f"</rect>"
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    lines = image_to_grid(SRC, COLS, ROWS)
    svg = build_svg(lines)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
