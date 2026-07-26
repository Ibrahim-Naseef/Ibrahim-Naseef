"""
prep_photo.py
Run locally (needs rembg, opencv-python, numpy, pillow) whenever the source
photo changes. Produces `source-prepped.png`, a background-free, contrast-
boosted grayscale image composited onto pure white — the ideal input for
make_ascii_svg.py's brightness-to-glyph mapping.

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep(src_path: str, out_path: str = "source-prepped.png") -> None:
    # 1. Remove the background so only the subject remains
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    cutout_bytes = remove(input_bytes)  # returns PNG bytes with alpha channel

    with open("_cutout_tmp.png", "wb") as f:
        f.write(cutout_bytes)

    cutout = Image.open("_cutout_tmp.png").convert("RGBA")

    # 2. Composite onto pure white so background maps to the blank end
    #    of the ASCII ramp (white -> space character)
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("RGB")

    # 3. Boost local contrast with CLAHE so a flatly-lit face gets real
    #    highlights and shadows instead of converting to a dark blob
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(out_path)
    print(f"Wrote {out_path} ({enhanced.shape[1]}x{enhanced.shape[0]})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <source-photo>")
        sys.exit(1)
    prep(sys.argv[1])
