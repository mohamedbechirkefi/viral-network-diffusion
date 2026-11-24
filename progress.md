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

## 2026-11-24, session DATA-FREEZE (real-data check, owner-approved amendments, freeze)

**Milestone:** M1 gate. **Starting state:** `43174d4`, tree clean, 158 tests passing. **Authority:** `../_shared/owner-approvals-2026-11-24b.md` sections 1 and 7 ("Approve all"; "yes for all others").

### Licence check (D-008)
- SNAP (https://snap.stanford.edu/data/, ego-Facebook and email-Enron pages): no licence text found (`grep -i licen|terms|copyright` returned nothing).
- Netzschleuder (https://networks.skewed.de/about): no dataset licence; code AGPLv3; data offered "with the belief that this is not only permitted...". API entries `karate`, `email_enron`, `facebook_friends`, `dolphins`: no licence field.
- `facebook_friends` upstream, https://github.com/benmaier/BFMaierFBnetwork: GitHub API licence `MIT`; LICENSE file read (MIT, Copyright (c) 2014 Benjamin F. Maier). Adopted for EXP-005.

### Commands and actual outputs
```
$ .venv/bin/python scripts/download_data.py
bfmaier_anonymized_fb_network.gml: 97876 bytes, sha256 cb94e2c6a02c4f8457730418fd4413d5abb75783f65c02b990eb1dade4a41aaa
LICENSE: 1074 bytes, sha256 bc424e303eb0d4a656b9ce6cda8a67a20d355d6c3cff0bddb53703a60a5600e1
README.md: 788 bytes, sha256 6260f8d817d96e92f9976b992f62d5bb15e3bec851ebe5de0eae5fb58536eb37
$ .venv/bin/python scripts/ingest_data.py
processed_sha256 e286957db7367d10bf401217116787ee4a7ccef0fd6a70ebbcb20e427fc529cc, 18959 bytes;
counts: 362 nodes, 1988 edges declared and kept; 0 missing, unknown, self-loop or duplicate; 14 isolated nodes
$ .venv/bin/python scripts/fit_calibration.py      (after protocol section 11.5 was written)
p_c 0.0483851339839852; mean degree 10.9834; <k^2> 237.98; 20 components; giant 0.9088
EXP-005 p grid: 0.005806 0.014516 0.029031 0.043547 0.058062 0.087093 0.145155   (0.22 s)
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> Audited 25 packages
$ .venv/bin/python -m pytest       -> before freeze record: 167 passed, 1 skipped; after: 168 passed in 5.84 s
$ guard: frozen_status on EXP-002, EXP-003, EXP-004 S1, EXP-005 configs -> (True, 'frozen')
$ .venv/bin/viral run --config <EXP-002 config with replicates 121>
REFUSED: ... config sha256 f0ea826f5777 is not a frozen EXP-002 config (changed or never frozen).   rc=3
```
Graph construction check only (no cascades) for EXP-005 replicate 0: real, real_er, real_dpr all 362 nodes, 1988 edges, no graph check failure; `real_dpr` 0.111 s.

### Changes
- Protocol section 11 and EXP-001 to EXP-004 amendment sections; new EXP-005 protocol; status FROZEN v1.0.
- Code: `viral.realdata`; config and result schemas 1.1.0; topologies `er_trim`, `ws_trim`, `ba_dpr`, `real`, `real_er`, `real_dpr`; `p_scale = pc_multiple`; `holm_bootstrap_contrasts`, `confirmatory_contrasts`; freeze-record guard. Tests: `tests/test_realdata_freeze.py` (synthetic GML fixture), updated gate tests (the CLI refusal test now uses a changed copy so it can never start a confirmatory run).
- Configs: EXP-002 (R = 120, seed 20261125), EXP-003, EXP-004 S1 to S4, EXP-005.
- Records: `data/manifest.json`, `data/real_network_calibration.json`, decision log D-008 to D-010, journal (exploratory calibration fit), registry, limitations, references, CITATION, manuscript metadata, `research/freeze.json`.

### Failures and risks
- None blocking. The S1 per-multiplier criterion and the interval construction were chosen by the session at the freeze (D-009); the owner may revisit them only by a post-freeze amendment.
- EXP-005 needs the git-ignored data on the run machine; `load_processed` refuses a file whose SHA-256 differs from the pinned value.

### Next action
Coordinator: schedule M3. No confirmatory run was made in this session.

## 2026-11-24, session ROUND3 (owner ratification, round 3)

**Milestone:** M1 gate passed; M3 not started. **Starting state:** `c477c99`, tree clean. **Authority:** `../_shared/owner-approvals-2026-11-24c.md` section 3 ("Approve all").

### Changes
- `research/decision_log.md`: D-011 records the ratification of the MIT-licensed real network for EXP-005 and of the D-009 session choices (interval construction, per-multiplier S1 criterion, EXP-003 and EXP-004 configs).
- `research/freeze.json`: new `ratifications` block (R-1 to R-4). No frozen protocol or config changed; all hashes unchanged.

### Commands and actual outputs
```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> Audited 25 packages
$ .venv/bin/python -m pytest       -> 168 passed in 5.51s
$ frozen_status on EXP-002, EXP-003, EXP-004 S1, EXP-005 configs -> (True, 'frozen') each
$ shasum -a 256 research/protocol.md -> d984f2f8f2fba8f5ddabe097b0a82be8d17ab652422769f9c22cc442f1a17b32 (unchanged)
```

### Failures and risks
- None. No confirmatory run, no push.

### Next action
Coordinator: schedule M3.

## 2026-11-25, session M3 (confirmatory runs)

**Milestone:** M3. **Starting state:** `ceeee8c`, tree clean, every frozen hash matching (study protocol, five EXP protocols, eight configs, data manifest, raw and processed real-network files). **Authority:** the coordinator's M3 brief (the owner said "Start next" on 2026-11-25). Times below are UTC (2026-11-24 evening UTC is 2026-11-25 local).

### Pre-run checks (all passed)
```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> Audited 25 packages
$ .venv/bin/python -m pytest                                     -> 168 passed in 6.10s
$ hash check against research/freeze.json                        -> all True (protocols, configs, manifest, raw GML, processed JSON)
$ nice .venv/bin/viral smoke --quiet --out <dir>                 -> EXP-001-20261124T233106Z-99c548ac (EXPLORATORY, seed 20261124)
  runtime 3.50 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)
$ .venv/bin/python scripts/validate_metrics.py <smoke dir> <json> -> 54 checks, 0 failed (EXPLORATORY)
```
Then `viral.confirmatory`, `scripts/analyse_confirmatory.py` and `tests/test_confirmatory.py` (6 tests) were written and committed as `32961c3` before any confirmatory output: `pytest` 174 passed. The freeze guard accepted all eight frozen configs.

### Confirmatory runs (revision 32961c3, clean tree, two workers under nice -n 10)
| run id | config | runtime | graphs / cascades | exit |
|---|---|---|---|---|
| EXP-002-20261124T233447Z-2c7febb6 | EXP-002 | 1047.8 s | 360 / 2,016,000 | 0 |
| EXP-003-20261124T234212Z-a2d668ab | EXP-003 | 502.4 s | 90 / 504,000 | 0 |
| EXP-004-20261124T233447Z-de14a4b3 | S1 | 104.3 s | 90 / 90,000 | 0 |
| EXP-004-20261124T233637Z-916e8d29 | S2 | 73.8 s | 60 / 84,000 | 0 |
| EXP-004-20261124T233755Z-e1d24091 | S3 | 90.2 s | 90 / 126,000 | 0 |
| EXP-004-20261124T235044Z-e31dba07 | S4 N=500 (optional) | 22.9 s | 90 / 126,000 | 0 |
| EXP-004-20261124T235110Z-40385ec3 | S4 N=2000 (optional) | 60.0 s | 90 / 126,000 | 0 |
| EXP-005-20261124T233932Z-d277f271 | EXP-005 | 138.3 s | 360 / 504,000 | 0 |

Wall clock 23:34:46Z to 23:52:52Z. 0 graph-check failures; no retry; no dropped run. EXP-004 graphs verified identical (seed and degree second moment) to EXP-002 replicates 0 to 29 (210 of 210 graphs).

### Frozen analysis (scripts/analyse_confirmatory.py; Holm, protocol 11.3 intervals)
- EXP-002: 13 of 14 rejected; 7 intervals inside the SESOI. Not rejected: WS - ER at p = 0.02. Largest: WS - ER at p = 0.30, -0.3529 [-0.3601, -0.3456] (level 0.9833); BA - ER at p = 0.20, +0.0969 [+0.0921, +0.1018] (level 0.9950). Both contrasts change sign with p.
- EXP-003 (grid mean, 10 random seeds): WS - ER +0.3664 [+0.3602, +0.3727] (level 0.95); BA - ER +0.0439 [+0.0366, +0.0498] (level 0.975); both rejected.
- EXP-004 S1: 10 of 10 rejected; inside SESOI at c = 0.5 and 1, outside at 1.5, 2, 3. S1 cross-reading: unresolved (owner, D-012).
- EXP-004 S2 (BA - ba_dpr): 3 of 7 rejected (p = 0.1: -0.0019; 0.3: +0.0276 [+0.0145, +0.0409]; 0.5: +0.0203 [+0.0116, +0.0295]); intervals inside SESOI for p = 0.02 to 0.20.
- EXP-004 S3: 13 of 14 rejected, same signs and magnitudes as EXP-002. S4 (optional): 13 of 14 at N = 500 and at N = 2000, same pattern.
- EXP-005: 11 of 14 rejected. real - real_er: 7 of 7 (+0.0385 at p = 0.087, -0.2080 at p = 0.145). real - real_dpr: 4 of 7, all negative (-0.0688 [-0.0724, -0.0653] at p = 0.087; -0.1317 [-0.1380, -0.1253] at p = 0.145); the three non-rejections have intervals inside the SESOI.

### Records
- `results/confirmatory/` (analysis JSON and CSV, figures, run manifests, logs, raw SHA-256; `MANIFEST.sha256`); raw `result.json` files git-ignored in `results/raw/confirmatory/`.
- `research/experiments/EXP-00{2..5}/`: config copies, run manifests, `metrics.csv`, figures.
- Journal (8 confirmatory entries, 2 exploratory), registry statuses, claims register (89 rows, `scripts/build_records.py`), `research/publication/artifact_manifest.json` (40 artifacts), limitations 12 to 17, decision log D-012, roadmap.

### Failures and risks
- **The 12-part experiment reports were not written:** the file tool refused to create `research/experiments/EXP-002/report.md`; per the coordinator's instruction they were left unwritten (EXP-001 to EXP-005). No PDFs were built.
- S1 cross-reading needs an owner decision (D-012).

### Final checks
```
$ .venv/bin/python -m pytest   -> 174 passed in 6.98s
$ freeze guard on all eight frozen configs -> accepted (hashes unchanged)
```

### Next action
Owner: decide the S1 cross-reading and how the experiment reports should be produced. Then M4 (interpretation, second review pass, manuscript).
