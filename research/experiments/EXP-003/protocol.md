<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-003 protocol: fractional-threshold diffusion, topology x threshold x initial exposure

**Status: FROZEN, version 1.0 (owner-approved 2026-11-24), not yet run. Secondary experiment; optional if the five-day budget is threatened.**
Version 1.0, 2026-11-24. Protocol hash: in `research/freeze.json`. Where the amendment section at the end and items 1 to 20 differ, the amendment section wins. Depends on EXP-001.

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
20. **Reproducibility commands.** `.venv/bin/viral run --config experiments/EXP-003/config.json`; `.venv/bin/viral report results/confirmatory/EXP-003/<run_id>`.

## Amendments before freeze (owner-approved 2026-11-24, round 2)

- **A-1 (item 8).** Threshold grid `phi` in {0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30} (`research/protocol.md` section 11.4). The hypotheses of item 5 (grid mean, seed count 10, random seeds, two contrasts) are unchanged: the per-probability amendment was approved for the IC primary analysis, not for EXP-003.
- **A-2 (item 11).** Master seed **20261126**. `R = 30` as drafted.
- **A-3 (item 15).** Holm intervals as in `research/protocol.md` section 11.3 (two contrasts).
- **Implementation note (item 11).** The runner draws `C = 200` seed sets for both seed rules. For the highest-degree rule the 200 draws differ only through the seeded tie-break among equal-degree nodes, so the per-graph mean is the mean over tie-breaks (identical to the `C = 1` value when there is no tie). Disclosed, not a design change.
- **Not amended.** Item 14 keeps the planning depth definition (1 + maximum generation among active neighbours). With synchronous updates this makes `D = T` for every LT cascade (D-007 A4, proof by induction, test-enforced); the proposed alternative definition was not on the approved list, so `D` and `T` are reported as identical by construction rather than as distinct outcomes.
- Exploratory LT values on the old grid (0.10 to 0.26) were seen in the planning probe; disclosed in `research/freeze.json` (C4). The new grid values 0.20, 0.24, 0.28 and 0.30 were never run.
