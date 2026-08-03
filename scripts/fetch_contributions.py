"""
fetch_contributions.py

Pulls a GitHub user's public contribution calendar WITHOUT the GraphQL
API and WITHOUT a personal access token, by scraping the public HTML
fragment GitHub itself uses for the profile page.
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "saurav-0080")
OUT = Path(__file__).parent.parent / "data" / "contributions.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        cells = soup.select("rect.ContributionCalendar-day")
    if not cells:
        raise RuntimeError(
            "No contribution cells found -- GitHub may have changed the "
            "markup for this endpoint."
        )

    days = []
    for cell in cells:
        d = cell.get("data-date")
        level = cell.get("data-level")
        if d is None or level is None:
            continue
        days.append({"date": d, "level": int(level)})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days: list) -> dict:
    if not days:
        return {}

    total = sum(1 for d in days if d["level"] > 0)
    longest = 0
    running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    by_date = {d["date"]: d["level"] for d in days}
    cursor = date.today()
    streak = 0
    while True:
        key = cursor.strftime("%Y-%m-%d")
        if key not in by_date:
            cursor -= timedelta(days=1)
            continue
        if by_date[key] > 0:
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break

    best = max(days, key=lambda d: (d["level"], d["date"]))

    monthly = {}
    for d in days:
        month_key = d["date"][:7]
        monthly[month_key] = monthly.get(month_key, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_active_days": total,
        "longest_streak": longest,
        "current_streak": streak,
        "best_day": best,
        "monthly_active_days": monthly,
    }


def main():
    username = USERNAME
    print(f"Fetching contribution calendar for '{username}'...")
    try:
        html = fetch_html(username)
        days = parse_days(html)
    except Exception as e:
        print(f"Fetch/parse failed: {e}", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(days)} days -> {OUT}")
    print(f"Stats: {stats.get('total_active_days')} active days, "
          f"streak {stats.get('current_streak')}, "
          f"longest {stats.get('longest_streak')}")


if __name__ == "__main__":
    main()