#!/usr/bin/env python3
"""Generate the per-bench banners from one template.

    python3 gen.py            # all banners, light and dark, into ../
    python3 gen.py jenkins-bench

Each banner in banners.json renders twice (light/dark) at 1760x440 — the 2x
export size the READMEs embed at width="880". Fonts are fetched from Google
Fonts into fonts/ on first run (Barlow Condensed for the wordmark and the
score, Barlow Semi Condensed for everything else; both OFL). The screenshot
is taken by headless Chromium: point CHROMIUM at a binary if the default
path does not exist.

The organization banner (banner-light/dark-1760x440.png) predates this script
and is NOT overwritten by it: the scm-bench entry here reproduces it closely
enough for a redesign to start from, but not pixel-identically, and the shipped
original stays authoritative until a redesign lands on purpose.
"""
import base64
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')
OUT = os.path.join(HERE, '..')
CHROME = os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

FAMILIES = [
    # (Google Fonts family, local prefix, weights)
    ('Barlow Semi Condensed', 'barlowsc', (400, 500, 600, 700)),
    ('Barlow Condensed', 'barlowc', (600,)),
]

THEMES = {
    'light': dict(paper='#F2F2F3', ink='#1D1F20', muted='#5D5D60', steel='#416180',
                  grid='#E5EFF8', cross='#5D5D60',
                  chipborder='#94BCE3', chiptext='#416180',
                  scorelabel='#416180', digits='#1D1F20', fraction='#8B8B8E', row='#5D5D60',
                  frame='#D4D4D7', sep='#D4D4D7'),
    'dark': dict(paper='#1D2D3D', ink='#F2F2F3', muted='#B5D9FD', steel='#416180',
                 grid='#25394D', cross='#749DC4',
                 chipborder='#597EA3', chiptext='#B5D9FD',
                 scorelabel='#94BCE3', digits='#F2F2F3', fraction='#597590', row='#B5D9FD',
                 frame='#416180', sep='#25394D'),
}


def fetch_fonts():
    os.makedirs(FONTS, exist_ok=True)
    for family, prefix, weights in FAMILIES:
        missing = [w for w in weights if not os.path.exists(os.path.join(FONTS, f'{prefix}-{w}.woff2'))]
        if not missing:
            continue
        url = (f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}"
               f":wght@{';'.join(map(str, missing))}&display=swap")
        css = subprocess.run(['curl', '-fsS', '-A', UA, url],
                             capture_output=True, text=True, check=True).stdout
        for subset, body in re.findall(r'/\* ([\w-]+) \*/\s*@font-face \{(.*?)\}', css, re.S):
            if subset != 'latin':
                continue
            w = re.search(r'font-weight: (\d+)', body).group(1)
            src = re.search(r'url\((https://[^)]+)\)', body).group(1)
            out = os.path.join(FONTS, f'{prefix}-{w}.woff2')
            subprocess.run(['curl', '-fsS', '-o', out, src], check=True)
            print('fetched', os.path.basename(out))


def font_face(weight, family='BarlowSC', prefix='barlowsc'):
    with open(os.path.join(FONTS, f'{prefix}-{weight}.woff2'), 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    return (f"@font-face {{ font-family:'{family}'; font-style:normal; font-weight:{weight}; "
            f"src:url(data:font/woff2;base64,{b64}) format('woff2'); }}")


# The mark: a branch line ending in an open commit node, curving into a checked
# box. Kept in sync with the avatar by eye, not by tooling.
MARK = """
<svg width="254" height="254" viewBox="0 0 254 254" fill="none" xmlns="http://www.w3.org/2000/svg">
  <g stroke="{steel}" stroke-width="13" stroke-linecap="round">
    <line x1="88" y1="68" x2="88" y2="141"/>
    <circle cx="88" cy="168" r="21" fill="none"/>
    <path d="M 111 172 C 140 172 167 152 167 122" fill="none" stroke-linecap="butt"/>
    <rect x="142" y="64" width="52" height="52" fill="{paper}" stroke-width="13"/>
    <path d="M 156 92 L 165 100 L 181 80" stroke-width="12" stroke-linejoin="round"/>
  </g>
</svg>
"""


def frame(x, y, w, h):
    """A hairline rect whose edges stop 12px short of the corners, with a
    registration cross centered on each corner — the technical-drawing
    register the whole identity hangs on."""
    gap = 12
    arm = 11
    parts = []
    for ey in (y, y + h):
        parts.append(f'<div class="edge" style="left:{x+gap}px;top:{ey-1}px;width:{w-2*gap}px;height:2px"></div>')
    for ex in (x, x + w):
        parts.append(f'<div class="edge" style="left:{ex-1}px;top:{y+gap}px;width:2px;height:{h-2*gap}px"></div>')
    for cx in (x, x + w):
        for cy in (y, y + h):
            parts.append(f'<div class="cross" style="left:{cx-arm}px;top:{cy-1}px;width:{2*arm}px;height:2px"></div>')
            parts.append(f'<div class="cross" style="left:{cx-1}px;top:{cy-arm}px;width:2px;height:{2*arm}px"></div>')
    return '\n'.join(parts)


def panel(cfg):
    """The right-hand panel is a verdict, not an ornament: for a shipped bench
    it is the real output of `scan --snapshot-in examples/snapshot.json`, and a
    planned bench states its status rather than inventing a score."""
    if 'status' in cfg:
        return f"""
  <div class="score-label">STATUS</div>
  <div class="score-line"><span class="digits status">{cfg['status']}</span></div>
  <div class="sep"></div>
  <div class="row">{''.join(f'<span>{s}</span>' for s in cfg['statusrow'])}</div>"""
    return f"""
  <div class="score-label">SCORE</div>
  <div class="score-line"><span class="digits">{cfg['score']}</span><span class="fraction">/100</span></div>
  <div class="sep"></div>
  <div class="row">{''.join(f'<span>{k}&nbsp;{v}</span>' for k, v in cfg['counts'])}</div>"""


def html(cfg, theme):
    t = THEMES[theme]
    faces = '\n'.join(
        [font_face(w) for w in (400, 500, 600, 700)]
        + [font_face(600, 'BarlowC', 'barlowc')])
    chips = ''.join(f'<div class="chip">{c}</div>' for c in cfg['tags'])
    wordsize = cfg.get('wordsize', 120)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{faces}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1760px; height:440px; }}
body {{
  position:relative; overflow:hidden; font-family:'BarlowSC'; background:{t['paper']};
  background-image:
    linear-gradient(to right, {t['grid']} 2px, transparent 2px),
    linear-gradient(to bottom, {t['grid']} 2px, transparent 2px);
  background-size:88px 88px; background-position:88px 82px;
}}
.border {{ position:absolute; inset:0; border:2px solid {t['frame']}; }}
.edge {{ position:absolute; background:{t['frame']}; }}
.cross {{ position:absolute; background:{t['cross']}; }}
.mark {{ position:absolute; left:80px; top:90px; }}
.word {{ position:absolute; left:396px; top:72px; font-size:{wordsize}px; font-family:'BarlowC'; font-weight:600; letter-spacing:-1px; line-height:1; color:{t['ink']}; white-space:nowrap; }}
.sub {{ position:absolute; left:395px; top:211px; width:900px; font-weight:400; font-size:38px; line-height:42px; color:{t['muted']}; }}
.chips {{ position:absolute; left:397px; top:321px; display:flex; gap:16px; }}
.chip {{ height:42px; border:2px solid {t['chipborder']}; color:{t['chiptext']};
  font-weight:600; font-size:20px; letter-spacing:1.5px; padding:0 15px; display:flex; align-items:center; }}
.panel {{ position:absolute; left:1256px; top:82px; width:419px; height:270px; }}
.score-label {{ position:absolute; left:40px; top:40px; font-weight:700; font-size:20px; letter-spacing:2.2px; color:{t['scorelabel']}; }}
.score-line {{ position:absolute; left:40px; top:82px; line-height:1; white-space:nowrap; }}
.digits {{ font-family:'BarlowC'; font-weight:600; font-size:78px; color:{t['digits']}; letter-spacing:0; }}
.digits.status {{ font-size:56px; letter-spacing:1px; }}
.fraction {{ font-family:'BarlowC'; font-weight:600; font-size:{cfg.get('fracsize', 40)}px; color:{t['fraction']}; }}
.sep {{ position:absolute; left:40px; top:179px; width:339px; height:2px; background:{t['sep']}; }}
.row {{ position:absolute; left:40px; top:203px; width:345px; display:flex; justify-content:space-between; font-weight:500; font-size:26px; color:{t['row']}; white-space:nowrap; }}
</style></head><body>
<div class="border"></div>
{frame(80, 90, 254, 254)}
{frame(1256, 82, 419, 270)}
<div class="mark">{MARK.format(steel=t['steel'], paper=t['paper'])}</div>
<div class="word">{cfg['name']}</div>
<div class="sub">{cfg['subtitle']}</div>
<div class="chips">{chips}</div>
<div class="panel">{panel(cfg)}</div>
</body></html>"""


def build(cfg, theme):
    page = os.path.join(HERE, 'build', f"{cfg['slug']}-{theme}.html")
    os.makedirs(os.path.dirname(page), exist_ok=True)
    with open(page, 'w') as f:
        f.write(html(cfg, theme))
    # The organization banner keeps its original name; per-bench banners carry
    # the bench in theirs.
    stem = f"banner-{theme}" if cfg['slug'] == 'scm-bench' else f"banner-{cfg['slug']}-{theme}"
    out_png = os.path.join(OUT, f'{stem}-1760x440.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                    '--hide-scrollbars', '--force-device-scale-factor=1',
                    '--window-size=1760,440', f'--screenshot={out_png}',
                    'file://' + page], check=True, capture_output=True)
    print('wrote', os.path.relpath(out_png, os.getcwd()))


if __name__ == '__main__':
    fetch_fonts()
    with open(os.path.join(HERE, 'banners.json')) as f:
        configs = json.load(f)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    matched = False
    for cfg in configs:
        if only and cfg['slug'] != only:
            continue
        matched = True
        if cfg['slug'] == 'scm-bench':
            # See the module docstring: the shipped organization banner is the
            # authoritative one; regenerate it only by asking for it by name.
            if not only:
                continue
        for theme in ('light', 'dark'):
            build(cfg, theme)
    if only and not matched:
        sys.exit(f'no banner named {only!r} in banners.json')
