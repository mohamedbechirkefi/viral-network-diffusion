<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-003 protocol: fractional-threshold diffusion, topology x threshold x initial exposure

**Status: DRAFT, awaiting owner freeze. Secondary experiment; optional if the five-day budget is threatened.**
Version 0.1, 2026-11-24. Protocol hash: none (not frozen). Depends on EXP-001.

1. **Precise question.** Under a fractional-threshold model, where a node activates once the fraction of active neighbours reaches `phi`, does the final cascade fraction differ between WS or BA and ER graphs at matched size and mean degree?
2. **Mechanism.** Threshold (complex) contagion needs multiple exposures; hubs are hard to activate and clustering supplies redundant exposure (Granovetter 1978; Watts 2002; Centola and Macy 2007). The topology ordering may differ from IC.
3. **Rationale.** Tests whether conclusions from EXP-002 depend on the contagion model.
4. **Competing explanations.** Seed count dominating (with one seed and `phi > 1/k_min` nothing spreads); degree heterogeneity alone.
5. **Hypotheses.** H0: `Delta^LT_WS = 0` and `Delta^LT_BA = 0` (mean over the `phi` grid, seed count 10, random seeds). H1: at least one differs (nondirectional).
6. **Estimand.** As EXP-002 with `S` from the threshold model.
7. **Experimental unit.** Graph replicate.
8. **Independent variables.** Topology; `phi` in {0.10, 0.14, 0.18, 0.22, 0.26} (planning values chosen around the Watts 2002 cascade window for `<k> = 6`); seed rule {random, highest degree}; seed count {1, 10}. **Dependent variables.** `S`, `D`, `T` (here `D` and `T` can differ), `T50`, Gini `G`.
9. **Treatment and control.** As EXP-002.
10. **Baseline.** ER, random seeds, seed count 10 (one seed rarely spreads under thresholds; to be confirmed in EXP-001 smoke, which is exploratory).
11. **Seed plan.** `R = 30` replicates; the threshold model is deterministic given graph and seed set, so `C = 200` random seed sets per graph for the random rule and `C = 1` for the highest-degree rule (ties broken by a seeded draw).
12. **Sample-size rationale.** As EXP-002.
13. **Compute budget.** At most 1 hour.
14. **Metric formulas.** As EXP-002. `D`: generation of a node is 1 + the maximum generation among the active neighbours present when it activated (planning definition; to be fixed at the freeze).
15. **Uncertainty.** As EXP-002, Holm over two contrasts within EXP-003.
16. **Exclusion and stopping.** As `research/protocol.md`.
17. **Anticipated failure modes.** All-or-nothing outcomes making intervals degenerate; report exact proportions.
18. **Sensitivity.** Heterogeneous thresholds (uniform random as in Kempe et al. 2003), exploratory.
19. **Contradiction.** Both intervals contain 0.
20. **Reproducibility commands (planned).** `uv run python -m viral.cli run --config research/experiments/EXP-003/config.json`.
