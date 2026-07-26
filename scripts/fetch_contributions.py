"""
fetch_contributions.py — scrape the public contribution calendar HTML.

No GraphQL API, no personal access token. GitHub serves the calendar
as a public HTML fragment at:

    https://github.com/users/<username>/contributions

Usage:
    python scripts/fetch_contributions.py

Produces: data/contributions.json
"""

import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = "Ibrahim-Naseef"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = "data/contributions.json"

COUNT_RE = re.compile(r"^(No|\d[\d,]*)\s+contributions?")


def fetch_html() -> str:
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    # tool-tips hold the human-readable "N contributions on <date>" text,
    # keyed by the day cell's id via the `for` attribute
    counts_by_id = {}
    for tip in soup.select("tool-tip"):
        target_id = tip.get("for")
        text = tip.get_text(strip=True)
        m = COUNT_RE.match(text)
        if target_id and m:
            n = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
            counts_by_id[target_id] = n

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        level = td.get("data-level")
        if date is None or level is None:
            continue
        cell_id = td.get("id")
        count = counts_by_id.get(cell_id, None)
        days.append({"date": date, "level": int(level), "count": count})
    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total_contributions = sum(d["count"] or 0 for d in days)
    total = sum(1 for d in days if d["level"] > 0)
    longest = current = 0
    running = 0
    today = datetime.utcnow().date().isoformat()
    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    for d in reversed(days):
        if d["level"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda d: d["level"], default=None)

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_contributions": total_contributions,
        "active_days": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day["date"] if best_day else None,
        "monthly_active_days": monthly,
        "generated_at": today,
    }


def main():
    html = fetch_html()
    days = parse_days(html)
    stats = derive_stats(days)
    payload = {"username": USERNAME, "days": days, "stats": stats}

    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {OUT} ({len(days)} days)")


if __name__ == "__main__":
    main()
