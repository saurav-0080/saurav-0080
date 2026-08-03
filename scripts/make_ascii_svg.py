"""
make_ascii_svg.py

Converts scripts/source-prepped.png (output of prep_photo.py) into an
animated, self-typing, monochrome ASCII-art SVG.
"""

from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(__file__).parent / "source-prepped.png"
OUT = Path(__file__).parent.parent / "avi-ascii.svg"

RAMP = " .`:-=+*cs#%@"

NUM_COLS = 100
FONT_SIZE = 8
CHAR_ASPECT = 0.55
FILL_COLOR = "#9aa5b1"
BG_COLOR = "transparent"
ROW_DELAY = 0.045
ROW_DURATION = 0.35


def image_to_char_grid(img, num_cols):
    w, h = img.size
    char_w = w / num_cols
    num_rows = max(1, round((h / char_w) * CHAR_ASPECT))
    small = img.resize((num_cols, num_rows), Image.LANCZOS)
    arr = np.array(small).astype("float32")

    ramp_len = len(RAMP)
    rows = []
    for y in range(num_rows):
        line_chars = []
        for x in range(num_cols):
            brightness = arr[y, x] / 255.0
            idx = int((1.0 - brightness) * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            line_chars.append(RAMP[idx])
        rows.append("".join(line_chars))
    return rows


def xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows):
    num_rows = len(rows)
    num_cols = max(len(r) for r in rows)
    cell_w = FONT_SIZE * CHAR_ASPECT
    cell_h = FONT_SIZE * 1.0

    width = num_cols * cell_w
    height = num_rows * cell_h

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width:.1f} {height:.1f}" '
        f'width="{width:.0f}" height="{height:.0f}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>')
    parts.append(
        f'<style>text{{font-family:"SFMono-Regular",Consolas,'
        f'"Liberation Mono",Menlo,monospace;font-size:{FONT_SIZE}px;'
        f'fill:{FILL_COLOR};white-space:pre;}}</style>'
    )

    for i, row_text in enumerate(rows):
        row_width = len(row_text) * cell_w
        y = (i + 1) * cell_h - (cell_h * 0.25)
        begin = f"{i * ROW_DELAY:.3f}s"
        clip_id = f"clip{i}"

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{i * cell_h:.1f}" height="{cell_h:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_width:.1f}" '
            f'begin="{begin}" dur="{ROW_DURATION}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'</rect>'
        )
        parts.append('</clipPath>')

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'<text x="0" y="{y:.1f}">{xml_escape(row_text)}</text>')
        parts.append('</g>')

        cursor_size = cell_h * 0.75
        parts.append(
            f'<rect x="0" y="{i * cell_h + cell_h * 0.1:.1f}" '
            f'width="{cell_w:.1f}" height="{cursor_size:.1f}" '
            f'fill="{FILL_COLOR}" opacity="0.9">'
            f'<animate attributeName="x" from="0" to="{row_width:.1f}" '
            f'begin="{begin}" dur="{ROW_DURATION}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" from="0.9" to="0" '
            f'begin="{i * ROW_DELAY + ROW_DURATION:.3f}s" dur="0.15s" '
            f'fill="freeze"/>'
            f'</rect>'
        )

    parts.append('</svg>')
    return "".join(parts)


def main():
    if not SRC.exists():
        print(f"Missing {SRC}. Run prep_photo.py first.")
        raise SystemExit(1)

    img = Image.open(SRC).convert("L")
    rows = image_to_char_grid(img, NUM_COLS)
    svg = build_svg(rows)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved: {OUT}  ({len(rows)} rows x {NUM_COLS} cols)")


if __name__ == "__main__":
    main()