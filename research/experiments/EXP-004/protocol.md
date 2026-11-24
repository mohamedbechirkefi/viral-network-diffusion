<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-004 protocol: sensitivity analyses for EXP-002

**Status: DRAFT, awaiting owner freeze. S1 to S3 are part of the minimum release; S4 is optional.**
Version 0.1, 2026-11-24. Protocol hash: none (not frozen). Depends on EXP-002 code and configuration (not on its results: these analyses are fixed now, before any result).

1. **Precise question.** Is any topology difference found in EXP-002 explained by the degree moments alone, by residual edge-count mismatch, or by finite size?
2. **Mechanism.** Under the locally tree-like approximation, the IC threshold is `p_c = <k> / (<k^2> - <k>)`; BA has a larger `<k^2>` than ER at the same `<k>` (Newman, Strogatz and Watts 2001; Pastor-Satorras et al. 2015).
3. **Analyses.**
   - **S1 threshold rescaling.** For each graph compute `p_c(G)`; run IC at `p = c p_c(G)` with `c` in {0.5, 1, 1.5, 2, 3}; contrast as EXP-002. If both Holm-adjusted intervals fall inside `[-0.02, 0.02]`, the EXP-002 effect is reported as a degree-heterogeneity effect.
   - **S2 degree-preserving null.** For each BA replicate, a randomised copy with `10 M` double-edge swaps (networkx `double_edge_swap`, seeded); contrast BA minus randomised BA on the EXP-002 `p` grid.
   - **S3 exact matching.** Trim ER and WS graphs to the BA edge count by removing uniformly chosen edges (seeded); repeat the primary contrast.
   - **S4 size (optional).** `N` in {500, 2000}, `<k> = 6`; primary contrast only.
4. **Experimental unit.** Graph replicate; `R = 30`, `C = 200`.
5. **Uncertainty.** As EXP-002; Holm within each sensitivity analysis.
6. **What would invalidate the main interpretation.** S1 or S2 showing no difference while EXP-002 shows one: then the "topology" effect is a degree-sequence effect and must be reported as such.
7. **Compute budget.** At most 3 hours in total.
8. **Reproducibility commands (planned).** `uv run python -m viral.cli run --config research/experiments/EXP-004/config.json`.
