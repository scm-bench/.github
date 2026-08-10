# Brand

These files live here rather than in `scm-bench/scm-bench` because more than
one repository draws on them: the organization profile above, the tool's own
README, and the avatar and social preview that are uploaded by hand. Anything
outside this repository references them by absolute `raw.githubusercontent.com`
URL, so moving or renaming a file here breaks a page somewhere else — grep the
organization before you do.

The identity has one job: look like a tool you would trust with a security
verdict. The register is print, not poster — paper ground, editorial margins,
monospace type, and a right-hand side that is not decoration but the product's
own output drawn carefully.

## The banner is a report

The right side of the banner renders the example snapshot shipped with the tool
(`examples/snapshot.json` in `scm-bench/scm-bench`) as an audit matrix, kept
here as hand-authored data rather than read across repositories at build time:
`payments-api` passes
everything, `legacy-billing` fails review after review, `vendor-mirror` could
not be read and shows as MANUAL amber. Columns group into the control families
(`REVIEW · HISTORY · CI · HYGIENE · ACCESS`). Above it, a pull request's life
in git-graph shorthand: work branches off, one commit needs a human's eyes
(the amber ring), and what merges back turns the line green.

Someone who knows the tool recognises their own terminal. Someone who does not
still reads "audits repositories, honestly".

## The mark

Three commit nodes joined by two strokes. Read quickly it is a check mark;
read slowly it is a commit graph — which is what the tool verifies.

It degrades rather than breaks: the nodes are only slightly wider than the
stroke, so at the 20px GitHub uses in a timeline the swelling vanishes and a
clean check remains, while at 48px and up the three nodes separate and the
graph reading arrives. Ring nodes were tried and rejected on evidence — the
holes closed up at exactly the sizes that matter.

In the wordmark lockup the mark stands where a terminal cursor would:
`scm-bench ✓` is a command that exited 0.

## Colour

Both palettes track GitHub's own themes, so each banner sits on the README as
part of the page rather than a poster pasted on. The four verdict colours are
used for nothing else.

| Token | Light | Dark | Meaning |
|---|---|---|---|
| paper | `#FFFFFF` | `#0D1117` | ground |
| ink | `#1F2328` | `#E6EDF3` | primary type |
| muted | `#59636E` | `#9198A1` | secondary type |
| green | `#2DA44E` | `#3FB950` | PASS, and the brand |
| green (texture) | `#8CE09F` | `#2EA043` | PASS, lighter cells |
| amber | `#D4A72C` | `#D29922` | MANUAL |
| red | `#E5534B` | `#F85149` | FAIL |
| na | `#EAEEF2` | `#21262D` | N/A |

`mark.svg` uses `#2DA44E`, which holds on either ground. The avatar is a white
tile with a faint dot grid and **one amber dot** — the project's defining
behaviour is admitting what it could not determine, and the identity says so
quietly rather than claiming everything is green.

## Type

**Geist Mono** only — bold for the wordmark, regular for everything else. The
output people actually see is a terminal, and one family keeps the register
honest.

## Files

| File | Use |
|---|---|
| `mark.svg` | The mark alone, transparent, no font dependency. Safe anywhere. |
| `avatar.svg` | Avatar source. Full bleed — GitHub rounds it itself. |
| `png/avatar-512.png` / `-1024.png` | Upload as the organization avatar. |
| `png/banner-light.png` / `-dark.png` | README header, one per theme. |
| `png/social-preview.png` | 1280×640 content at 2×; the single image GitHub allows. |

Embed the banner with theme switching. The URLs are absolute because the
consumers are in other repositories, where a relative path would resolve
against the wrong tree:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/png/banner-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/png/banner-light.png">
  <img src="https://raw.githubusercontent.com/scm-bench/.github/main/brand/png/banner-light.png" alt="scm-bench" width="880">
</picture>
```

Absolute URLs also survive the trip into a release archive: `README.md` is
shipped inside every tarball, where a repository-relative image path points at
nothing at all.

## Rebuilding

`mark.svg` and `avatar.svg` are hand-edited. The banners and social preview
carry type and are generated, because a standalone SVG would render
differently wherever the font is missing:

```bash
node brand/build.mjs
```

Requires `playwright`; the project itself does not depend on it. The matrix is
hand-authored data, not randomness, so rebuilding without editing produces an
identical file rather than a spurious diff.
