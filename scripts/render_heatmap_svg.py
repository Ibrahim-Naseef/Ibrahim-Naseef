"""
render_heatmap_svg.py
Renders data/contributions.json as the classic 53-week x 7-day calendar of
rounded boxes, revealed once with a diagonal slide-down (CSS keyframes,
no looping), plus a legend and a stats footer line.

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
from datetime import datetime, timedelta

DATA_PATH = "data/contributions.json"
OUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# none -> brightest (level 5 is a neon top end, level 0-4 mirror GitHub's own ramp)

CELL = 11
GAP = 3
LEFT_PAD = 30   # room for day-of-week labels
TOP_PAD = 20    # room for month labels
FOOTER_H = 26
LEGEND_H = 20


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_grid(days: list[dict]):
    """Bucket days into a week-major 53x7 grid keyed by (week_index, weekday)."""
    if not days:
        return {}, []
    parsed = [
        {"date": datetime.strptime(d["date"], "%Y-%m-%d"), "level": d["level"]}
        for d in days
    ]
    parsed.sort(key=lambda x: x["date"])
    start = parsed[0]["date"]
    # align to the preceding Sunday so columns are full weeks
    start -= timedelta(days=(start.weekday() + 1) % 7)

    grid = {}
    month_labels = []  # (week_index, label) for months that start a new column
    seen_months = set()
    for d in parsed:
        delta = (d["date"] - start).days
        week = delta // 7
        weekday = delta % 7  # 0=Sun .. 6=Sat
        grid[(week, weekday)] = d["level"]

        key = (d["date"].year, d["date"].month)
        if key not in seen_months and d["date"].day <= 7:
            seen_months.add(key)
            month_labels.append((week, d["date"].strftime("%b")))

    return grid, month_labels


def build_svg(payload: dict) -> str:
    days = payload["days"]
    stats = payload.get("stats", {})
    grid, month_labels = build_grid(days)

    weeks = (max(w for w, _ in grid.keys()) + 1) if grid else 53
    width = LEFT_PAD + weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="10">'
    )
    parts.append(
        "<style>"
        ".cell{opacity:0;animation:reveal .5s ease forwards;}"
        "@keyframes reveal{to{opacity:1;}}"
        "</style>"
    )
    parts.append(f'<rect width="100%" height="100%" fill="transparent"/>')

    # month labels
    for week, label in month_labels:
        x = LEFT_PAD + week * (CELL + GAP)
        parts.append(f'<text x="{x}" y="{TOP_PAD-6}" fill="#8b949e">{label}</text>')

    # day-of-week labels (Mon/Wed/Fri like GitHub's own graph)
    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for wd, label in dow_labels.items():
        y = TOP_PAD + wd * (CELL + GAP) + CELL - 1
        parts.append(f'<text x="0" y="{y}" fill="#8b949e">{label}</text>')

    # cells, diagonal stagger: delay based on week + weekday
    max_delay_units = weeks + 7
    for (week, weekday), level in grid.items():
        x = LEFT_PAD + week * (CELL + GAP)
        y = TOP_PAD + weekday * (CELL + GAP)
        color = PALETTE[min(level, len(PALETTE) - 1)]
        delay = ((week + weekday) / max_delay_units) * 1.6  # spread reveal over ~1.6s
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s"/>'
        )

    # legend
    legend_y = TOP_PAD + 7 * (CELL + GAP) + 14
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 34
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y-9}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y}" fill="#8b949e">More</text>')

    # stats footer
    active = stats.get("active_days_last_year", "?")
    streak = stats.get("current_streak", "?")
    longest = stats.get("longest_streak", "?")
    footer = f"{active} active days in the last year  ·  current streak {streak}  ·  longest streak {longest}"
    parts.append(
        f'<text x="{LEFT_PAD}" y="{height-8}" fill="#c9d1d9" font-size="11">{footer}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    payload = load_data()
    svg = build_svg(payload)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT}")
