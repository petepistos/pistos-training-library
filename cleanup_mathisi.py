#!/usr/bin/env python3
"""
Mathisi cleanup script — applies all Tier 1 + Tier 2 (home redundancy) edits
to every .html file in the pistos-training-library repo.
"""

import re
from pathlib import Path

RE_TOPBAR_FIX = re.compile(
    r'(    </div>\s*\n)\s*\n(<div class="nav-bar")',
    re.MULTILINE
)

RE_TOPBAR_RIGHT = re.compile(
    r'\s*<div class="topbar-right">.*?</div>\s*\n',
    re.DOTALL
)

# Anchor-based: remove from <div class="menu-panel" up to and including the
# blank line before <div id="home"
RE_MENU_PANEL = re.compile(
    r'\s*<div class="menu-panel" id="menuPanel">.*?(?=\n<div id="home">)',
    re.DOTALL
)

# Anchor-based: remove from <div id="home"> up to but not including
# <div class="page" id="pg1"
RE_HOME_DIV = re.compile(
    r'\s*<div id="home">.*?(?=<div class="page" id="pg1")',
    re.DOTALL
)

RE_OVERVIEW_PILL = re.compile(
    r'<button class="nav-pill active" id="nav-home" onclick="gotoPage\(\'home\'\)">Overview</button>'
)
OVERVIEW_PILL_NEW = '<button class="nav-pill active" id="nav-pg1" onclick="gotoPage(\'pg1\')">Overview</button>'

RE_DUPLICATE_PG1_PILL = re.compile(
    r'<button class="nav-pill" id="nav-pg1" onclick="gotoPage\(\'pg1\'\)">[^<]*</button>'
)

RE_PG1_VISIBLE = re.compile(
    r'<div class="page" id="pg1" style="display:none;">'
)
PG1_VISIBLE_NEW = '<div class="page" id="pg1">'

RE_TOGGLE_MENU = re.compile(
    r'\s*function toggleMenu\(\)\{[^}]*?\}\s*\n',
    re.DOTALL
)

RE_GOTOPAGE_MENU_LINES = re.compile(
    r'\s*const menuOverlay=document\.getElementById\(\'menuOverlay\'\);\s*\n'
    r'\s*const menuPanel=document\.getElementById\(\'menuPanel\'\);\s*\n'
    r"\s*if\(menuOverlay\)\{menuOverlay\.style\.display='none';menuPanel\.style\.display='none';\}\s*\n"
)

RE_CSS_TOPBAR_LEVEL = re.compile(r'\s*\.topbar-level\{[^}]*\}\s*\n')
RE_CSS_TOPBAR_RIGHT = re.compile(r'\s*\.topbar-right\{[^}]*\}\s*\n')
RE_CSS_MODULES_BTN = re.compile(r'\s*\.modules-btn\{[^}]*\}\s*\n')
RE_CSS_MODULES_BTN_HOVER = re.compile(r'\s*\.modules-btn:hover\{[^}]*\}\s*\n')
RE_CSS_MENU_OVERLAY = re.compile(r'\s*\.menu-overlay\{[^}]*\}\s*\n')
RE_CSS_MENU_PANEL = re.compile(r'\s*\.menu-panel\{[^}]*\}\s*\n')
RE_CSS_MENU_CLOSE = re.compile(r'\s*\.menu-close\{[^}]*\}\s*\n')
RE_CSS_MENU_HEADING = re.compile(r'\s*\.menu-heading\{[^}]*\}\s*\n')
RE_CSS_MENU_COMMENT = re.compile(r'\s*/\* MENU \*/\s*\n')
RE_CSS_HOME_COMMENT = re.compile(r'\s*/\* HOME \*/\s*\n')
RE_CSS_HOME_RULES = re.compile(r'\s*#home\{[^}]*\}\s*\n\s*\.home-title\{[^}]*\}\s*\n\s*\.home-sub\{[^}]*\}\s*\n\s*\.home-grid\{[^}]*\}\s*\n')


def clean_file(path):
    original = path.read_text(encoding='utf-8')
    content = original
    applied = {}

    new, n = RE_TOPBAR_FIX.subn(r'\1</div>\n\n\2', content)
    if n: applied['topbar_close'] = n; content = new

    new, n = RE_TOPBAR_RIGHT.subn('\n', content)
    if n: applied['topbar_right'] = n; content = new

    new, n = RE_MENU_PANEL.subn('\n', content)
    if n: applied['menu_panel'] = n; content = new

    new, n = RE_HOME_DIV.subn('\n', content)
    if n: applied['home_div'] = n; content = new

    new, n = RE_OVERVIEW_PILL.subn(OVERVIEW_PILL_NEW, content)
    if n: applied['overview_pill'] = n; content = new

    new, n = RE_DUPLICATE_PG1_PILL.subn('', content)
    if n: applied['duplicate_pg1'] = n; content = new

    new, n = RE_PG1_VISIBLE.subn(PG1_VISIBLE_NEW, content)
    if n: applied['pg1_visible'] = n; content = new

    new, n = RE_TOGGLE_MENU.subn('\n', content)
    if n: applied['toggle_menu'] = n; content = new

    new, n = RE_GOTOPAGE_MENU_LINES.subn('\n', content)
    if n: applied['gotopage_menu'] = n; content = new

    for name, pattern in [
        ('css_topbar_level', RE_CSS_TOPBAR_LEVEL),
        ('css_topbar_right', RE_CSS_TOPBAR_RIGHT),
        ('css_modules_btn', RE_CSS_MODULES_BTN),
        ('css_modules_btn_hover', RE_CSS_MODULES_BTN_HOVER),
        ('css_menu_overlay', RE_CSS_MENU_OVERLAY),
        ('css_menu_panel', RE_CSS_MENU_PANEL),
        ('css_menu_close', RE_CSS_MENU_CLOSE),
        ('css_menu_heading', RE_CSS_MENU_HEADING),
        ('css_menu_comment', RE_CSS_MENU_COMMENT),
        ('css_home_comment', RE_CSS_HOME_COMMENT),
        ('css_home_rules', RE_CSS_HOME_RULES),
    ]:
        new, n = pattern.subn('\n', content)
        if n: applied[name] = n; content = new

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