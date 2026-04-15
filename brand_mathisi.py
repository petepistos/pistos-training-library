#!/usr/bin/env python3
"""
Mathisi branding script — applies Pistos brand colors, taller topbar,
and the real logo to every .html file in the pistos-training-library repo.
"""

import re
from pathlib import Path

BRAND_NAVY = "#1B2A4A"
BRAND_NAVY_DARK = "#0F1E33"
BRAND_CREAM = "#F5F1EB"
BRAND_CREAM_DARK = "#EDE8E0"
BRAND_GOLD = "#C4AA88"
BRAND_GOLD_DARK = "#A08860"
BRAND_BORDER = "#D6CCBC"
BRAND_TEXT_DARK = "#2E2A25"
BRAND_TEXT_MID = "#5A4E3F"
BRAND_TEXT_MUTED = "#8A7D6B"

COLOR_MAP = {
    "#9b7fe8": BRAND_NAVY,
    "#e05252": BRAND_NAVY,
    "#4b8ef0": BRAND_GOLD,
    "#f0a04a": BRAND_GOLD_DARK,
    "#6db86d": BRAND_GOLD_DARK,
    "#2a9d8f": BRAND_GOLD,
    "#e8f0f9": BRAND_CREAM,
    "#d4e3f0": BRAND_CREAM_DARK,
    "#b8cfe0": BRAND_BORDER,
    "#0a0f1a": BRAND_TEXT_DARK,
    "#4a5568": BRAND_TEXT_MID,
    "#1e2235": BRAND_NAVY,
    "#12162a": BRAND_NAVY_DARK,
    "#94a0b8": BRAND_BORDER,
    "#56617a": BRAND_TEXT_MUTED,
    "rgba(75,142,240,0.06)": "rgba(196,170,136,0.10)",
    "rgba(75,142,240,0.2)":  "rgba(196,170,136,0.25)",
    "rgba(109,184,109,0.05)": "rgba(160,136,96,0.08)",
    "rgba(109,184,109,0.15)": "rgba(160,136,96,0.18)",
    "rgba(224,82,82,0.1)":   "rgba(27,42,74,0.10)",
}

RE_TOPBAR_HEIGHT = re.compile(
    r'(\.topbar\{[^}]*?height:)60px'
)

RE_LOGO_IMG = re.compile(
    r'<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII=" style="height:78px;width:auto;display:block;" alt="Pistos">'
)
LOGO_IMG_NEW = '<img src="../images/pistos-logo.png" style="height:72px;width:auto;display:block;" alt="Pistos Information Protection">'


def clean_file(path):
    original = path.read_text(encoding='utf-8')
    content = original
    applied = {}

    color_count = 0
    for old, new in COLOR_MAP.items():
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        new_content, n = pattern.subn(new, content)
        if n:
            color_count += n
            content = new_content
    if color_count:
        applied['colors'] = color_count

    new, n = RE_TOPBAR_HEIGHT.subn(r'\g<1>90px', content)
    if n: applied['topbar_height'] = n; content = new

    new, n = RE_LOGO_IMG.subn(LOGO_IMG_NEW, content)
    if n: applied['logo'] = n; content = new

    if content != original:
        path.write_text(content, encoding='utf-8')

    return applied


def main():
    repo_root = Path(__file__).parent
    html_files = sorted(repo_root.rglob('*.html'))
    html_files = [f for f in html_files if '.git' not in f.parts and 'node_modules' not in f.parts]

    print(f"Found {len(html_files)} HTML files\n")
    total_changed = 0
    for f in html_files:
        applied = clean_file(f)
        rel = f.relative_to(repo_root)
        if applied:
            total_changed += 1
            edits = ', '.join(f"{k}({v})" for k, v in applied.items())
            print(f"  CHANGED  {rel}")
            print(f"           {edits}")
        else:
            print(f"  no-op    {rel}")

    print(f"\nDone. {total_changed} of {len(html_files)} files changed.")


if __name__ == '__main__':
    main()