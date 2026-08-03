"""
render_heatmap_svg.py

Renders data/contributions.json as the classic 53-week x 7-day GitHub
contribution calendar: rounded, colored boxes on a green ramp, revealed
with a diagonal slide-down animation.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "contributions.json"
OUT = Path(__file__).parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 20
LEGEND_H = 26
FOOTER_H = 22

STAGGER = 0.012
CELL_DUR = 0.28

BG = "transparent"
TEXT_DIM = "#8b949e"
TEXT_MAIN = "#c9d1d9"


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def build_week_grid(days: list) -> list:
    by_date = {d["date"]: d["level"] for d in days}
    if not days:
        return []

    start = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    end = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    start_sunday = start - timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cursor = start_sunday
    current_week = []
    while cursor <= end:
        key = cursor.strftime("%Y-%m-%d")
        level = by_date.get(key)
        current_week.append({"date": key, "level": level} if level is not None else None)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
        cursor += timedelta(days=1)
    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    return weeks


def month_labels(weeks: list) -> list:
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            d = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if d.month != last_month:
                labels.append((wi, d.strftime("%b")))
                last_month = d.month
            break
    return labels


def build_svg(payload: dict) -> str:
    days = payload["days"]
    stats = payload.get("stats", {})
    weeks = build_week_grid(days)
    labels = month_labels(weeks)

    num_weeks = len(weeks)
    width = LEFT_PAD + num_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

    best_day = stats.get("best_day", {})
    best_date = best_day.get("date")

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    parts.append(
        f'<style>text{{font-family:"SFMono-Regular",Consolas,'
        f'"Liberation Mono",Menlo,monospace;}}</style>'
    )

    for wi, label in labels:
        x = LEFT_PAD + wi * (CELL + GAP)
        parts.append(
            f'<text x="{x}" y="12" font-size="10" fill="{TEXT_DIM}">{label}</text>'
        )

    weekday_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in weekday_labels.items():
        y = TOP_PAD + row * (CELL + GAP) + CELL - 1
        parts.append(
            f'<text x="0" y="{y}" font-size="9" fill="{TEXT_DIM}">{label}</text>'
        )

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            if day is None:
                continue
            level = day["level"]
            color_idx = min(level, 4)
            color = PALETTE[color_idx]
            if best_date and day["date"] == best_date and level > 0:
                color = PALETTE[5]

            delay = (wi + di) * STAGGER
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0" transform="translate(0,-6)">'
                f'<title>{day["date"]}: level {level}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="{CELL_DUR}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 -6" to="0 0" begin="{delay:.3f}s" dur="{CELL_DUR}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                f'</rect>'
            )

    legend_y = TOP_PAD + 7 * (CELL + GAP) + 16
    parts.append(
        f'<text x="{LEFT_PAD}" y="{legend_y}" font-size="10" '
        f'fill="{TEXT_DIM}">Less</text>'
    )
    legend_x = LEFT_PAD + 34
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{legend_x + i * (CELL + GAP)}" y="{legend_y - CELL + 2}" '
            f'width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{legend_x + len(PALETTE) * (CELL + GAP) + 6}" y="{legend_y}" '
        f'font-size="10" fill="{TEXT_DIM}">More</text>'
    )

    total = stats.get("total_active_days", "?")
    streak = stats.get("current_streak", "?")
    longest = stats.get("longest_streak", "?")
    footer_y = legend_y + 20
    parts.append(
        f'<text x="{LEFT_PAD}" y="{footer_y}" font-size="10" fill="{TEXT_MAIN}">'
        f'{total} active days in the last year &#183; current streak {streak} '
        f'&#183; longest streak {longest}</text>'
    )

    parts.append('</svg>')
    return "".join(parts)


def main():
    if not DATA_PATH.exists():
        print(f"Missing {DATA_PATH}. Run fetch_contributions.py first.")
        raise SystemExit(1)

    payload = load_data()
    svg = build_svg(payload)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()