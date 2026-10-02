# Banner source

One set of templates, one JSON file of per-entry content, Playwright to export:

```sh
pip install playwright && playwright install chromium   # once
python3 gen.py                   # every banner (light and dark) and social preview
python3 gen.py jenkins-bench     # one entry
```

`banners.json` holds what differs between entries — the wordmark, the subtitle,
the tags (`status_tags` render filled, in front), the right-hand panel and the
social preview's copy. The organization is an entry like any other, `scm-bench`.

The panel is a verdict, not an ornament: for a shipped bench its numbers are the
real output of `scan --snapshot-in examples/snapshot.json` against that bench's
bundled example, so regenerate the images whenever the example snapshot's score
changes. A planned bench states `PLANNED` instead of inventing a score. A bench's
social preview carries the same numbers, so the card makes no claim the banner
does not.

Fonts (Barlow Condensed for the wordmark and score, Barlow Semi Condensed for
everything else — both OFL) are fetched from Google Fonts into `fonts/` on first
run and embedded in the page, so a render never depends on the network; `build/`
holds the intermediate HTML. Both are gitignored.

Exports are screenshots at the exact viewport, and the script refuses to write
one whose viewport came out any other size. The first version drove Chromium's
command line with `--headless=new --window-size=1760,440`, which leaves the page
about 90px short: every per-bench banner shipped with its tag row cut in half.
