#!/usr/bin/env python3
"""Generate the README banners and social previews from one set of templates.

    python3 gen.py                  # everything: every banner (light and dark) and social preview
    python3 gen.py jenkins-bench    # one entry of banners.json

Each entry renders a 1760x440 banner per theme — the 2x export size the
READMEs embed at width="880" — and a 1280x640 social preview, the size
GitHub asks for. The organization's social preview is also exported at
2560x1280. Fonts are fetched from Google Fonts into fonts/ on first run
(Barlow Condensed for the wordmark and the score, Barlow Semi Condensed for
everything else; both OFL) and embedded, so a render never depends on the
network.

Screenshots are taken with Playwright, which sets the viewport to the exact
export size. The script used to drive Chromium's command line with
--headless=new --window-size=1760,440; the new headless mode counts browser
chrome it does not draw against that window, so the page got a viewport about
90px short and every banner shipped with its bottom edge — half of the tag row,
the frame corners — cut off.
"""
import base64
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')
BUILD = os.path.join(HERE, 'build')
OUT = os.path.join(HERE, '..')
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

FAMILIES = [
    # (Google Fonts family, local prefix, weights)
    ('Barlow Semi Condensed', 'barlowsc', (400, 500, 600, 700)),
    ('Barlow Condensed', 'barlowc', (600,)),
]

# `fraction` (the "/100") is the one value darkened from the first export: at
# #8B8B8E on paper and #597590 on navy it fell under 3:1, the floor even for
# 40px type.
THEMES = {
    'light': dict(paper='#F2F2F3', ink='#1D1F20', muted='#5D5D60', steel='#416180',
                  grid='#E5EFF8', cross='#5D5D60',
                  chipborder='#94BCE3', chiptext='#416180', chipfill='#416180', chipfilltext='#F2F2F3',
                  scorelabel='#416180', digits='#1D1F20', fraction='#7A7A7D', row='#5D5D60',
                  frame='#D4D4D7', sep='#D4D4D7'),
    'dark': dict(paper='#1D2D3D', ink='#F2F2F3', muted='#B5D9FD', steel='#416180',
                 grid='#25394D', cross='#749DC4',
                 chipborder='#597EA3', chiptext='#B5D9FD', chipfill='#B5D9FD', chipfilltext='#1D2D3D',
                 scorelabel='#94BCE3', digits='#F2F2F3', fraction='#6F8DAA', row='#B5D9FD',
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


def faces():
    return '\n'.join([font_face(w) for w in (400, 500, 600, 700)]
                     + [font_face(600, 'BarlowC', 'barlowc')])


# The mark: a branch line ending in an open commit node, curving into a checked
# box. Kept in sync with the avatar by eye, not by tooling.
MARK = """
<svg width="{size}" height="{size}" viewBox="0 0 254 254" fill="none" xmlns="http://www.w3.org/2000/svg">
  <g stroke="{steel}" stroke-width="13" stroke-linecap="round">
    <line x1="88" y1="68" x2="88" y2="141"/>
    <circle cx="88" cy="168" r="21" fill="none"/>
    <path d="M 111 172 C 140 172 167 152 167 122" fill="none" stroke-linecap="butt"/>
    <rect x="142" y="64" width="52" height="52" fill="{paper}" stroke-width="13"/>
    <path d="M 156 92 L 165 100 L 181 80" stroke-width="12" stroke-linejoin="round"/>
  </g>
</svg>
"""


def mark(t, size):
    return MARK.format(size=size, steel=t['steel'], paper=t['paper'])


def frame(x, y, w, h, gap=12, arm=11, edges=True, edge_class='edge', cross_class='cross'):
    """A hairline rect whose edges stop short of the corners, with a
    registration cross centered on each corner — the technical-drawing
    register the whole identity hangs on. Without edges, only the crosses:
    the page-corner marks of the social preview."""
    parts = []
    if edges:
        for ey in (y, y + h):
            parts.append(f'<div class="{edge_class}" style="left:{x+gap}px;top:{ey-1}px;width:{w-2*gap}px;height:2px"></div>')
        for ex in (x, x + w):
            parts.append(f'<div class="{edge_class}" style="left:{ex-1}px;top:{y+gap}px;width:2px;height:{h-2*gap}px"></div>')
    for cx in (x, x + w):
        for cy in (y, y + h):
            parts.append(f'<div class="{cross_class}" style="left:{cx-arm}px;top:{cy-1}px;width:{2*arm}px;height:2px"></div>')
            parts.append(f'<div class="{cross_class}" style="left:{cx-1}px;top:{cy-arm}px;width:2px;height:{2*arm}px"></div>')
    return '\n'.join(parts)


def chips(cfg):
    """Status chips come first and are filled — PREVIEW says something about
    the tool itself, not a feature of it, and must not read as one more tag."""
    status = ''.join(f'<div class="chip filled">{c}</div>' for c in cfg.get('status_tags', []))
    return status + ''.join(f'<div class="chip">{c}</div>' for c in cfg['tags'])


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


def grid_css(t, size, x, y):
    return (f"background:{t['paper']}; background-image:"
            f" linear-gradient(to right, {t['grid']} 2px, transparent 2px),"
            f" linear-gradient(to bottom, {t['grid']} 2px, transparent 2px);"
            f" background-size:{size}px {size}px; background-position:{x}px {y}px;")


def banner_html(cfg, theme):
    t = THEMES[theme]
    wordsize = cfg.get('wordsize', 120)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{faces()}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1760px; height:440px; }}
body {{ position:relative; overflow:hidden; font-family:'BarlowSC'; {grid_css(t, 88, 88, 82)} }}
.border {{ position:absolute; inset:0; border:2px solid {t['frame']}; }}
.edge {{ position:absolute; background:{t['frame']}; }}
.cross {{ position:absolute; background:{t['cross']}; }}
.mark {{ position:absolute; left:80px; top:90px; }}
.word {{ position:absolute; left:396px; top:72px; font-size:{wordsize}px; font-family:'BarlowC'; font-weight:600; letter-spacing:-1px; line-height:1; color:{t['ink']}; white-space:nowrap; }}
.sub {{ position:absolute; left:395px; top:211px; width:900px; font-weight:400; font-size:38px; line-height:42px; color:{t['muted']}; }}
.chips {{ position:absolute; left:397px; top:321px; display:flex; gap:16px; }}
.chip {{ height:42px; border:2px solid {t['chipborder']}; color:{t['chiptext']};
  font-weight:600; font-size:20px; letter-spacing:1.5px; padding:0 15px; display:flex; align-items:center; }}
.chip.filled {{ border-color:{t['chipfill']}; background:{t['chipfill']}; color:{t['chipfilltext']}; font-weight:700; }}
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
<div class="mark">{mark(t, 254)}</div>
<div class="word">{cfg['name']}</div>
<div class="sub">{cfg['subtitle']}</div>
<div class="chips">{chips(cfg)}</div>
<div class="panel">{panel(cfg)}</div>
</body></html>"""


def social_html(cfg):
    """The card a shared link unfurls into. The organization's card carries the
    PASS/FAIL/MANUAL legend; a bench's carries its verdict, the same real numbers
    as its banner panel, so the card makes no claim the banner does not."""
    t = THEMES['light']
    s = cfg['social']
    if 'counts' in cfg and not s.get('legend'):
        (pk, pv), (fk, fv), (mk, mv) = cfg['counts']
        verdict = (f'<div class="sscore"><span class="sdigits">{cfg["score"]}</span><span class="sfrac">/100</span></div>'
                   f'<div class="schip filled">{pk} {pv}</div><div class="schip">{fk} {fv}</div>'
                   f'<div class="schip grey">{mk} {mv}</div>')
    else:
        verdict = '<div class="schip filled">PASS</div><div class="schip">FAIL</div><div class="schip grey">MANUAL</div>'
    status = ''.join(f'<div class="schip filled">{c}</div>' for c in cfg.get('status_tags', []))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{faces()}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:1280px; height:640px; }}
body {{ position:relative; overflow:hidden; font-family:'BarlowSC'; {grid_css(t, 64, 46, 54)} }}
.border {{ position:absolute; inset:0; border:2px solid {t['frame']}; }}
.edge {{ position:absolute; background:#CDCDD0; }}
.cross {{ position:absolute; background:{t['cross']}; }}
.corner {{ position:absolute; background:#749DC4; }}
.mark {{ position:absolute; left:110px; top:183px; }}
.head {{ position:absolute; left:390px; top:196px; display:flex; align-items:center; gap:18px; }}
.word {{ font-family:'BarlowC'; font-weight:600; font-size:{s.get('wordsize', 96)}px; letter-spacing:-1px; line-height:1; color:{t['ink']}; white-space:nowrap; }}
.sub {{ position:absolute; left:390px; top:304px; width:660px; font-weight:400; font-size:27px; line-height:36px; color:{t['muted']}; text-wrap:pretty; }}
.sep {{ position:absolute; left:110px; top:494px; width:1058px; height:2px; background:{t['sep']}; }}
.verdict {{ position:absolute; left:110px; top:517px; display:flex; align-items:center; gap:10px; }}
.sscore {{ display:flex; align-items:baseline; margin-right:8px; line-height:1; }}
.sdigits {{ font-family:'BarlowC'; font-weight:600; font-size:36px; color:{t['ink']}; }}
.sfrac {{ font-family:'BarlowC'; font-weight:600; font-size:20px; color:{t['fraction']}; }}
.schip {{ height:33px; border:2px solid {t['chipborder']}; color:{t['chiptext']}; font-weight:600; font-size:15px; letter-spacing:1px; padding:0 11px; display:flex; align-items:center; }}
.schip.filled {{ border-color:{t['chipfill']}; background:{t['chipfill']}; color:{t['chipfilltext']}; font-weight:700; }}
.schip.grey {{ border-color:#C4C4C7; color:{t['muted']}; }}
.url {{ position:absolute; right:112px; top:521px; font-weight:700; font-size:20px; letter-spacing:0.5px; color:{t['steel']}; }}
</style></head><body>
<div class="border"></div>
{frame(52, 54, 1172, 532, arm=12, edges=False, cross_class='corner')}
{frame(110, 183, 224, 224, gap=10, arm=8)}
<div class="mark">{mark(t, 224)}</div>
<div class="head"><div class="word">{cfg['name']}</div>{status}</div>
<div class="sub">{s['text']}</div>
<div class="sep"></div>
<div class="verdict">{verdict}</div>
<div class="url">{s['url']}</div>
</body></html>"""


def outputs(cfg):
    """(file name, html, width, height, device scale) for every image of one entry."""
    org = cfg['slug'] == 'scm-bench'
    out = []
    for theme in ('light', 'dark'):
        # The organization banner keeps its original name; per-bench banners
        # carry the bench in theirs.
        stem = f'banner-{theme}' if org else f"banner-{cfg['slug']}-{theme}"
        out.append((f'{stem}-1760x440.png', banner_html(cfg, theme), 1760, 440, 1))
    if 'social' in cfg:
        stem = 'social-preview' if org else f"social-preview-{cfg['slug']}"
        out.append((f'{stem}-1280x640.png', social_html(cfg), 1280, 640, 1))
        if org:
            out.append((f'{stem}-2560x1280.png', social_html(cfg), 1280, 640, 2))
    return out


def render(jobs):
    from playwright.sync_api import sync_playwright  # pip install playwright && playwright install chromium

    os.makedirs(BUILD, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, page_html, w, h, scale in jobs:
            src = os.path.join(BUILD, name.replace('.png', '.html'))
            with open(src, 'w') as f:
                f.write(page_html)
            page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=scale)
            page.goto('file://' + src)
            page.evaluate('document.fonts.ready')
            size = page.evaluate('[innerWidth, innerHeight]')
            if size != [w, h]:
                sys.exit(f'{name}: the viewport is {size[0]}x{size[1]}, not {w}x{h}; refusing to export a cropped image')
            out_png = os.path.join(OUT, name)
            page.screenshot(path=out_png, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
            page.close()
            print('wrote', os.path.relpath(out_png, os.getcwd()))
        browser.close()


if __name__ == '__main__':
    fetch_fonts()
    with open(os.path.join(HERE, 'banners.json')) as f:
        configs = json.load(f)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    selected = [c for c in configs if not only or c['slug'] == only]
    if not selected:
        sys.exit(f'no entry named {only!r} in banners.json')
    render([job for cfg in selected for job in outputs(cfg)])
