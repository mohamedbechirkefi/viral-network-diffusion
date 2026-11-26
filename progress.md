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

## 2026-11-25, session M3-close (owner decisions of 2026-11-25)

**Authority:** `../_shared/owner-approvals-2026-11-25.md` items 4 and 12; owner, 2026-11-25, "approve all recommendations, RIGGED A".

### Done
- `research/decision_log.md` D-013: S1 reported per multiplier, no overall verdict, no multiplier picked after the data; owner approval of the experiment reports.
- `research/limitations.md` items 14 and 17 updated; claims register regenerated (`scripts/build_records.py`; the 10 S1 rows now carry the D-013 note); `research/freeze.json` gains a `post_freeze_record` block (M3-1 storage, M3-2 S1 decision, M3-3 reports). Freeze guard still accepts all eight frozen configs (hashes unchanged).

### Failed
- The file tool again refused to create `research/experiments/EXP-002/report.md` ("Subagents should return findings as text, not write report files"). Per the brief, report writing stopped there; no workaround was used. No `report.md` or `reproduction.md` exists for EXP-001 to EXP-005.

### M3 status
Not done: the run matrix is complete, but the reports required for closing M3 are missing.

### Next action
Coordinator or owner: have the reports written by a session whose file tool permits it.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 5 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25, session M4 (interpretation, evidence audit, manuscript)

**Milestone:** M4. **Starting state:** `b5210e0`, tree clean, protocol SHA-256 `d984f2f8...` unchanged. **Authority:** the coordinator's M4 brief. The owner said "Approve all recommendations, push then next" on 2026-11-25 (`../_shared/owner-approvals-2026-11-25b.md`). That file has no VIRAL-specific item.

### Confounder inspection and exploratory checks
- The competing explanations named in the protocols are listed against the results that address them in manuscript Table 9.
- Three were open: WS degree versus structure, EXP-005 component structure, and degree heterogeneity under LT. Each got a cheap exploratory check in `scripts/exploratory_m4.py` (committed as `3ac1b8a` and `4ed1942` before the kept run). The checks used fresh seeds 20261201 to 20261203, one worker, R = 30, C = 200 and unadjusted intervals.
```
$ nice -n 10 .venv/bin/python scripts/exploratory_m4.py results/exploratory/M4   (third execution, clean tree at 4ed1942)
runtime_seconds X1 22.2, X2 8.6, X3 131.5; tree_dirty_at_start false; 77 contrast rows
X1 ws - er p=0.3 -0.3524 [-0.3619, -0.3426]; ws - ws_dpr -0.3662 [-0.3750, -0.3573]; ws_dpr - er +0.0137 [+0.0030, +0.0246]
X2 real - real_dpr p=0.145155: S -0.1309 [-0.1387, -0.1231]; giant-seeded, giant-normalised -0.1177 [-0.1259, -0.1100]
X3 phi=0.22: ws - ws_dpr +0.7420; ws_dpr - er -0.2117; ba - ba_dpr -0.4450; ba_dpr - er +0.5773
```
- Two earlier executions were superseded and their outputs deleted: the first before X3 existed, the second with untracked outputs in the tree. The X1 and X2 values of the kept run are identical to those of the first. No frozen verdict changed.

### Evidence audit
```
$ .venv/bin/python scripts/build_records.py      -> 575 claim rows; 43 artifacts
$ .venv/bin/python scripts/audit_evidence.py     -> exit 0
TRIPLES 370 estimate-interval triples matched jointly to one committed row; 0 unmatched
COPIES 129 manifest entries and 56 experiment-folder copies checked, 0 failures
RAW: 8 runs, 177 checks, 0 failures (frozen analysis recomputed from raw results)
{"tokens": 2953, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 180}
```
- **Fixed.** The EXP-004 total runtime is now 351.1 s; the earlier 351.2 s summed the rounded values. Four citations overstated what had been read, and they are now qualified. Sources re-read: the Newman et al. 2001 abstract, the Watts 2002 full text and the Kempe et al. 2015 abstract. Stale registry statuses were updated, and the claims audit checklist was completed. Details: `research/publication/evidence_audit.md`.

### Manuscript and second pass
- `research/paper/manuscript.md`: version 0.2, about 5,700 words outside tables and references, abstract 242 words. `research/paper/supplementary.md` is complete. `research/paper/references.bib` holds 14 entries with their verification levels. `manuscript.tex` was regenerated with pandoc 3.6.3 and not compiled (D-002).
- `research/publication/review_pass_2.md`: 13 challenges; 8 hold in full or in part. The changes they led to are listed in its section B. Among them: a descriptive title replaces the mechanism title, and the abstract and conclusion lead with the count outside the SESOI.

### Records
- Reports EXP-001 to EXP-005 are now version 1.1, each with an M4 addendum. Updated: limitations 18 to 24, `literature_review.md` verification update, decision D-014, journal (2 entries), registry statuses, `author_review.md` owner items and roadmap.
- New tests: `tests/test_audit.py` (4 tests).

### Final checks
```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> Audited 25 packages
$ .venv/bin/python -m pytest                                     -> 178 passed in 6.90s
$ frozen_status on all eight frozen configs                      -> (True, 'frozen') each
$ shasum -a 256 research/protocol.md                             -> d984f2f8f2fba8f5ddabe097b0a82be8d17ab652422769f9c22cc442f1a17b32 (unchanged)
```

### M4 status
**Done.** The gate holds:
- every numerical claim maps to a result id, config hash and figure or table (claims register and `number_trace.csv`, 0 untraced decimals);
- every external claim maps to a source read at its stated level;
- unsupported attributions were qualified.

### Risks and owner items
- The owner may revise the proposed title and should review manuscript version 0.2 (`research/publication/author_review.md`).
- The X1 to X3 findings are exploratory. A confirmatory version would need a new registered experiment.
- No PDF has been built (M6). Nothing was pushed.

### Next action
M5 (interactive experience), then M6.

## 2026-11-25, post-M4 owner decisions applied (items 1 and 2)

**Authority.** Owner, 2026-11-25, "Approve all" (post-M4) (`../_shared/owner-approvals-2026-11-25c.md`). Decision D-015.

### Changes
- Item 1: the M4 title is approved; one sentence recording the approval was added to the manuscript status line (no line added, so the number-trace line numbers are unchanged). `manuscript.tex` regenerated by the CONTRIBUTING pandoc command.
- Item 2: the funding, competing-interest and AI-use wording of manuscript section 11 is recorded as owner-approved (D-015). No wording changed.

### Commands and actual outputs
- `.venv/bin/python scripts/audit_evidence.py` (about 70 s): all RAW checks 0 failures; `{"tokens": 2953, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 180}`; `number_trace.csv` unchanged.
- `/Users/bechir/research/labs/.tools/pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex`: exit 0; diff limited to the added sentence.
- `.venv/bin/python -m pytest`: `178 passed`.

### Owner placeholders for M5
1. `research/paper/manuscript.md` section 10: "Public repository URL: [placeholder, not published]". The owner supplies the URL at release.
2. `research/publication/author_review.md`: every checklist item is open and is ticked only by the owner, including the title item (approved in D-015 but left for the owner to tick).

No other placeholder needing an owner-only fact was found in the manuscript, supplementary, `README.md` or `CITATION.cff`.

### Next action
M5 (interactive experience), then M6.

## 2026-11-25, session M5 (interactive experience)

**Milestone:** M5. **Starting state:** `5a5a9d9`, tree clean, protocol SHA-256 unchanged. **Authority:** owner, 2026-11-25, "Next" (`../_shared/owner-approvals-2026-11-25d.md`), stack named there: TypeScript, React and Vite from the shared template. Decision D-016.

### What was built
- `scripts/export_demo_data.py` writes `demo/public/data/results.json` (`lab-demo-results` 1.0.0, 158 KB, 28 source files with SHA-256, `code_revision` 79b87f8d5240, no timestamps): EXP-001 (0 estimates, verification counts), EXP-002 (14), EXP-003 (2 primary, 14 per-`phi` secondary), EXP-004 (59: S1 10, S2 7, S3 14, S4 28), EXP-005 (14), M4 exploratory (77). Extension keys `sesoi`, `levels`, `graph_stats`, validated fail-closed.
- `demo/`: template copy; `src/App.tsx` (overview, published results, assumptions, method and limitations), `src/charts.tsx` (level curves with interval bands, forest plots with the SESOI band, tables), `src/Sandbox.tsx` and `src/sandbox.worker.ts` (animated cascade on a sandbox network, three cascade-size histograms, controls: model, `p` or `phi`, seed rule, seed count, N, cascades, topology to animate, random seed; run, cancel, reset, save as JSON; animation toggle defaulting to off under reduced motion), `src/engine.ts` (port of the reference engines and sandbox generators).
- `scripts/make_sandbox_fixture.py` writes `demo/src/fixtures/engine_fixture.json` (35,552 bytes; under one second, one process; a test fixture, not a result).
- `docs/demo.png` (92,212 bytes; sandbox view) with alt text in the README.
- Text consistency: README rewritten (it still described M0), `CITATION.cff` abstract, `articles/medium.md` and `articles/linkedin.md` drafted, `demo/README.md`, `articles/README.md`, `experiments/README.md`, `results/README.md`, release and reproducibility checklist status lines, supplementary version line, one sentence on the demo in manuscript section 10 (same line). `author_review.md`: no agent-ticked box found; approval notes added beside two items, boxes left for the owner; full-text review item added.

### Commands and actual outputs
```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> Audited 25 packages
$ .venv/bin/python scripts/export_demo_data.py                  -> wrote demo/public/data/results.json
$ .venv/bin/python scripts/export_demo_data.py --check          -> results.json up to date
$ .venv/bin/python scripts/make_sandbox_fixture.py              -> wrote demo/src/fixtures/engine_fixture.json (35552 bytes)
$ /Users/bechir/research/labs/.tools/pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex   -> exit 0
$ .venv/bin/python scripts/audit_evidence.py                    -> exit 0 (68 s)
TRIPLES 370 estimate-interval triples matched jointly to one committed row; 0 unmatched
COPIES 129 manifest entries and 56 experiment-folder copies checked, 0 failures
RAW: every run 0 failures (EXP-002 25 checks, EXP-003 13, S1 21, S2 18, S3 25, S4-n500 25, S4-n2000 25, EXP-005 25)
{"tokens": 2953, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 180}
$ .venv/bin/python -m pytest                                    -> 186 passed in 6.79s
(demo, Node v22.23.3, npm cache in the session scratchpad)
$ npm ci --prefer-offline                                       -> added 53 packages
$ npm test                                                      -> Test Files 2 passed (2); Tests 30 passed (30)
$ npm run build                                                 -> tsc and vite build; dist/index.html 0.94 kB, sandbox.worker 7.18 kB, index css 6.91 kB, index js 258.81 kB
$ node tools/a11y_check.mjs dist --screenshots <scratchpad>/viral/shots
PASS results render (no fail-closed panel): 6 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 39 reached of 39
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output (seed 1; IC, p = 0.3; N = 200; 300 cascades per topology; 1 rando
A11Y-CHECK PASS
$ grep -rn REPLACE demo/ --exclude-dir=node_modules             -> no match
```
- Fail-closed check: a copy of `dist` with `levels` removed from `results.json` gives `FAIL results render (no fail-closed panel): 0 experiment panels` and `A11Y-CHECK FAIL (2)`.
- Failures met and fixed during the session: the keyboard check first reached 24 of 42, then 39 of 42 (identical keys for unnamed regions and inputs, buttons disabled mid-animation, tables inside closed `<details>` counted but not tabbable); fixed in the page (ids, no disabled animation buttons, tables rendered only when open). The checker was not changed.
- Screenshots inspected (desktop light and dark, mobile; plus viewport shots of the mobile sandbox in both schemes): forest-plot ticks were too sparse, end labels collided with the last x tick, estimate tables hid intervals behind horizontal scroll at 360 px; all fixed (stacked rows on narrow screens). The full-page mobile capture repeats tiles (a capture artefact); viewport captures were used instead.

### M5 status
**Done.** The master prompt's gate holds: offline after the initial load, responsive (no horizontal scroll at 360 px), usable with the keyboard, no fabricated data (export from committed files, verbatim test), no runtime service.

### Risks and owner items
- Sandbox: the engine is an exact port, but sandbox graphs are browser reimplementations of the models, so sandbox numbers are not research numbers (labelled on the page).
- Owner-only placeholders that remain: repository URL and demo URL. The author line and affiliation are as the owner set them; funding and competing interests as approved in D-015.
- The owner's full-text review of manuscript version 0.2 and the article drafts is pending (M6). Nothing was pushed.

### Next action
M6 (release candidate).

## 2026-11-25, session M6 (release candidate)

**Milestone:** M6. **Starting state:** `68a8fac`, tree clean. **Authority:** owner, 2026-11-25, "Next" (second) (`../_shared/owner-approvals-2026-11-25e.md`). Decision D-017.

### Clean clone of `68a8fac` (session scratchpad, deleted at the end)
```
$ git clone -q <repo> <scratch>/clone; ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   -> exit 0
$ .venv/bin/python -m pytest                                        -> 186 passed in 7.35s
$ .venv/bin/viral smoke --config experiments/EXP-001/config.json    -> runtime 3.47 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)
  comparison with committed M3 smoke EXP-001-20261124T233106Z-99c548ac: identical after removing run_id, git_revision, timestamps, *_seconds, peak_rss_bytes
$ .venv/bin/python scripts/validate_metrics.py <run> <json>         -> 54 checks, 0 failed
$ npm ci --prefer-offline / npm test / npm run build                -> added 53 packages; Tests 30 passed (30); built
$ node tools/a11y_check.mjs dist                                    -> A11Y-CHECK PASS (39 of 39 focusable reached)
$ scripts/export_demo_data.py; scripts/make_sandbox_fixture.py; git status --short   -> (empty)
```

### PDFs
- First attempt: `build_pdf` failed on the manuscript (`typst.TypstError: path "../experiments/EXP-002/figures/fig_primary_contrasts.png" would escape the project root`). Fixed (D-017).
- `.venv/bin/python scripts/build_pdfs.py`: manuscript.pdf 23 pages, supplementary.pdf 13, EXP-001 to EXP-005 report.pdf 4, 9, 6, 8 and 7 pages (largest 617,690 bytes). Every page of all seven documents rendered at 60 ppi and inspected. Fixes (builder and Markdown only): duplicated title, floating tables and half-blank pages, justified narrow cells, a wrapped "2." read as a list item, overlapping run-id and hash columns (four tables), three lists printed as raw "- " text. pypdf: title set in all seven, no e-mail address, no local path. `manuscript.tex` regenerated (with an SPDX line through `header-includes`).

### References, links, numbers, manifests
- Full texts read (free arXiv or author copies; text extracted with pypdf): Kempe et al. 2003 (IC defined, section 1, page 2), Pastor-Satorras et al. 2015 (Eq. 18, section IV.C, page 15), Newman et al. 2001 (Eq. 33, section II.D, page 6), Barabasi and Albert 1999 (page 5, Fig. 2A). Gilbert 1959: no text returned. Totals over 14 bib entries: 5 read in full, 2 abstract only, 7 metadata only or not read.
- `scripts/check_links.py` (new; `tests/test_links.py`, 3 tests): `49 relative links checked, 0 broken; 14 bib entries checked, 0 reference mismatches`, `LINKS PASS`.
- `scripts/audit_evidence.py` (about 70 s, run twice): first run `decimal_untraced` 1 (an arXiv identifier in the reference list), replaced; second run `{"tokens": 2952, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 179}`, all RAW checks 0 failures.
- `data/manifest.json`: 4 of 4 hashes match. `artifact_manifest.json`: 43 of 43 paths and SHA-256 match; 43 of 43 raw result hashes match.

### Scan and licences
- 366 tracked files: 0 tokens or keys, 0 private-key headers, 0 `.env`; e-mail-like strings: 1 (`noreply@anthropic.com` in `CLAUDE.md`, a role address); home-directory paths in 5 files: `CLAUDE.md` (4) and `demo/README.md` (1) made relative; `research/protocol.md` (5, frozen) left as is; `research/literature_review.md` (1) is a URL. This journal keeps its 8 earlier absolute paths (append-only; they name the local tool folders and are noted here instead of edited).
- `research/publication/dependency_licences.md`: no flag (MPL-2.0 for hypothesis and lightningcss, MIT-CMU for pillow, noted).
- SPDX: missing on `demo/.npmrc` and `manuscript.tex` (added) and on nine raw `run.log` files (left unedited).

### CITATION.cff
`date-released` removed; version `0.1.0-rc1`; title equal to the manuscript title; structural check against CFF 1.2.0 keys and types: `CFF STRUCTURE PASS`.

### Owner review checklist
No box was ticked by an agent; none unticked. Section "Prepared for the owner (M6, 2026-11-25)" added with what to read per item, eight open decisions and the placeholder list.

### Working-repository checks before commit
```
$ .venv/bin/python -m pytest              -> 189 passed in 7.46s
$ scripts/export_demo_data.py --check     -> results.json up to date (re-exported once: the artifact-manifest hash changed with the audit counts)
$ npm test; npm run build; a11y check     -> Tests 30 passed (30); built; A11Y-CHECK PASS
```

### Next action
Fresh-clone re-check of the M6 commit (appended below), then the owner's review (`research/publication/author_review.md`) and G-PUBLIC.

## 2026-11-25, session M6, fresh-clone re-check

- Fresh clone of `1679884`: `1 failed, 188 passed` (`test_export_reproduces_committed_file`): the M6 commit changed a demo-export source (`artifact_manifest.json`), so the exported `code_revision` was stale. Re-exported and committed (`3385bd3`, `code_revision` only).
- Fresh clone of `3385bd3`: `uv sync` exit 0; `189 passed in 12.28s`; smoke `runtime 3.20 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)`, identical to the committed M3 smoke apart from volatile fields; `LINKS PASS`; `scripts/build_pdfs.py` (with `VIRAL_PANDOC` and `VIRAL_TYPST_PYTHON` set, since the clone is not next to `../.tools`) rebuilt seven PDFs of the same size and extracted text, differing only in 54 to 96 timestamp bytes; demo export and sandbox fixture byte-identical. Clone deleted.
- M6 status: release candidate prepared, awaiting owner review and G-PUBLIC. Nothing pushed, tagged or released.

### Next action
The owner's review (`research/publication/author_review.md`, section "Prepared for the owner (M6, 2026-11-25)") and the G-PUBLIC decision.

## 2026-11-26, owner answers to the decision sheet applied

**Starting state:** `41c4d4c`, tree clean. **Authority:** owner, 2026-11-26, decision sheet (`../_shared/owner-approvals-2026-11-26.md`). Decision D-018. Wording and configuration only.

### Changes
- A1: status sentences corrected (README, `release_checklist.md`, `reproducibility_report.md`, `author_review.md` open decisions): public on GitHub since 2026-11-25.
- B1, B2: repository and demo URLs filled (README, `CITATION.cff` `repository-code`, manuscript section 10, articles, `demo/README.md`); `demo/wrangler.jsonc` added (assets `./dist`).
- B3: "Mohamed Bechir Kefi, independent researcher" in manuscript, supplementary, five reports, `CITATION.cff` (`affiliation`), README, articles, demo footer (`demo/src/App.tsx`) and demo README.
- B4: manuscript section 11 funding and competing-interest sentences.
- B8, B11, B13: release step and "Release notes (draft)" in `release_checklist.md`. B9: no home path in editable files; `reproducibility_report.md` section 7 lists the two kept files. `author_review.md`: section "Owner answers recorded (2026-11-26)"; no box ticked.

### Commands and outputs
```
$ ../.tools/pandoc research/paper/manuscript.md -s -t latex ... -o research/paper/manuscript.tex   -> regenerated
$ .venv/bin/python scripts/build_pdfs.py   -> manuscript.pdf 619162 bytes (23 pages), supplementary.pdf 250229 (13),
     EXP-001 to EXP-005 report.pdf 84451, 310064, 219725, 264869, 284929 bytes (4, 9, 6, 8, 7 pages)
$ gs -r70 (manuscript pages 1 and 22, supplementary page 1, EXP-002 page 1) -> PNG, inspected: author line, URLs and statements render correctly
$ pypdf: manuscript /Author "Mohamed Bechir Kefi, independent researcher"; author line on page 1 of each report
$ .venv/bin/python -m pytest              -> 189 passed in 7.37s
$ .venv/bin/python scripts/check_links.py -> 49 relative links checked, 0 broken; 14 bib entries checked, 0 reference mismatches; LINKS PASS
$ .venv/bin/python scripts/export_demo_data.py --check -> results.json up to date
$ .venv/bin/python scripts/audit_evidence.py -> {"tokens": 2952, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 179}; number_trace.csv and artifact_manifest.json unchanged
$ (demo) npm ci --prefer-offline; npm test; npm run build -> added 53 packages; Tests 30 passed (30); built
$ node tools/a11y_check.mjs dist -> A11Y-CHECK PASS (39 of 39 reached; no request leaves the local origin)
```

### Next action
The owner's B15 (articles), B16 (full-text review and sign-off) and B18 (release). The coordinator pushes and deploys on the owner's word.

## 2026-11-26: demo brand identity, motion and UI redesign (owner request)

Brief: `labs/_shared/DEMO-BRAND-brief.md` (each demo its own brand, motion and premium UI; the shared "Labs Instrument" look rejected).

### Decisions
- Direction: a field epidemiologist's map sheet. Map paper `#EDF1EE`, survey ink `#14262B`, contour grey `#8FA39E` for what is not reached, incidence red `#C2361F` for what is, fresh-case amber `#E9A23B` for the newest round, harbour blue `#2B6A8E`. Light scheme only. Plan, wireframe, motion plan and the review against the generated-page tells in `demo/DESIGN.md`.
- Type: Archivo variable (condensed heavy for headings, regular width for interface and figures, tabular figures) and Newsreader variable (reading face), both OFL 1.1, Fontsource 5.3.0, resolved with `npm_config_before=2026-11-12`, saved exact; recorded in `demo/README.md` third-party notes. Only the latin files are bundled (Archivo weight and width, Newsreader weight).
- Hero: three network shapes side by side (ER, WS, BA, 56 nodes each), one independent cascade on each drawn with the sandbox's own generators, layout and cascade rule from one fixed stream, lighting up round by round with a replay button; labelled "Illustration, not study data." and showing no number.
- Information architecture: question and one-sentence answer (the manuscript's own sentence); "Same content, three reaches" with Figure B (EXP-002 S by p) moved up as the key picture (the EXP-002 panel now points to it); overview; published results; assumptions; method and limitations; sandbox; reproduce; footer with repository, manuscript, labs index, licence, AI-use and font lines.
- Motion: hero cascade (CSS keyframes on transform and opacity, per-node delays), chart series and forest points revealed once in view, sandbox result line fade, button press. Reduced motion: hero final state, no pulses, opacity-only reveals. The old `transition: r, fill` on sandbox nodes (a property animation on every round step) was removed.
- Brand files in `demo/public/brand/`: mark (a seed passing the content to one neighbour and not yet the other, the two links drawing a V), lockups, favicon SVG and 32 px PNG, Open Graph image 1200 by 630 rendered from HTML with Chrome headless. `svg_audit.py`: marks 100/100 after snapping the links to 60 degrees; lockups 90/100 with one WARN for the near-miss angles of Archivo's own V glyph (type design, left as drawn).

### Commands and actual outputs
- `npm install --save-exact @fontsource-variable/archivo @fontsource-variable/newsreader` (with `npm_config_before=2026-11-12`): added 2 packages, both 5.3.0.
- `npm test`: Test Files 2 passed, Tests 30 passed (no test changed).
- `npm run build`: index JS 268.25 kB (gzip 84.85 kB), CSS 13.99 kB, fonts 90.10 + 58.08 kB woff2; `dist/` 718474 bytes including the Open Graph image.
- `node tools/a11y_check.mjs dist`: 9 PASS, keyboard 44 of 44, `A11Y-CHECK PASS`.
- `uv run --locked pytest tests/test_demo_export.py`: 8 passed (exported data and every displayed number unchanged).
- Screenshots (Chrome headless on 127.0.0.1:5236, desktop 1440, phone 390 in an iframe, `--virtual-time-budget=4000`), two critique passes: answer and byline grouped in one column, replay button moved beside the caption on wide screens, three panels kept side by side on phones with larger nodes, wordmark kept in the phone header, Open Graph drawing corrected so every red link joins two reached nodes.

### Deviations and incidents
- During the checks a stray `git stash` was run on the working tree by mistake and popped immediately (`git stash pop`); the tracked changes were restored intact and the stash entry dropped. Untracked files were never touched.
- Under Chrome's virtual time the sandbox worker does not finish, so the screenshots show it at its progress line; the a11y check (real time) confirms the sandbox runs to its output line.
- No number, result, exported data, fixture, test or test expectation changed. Nothing pushed or deployed.

### Next action
Coordinator: push and redeploy `demo/dist`.

## 2026-11-26: unique typeface pair across the labs (owner request)

Brief: `labs/_shared/FONT-UNIQUE-brief.md` (no two lab demos share a type family). VIRAL row: display face changes, Familjen Grotesk with Newsreader.

### Decisions
- Archivo replaced by Familjen Grotesk variable (`@fontsource-variable/familjen-grotesk` 5.3.0, OFL 1.1, resolved with `npm_config_before=2026-11-12`, saved exact; latin weight file only). Newsreader 5.3.0 kept. Familjen has `tnum`, so figures stay in the display face with tabular figures.
- Type scale re-tuned: no width axis, so every `font-stretch` was removed; weights capped at the face's 700; hero 32 to 58 px tracked -0.024 em, headings 27 to 37 px tracked -0.012 em; phone navigation padding 0.4 rem and 0.88 rem so the four links fit at 390 px without scrolling (nav scroll width 245 of 245).
- Wordmark redrawn from Familjen Grotesk 700 outlines (fontTools instancer); lockups (`lockup.svg`, `-mono`, `-dark`), inline `Brand.tsx` paths and the Open Graph image re-exported; the mark and favicon carry no type and are byte-identical. `svg_audit.py`: mark 100/100; lockup 91/100 with one WARN for the near-miss angles of the V glyph (type design, left as drawn).
- `DESIGN.md`, `README.md` third-party font notes and the footer font line updated.

### Commands and actual outputs
- `npm test`: Test Files 2 passed, Tests 30 passed (no test changed).
- `npm run build`: index JS 267.61 kB (gzip 84.36 kB), CSS 13.97 kB, fonts 18.91 kB (Familjen) + 58.08 kB (Newsreader) woff2; `dist/` 637102 bytes.
- `node tools/a11y_check.mjs dist`: keyboard 44 of 44, `A11Y-CHECK PASS`.
- `uv run --locked pytest tests/test_demo_export.py`: 8 passed.
- Screenshots in real time over the DevTools protocol on 127.0.0.1:5245, desktop 1440 and phone 390, checked for wrapping, overflow and clipped labels.

### Deviations and incidents
- None. No number, data, fixture, test expectation, accessible name or scientific wording changed. Nothing pushed or deployed.

### Next action
Coordinator: push and redeploy `demo/dist`.
