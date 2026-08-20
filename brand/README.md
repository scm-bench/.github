# Brand

These files live here rather than in any one project repository because every
repository in the organization draws on them: the organization profile above,
each bench's README, the umbrella spec repository, and the avatar and social
preview that are uploaded by hand. Everything outside this repository references
them by absolute `raw.githubusercontent.com` URL, so moving or renaming a file
here breaks a page somewhere else — grep the organization before you do.

The identity has one job: look like a tool you would trust with a security
verdict. The register is technical drawing, not poster — a measured grid,
registration marks at the corners, hairline frames, and a single steel blue
doing all the accent work. Nothing is decorative; everything reads as something
that was measured rather than styled.

## The mark

A branch line ending in an open commit node, curving into a checked box. Read
quickly it is a check mark; read slowly it is a branch that was inspected and
cleared — which is what the tool verifies. The node stays open rather than
filled, because the tool reports on a repository, it does not close anything.

It carries no type, so it survives at avatar sizes where the wordmark would not.

## The banner is a verdict

The right-hand panel of the banner is real output, not an ornament: the score
from the example snapshot shipped with the reference implementation
(`examples/snapshot.json` in `scm-bench/bitbucket-bench`) — `53/100`, `PASS 15`,
`FAIL 13`, `MANUAL 19`. The
`MANUAL` count sits in the same row as the other two on purpose. A tool that
hides how much it could not determine is the thing this project exists not to be.

The three tags underneath — `READ-ONLY`, `REGO POLICIES`, `SARIF` — are what
someone scanning the README needs to know before they read a word of prose.

## Colour

Two grounds, one accent. The steel blue holds its value on both, so the mark
needs no second version to survive the theme switch.

| Token | Light | Dark | Use |
|---|---|---|---|
| paper | `#F2F2F3` | `#1D2D3D` | ground |
| ink | `#1D1F20` | `#F2F2F3` | wordmark, primary type |
| muted | `#5D5D60` | `#B5D9FD` | secondary type, score detail |
| steel | `#416180` | `#416180` | the mark, badge rules, accents |
| grid | `#E5EFF8` | `#25394D` | the blueprint grid |
| hairline | `#D4D4D7` | `#25394D` | frames, separators, registration marks |

The dark ground is a navy rather than GitHub's near-black, which keeps the
banner reading as a drawing on paper rather than as a hole in the page.

## Files

| File | Size | Use |
|---|---|---|
| `banner-light-1760x440.png` / `banner-dark-1760x440.png` | 1760×440 | The organization banner: the spec repository's README header and the organization profile, one per theme. Embedded at `width="880"` — the file is 2× so it stays sharp on retina. |
| `banner-<bench>-{light,dark}-1760x440.png` | 1760×440 | Each bench repository's own README header, same construction: its wordmark, its subtitle, and its own verdict panel — the real score of its bundled example snapshot, or `PLANNED`. Regenerated from [`src/`](src/). |
| `avatar-light-464.png` | 464×464 | Avatar on a light surface. |
| `avatar-dark-512.png` | 512×512 | Avatar on a dark surface. |
| `social-preview-1280x640.png` | 1280×640 | GitHub's social preview at the exact size it asks for. |
| `social-preview-2560x1280.png` | 2560×1280 | The same image at 2×, for anywhere that wants it sharper. |

GitHub allows exactly one organization avatar, so only one of the two is ever
uploaded; the other is kept for slides, talks, and any surface with the opposite
ground. The two are not the same pixel size — 464 is what the light export
happened to produce. Even them up at 512 the next time these are regenerated.

Embed the banner with theme switching. The URLs are absolute because the
consumers are in other repositories, where a relative path would resolve
against the wrong tree:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-dark-1760x440.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-light-1760x440.png">
  <img src="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-light-1760x440.png" alt="scm-bench" width="880">
</picture>
```

Absolute URLs also survive the trip into a release archive: `README.md` is
shipped inside every tarball, where a repository-relative image path points at
nothing at all.

## Source

The per-bench banners are generated from [`src/`](src/) — one HTML template,
one JSON file of per-bench content, exported by headless Chromium. Changing one
means editing `src/banners.json` and re-running `src/gen.py`, never retouching
a PNG: a hand-edited raster is a file nobody can regenerate.

The organization banner and the avatars predate that script and **those PNGs
are the only copies** — the generator reproduces the banner closely (same
grid, frames, mark and type) but not pixel-identically, so the shipped
originals stay authoritative until a redesign lands on purpose. The previous
identity's `build.mjs`, SVG sources and bundled Geist Mono were removed when
this set landed, because they render the old mark and nothing else.
