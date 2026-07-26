"""
fetch_contributions.py
Scrapes the public contribution calendar HTML fragment GitHub serves at
https://github.com/users/<username>/contributions — no GraphQL API, no
personal access token needed. Writes data/contributions.json with raw
days plus derived stats (current streak, longest streak, best day,
monthly totals).

Usage:
    python scripts/fetch_contributions.py [username]
"""

import sys
import json
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "Ibrahim-Naseef"
OUT_PATH = "data/contributions.json"


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []
    # GitHub renders each day as a <td> with class "ContributionCalendar-day"
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        level = td.get("data-level")
        if d is None:
            continue
        days.append({"date": d, "level": int(level) if level is not None else 0})
    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    # current streak: walk backwards from most recent day while level > 0
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest_streak = 0
    running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda x: x["level"])
    total = sum(1 for d in days if d["level"] > 0)

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day["date"],
        "active_days_last_year": total,
        "monthly_active_days": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    html = fetch_html(username)
    days = parse_days(html)
    stats = derive_stats(days)

    payload = {"username": username, "days": days, "stats": stats}

    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {OUT_PATH}: {len(days)} days, streak={stats.get('current_streak')}")


if __name__ == "__main__":
    main()
