# Banner source

One template, one JSON file of per-bench content, headless Chromium to export:

```sh
python3 gen.py                  # every per-bench banner, light and dark
python3 gen.py jenkins-bench    # one bench
```

`banners.json` holds what differs between benches — the wordmark, the subtitle,
the tags, and the right-hand panel. The panel is a verdict, not an ornament:
for a shipped bench its numbers are the real output of
`scan --snapshot-in examples/snapshot.json` against that bench's bundled
example, so regenerate the banner when the example snapshot's score changes. A
planned bench states `PLANNED` instead of inventing a score.

Fonts (Barlow Condensed for the wordmark and score, Barlow Semi Condensed for
everything else — both OFL) are fetched from Google Fonts into `fonts/` on
first run; `build/` holds the intermediate HTML. Both are gitignored. The
Chromium binary is found at the Playwright default path, or set `CHROMIUM`.

The organization's own banner (`banner-light/dark-1760x440.png`) predates this
script and stays the authoritative export — `gen.py` skips it unless asked for
`scm-bench` by name, and its reproduction is close but not pixel-identical.
