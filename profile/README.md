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

### The projects

One tool per platform, each named after what it audits, each a read-only CLI
that reports in the same shape: a score, a verdict per control, and the exact
settings path to fix whatever it finds.

| | | |
|---|---|---|
| [**bitbucket-bench**](https://github.com/scm-bench/bitbucket-bench) | Bitbucket Data Center | the reference implementation · verified on Data Center 8.19–10.5 |
| [**jenkins-bench**](https://github.com/scm-bench/jenkins-bench) | Jenkins controllers | verified on Jenkins 2.580 LTS |
| [**azure-devops-bench**](https://github.com/scm-bench/azure-devops-bench) | Azure DevOps Services and Server | preview · not yet verified against a live organization |
| [**scm-bench**](https://github.com/scm-bench/scm-bench) | — | the specification they all follow |

`scm-bench` is the umbrella: the policy contract, the control metadata format,
the scoring rule and the snapshot schemas live there, so a `FAIL` from one tool
means what a `FAIL` from another means. It is a specification, not a library —
each bench stays a self-contained binary you can download and run.

A tool says it works on a platform once it has been checked against a real
one: a disposable instance, seeded so every control is in a known state, and
scanned with tokens of different reach — every verdict compared with what the
fixture actually is. Controls no API can answer are carried as documented manual
checks, so the mapping to the benchmark is complete rather than quietly partial.

A scan of bitbucket-bench's bundled example, start and end:

```
PLAT/legacy-billing  CIS-1.1.3 HIGH: Pull requests require 0 approval(s); at least 2
    independent approvals are needed.
    fix: Set "Minimum approvals" to at least 2 at Repository settings -> Pull
    requests -> Merge checks.
    · requiredApprovers = 0

...

SCORE 52/100   15 passed  14 failed  19 manual  14 n/a
      14 controls failed
      weighted 30/57 (HIGH=3, MEDIUM=2, LOW=1; manual and n/a excluded)
      scored 29 of 48 findings (60%); 19 could not be evaluated
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
the UI actually says, is worth more than a refactor. The end-to-end suites
cover the versions we could boot, and a real deployment always has a shape no
fixture thought of.

Start with
[bitbucket-bench's CONTRIBUTING.md](https://github.com/scm-bench/bitbucket-bench/blob/main/CONTRIBUTING.md)
— it is where the practice is written down. What a verdict has to mean, in any
of these tools, is in the
[bench contract](https://github.com/scm-bench/scm-bench/blob/main/docs/bench-contract.md).

Security issues go through private advisories on the repository concerned
([bitbucket-bench](https://github.com/scm-bench/bitbucket-bench/security/advisories/new),
[jenkins-bench](https://github.com/scm-bench/jenkins-bench/security/advisories/new)),
never a public issue.

<sub>Apache 2.0 · Not affiliated with CIS, Atlassian, Microsoft or the Jenkins project.</sub>
