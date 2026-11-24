<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# VIRAL roadmap

Updated 2026-11-24 (session DATA-FREEZE). Effort is a planning estimate in focused days (total target: five). Status values: not started, in progress, done, blocked, gated (owner).

| Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|
| M0 Bootstrap and feasibility | none | P0 | 0.25 d | done (pending owner review of scope and cost) | none |
| M1 Research and preregistration | M0 | P0 | 0.5 d | done: gate passed, protocol v1.0 frozen (owner-approved 2026-11-24; `research/freeze.json`) | none |
| M2 Core implementation | M1 drafts (implementation may start before the freeze) | P0 | 1.5 d | done for the pre-freeze scope (see M2 section); EXP-001 report.md pending (M3) | none for implementation; owner decisions D-007 before the freeze |
| M3 Experiments | M2; M1 freeze for confirmatory runs | P0 | 1 d | not started; EXP-002 to EXP-005 frozen, not yet run | scheduling by the coordinator |
| M4 Interpretation | M3 | P0 | 0.75 d | not started | none |
| M5 Interactive experience | M3 results (sandbox can start at M2) | P1 | 0.75 d | not started | none |
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

## M4 Interpretation

- Tasks: confounder inspection; sensitivity analyses; expected versus observed; claims register; limitations; second review pass challenging the preferred hypothesis.
- 11.6 additions: finish experiment reports and evidence audit; synthesise into the manuscript including contradictory results.
- Acceptance: every numerical claim maps to result id, config and figure; every external claim to a verified source.

## M5 Interactive experience

- Tasks: static page (TypeScript, React, Vite, Web Worker) with animated cascades, seed controls, distribution plots; precomputed published results clearly separated from visitor sandbox results.
- 11.6 additions: demo, paper, reports and articles use identical verified results, labels and scope.
- Acceptance: offline after initial load, responsive, keyboard usable, reduced-motion option, no runtime service. Node 22.23.3 used read-only.

## M6 Release candidate

- Tasks: clean clone, `uv sync --locked`, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan.
- 11.6 additions: compile and visually inspect manuscript and report PDFs (pandoc to Typst); verify references, cross-links, equations, figures, metadata; owner review checklist.
- Acceptance: actual command outputs recorded. No publication or push without owner approval (G-PUBLIC).
