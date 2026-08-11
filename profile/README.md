<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-dark-1760x440.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-light-1760x440.png">
    <img src="https://raw.githubusercontent.com/scm-bench/.github/main/brand/banner-light-1760x440.png" alt="scm-bench — audit source control against the CIS supply chain benchmark" width="880">
  </picture>
</p>

## Benchmarks for the software supply chain, starting where the code lives

Most supply chain tooling looks at what you build. Rather less looks at the
place the build starts — the repository, and whether the settings around it
actually stop unreviewed code from shipping.

That is what this organization works on.

### [scm-bench](https://github.com/scm-bench/scm-bench)

A read-only CLI that audits a source control platform against the **Source
Code** section of the CIS Software Supply Chain Security Guide, and tells you
the exact settings path to fix whatever it finds.

**v0.1 targets Bitbucket Data Center**, which has the least tooling in this
space. 15 controls are evaluated automatically; 5 more are carried as
documented manual checks so the mapping is complete rather than quietly
partial.

```
SCORE 53/100   15 passed  13 failed  19 manual  1 n/a
      weighted 29/55 (HIGH=3, MEDIUM=2, LOW=1; manual and n/a excluded)

┌────────────┬──────────┬────────┬───────────┬────────────────────────────────────────┐
│  Control   │ Severity │ Status │ Resources │                 Title                  │
├────────────┼──────────┼────────┼───────────┼────────────────────────────────────────┤
│ CIS-1.1.15 │ HIGH     │ FAIL   │       1/3 │ No direct pushes to the default branch │
└────────────┴──────────┴────────┴───────────┴────────────────────────────────────────┘

fix: Repository settings -> Branch permissions -> Add restriction: select
     the default branch and enable "Prevent changes without a pull request".
```

---

### What we will not do

**Report `PASS` for something nobody checked.**

If a token lacks a permission, if an add-on is not installed, if the API never
exposed the field — the answer is `MANUAL`, and the control is excluded from
the score entirely. An instance is never credited for a question the tool could
not ask, and never penalised for one either.

This sounds like a detail. It is the whole thing. A benchmark tool that reports
`FAIL` because it got a `403` teaches people to ignore its output, and a tool
that reports `PASS` on missing data is worse than no tool at all — it tells
someone they are secure when nothing was verified.

The scan is read-only in the strict sense: it issues only `GET` requests, and
that is enforced by a test rather than by convention.

---

### Contributing

The most valuable contribution here is usually not code. A control that fires
wrongly against a real instance, or remediation text that does not match what
the UI actually says, is worth more than a refactor — most of this has only
ever run against a stand-in server.

Start with [CONTRIBUTING.md](https://github.com/scm-bench/scm-bench/blob/main/CONTRIBUTING.md).
Security issues go through
[private advisories](https://github.com/scm-bench/scm-bench/security/advisories/new),
never a public issue.

<sub>Apache 2.0 · Not affiliated with CIS or Atlassian.</sub>
