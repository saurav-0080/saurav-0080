"""
make_info_card.py

Builds a neofetch-style info panel as an animated SVG: a title bar,
then colored key/value rows that fade + slide in with a short stagger.

EDIT THE `FIELDS` LIST BELOW with your own info before running.
"""

import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "info-card.svg"

# ---- EDIT THIS with your own details ----
TITLE = "saurav@github"
FIELDS = [
    ("Now", "Final-year B.Tech CS (Data Science) student"),
    ("Prev", "DevOps & QA tooling -- Docker, Jenkins, Selenium"),
    ("Stack", "Python development, FastAPI, DSA"),
    ("Highlights", "Building Smart File Organizer, active on LeetCode"),
]

STATIC = os.environ.get("STATIC") == "1"

WIDTH = 560
FONT_SIZE = 13
LINE_HEIGHT = 30
PADDING_X = 20
TITLE_BAR_H = 34

KEY_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"

STAGGER = 0.12
ROW_DUR = 0.35


def xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg():
    height = TITLE_BAR_H + len(FIELDS) * LINE_HEIGHT + 24

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">'
    )
    parts.append(
        f'<style>'
        f'.mono{{font-family:"SFMono-Regular",Consolas,'
        f'"Liberation Mono",Menlo,monospace;}}'
        f'.key{{fill:{KEY_COLOR};font-weight:600;}}'
        f'.val{{fill:{VALUE_COLOR};}}'
        f'.dim{{fill:{DIM_COLOR};}}'
        f'</style>'
    )

    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" '
        f'rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}"/>'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TITLE_BAR_H}" '
        f'rx="8" fill="#161b22"/>'
    )
    parts.append(
        f'<rect x="0.5" y="{TITLE_BAR_H / 2:.1f}" width="{WIDTH - 1}" '
        f'height="{TITLE_BAR_H / 2:.1f}" fill="#161b22"/>'
    )
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        cx = PADDING_X + i * 18
        parts.append(f'<circle cx="{cx}" cy="{TITLE_BAR_H/2:.1f}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH/2:.1f}" y="{TITLE_BAR_H/2 + 4:.1f}" '
        f'text-anchor="middle" class="mono dim" font-size="12">'
        f'{xml_escape(TITLE)}</text>'
    )

    key_col_w = max(len(k) for k, _ in FIELDS) * (FONT_SIZE * 0.62) + 10

    for i, (key, val) in enumerate(FIELDS):
        row_y = TITLE_BAR_H + 16 + i * LINE_HEIGHT + FONT_SIZE
        begin = f"{i * STAGGER:.3f}s"

        if not STATIC:
            group_attrs = (
                f' opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-14 0" to="0 0" begin="{begin}" dur="{ROW_DUR}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            )
        else:
            group_attrs = '>'

        parts.append(f'<g{group_attrs}')
        parts.append(
            f'<text x="{PADDING_X}" y="{row_y:.1f}" class="mono key" '
            f'font-size="{FONT_SIZE}">{xml_escape(key)}</text>'
        )
        parts.append(
            f'<text x="{PADDING_X + key_col_w:.1f}" y="{row_y:.1f}" '
            f'class="mono dim" font-size="{FONT_SIZE}">:</text>'
        )
        parts.append(
            f'<text x="{PADDING_X + key_col_w + 14:.1f}" y="{row_y:.1f}" '
            f'class="mono val" font-size="{FONT_SIZE}">{xml_escape(val)}</text>'
        )
        parts.append('</g>')

    parts.append('</svg>')
    return "".join(parts)


def main():
    svg = build_svg()
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved: {OUT}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()