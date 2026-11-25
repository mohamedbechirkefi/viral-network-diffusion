<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-001 report: engine verification and smoke matrix (EXPLORATORY)

**EXPLORATORY EXPERIMENT. Not a finding.** EXP-001 has no confirmatory config. No claim about topology may be drawn from it.

## 1. Identification

- Experiment: EXP-001 (exploratory by design). Report version 1.0, 2026-11-25. Status: **exploratory runs complete; every verification check passed.**
- Authorship: Mohamed Bechir Kefi (no affiliation). An AI research and development assistant (Claude, Anthropic) ran the checks and drafted this report under the owner's direction; it is not an author.
- Protocol `research/experiments/EXP-001/protocol.md`, text frozen v1.0, SHA-256 `e65cf620d66b6fd8cf98815f626693b7744dc7d801f30bdbdd55875da14f9ff0` (`research/freeze.json`). Study protocol SHA-256 `d984f2f8f2fba8f5ddabe097b0a82be8d17ab652422769f9c22cc442f1a17b32`.
- Code revisions: `6edd91e1d23537dae822553fd56edaf08a235545` (M2 smoke run and planning probe) and `ceeee8c13d460f6772a5a09f392c114884b1b1bf` (M3 pre-run smoke).
- Written after the runs from committed files only, with the owner's approval of 2026-11-25 (D-013).

## 2. Executive summary

- **Question.** Does the engine implement IC and fractional-threshold diffusion correctly on ER, WS and BA graphs? What runtime and between-replicate variability should size EXP-002?
- **Method.** Smoke matrix: 3 topologies; IC `p` in {0, 0.05, 0.20, 1}; LT `phi` in {0, 0.18, 1.01}; one random seed; `R = 5`; `C = 50`. Every cascade passed through the verification checks. A planning probe ran the draft EXP-002 and EXP-003 grids at `R = 10`. All runs used the pilot master seed 20261124.
- **Outcome.** 0 verification failures in both smoke runs: 15 graphs and 5,250 cascades in each. 54 of 54 known-case metric checks passed. The probe ran 288,000 cascades in 114.8 s.
- **Caveat.** The probe values of the primary contrast were seen before the freeze. They motivated the owner-approved amendments and are disclosed in `research/freeze.json` (C4).

## 3. Rationale

The IC and LT definitions follow Kempe, Kleinberg and Tardos (2003), doi:10.1145/956750.956769, and Watts (2002). The generators are from networkx 3.7. Verification levels are in `research/literature_review.md`. Before any confirmatory run, a topology difference has to be shown to come from structure and not from a bug, such as duplicate activation.

## 4. Checks (pass/fail, protocol item 5)

`p = 0` gives the seed set only, with depth 0 and duration 0. `p = 1` activates exactly the seeded components. No activation crosses components, and no node is activated twice. IC depth equals duration. LT with `phi = 0` activates the seeded components, and LT with `phi > 1` activates only the seeds. Graph invariants hold: node and edge counts, no self-loops or multi-edges, mean degree within 1 percent, determinism. Hand-computed examples match on path, star and triangle graphs. Disconfirmation (item 18): any failed check means the engine is not ready.

## 5. Methodology

- Smoke config `experiments/EXP-001/config.json`, canonical hash `99c548ac3da117e55003d39e0fb70fa44ad73faaeac858992e8555a9f3b33f25`, `verify: true`, vectorised engines. `N = 1000`, `<k> = 6`, WS `beta = 0.1`.
- Probe config `experiments/EXP-001/probe-config.json`, canonical hash `d947f41d5aa9859419b9aadf92f017170fb470e0d93932f37d7af2c3e5189597`. It covers the full draft EXP-002 `p` grid and LT at `phi` in {0.10, 0.14, 0.18, 0.22, 0.26}, with `R = 10`.
- Metric validation: `scripts/validate_metrics.py`. It checks S, D, T, T50, structural virality, Gini, large-cascade share, `p_c`, Holm and the bootstrap family on hand-computed cases, plus the smoke `p = 0` cells.
- Hardware: Apple M1 Pro (10 logical CPUs), macOS 15.3.1, Python 3.12.1, numpy 2.5.4, networkx 3.7. The budget was 10 minutes, and every run stayed within it.

## 6. Implementation verification

- Test suite: 158 passed at M2 (2026-11-24) and 174 passed before the M3 confirmatory runs (`progress.md`).
- Reference and vectorised IC engines are exactly differential-tested, and so are the two LT engines (M2).
- Under the frozen LT depth definition, LT depth equals duration in every case, as proved (D-007 A4). This is disclosed, not a failure.

## 7. Execution record

| run id | purpose | revision | started (UTC) | runtime | graphs / cascades | verification failures |
|---|---|---|---|---|---|---|
| EXP-001-20261124T162117Z-99c548ac | M2 smoke | 6edd91e | 2026-11-24T16:21:17Z | 3.28 s | 15 / 5,250 | 0 |
| EXP-001-20261124T162121Z-d947f41d | M2 planning probe | 6edd91e | 2026-11-24T16:21:21Z | 114.82 s | 288,000 cascades | not applicable (probe) |
| EXP-001-20261124T233106Z-99c548ac | M3 pre-run smoke | ceeee8c | 2026-11-24T23:31:06Z | 3.50 s | 15 / 5,250 | 0 |
| EXP-001-M3-metric-validation-20261125 | known-case checks | ceeee8c plus M3 scripts (committed as 32961c3) | 2026-11-25 | not recorded | 54 checks | 0 |

No run failed or was dropped. The probe's raw `result.json` is git-ignored, and its SHA-256 is committed (`result.json.sha256`).

## 8. Results (descriptive, exploratory)

- Verification: 0 graph failures and 0 cascade failures over 5,250 checked cascades, in both smoke runs. Metric validation: 54 checks, 0 failed.
- Planning probe, per-`p` replicate-level contrasts at `R = 10` (`tables/contrasts_by_param.csv` of the probe run). Descriptive only:

| p | BA - ER mean diff | BA - ER sd_diff | WS - ER mean diff | WS - ER sd_diff |
|---|---|---|---|---|
| 0.02 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 0.05 | 0.0003 | 0.0001 | 0.0000 | 0.0000 |
| 0.10 | 0.0061 | 0.0016 | -0.0004 | 0.0002 |
| 0.15 | 0.0548 | 0.0065 | -0.0047 | 0.0013 |
| 0.20 | 0.1019 | 0.0166 | -0.0835 | 0.0095 |
| 0.30 | -0.0540 | 0.0327 | -0.3564 | 0.0369 |
| 0.50 | -0.0445 | 0.0279 | 0.0531 | 0.0242 |

- Sizing consequence (D-007 A2, owner-approved): the largest per-`p` sd of paired differences was 0.037 (WS - ER at `p = 0.30`). With 14 Holm tests, a half-width of 0.01 needs `R = 116`, so EXP-002 uses `R = 120`. The projected EXP-002 engine time was about 142 s from the probe, or about 9.5 minutes at `R = 120` (protocol 11.2). The confirmatory run took 1047.8 s of total runtime (EXP-002 run manifest).
- The probe showed that LT `phi` 0.10 and 0.14 saturate. This motivated the new EXP-003 grid of 0.18 to 0.30 (D-007 A3).

## 9. Interpretation

Every pass/fail check passed, so under item 18 the engine was ready for EXP-002. The probe contrasts served only for planning. They are not evidence for any hypothesis. The confirmatory EXP-002 values (new seed 20261125, `R = 120`) are close to them, but this agreement was not a test.

## 10. Threats to validity

The checks cover the stated invariants and small hand-computed cases, not every possible graph. The probe's exposure of primary-contrast values before the freeze is a known threat, disclosed in C4. It is mitigated by a new confirmatory master seed and by an analysis plan fixed before the confirmatory runs.

## 11. Conclusion

The engine and metrics are verified to the level the protocol requires. EXP-001 supports no scientific claim.

## 12. Reproduction appendix

See `reproduction.md` in this folder.
