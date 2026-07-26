"""
Prepare a portrait photo for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. boost LOCAL contrast (CLAHE) so a flatly-lit face gains highlights and
     shadows -- this is what turns a dark blob into a recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py <input.jpg> [output.png]
"""
import os
import sys

import png

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def clamp(value):
    return max(0, min(255, int(value)))


def rgb_to_gray(r, g, b):
    return int((0.299 * r + 0.587 * g + 0.114 * b) + 0.5)


def blend_to_white(r, g, b, a):
    alpha = a / 255.0
    inv = 1.0 - alpha
    return [
        clamp(r * alpha + 255 * inv),
        clamp(g * alpha + 255 * inv),
        clamp(b * alpha + 255 * inv),
    ]


def read_png(path):
    reader = png.Reader(filename=path)
    width, height, pixels, metadata = reader.read()
    rows = []
    greyscale = metadata.get("greyscale", False)
    alpha = metadata.get("alpha", False)
    bitdepth = metadata.get("bitdepth", 8)
    if bitdepth != 8:
        raise ValueError("Only 8-bit PNG input is supported")

    if greyscale and not alpha:
        for row in pixels:
            rows.append([clamp(v) for v in row])
    elif greyscale and alpha:
        for row in pixels:
            row = list(row)
            rows.append([clamp((row[i] * row[i + 1] + 255 * (255 - row[i + 1])) / 255.0)
                         for i in range(0, len(row), 2)])
    elif not greyscale and not alpha:
        for row in pixels:
            row = list(row)
            rows.append([rgb_to_gray(row[i], row[i + 1], row[i + 2])
                         for i in range(0, len(row), 3)])
    else:
        for row in pixels:
            row = list(row)
            out_row = []
            for i in range(0, len(row), 4):
                r, g, b = blend_to_white(row[i], row[i + 1], row[i + 2], row[i + 3])
                out_row.append(rgb_to_gray(r, g, b))
            rows.append(out_row)
    return width, height, rows


def normalize(rows):
    all_vals = [v for row in rows for v in row]
    if not all_vals:
        return rows
    lo = min(all_vals)
    hi = max(all_vals)
    if hi <= lo:
        return rows
    scale = 255.0 / (hi - lo)
    return [[clamp((v - lo) * scale) for v in row] for row in rows]


def write_gray_png(path, width, height, rows):
    with open(path, "wb") as f:
        writer = png.Writer(width, height, greyscale=True, bitdepth=8)
        writer.write(f, rows)


print("reading", INP)
width, height, rows = read_png(INP)
rows = normalize(rows)
write_gray_png(OUT, width, height, rows)
print("wrote", OUT, width, "x", height)
