"""
render_heatmap_svg.py — draw data/contributions.json as a 53x7 grid of
rounded boxes, revealed diagonally, with a legend + stats footer.

Usage:
    python scripts/render_heatmap_svg.py

Produces: contrib-heatmap.svg
"""

import json
from datetime import datetime, timedelta

SRC = "data/contributions.json"
OUT = "contrib-heatmap.svg"

PALETTE = [
    "#161b22",  # level 0 — none
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",  # level 5 — neon top end (beyond GitHub's usual 4)
]

CELL = 12
GAP = 3
PAD_LEFT = 30
PAD_TOP = 20
FOOTER_H = 46
WEEKDAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""]


def load_data():
    with open(SRC) as f:
        return json.load(f)


def to_grid(days: list[dict]) -> list[list[dict | None]]:
    """Bucket the flat day list into 53 week-columns x 7 day-rows,
    aligned so each column starts on Sunday."""
    if not days:
        return [[None] * 7 for _ in range(53)]

    parsed = [
        {**d, "dt": datetime.strptime(d["date"], "%Y-%m-%d")}
        for d in days
    ]
    parsed.sort(key=lambda d: d["dt"])

    first = parsed[0]["dt"]
    first_sunday = first - timedelta(days=(first.weekday() + 1) % 7)

    weeks = 53
    grid = [[None] * 7 for _ in range(weeks)]
    for d in parsed:
        offset_days = (d["dt"] - first_sunday).days
        week = offset_days // 7
        weekday = offset_days % 7
        if 0 <= week < weeks:
            grid[week][weekday] = d
    return grid


def build_svg(payload: dict) -> str:
    days = payload.get("days", [])
    stats = payload.get("stats", {})
    grid = to_grid(days)

    weeks = len(grid)
    width = PAD_LEFT + weeks * (CELL + GAP)
    height = PAD_TOP + 7 * (CELL + GAP) + FOOTER_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Consolas, Menlo, monospace" font-size="11">',
        f'<rect width="{width}" height="{height}" fill="transparent"/>',
    ]

    # weekday labels
    for row, label in enumerate(WEEKDAY_LABELS):
        if label:
            y = PAD_TOP + row * (CELL + GAP) + CELL - 2
            parts.append(f'<text x="0" y="{y}" fill="#8b949e">{label}</text>')

    # cells: row-by-row reveal (line by line, top to bottom) — each of the
    # 7 day-rows fills in left-to-right across all 53 weeks before the
    # next row starts
    row_stagger = 0.35    # seconds before the next row begins
    cell_stagger = 0.006  # seconds between cells within a row
    for w, col in enumerate(grid):
        for r, d in enumerate(col):
            level = d["level"] if d else 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = PAD_LEFT + w * (CELL + GAP)
            y = PAD_TOP + r * (CELL + GAP)
            begin = r * row_stagger + w * cell_stagger
            title = ""
            if d:
                count = d.get("count")
                label = f"{count} contributions" if count is not None else ""
                title = f'<title>{label} on {d["date"]}</title>'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" opacity="0" transform="translate(0,-6)">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.3f}s" '
                f'dur="0.25s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0,-6" to="0,0" begin="{begin:.3f}s" dur="0.25s" fill="freeze"/>'
                f"{title}</rect>"
            )

    # legend
    legend_y = height - FOOTER_H + 14
    parts.append(f'<text x="{PAD_LEFT}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = PAD_LEFT + 40
    for c in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y-10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y}" fill="#8b949e">More</text>')

    # stats footer line
    total = stats.get("total_contributions")
    streak = stats.get("current_streak")
    longest = stats.get("longest_streak")
    footer_bits = []
    if total is not None:
        footer_bits.append(f"{total:,} contributions in the last year")
    if streak is not None:
        footer_bits.append(f"current streak: {streak}d")
    if longest is not None:
        footer_bits.append(f"longest streak: {longest}d")
    footer_text = "  ·  ".join(footer_bits) if footer_bits else "no data yet — run fetch_contributions.py"

    parts.append(
        f'<text x="{PAD_LEFT}" y="{height-8}" fill="#c9d1d9">{footer_text}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    payload = load_data()
    svg = build_svg(payload)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
