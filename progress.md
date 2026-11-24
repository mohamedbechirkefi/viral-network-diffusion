<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24, session M0 (bootstrap and feasibility, plus M1 drafts)

**Milestone:** M0. **Starting state:** one commit (`d470109`, master prompt and the owner's licence package); working tree clean.

### Decisions
- D-001 licence is the owner's protective non-commercial licence (recorded as first decision-log entry).
- D-002 zero-cost toolchain without TeX (pandoc to Typst, typst Python package).
- D-003 synthetic graphs only; external network datasets excluded pending rights.
- D-004 proposed primary design (DRAFT; awaiting owner freeze).

### Commands and actual outputs

Hardware and tools:

```
$ sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize
Apple M1 Pro
10
17179869184
$ sw_vers
ProductName:    macOS
ProductVersion: 15.3.1
BuildVersion:   24D70
$ df -h /Users/bechir | tail -1
/dev/disk3s1   460Gi   312Gi   128Gi    71%    3.1M  1.3G    0%   /System/Volumes/Data
$ /usr/local/bin/python3 --version
Python 3.12.1
$ /Users/bechir/research/labs/.tools/py/bin/uv --version
uv 0.9.5 (d5f39331a 2025-10-21)
$ /Users/bechir/research/labs/.tools/py/bin/python -c "...importlib.metadata versions..."
typst 0.15.0 pypdf 6.20.0 pillow 11.3.0
$ /Users/bechir/research/labs/.tools/pandoc --version | head -1
pandoc 3.6.3
$ /Users/bechir/research/helix/.tools/node/bin/node --version
v22.23.3
$ git --version
git version 2.42.1
$ which tex pdflatex xelatex
tex not found
pdflatex not found
xelatex not found
```

Note: the brief lists typst under `.tools/py/bin/`; there is no `typst` executable there. typst 0.15.0 is available as a Python package in that environment, which is how it is used.

Dependency versions (PyPI JSON API, latest release uploaded before 2026-11-10): networkx 3.7 (2026-09-21), numpy 2.5.4 (2026-10-10), jsonschema 4.26.0 (2026-01-07), pytest 9.2.0 (2026-10-27), hypothesis 6.170.15 (2026-11-06), matplotlib 3.11.2 (2026-09-11).

Lockfile:

```
$ /Users/bechir/research/labs/.tools/py/bin/uv lock
Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
Resolved 26 packages in 345ms
```

`pyproject.toml` sets `exclude-newer = "2026-11-10T00:00:00Z"` so transitive dependencies are also at least two weeks old. Nothing was installed (`uv sync` not run).

Toolchain smoke check (EXPLORATORY, not a research artifact; files in the session scratchpad, not committed):

```
$ pandoc smoke.md -s -t typst -o smoke.typ                         -> exit 0
$ python -c "import typst; typst.compile('smoke.typ', output='smoke.pdf')"
typst.TypstError: font fallback list must not be empty               -> FAILED
$ pandoc smoke.md -s -t typst -V mainfont="Libertinus Serif" -o smoke2.typ   -> exit 0
$ python -c "import typst; typst.compile('smoke2.typ', output='smoke.pdf')"  -> exit 0
$ python -c "import pypdf; ..."
pages 1
'Toolchain smoke\nExploratory check, not a research artifact. Inline math 𝑆 = |𝐴|/𝑁.\na b\n1 2\n1'
$ pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex  -> exit 0 (96 lines)
```

Finding: pandoc 3.6.3's Typst template emits `font: ()` when no font is given, which typst 0.15.0 rejects. Passing `-V mainfont="Libertinus Serif"` fixes it. Recorded in CONTRIBUTING.md development commands.

Literature and data: Crossref API metadata checks for 14 DOIs (all resolved); abstract pages opened for 4 arXiv entries; publisher pages for Watts 2002 and Salganik 2006 returned HTTP 403; networkx 3.7 generator documentation and BSD-3 licence opened; SNAP and Netzschleuder pages opened (no dataset licence stated). Details in `research/literature_review.md` and `data/manifest.json`.

### Files created
CLAUDE.md, roadmap.md, progress.md, README.md, CITATION.cff, pyproject.toml, uv.lock; research/{decision_log.md, literature_review.md, protocol.md, limitations.md, claims_register.csv, experiment_journal.jsonl, experiment_registry.csv}; research/experiments/EXP-001..EXP-004/protocol.md and README; research/paper/{manuscript.md, manuscript.tex, references.bib, supplementary.md, figures/README.md}; research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}; data/manifest.json; README files in results/, src/, tests/, experiments/, demo/, articles/. CONTRIBUTING.md: development commands appended (licence text untouched).

### Failures
- First typst compile failed (empty font list); fixed as above.
- Watts 2002 and Salganik 2006 full texts not accessible (HTTP 403); cited at metadata level only.

### Outstanding risks
- The protocol is a draft; confirmatory runs are blocked on the owner's freeze.
- The sample-size rationale rests on an unmeasured `sd_diff`; EXP-001 must estimate it before the freeze.
- IC runtime at `p = 0.5` with 504,000 cascades is unmeasured.
- `manuscript.tex` cannot be compile-checked locally.

### Next action
Owner: review `research/protocol.md` and EXP-001 to EXP-004 protocols, then freeze or amend. Session: start M2 (graph generators, IC reference engine, verification tests of EXP-001), which may proceed before the freeze as exploratory work.
