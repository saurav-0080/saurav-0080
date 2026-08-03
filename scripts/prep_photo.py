"""
prep_photo.py

Takes a normal photo and prepares it for ASCII conversion:
  1. Removes the background (rembg) so only the subject remains.
  2. Applies GLOBAL contrast stretching so a flatly-lit face gets some
     punch (otherwise it converts to a dark, muddy blob). Deliberately
     NOT using local/adaptive contrast (e.g. CLAHE) -- that amplifies
     every small variation (hair strands, stubble, fabric weave) into
     per-pixel noise, which wrecks the ASCII conversion once the image
     gets downsampled to a small character grid.
  3. Composites the result onto pure white, so the background maps to
     the blank end of the ASCII ramp (white -> space character).

Run once per photo, whenever you change your picture:
    python scripts/prep_photo.py source-photo.jpg

Output: scripts/source-prepped.png (grayscale, ready for make_ascii_svg.py)
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from rembg import remove

OUTPUT_PATH = Path(__file__).parent / "source-prepped.png"

MAX_DIM = 900


def load_and_resize(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = MAX_DIM / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


def remove_background(img: Image.Image) -> Image.Image:
    """Returns an RGBA image with the background made transparent."""
    return remove(img)


def composite_on_white(rgba: Image.Image) -> Image.Image:
    """Flattens an RGBA image onto a solid white background."""
    white_bg = Image.new("RGB", rgba.size, (255, 255, 255))
    white_bg.paste(rgba, mask=rgba.split()[3])
    return white_bg


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    if not src_path.exists():
        print(f"File not found: {src_path}")
        sys.exit(1)

    print("Loading photo...")
    img = load_and_resize(src_path)

    print("Removing background (this can take 10-30s on first run, "
          "it downloads a small model)...")
    no_bg = remove_background(img)

    print("Compositing onto white...")
    on_white = composite_on_white(no_bg)

    print("Converting to grayscale + global contrast stretch...")
    gray = on_white.convert("L")
    contrasted = ImageOps.autocontrast(gray, cutoff=1)

    contrasted_arr = np.array(contrasted)
    alpha = np.array(no_bg.split()[3])
    contrasted_arr = np.where(alpha > 10, contrasted_arr, 255).astype("uint8")

    out = Image.fromarray(contrasted_arr)
    out.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()