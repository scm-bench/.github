// Renders the brand assets that carry type.
//
// mark.svg and avatar.svg are hand-written and self-contained — pure geometry,
// no font dependency. The banner and social preview set text in Geist Mono, so
// a standalone SVG would render differently everywhere the font is absent.
// They are produced as PNG instead, and this file is the source.
//
//   node docs/brand/build.mjs
//
// Requires playwright (the repository does not depend on it; this runs by hand
// when the assets change).
//
// The right-hand side of the banner is not decoration. It is the bundled
// example snapshot shipped with the tool (scm-bench/scm-bench,
// examples/snapshot.json) rendered as an audit matrix:
// payments-api passes everything, legacy-billing fails review after review,
// vendor-mirror could not be read and shows as MANUAL. The banner is a report.

import { chromium } from 'playwright';
import { mkdirSync, rmSync, writeFileSync } from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));

// Palettes track GitHub's own light and dark themes, so each banner sits on
// the README as if it were part of the page rather than a poster pasted on.
const THEMES = {
  light: {
    paper: '#FFFFFF',
    ink: '#1F2328',
    muted: '#59636E',
    faint: '#818B98',
    hairline: '#D1D9E0',
    na: '#EAEEF2',
    green: '#2DA44E',
    green2: '#8CE09F',
    amber: '#D4A72C',
    red: '#E5534B',
    node: '#8B949E',
  },
  dark: {
    paper: '#0D1117',
    ink: '#E6EDF3',
    muted: '#9198A1',
    faint: '#6E7681',
    hairline: '#30363D',
    na: '#21262D',
    green: '#3FB950',
    green2: '#2EA043',
    amber: '#D29922',
    red: '#F85149',
    node: '#6E7681',
  },
};

// The verdict matrix, hand-authored to tell the example snapshot's story.
// G/g = pass (two greens for texture), A = manual, R = fail, N = not applicable.
const MATRIX = [
  { label: 'payments-api', cells: 'GgGGgGGgGGGgGGgGGGgGGgGG' },
  { cells: 'GgGGAGGgGGgGGAgGGgGGGgGG' },
  { cells: 'GGgGGgGRGGgGGgGGAGGgGGgG' },
  { label: 'legacy-billing', cells: 'RARgRRAGRRARgAARRAgRARRA' },
  { cells: 'GgGGgGGGgGGAgGGgGGgGGGgG' },
  { label: 'vendor-mirror', cells: 'AANAAANAANAAANAAANAANAAN' },
  { cells: 'GGgGGgGGgGNGGgGGgGGGgGNG' },
];
const COLS = 24;
for (const row of MATRIX) {
  if (row.cells.length !== COLS) {
    throw new Error(`matrix row has ${row.cells.length} cells, want ${COLS}`);
  }
}

// Column groups, labelled with what each family of controls actually checks.
const FAMILIES = [
  { name: 'REVIEW', span: 5 },
  { name: 'HISTORY', span: 4 },
  { name: 'CI', span: 4 },
  { name: 'HYGIENE', span: 5 },
  { name: 'ACCESS', span: 6 },
];

const fonts = `
  @font-face { font-family: 'GeistMono'; src: url('fonts/GeistMono-Bold.ttf') format('truetype'); font-weight: 700; }
  @font-face { font-family: 'GeistMono'; src: url('fonts/GeistMono-Regular.ttf') format('truetype'); font-weight: 400; }
  html, body { margin: 0; padding: 0; }
`;

const mark = (t, x, y, scale, color) => `
    <g transform="translate(${x} ${y}) scale(${scale})">
      <path d="M14 33 L27 46 L50 18" fill="none" stroke="${color}"
            stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/>
      <g fill="${color}">
        <circle cx="14" cy="33" r="7.5"/>
        <circle cx="27" cy="46" r="7.5"/>
        <circle cx="50" cy="18" r="7.5"/>
      </g>
    </g>`;

// A pull request's life drawn in git-graph shorthand: work branches off, two
// commits happen — one of them needing a human's eyes — and what merges back
// turns the line green. The merge node is the mark's final node doing its job.
function branchStrip(t, x0, x1, yMain) {
  const xFork = x0 + (x1 - x0) * 0.14;
  const xMerge = x0 + (x1 - x0) * 0.66;
  const yBranch = yMain - 30;
  const c1 = xFork + 34;
  const c2 = xMerge - 34;
  const openR = 5;
  return `
    <line x1="${x0}" y1="${yMain}" x2="${xMerge}" y2="${yMain}" stroke="${t.hairline}" stroke-width="2"/>
    <line x1="${xMerge}" y1="${yMain}" x2="${x1}" y2="${yMain}" stroke="${t.green}" stroke-width="2.5"/>
    <path d="M${xFork} ${yMain} C ${c1} ${yMain}, ${c1} ${yBranch}, ${xFork + 68} ${yBranch}
             L ${xMerge - 68} ${yBranch}
             C ${c2} ${yBranch}, ${c2} ${yMain}, ${xMerge} ${yMain}"
          fill="none" stroke="${t.node}" stroke-width="2"/>
    <circle cx="${xFork}" cy="${yMain}" r="4.5" fill="${t.node}"/>
    <circle cx="${xFork + (xMerge - xFork) * 0.4}" cy="${yBranch}" r="${openR}"
            fill="${t.paper}" stroke="${t.node}" stroke-width="2.5"/>
    <circle cx="${xFork + (xMerge - xFork) * 0.62}" cy="${yBranch}" r="${openR}"
            fill="${t.paper}" stroke="${t.amber}" stroke-width="2.5"/>
    <circle cx="${xMerge}" cy="${yMain}" r="6.5" fill="${t.green}"/>`;
}

// The audit matrix with sparse repository labels and a family axis, drawn the
// way a well-set table is: hairline baseline, ticks at group boundaries.
function matrix(t, x, y, { cell = 16, pitch = 21, labelGap = 14, axisGap = 16 } = {}) {
  const fill = { G: t.green, g: t.green2, A: t.amber, R: t.red, N: t.na };
  const parts = [];

  MATRIX.forEach((row, r) => {
    const cy = y + r * pitch;
    if (row.label) {
      parts.push(
        `<text x="${x - labelGap}" y="${cy + cell / 2 + 4}" text-anchor="end"
               font-family="GeistMono" font-size="11.5" fill="${t.muted}">${row.label}</text>`,
      );
    }
    for (let c = 0; c < COLS; c++) {
      const v = row.cells[c];
      parts.push(
        `<rect x="${x + c * pitch}" y="${cy}" width="${cell}" height="${cell}" rx="3.5"
               fill="${fill[v]}"/>`,
      );
    }
  });

  const bottom = y + MATRIX.length * pitch - (pitch - cell);
  const axisY = bottom + axisGap;
  const width = (COLS - 1) * pitch + cell;
  parts.push(
    `<line x1="${x}" y1="${axisY}" x2="${x + width}" y2="${axisY}" stroke="${t.hairline}" stroke-width="1.5"/>`,
  );

  let col = 0;
  for (const fam of FAMILIES) {
    const first = x + col * pitch;
    const last = x + (col + fam.span - 1) * pitch + cell;
    parts.push(
      `<line x1="${first}" y1="${axisY}" x2="${first}" y2="${axisY + 6}" stroke="${t.hairline}" stroke-width="1.5"/>`,
      `<text x="${(first + last) / 2}" y="${axisY + 24}" text-anchor="middle"
             font-family="GeistMono" font-size="10.5" letter-spacing="2" fill="${t.faint}">${fam.name}</text>`,
    );
    col += fam.span;
  }
  parts.push(
    `<line x1="${x + width}" y1="${axisY}" x2="${x + width}" y2="${axisY + 6}" stroke="${t.hairline}" stroke-width="1.5"/>`,
  );

  return parts.join('\n  ');
}

// The left column: kicker, wordmark with the mark standing where a terminal
// cursor would, tagline, and the command. The identity is typographic — the
// reference points here are print front matter and a quiet shell prompt.
function masthead(t, x, yBase, { wordSize = 64 } = {}) {
  const charW = wordSize * 0.6; // Geist Mono advance width
  const markScale = wordSize / 82;
  const markX = x + charW * 9 + wordSize * 0.28 - 6.5 * markScale;
  const markY = yBase - 53.5 * markScale;
  return `
  <text x="${x}" y="${yBase - wordSize * 1.42}" font-family="GeistMono" font-size="${wordSize * 0.203}"
        letter-spacing="3.5" fill="${t.muted}">// CIS SUPPLY CHAIN BENCHMARK</text>
  <text x="${x}" y="${yBase}" font-family="GeistMono" font-weight="700" font-size="${wordSize}"
        letter-spacing="-1.5" fill="${t.ink}">scm-bench</text>
  ${mark(t, markX, markY, markScale, t.green)}
  <text x="${x}" y="${yBase + wordSize * 0.78}" font-family="GeistMono" font-size="${wordSize * 0.345}"
        fill="${t.ink}">no pass without proof.</text>
  <text x="${x}" y="${yBase + wordSize * 1.62}" font-family="GeistMono" font-size="${wordSize * 0.25}">
    <tspan fill="${t.green}">$</tspan><tspan fill="${t.muted}" dx="10">scm-bench scan</tspan>
  </text>`;
}

// 1280x400, rendered at 2x -> 2560x800. Github renders it ~880px wide, where
// the 11px matrix labels land at readable size.
function banner(mode) {
  const t = THEMES[mode];
  return `
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="400" viewBox="0 0 1280 400">
  <rect width="1280" height="400" fill="${t.paper}"/>
  ${masthead(t, 64, 196)}
  <line x1="576" y1="64" x2="576" y2="336" stroke="${t.hairline}" stroke-width="1.5"/>
  ${branchStrip(t, 640, 1216, 96)}
  ${matrix(t, 736, 150)}
</svg>`;
}

// 1280x640, the single image GitHub allows for the social preview, so it is
// built on the light theme and given room to breathe.
function socialPreview() {
  const t = THEMES.light;
  return `
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
  <rect width="1280" height="640" fill="${t.paper}"/>
  ${masthead(t, 80, 292, { wordSize: 72 })}
  <text x="80" y="560" font-family="GeistMono" font-size="15" fill="${t.faint}">github.com/scm-bench/scm-bench</text>
  <line x1="624" y1="96" x2="624" y2="544" stroke="${t.hairline}" stroke-width="1.5"/>
  ${branchStrip(t, 680, 1216, 200)}
  ${matrix(t, 760, 290, { axisGap: 20 })}
</svg>`;
}

const avatarSvg = (await import('fs')).readFileSync(resolve(here, 'avatar.svg'), 'utf8');

const jobs = [
  { name: 'banner-light', html: banner('light'), w: 1280, h: 400, scale: 2 },
  { name: 'banner-dark', html: banner('dark'), w: 1280, h: 400, scale: 2 },
  { name: 'social-preview', html: socialPreview(), w: 1280, h: 640, scale: 2 },
  { name: 'avatar-512', html: avatarSvg, w: 512, h: 512, scale: 1, raw: true },
  { name: 'avatar-1024', html: avatarSvg, w: 512, h: 512, scale: 2, raw: true },
];

const browser = await chromium.launch();
try {
  mkdirSync(resolve(here, 'png'), { recursive: true });
  for (const job of jobs) {
    const css = job.raw
      ? 'html,body{margin:0}svg{display:block;width:100vw;height:100vh}'
      : fonts;
    const htmlPath = resolve(here, `.build-${job.name}.html`);
    writeFileSync(htmlPath, `<!doctype html><meta charset="utf-8"><style>${css}</style>${job.html}`);

    const page = await browser.newPage({
      viewport: { width: job.w, height: job.h },
      deviceScaleFactor: job.scale,
    });
    await page.goto(`file://${htmlPath}`, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: resolve(here, `png/${job.name}.png`) });
    await page.close();
    // The page has to be a real file for file:// to load it, but nothing needs
    // it afterwards. Removing it here keeps a rebuild from leaving five
    // untracked dotfiles behind in the repository the assets now live in.
    rmSync(htmlPath, { force: true });
    console.log(`  ${job.name}.png  ${job.w * job.scale}x${job.h * job.scale}`);
  }
} finally {
  await browser.close();
}
