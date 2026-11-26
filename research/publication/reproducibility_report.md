<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Reproducibility report

Status at M6 (2026-11-25): checked in a clean local clone of revision `68a8fac` (the M5 commit), then re-checked in a fresh clone of the M6 commit after the fixes listed in section 4. Every line below is an actual command output. Nothing was pushed in the M6 session; the repository was pushed and has been public on GitHub since 2026-11-25 (correction of 2026-11-26).

- [x] Clean clone into a separate directory (`git clone -q <working repository> <session scratchpad>/clone`; local clone, no network).
- [x] `uv sync --frozen --all-groups --all-extras` succeeds (uv 0.9.5; 25 packages plus the project).
- [x] Test suite runs; actual count and result recorded (section 1).
- [x] Smoke reproduction matches stored results within the documented tolerance (section 1).
- [x] Demo builds offline; accessibility and offline checker passes (section 2).
- [x] Data manifest and links verified (section 3).
- [x] Secret and licence scan (section 3; `dependency_licences.md`).
- [x] Hardware, OS, package versions and git revision recorded (section 5).

## 1. Python environment, tests and smoke reproduction (clone of `68a8fac`)

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras      -> installed, exit 0
$ .venv/bin/python -m pytest                                       -> 186 passed in 7.35s
$ .venv/bin/viral smoke --config experiments/EXP-001/config.json
run EXP-001-20261125T191738Z-99c548ac (exploratory) written to <clone>/results/exploratory/EXP-001/...
runtime 3.47 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)
$ .venv/bin/python scripts/validate_metrics.py <new smoke run dir> <scratch json>
54 checks, 0 failed
```

Smoke comparison with the committed M3 smoke run `EXP-001-20261124T233106Z-99c548ac` (documented in `research/experiments/EXP-001/reproduction.md`: "Seeded streams make reruns on the same platform and package versions identical"):

- The new `result.json` has SHA-256 `e5c4f53e...` against the committed `d299dfac...`; the files differ only in volatile fields.
- After removing `run_id`, `git_revision`, `started_utc`, `finished_utc`, `peak_rss_bytes` and every `*_seconds` timing field, the two documents are identical (structural JSON comparison: "IDENTICAL"). The differing fields were 15 `generation_seconds`, 106 `runtime_seconds`, and one each of the run id (twice), revision, timestamps and peak memory.
- Outcome: the smoke reproduction matches exactly on every simulated value (tolerance zero). The new run folder was deleted from the clone.

Confirmatory runs were not repeated (no confirmatory runs at M6). Their raw `result.json` files are git-ignored; `scripts/audit_evidence.py`, run in the working repository, recomputed every confirmatory table from them with 0 failures (section 3).

## 2. Demo (clone of `68a8fac`; Node v22.23.3, npm cache in the session scratchpad)

```
$ npm ci --prefer-offline        -> added 53 packages in 763ms
$ npm test                       -> Test Files 2 passed (2); Tests 30 passed (30)
$ npm run build                  -> dist/index.html 0.94 kB; sandbox.worker 7.18 kB; index css 6.91 kB; index js 258.81 kB; built in 284ms
$ node tools/a11y_check.mjs dist
PASS results render (no fail-closed panel): 6 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 39 reached of 39
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs
A11Y-CHECK PASS
```

Export determinism: in the clone, `scripts/export_demo_data.py` and `scripts/make_sandbox_fixture.py` were re-run (`wrote demo/public/data/results.json`; `wrote demo/src/fixtures/engine_fixture.json (35552 bytes)`), and `git status --short` printed nothing: both outputs are byte-identical to the committed files.

## 3. Manifests, links, references and scans (working repository)

- `data/manifest.json`: 4 hashed files (3 raw files of the real network, git-ignored but present locally, and `data/processed/maier_fb.json`); 4 of 4 SHA-256 values match. The two external-dataset entries with `"sha256": null` are sources that were evaluated and not used.
- `research/publication/artifact_manifest.json`: 43 artifacts; 43 of 43 paths exist and match their SHA-256; 43 of 43 git-ignored raw `result.json` files present locally match `result_sha256`.
- `scripts/audit_evidence.py` (about 70 s): every RAW check 0 failures; `{"tokens": 2952, "decimal_traced": 2217, "decimal_traced_weak": 1392, "decimal_untraced": 0, "integer_traced": 556, "integer_constant_or_count": 179}`.
- `scripts/check_links.py` (new at M6, tested by `tests/test_links.py`): `49 relative links checked, 0 broken; 14 bib entries checked, 0 reference mismatches`, `LINKS PASS`.
- Secret and identifier scan over the 366 tracked files (`git ls-files`): 0 tokens or keys, 0 private-key headers, 0 `.env` files; 1 e-mail-like string (the commit-trailer address `noreply@anthropic.com` quoted in `CLAUDE.md`, a role address, not a personal one); absolute home-directory paths in 5 files (section 4).
- Dependency licences: `research/publication/dependency_licences.md` (no flag outside the permissive list).

## 4. Findings and fixes

| # | finding | fix | re-check |
|---|---|---|---|
| 1 | `viral.report.build_pdf` could not compile the manuscript: Typst refused `../experiments/EXP-002/figures/...` ("would escape the project root"). | `build_pdf` takes a `root` argument; `scripts/build_pdfs.py` passes the repository root. | all seven PDFs compile |
| 2 | Visual inspection: the manuscript title printed twice; long tables floated to the next page and left half-blank pages; narrow justified table cells; a wrapped line starting "2." became a numbered list item (manuscript section 4.4); run-id and hash columns overlapped in supplementary S3, EXP-001 and EXP-004 execution tables; two lists in EXP-002 and one in EXP-005 printed as raw "- " text. | Builder: a Lua filter drops the repeated title heading (and takes the first heading as the title when the YAML has none, so every PDF has title metadata), tables may break across pages, table cells are not justified, table text is 0.9 em, pandoc runs with `--wrap=none`. Sources: column widths in four pipe tables; a blank line before three lists. No number or wording changed. | pages re-rendered and inspected |
| 3 | Stale text: supplementary S5, `research/limitations.md` item 17 and the README said no PDF existed. | Updated to point to the M6 PDFs. | |
| 4 | Absolute home-directory paths in `CLAUDE.md` (4) and `demo/README.md` (1). | Replaced by paths relative to the repository root. `research/protocol.md` (5, frozen) and `progress.md` (8, append-only) are left unchanged; the URL hit in `research/literature_review.md` (`cs.cornell.edu/home/...`) is a web address. | |
| 5 | Files without an SPDX header among those added since M0: `demo/.npmrc`, `research/paper/manuscript.tex`, nine `run.log` files. | Header added to `demo/.npmrc` and, through pandoc `header-includes`, to `manuscript.tex` (command updated in `CONTRIBUTING.md`). The `run.log` files are raw run outputs and are not edited. | |
| 6 | Four sources the manuscript leans on were at abstract level. | Free arXiv or author copies read (Kempe et al. 2003, Newman et al. 2001, Barabasi and Albert 1999, Pastor-Satorras et al. 2015 section IV.C); manuscript section 2, the reference list and `references.bib` updated (`research/literature_review.md`, M6 update). | audit: 0 untraced |

## 5. Environment

Apple M1 Pro, arm64, macOS 15.3.1; Python 3.12.1; uv 0.9.5; networkx 3.7, numpy 2.5.4, jsonschema 4.26.0, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15; pandoc 3.6.3; typst 0.15.0 (Python package), pypdf 6.20.0; Node v22.23.3, npm packages from `demo/package-lock.json`. Git revision of the first clone: `68a8fac`.

## 6. Fresh-clone re-check of the M6 commits

The first fresh clone of the M6 commit `1679884` found one failure: `tests/test_demo_export.py::test_export_reproduces_committed_file` (1 failed, 188 passed). The exporter records the last commit that touched a source file, and the M6 commit itself changed one source (`artifact_manifest.json`), so the committed export still named `79b87f8`. Fixed by re-exporting after the commit (`3385bd3`; only `code_revision` changed). The same clone showed that `scripts/build_pdfs.py` needs `VIRAL_PANDOC` and `VIRAL_TYPST_PYTHON` when the clone is not next to the shared tools folder (its default is `../.tools`).

Fresh clone of `3385bd3`:

```
$ uv sync --frozen --all-groups --all-extras                 -> exit 0
$ .venv/bin/python -m pytest                                 -> 189 passed in 12.28s
$ .venv/bin/viral smoke --config experiments/EXP-001/config.json
runtime 3.20 s; graphs 15 (failures 0); cascades checked 5250 (failures 0)
  structural comparison with the committed M3 smoke: IDENTICAL after removing volatile fields
$ .venv/bin/python scripts/check_links.py                    -> LINKS PASS (49 links, 14 bib entries)
$ VIRAL_PANDOC=... VIRAL_TYPST_PYTHON=... scripts/build_pdfs.py   -> seven PDFs, same byte sizes as committed
$ scripts/export_demo_data.py; scripts/make_sandbox_fixture.py; git status   -> only the seven PDFs listed
```

The rebuilt PDFs have the same size, page count and extracted text as the committed ones; they differ in 54 to 96 bytes, the creation and modification timestamps that Typst writes. The PDFs are therefore reproducible in content, not byte for byte. The demo export and the sandbox fixture are byte-identical. The clone was deleted.

## 7. Local home paths remaining (B9, 2026-11-26)

Owner, 2026-11-26, decision sheet, B9: local home paths are removed from editable files in a new commit; frozen, append-only and checksummed files are untouched and history is not rewritten. A search of the tracked files for absolute home-directory paths after the 2026-11-26 changes finds them in two files only, both left unchanged on purpose:

| file | occurrences | why it is kept |
|---|---|---|
| `research/protocol.md` | 5 | frozen protocol (version 1.0, hash in `research/freeze.json`); editing it would change the freeze hash |
| `progress.md` | 8 lines, all in entries before 2026-11-26 | append-only journal; its dated entries stay true for their date |

`CLAUDE.md`, the README files, docs, scripts, source code and demo files carry no absolute home path (they were made relative at M6). The committed PDFs were checked at M6 with pypdf and contain no local path.
