"""
prep_photo.py — one-time photo prep for the ASCII portrait.

Usage:
    python scripts/prep_photo.py source-photo.png

Produces: source-prepped.png (grayscale, white background, contrast-boosted)

Pipeline:
  1. (optional) remove the background with rembg, if installed
  2. boost local contrast with CLAHE so a flat face gets real
     highlights/shadows
  3. composite onto pure white so the background maps to the blank
     end of the ASCII ramp (white -> spaces)
"""

import sys
import numpy as np
import cv2
from PIL import Image


def remove_background(img: Image.Image) -> Image.Image:
    """Try rembg if it's installed; otherwise return the image unchanged.
    A plain, evenly lit background (like a light blue/white studio shot)
    works fine without this step."""
    try:
        from rembg import remove
        return remove(img).convert("RGBA")
    except ImportError:
        print("rembg not installed — skipping background removal "
              "(fine if your background is already plain/light).")
        return img.convert("RGBA")


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def composite_on_white(rgba: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, rgba).convert("RGB")


def main(src_path: str, out_path: str = "source-prepped.png"):
    img = Image.open(src_path)
    img = remove_background(img)
    img = composite_on_white(img)

    gray = np.array(img.convert("L"))
    gray = apply_clahe(gray)

    Image.fromarray(gray).save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    main(src)
