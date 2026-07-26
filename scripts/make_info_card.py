"""
make_info_card.py — neofetch-style info panel that fades in line by line.

Usage:
    python scripts/make_info_card.py
    STATIC=0 python scripts/make_info_card.py   # explicit animation mode if needed

Produces: info-card.svg

Edit the CONTENT block below to change what shows on the card — this is
the "story numbers can't tell" panel, so keep it to a handful of lines.
"""

import os

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

TITLE = "ibrahim@devops"
WIDTH = 490
LINE_H = 26
PAD_X = 24
PAD_TOP = 56

# label, value, accent color for the label
CONTENT = [
    ("Role",           "DevOps Engineer @ TCS",              "#58a6ff"),
    ("Designation",         "System Engineer, Aug 2024 - Present", "#58a6ff"),
    ("Now",          "Learning Agentic AI",                 "#3fb950"),
    ("CI/CD",        "Azure DevOps, Jenkins, Git",           "#e3b341"),
    ("Cloud & IaC",  "AWS, Terraform, AWS CDK",               "#e3b341"),
    ("Containers",   "Docker",                                "#e3b341"),
    ("Scripting",    "Python, Linux Shell",                   "#e3b341"),
    ("Database",     "MySQL",                                  "#e3b341"),
    ("Certifications",        "AWS SAA · Azure AZ-900 · AZ-204",        "#f778ba"),
]


HEIGHT = PAD_TOP + LINE_H * len(CONTENT) + 24


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="xMidYMid meet" '
        f'font-family="Consolas, Menlo, monospace" font-size="13">',
        "<defs>",
        '<clipPath id="cardclip"><rect x="0" y="0" width="' + str(WIDTH) +
        '" height="' + str(HEIGHT) + '" rx="10"/></clipPath>',
        "</defs>",
        f'<g clip-path="url(#cardclip)">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#0d1117"/>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="none" stroke="#30363d" stroke-width="1"/>',
        # title bar
        f'<rect x="0" y="0" width="{WIDTH}" height="34" fill="#161b22"/>',
        '<circle cx="20" cy="17" r="6" fill="#ff5f56"/>',
        '<circle cx="40" cy="17" r="6" fill="#ffbd2e"/>',
        '<circle cx="60" cy="17" r="6" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="21" fill="#8b949e" text-anchor="middle" font-size="12">{TITLE}</text>',
        f'<text x="{WIDTH - PAD_X}" y="21" fill="#8b949e" text-anchor="end" font-size="12">loading</text>',
        '<g transform="translate(0,0)">',
        f'<circle cx="{WIDTH - PAD_X - 18}" cy="17" r="3" fill="#58a6ff" opacity="0.35">',
        f'<animate attributeName="opacity" values="0.35;1;0.35" dur="1.0s" begin="0s" repeatCount="indefinite"/></circle>',
        f'<circle cx="{WIDTH - PAD_X - 8}" cy="17" r="3" fill="#58a6ff" opacity="0.35">',
        f'<animate attributeName="opacity" values="0.35;1;0.35" dur="1.0s" begin="0.2s" repeatCount="indefinite"/></circle>',
        f'<circle cx="{WIDTH - PAD_X + 2}" cy="17" r="3" fill="#58a6ff" opacity="0.35">',
        f'<animate attributeName="opacity" values="0.35;1;0.35" dur="1.0s" begin="0.4s" repeatCount="indefinite"/></circle>',
        '</g>',
    ]

    for i, (label, value, color) in enumerate(CONTENT):
        y = PAD_TOP + i * LINE_H
        label_txt = escape(label)
        value_txt = escape(value)
        line = (
            f'<tspan fill="{color}" font-weight="bold">{label_txt}</tspan>'
            f'<tspan fill="#c9d1d9">: {value_txt}</tspan>'
        )
        if STATIC:
            parts.append(f'<text x="{PAD_X}" y="{y}" xml:space="preserve">{line}</text>')
        else:
            start = 0.4 + i * 0.12
            parts.append(
                f'<g opacity="1" transform="translate(0,0)">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{start:.2f}s" '
                f'dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8,0" to="0,0" begin="{start:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<text x="{PAD_X}" y="{y}" xml:space="preserve">{line}</text>'
                f"</g>"
            )

    # accent divider under the "OS" line to mimic neofetch color swatches
    swatch_y = HEIGHT - 20
    colors = ["#f85149", "#3fb950", "#e3b341", "#58a6ff", "#bc8cff", "#39d9d9"]
    for i, c in enumerate(colors):
        parts.append(f'<rect x="{PAD_X + i*18}" y="{swatch_y}" width="14" height="14" rx="3" fill="{c}"/>')

    parts.append("</g></svg>")
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()