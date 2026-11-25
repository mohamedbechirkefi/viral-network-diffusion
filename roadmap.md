<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# VIRAL roadmap

Updated 2026-11-25 (session M5). Effort is a planning estimate in focused days (total target: five). Status values: not started, in progress, done, blocked, gated (owner).

| Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|
| M0 Bootstrap and feasibility | none | P0 | 0.25 d | done: scope, cost and exclusions are in `research/protocol.md` section 1, frozen with the owner's approval on 2026-11-24 (D-010) | none |
| M1 Research and preregistration | M0 | P0 | 0.5 d | done: gate passed, protocol v1.0 frozen (owner-approved 2026-11-24; `research/freeze.json`) | none |
| M2 Core implementation | M1 drafts (implementation may start before the freeze) | P0 | 1.5 d | done (see M2 section); the EXP-001 report was written at M3 (D-013); the D-007 amendments were decided before the freeze (D-009, D-010) | none |
| M3 Experiments | M2; M1 freeze for confirmatory runs | P0 | 1 d | done (2026-11-25): full frozen matrix of EXP-002 to EXP-005 run, 8 runs, none failed or dropped; reports written (D-013) | none |
| M4 Interpretation | M3 | P0 | 0.75 d | done (2026-11-25): gate holds (evidence audit; manuscript v0.2; second review pass); title and statements owner-approved (D-015) | owner full-text review of the manuscript (M6; author_review.md) |
| M5 Interactive experience | M3 results (sandbox can start at M2) | P1 | 0.75 d | done (2026-11-25): gate holds (offline, responsive, keyboard, no fabricated data, no runtime service; D-016) | none |
| M6 Release candidate | M4, M5 | P0 | 0.25 d | not started | G-PUBLIC for any publication |

## M0 Bootstrap and feasibility

- Acceptance: control files of section 2 exist; hardware and tools confirmed by commands; budget, scope, exclusions and fallback written (`research/protocol.md` section 1); licence decision recorded (D-001).
- 11.6 additions: experiment registry initialised; manuscript skeleton exists; zero-cost local publication toolchain confirmed (D-002; exploratory smoke check in `progress.md`).
- Gate: the owner can understand question, cost and exclusions.

## M1 Research and preregistration

- Acceptance: evidence review with verification levels; formal model and baselines; protocol with H0/H1, primary metric, unit, seeds, sample-size rationale, uncertainty, exclusion and stopping rules, smoke and full matrix, sensitivity analyses; experiment-specific protocols (11.2) for EXP-001 to EXP-004; fixture manifest (`data/manifest.json`).
- 11.6 additions: freeze confirmatory protocols before execution, with hash and recorded owner approval.
- Gate: protocol frozen before confirmatory runs; exploratory results visibly separated.
- Status: drafts done 2026-11-24; amendments applied and protocol v1.0 frozen 2026-11-24 (owner-approved, D-009, D-010). Real-data check done (D-008): one MIT-licensed real network adopted for EXP-005.

## M2 Core implementation

- Tasks: graph generators with matching checks; IC engine (reference loop first, then vectorised variant with differential test); fractional-threshold engine; metrics (S, D, T, T50, Gini, variance decomposition); seeded runner; versioned JSON result schema with validation; run manifests (runtime, peak memory, OS, CPU, package versions, git revision, config hash); CLI `smoke`, `run`, `report`, `test`.
- Tests: no-transmission and all-transmission cases, disconnected components, duplicate activation, graph invariants, hand-computed examples, determinism, invalid inputs, extreme parameters.
- 11.6 additions: versioned output schemas, reproducibility manifests and report generators built alongside the core.
- Acceptance: tests executed with recorded counts; EXP-001 smoke run (exploratory) passes all checks. Gate: correctness before UI polish.
- Status (2026-11-24, session M2):
  - Done: generators with invariant checks; IC reference and vectorised engines (exact differential test); LT reference and vectorised engines; metrics S, D, T, T50, Gini, large-cascade share, structural virality; variance decomposition; paired cluster bootstrap and Holm; seeded runner with common random numbers; config and result JSON schemas (1.0.0) validated at export and import; run manifests; fail-closed protocol gate; CLI `smoke`, `run`, `report`, `test`; report generator (Markdown, CSV tables, PNG/SVG figures, PDF via pandoc to Typst); EXP-004 helpers (degree-preserving randomisation, edge trimming).
  - Tests: 158 passed, 0 failed (`uv run --locked pytest`, 2026-11-24).
  - EXP-001 smoke (exploratory): 15 graphs and 5,250 cascades, 0 verification failures, 3.3 s.
  - Planning probe (exploratory): 288,000 cascades in 114.8 s; EXP-002 projected at about 142 s of engine time.
  - Not done: the 12-part EXP-001 `report.md` (moved to M3 with the other reports); S1 to S4 runner wiring (the helpers exist, the configs do not); proposed amendments D-007 await the owner.

## M3 Experiments

- Tasks: EXP-001 report; after the freeze, EXP-002 full matrix, EXP-004 (S1 to S3, S4 optional), EXP-003 (optional if the budget is threatened).
- 11.6 additions: individual reports generated as experiments finish; unsuccessful experiments and deviations recorded; provenance captured at run time.
- Acceptance: complete planned matrix or documented failure; no silently dropped runs; raw results retained.
- Status (2026-11-25, session M3): gate holds. EXP-002 (2,016,000 cascades), EXP-003 (504,000), EXP-004 S1 to S3 and optional S4 (552,000), EXP-005 (504,000) all complete at revision `32961c3`; raw results git-ignored with committed SHA-256; analysis tables, figures, run manifests and logs in `results/confirmatory/`; 89 claim rows generated. Outstanding: the 12-part `report.md` of each experiment (file tool refused; coordinator instruction to leave them unwritten) and the owner's S1 cross-reading decision (D-012).

## M4 Interpretation

- Tasks: confounder inspection; sensitivity analyses; expected versus observed; claims register; limitations; second review pass challenging the preferred hypothesis.
- 11.6 additions: finish experiment reports and evidence audit; synthesise into the manuscript including contradictory results.
- Acceptance: every numerical claim maps to result id, config and figure; every external claim to a verified source.
- Status (2026-11-25, session M4): done. Exploratory confounder checks X1 to X3 (`results/exploratory/M4/`); claims register extended to 575 rows with result id, config hash, figure or table and section; evidence audit (`research/publication/evidence_audit.md`: 177 raw recomputation checks, 0 failures; 0 untraced decimals; 370 interval triples matched; one runtime mismatch and four over-stated citations fixed); manuscript and supplementary synthesised, revised after `research/publication/review_pass_2.md` (version 0.2); limitations 18 to 24; D-014. Tests 178 passed.

## M5 Interactive experience

- Tasks: static page (TypeScript, React, Vite, Web Worker) with animated cascades, seed controls, distribution plots; precomputed published results clearly separated from visitor sandbox results.
- 11.6 additions: demo, paper, reports and articles use identical verified results, labels and scope.
- Acceptance: offline after initial load, responsive, keyboard usable, reduced-motion option, no runtime service. Node 22.23.3 used read-only.
- Status (2026-11-25, session M5): done. `demo/` (shared template stack: TypeScript, React, Vite, Web Worker; no added dependency) shows every registered experiment and the M4 checks with intervals, the level curves and forest plots, assumptions, method and limitations, and a sandbox with animated cascades, seed controls and distribution plots. Data exported by `scripts/export_demo_data.py`; `tests/test_demo_export.py` (8 tests) checks the export and that the page, README, CITATION.cff and article drafts print only manuscript numbers. Sandbox engine: exact port, zero-tolerance fixture test; sandbox graphs reimplemented (D-016). Checker: A11Y-CHECK PASS. Tests: 186 Python, 30 vitest. Article drafts `articles/medium.md` and `articles/linkedin.md` written.

## M6 Release candidate

- Tasks: clean clone, `uv sync --locked`, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan.
- 11.6 additions: compile and visually inspect manuscript and report PDFs (pandoc to Typst); verify references, cross-links, equations, figures, metadata; owner review checklist.
- Acceptance: actual command outputs recorded. No publication or push without owner approval (G-PUBLIC).
