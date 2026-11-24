<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-002 protocol: independent cascade, topology x transmission x initial exposure

**Status: DRAFT, awaiting owner freeze. Planned confirmatory experiment; no run may be called confirmatory before the owner freezes this file.**
Version 0.1, 2026-11-24. Protocol hash: none (not frozen). Depends on EXP-001 passing all verification checks.

1. **Precise question.** At matched node count, mean degree and transmission probability, does the expected final IC cascade fraction differ between small-world (WS) or scale-free (BA) graphs and Erdos-Renyi (ER) graphs, and how does initial exposure (seed rule, seed count) change it?
2. **Mechanism.** On locally tree-like graphs, IC final size relates to bond percolation; the threshold depends on the first two degree moments (Newman, Strogatz and Watts 2001; Pastor-Satorras and Vespignani 2001). WS adds clustering and short paths (Watts and Strogatz 1998); BA adds hubs (Barabasi and Albert 1999).
3. **Rationale from verified sources.** See `research/literature_review.md`. Gap: a small, fully reproducible, matched comparison that reports final size together with depth, duration and outcome inequality, with replicate-level uncertainty and an explicit test of whether degree moments alone explain the effect (EXP-004). This is a replication-and-integration contribution, not a novelty claim.
4. **Competing explanations.** (a) Degree heterogeneity alone (tested in EXP-004 S1, S2). (b) Residual edge-count mismatch (S3). (c) Finite size (S4). (d) Stochastic variability across cascades mistaken for a topology effect (handled by replicate-level inference and the variance decomposition).
5. **Hypotheses.** H0: `Delta_WS = 0` and `Delta_BA = 0`. H1: at least one differs (nondirectional). Definitions in `research/protocol.md` section 3 and 4.
6. **Estimand.** `Delta_T = E_r[Sbar_{T,r} - Sbar_{ER,r}]`, `T` in {WS, BA}, random single seed, mean over the `p` grid.
7. **Experimental unit.** Graph replicate. Population: synthetic graphs with `N = 1000`, `<k> = 6` (planning values).
8. **Independent variables.** Topology; `p` in {0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50}; seed rule {random, highest degree}; seed count {1, 10}. **Dependent variables.** `S` (primary), `D`, `T`, `T50`, Gini `G`, large-cascade probability, variance shares.
9. **Treatment and control.** Treatments WS (`k = 6`, `beta = 0.1`) and BA (`m = 3`); control ER G(n, M = 3000).
10. **Baseline.** ER, random single seed.
11. **Seed plan.** Master seed fixed at the freeze; per-run seeds from `SeedSequence.spawn`; matched sets across topologies by replicate index; `R = 30`, `C = 200`.
12. **Sample-size rationale.** Target Holm-adjusted half-width 0.01 for each primary contrast; `R = 30` is sufficient if `sd_diff <= 0.028`; checked against EXP-001 before the freeze.
13. **Compute budget.** 504,000 cascades; at most 4 hours wall clock on the M1 Pro (planning value; confirmed from EXP-001 runtime before the freeze).
14. **Metric formulas and units.** `S = |A_final|/N` (fraction); `D` = max activation-tree generation (edges); `T` = rounds with new activations (rounds); `T50` (rounds); `G = sum_i sum_j |x_i - x_j| / (2 n^2 xbar)` over cascade sizes (dimensionless).
15. **Uncertainty method.** Paired cluster bootstrap over replicate index, `B = 10000`, percentile 95 percent intervals, Holm over the two primary contrasts; secondary metrics unadjusted and labelled.
16. **Exclusion and stopping rules.** As in `research/protocol.md` section 5.
17. **Anticipated failure modes.** Runtime above budget at `p = 0.5` (large cascades): mitigate by vectorised frontier expansion, not by dropping cells. Bootstrap degenerate when all replicates are equal at `p = 0.5` near saturation: report exact values.
18. **Sensitivity tests.** EXP-004 (S1 to S4).
19. **What would contradict H1.** Both Holm-adjusted intervals contain 0. What would contradict the "topology" interpretation even if H1 holds: the S1 or S2 result in EXP-004.
20. **Reproducibility commands (planned).** `uv run python -m viral.cli run --config research/experiments/EXP-002/config.json`; `uv run python -m viral.cli report EXP-002`.
