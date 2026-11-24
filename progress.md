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

## 2026-11-24, session M2 (core implementation while the freeze is pending)

**Milestone:** M2. **Starting state:** `d15ab0b`, tree clean; protocol DRAFT, not frozen. No confirmatory run was made; no protocol was edited or hashed.

### What was built
Package `src/viral` (see `src/README.md`): generators and graph invariants; IC and LT engines, each with a plain reference loop and a vectorised version; metrics; statistics helpers; EXP-001 verification checks; versioned config and result schemas (1.0.0) validated at export and import; run manifests (config hash, seed, git revision and dirty flag, package versions, OS, CPU, runtime, process peak RSS); fail-closed protocol gate; CLI `viral smoke | run | report | test`; report generator (Markdown, CSV, PNG/SVG, PDF through pandoc to Typst with `-V mainfont="Libertinus Serif"`). Configs in `experiments/`. Decisions D-005 to D-007.

### Commands and actual outputs

```
$ uv lock                                   -> Resolved 26 packages; Updated viral v0.0.1 -> v0.1.0
$ uv sync --locked --all-groups             -> installed, including viral==0.1.0 (editable)
$ uv run --locked pytest   (first run)      -> 2 failed, 156 passed
```
Failure: the test fixture used `n = 60` with BA `m = 2`, whose mean degree `2 m (n - m) / n = 3.87` is outside the 1 percent tolerance; the graph check correctly flagged it. Fixture changed to `n = 400` (mean degree 3.98). Then:
```
$ uv run --locked pytest                    -> 158 passed in 5.41s
```
Commit `aa840f2`. A first smoke and probe run at `aa840f2` recorded `git_dirty: true` because the dirty check counted the untracked smoke output; the check now excludes `results/` (commit `6edd91e`, 158 passed). Those two runs were deleted (created this session) and rerun:
```
$ uv run --locked viral smoke --quiet
run EXP-001-20261124T162117Z-99c548ac (exploratory) ...
runtime 3.28 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)
$ /usr/bin/time -l uv run --locked viral run --config experiments/EXP-001/probe-config.json --quiet
run EXP-001-20261124T162121Z-d947f41d (exploratory) ...
runtime 114.82 s; graphs 30 (failures 0); cascades checked 0 (failures 0)
      120.41 real       119.99 user         0.25 sys
           218972160  maximum resident set size
$ uv run --locked viral smoke --quiet --out <scratchpad>     (determinism check)
rerun identical per-cascade outputs and graph stats: True
$ VIRAL_PANDOC=... VIRAL_TYPST_PYTHON=... uv run --locked viral report <run_dir> --project experiments/EXP-002/config.json --pdf
-> report.md, tables/, figures/, report.pdf (8 pages smoke, 9 pages probe; text and 2 figures checked with pypdf)
$ uv run --locked viral run --config experiments/EXP-002/config.json   (in tests)
-> exit 3, "REFUSED: EXP-002 config is confirmatory but its protocol is not frozen"
```
Peak memory: the manifest records process peak RSS at the end of the run (60.7 MB smoke, 85.9 MB probe); `/usr/bin/time` reports 219 MB for the probe including result serialisation.

### Exploratory measurements (EXPLORATORY, not findings)
- Runtime per run: smoke 3.3 s (5,250 cascades); probe 114.8 s (288,000 cascades, about 0.4 ms per cascade). Per-cascade IC time ranged from below 0.1 ms (p = 0.02) to about 1 ms (p = 0.5, one seed).
- Projected EXP-002 full matrix (504,000 cascades): about 142 s of engine time plus graph generation, from measured rates in all 84 cells; against a 4-hour planning budget.
- Seed spread: graph-replicate sd of the paired grid-mean difference 0.0076 (BA minus ER) and 0.0072 (WS minus ER) at R = 10, against the 0.028 planning bound, so R = 30 is adequate for the drafted estimand. Per-p sd_diff reaches 0.037 (WS minus ER, p = 0.30).
- Degenerate cells: p = 0 and p = 1 (by design); LT phi in {0.10, 0.14}, and phi = 0.18 with 10 seeds, saturate; LT phi = 0.26 with one random seed almost never spreads.
- Graph checks: ER 3000 edges, WS 3000, BA 2991 (mean degree 5.982); giant-component fraction about 0.998 for ER, 1.0 for WS and BA.
- Verification: 0 failures over 15 graphs and 5,250 smoke cascades. LT depth equals duration in every case, as proved (D-007 A4).

### Proposed amendments for the owner
D-007 A1 to A7 (not applied): grid-mean estimand cancels across a sign crossing; replicate count for per-p contrasts; EXP-003 threshold grid mostly saturated; LT depth identical to duration; Holm-interval construction to specify; budget far above need; new master seed for the confirmatory run.

### Files changed
pyproject.toml, uv.lock, src/viral/*, tests/*, experiments/*, results/exploratory/EXP-001/* (probe `result.json` moved to git-ignored `results/raw/`, D-006), research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv}, roadmap.md, README.md, CONTRIBUTING.md (development commands), README files in src/, tests/, results/, experiments/.

### Outstanding risks
- Protocol still DRAFT; D-007 decisions are needed before the freeze.
- Pilot data informed A1 and A3; adopting them must be disclosed in the protocol.
- `research/experiments/EXP-001/report.md` (12-part report) is not written yet.
- S1 to S4 helpers exist but no EXP-004 config or runner wiring yet.

### Next action
Owner: decide on D-007 and freeze the protocols (G-FREEZE). Session: write the EXP-001 12-part report from the two exploratory runs, add EXP-003 and EXP-004 configs, and wire S1 to S3 into the runner.
