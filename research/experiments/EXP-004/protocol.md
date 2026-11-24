<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-004 protocol: sensitivity analyses for EXP-002

**Status: FROZEN, version 1.0 (owner-approved 2026-11-24), not yet run. S1 to S3 are part of the minimum release; S4 is optional.**
Version 1.0, 2026-11-24. Protocol hash: in `research/freeze.json`. Where the amendment section at the end and items 1 to 8 differ, the amendment section wins. Depends on EXP-002 code and configuration (not on its results: these analyses are fixed now, before any result).

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
8. **Reproducibility commands.** `.venv/bin/viral run --config experiments/EXP-004/S1-config.json` (and `S2-config.json`, `S3-config.json`, `S4-n500-config.json`, `S4-n2000-config.json`).

## Amendments before freeze (owner-approved 2026-11-24, round 2)

- **Consequence of the per-probability primary analysis (EXP-002 A-1).** Each sensitivity analysis compares per parameter value, with Holm within the analysis and the interval method of `research/protocol.md` section 11.3: S1 has 2 contrasts x 5 multipliers = 10 tests; S2 has 1 x 7 = 7 (BA minus `ba_dpr`); S3 has 2 x 7 = 14 (WS-trimmed minus ER-trimmed, BA minus ER-trimmed); S4 has 14 per size. The S1 criterion of item 3 reads per multiplier: the EXP-002 effect is reported as a degree-heterogeneity effect at the probabilities where EXP-002 rejects but all S1 Holm-adjusted intervals at the corresponding multipliers lie inside `[-0.02, 0.02]`. This is the only reading of item 3 consistent with a per-probability primary analysis; it was made at the freeze, before any EXP-004 value was seen.
- **Seeds and graphs.** Master seed 20261125 (the EXP-002 seed), so that replicates 0 to 29 are the EXP-002 graphs with the same index, as item 3 requires; random single seed only (the primary cells). `R = 30`, `C = 200` as drafted. S2 uses `10 M` swaps; S3 trims ER and WS to the BA edge count 2991.
- **Configs.** `experiments/EXP-004/S1-config.json` (`p_scale = pc_multiple`, multipliers {0.5, 1, 1.5, 2, 3}, `p = min(1, c p_c(G))`), `S2-config.json`, `S3-config.json`, `S4-n500-config.json`, `S4-n2000-config.json`; hashes in `research/freeze.json`.
