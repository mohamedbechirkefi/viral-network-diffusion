<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-001 protocol: engine verification and smoke matrix

**Status: DRAFT, awaiting owner freeze. Exploratory by design: no confirmatory claim may come from EXP-001.**
Version 0.1, 2026-11-24. Protocol hash: none (not frozen). Parent protocol: `research/protocol.md` (DRAFT).

1. **Precise question.** Does the diffusion engine implement IC and fractional-threshold diffusion correctly on the three graph families, and what are the runtime and the between-replicate variability needed to size EXP-002?
2. **Mechanism.** Not a scientific mechanism test. Verifies that the code operationalises the models of Kempe, Kleinberg and Tardos (2003) and Watts (2002).
3. **Rationale from verified sources.** IC and LT definitions: Kempe, Kleinberg and Tardos (2003), doi:10.1145/956750.956769 (metadata verified; Theory of Computing journal version page opened). Generators: networkx 3.7 documentation (opened 2026-11-24).
4. **Competing explanations.** A difference between topologies in the smoke run could come from a bug (for example duplicate activation inflating size) rather than structure; verification cases below exist to rule this out.
5. **Falsifiable checks (pass/fail).**
   - `p = 0`: final active set equals seed set exactly; depth 0; duration 0.
   - `p = 1`: final active set equals the union of connected components containing a seed.
   - Disconnected components: no activation crosses components.
   - Duplicate activation: no node is activated twice; `|A_final|` equals the number of distinct activated nodes; each non-seed node has exactly one parent.
   - IC synchronous: depth equals duration.
   - LT with `phi = 0`: every node in a seeded component activates; with `phi > 1`: only seeds are active.
   - Graph invariants: node count `N`; edge count as specified per generator; no self-loops; no multi-edges; mean degree within 1 percent of target; determinism (same seed, identical graph and cascades).
   - Hand-computed examples: path graph, star graph and triangle with known activation sequences.
6. **Estimand.** None (verification). Descriptive outputs: runtime per cascade, peak memory, `sd_diff` of replicate means for the two primary contrasts.
7. **Experimental unit and scope.** Graph replicate; synthetic graphs only.
8. **Variables.** Topology {ER, WS, BA}; `p` in {0, 0.05, 0.20, 1}; random single seed; LT `phi` in {0, 0.18, 1.01}.
9. **Treatment and control.** ER is the control topology, as in EXP-002.
10. **Seed plan.** Master seed 20261124; `R = 5` replicates per topology; `C = 50` cascades per (graph, setting).
11. **Sample-size rationale.** Smallest matrix that exercises every code path and gives a rough `sd_diff`; 5 replicates satisfy the minimum of the master prompt.
12. **Compute budget.** At most 10 minutes wall clock.
13. **Metric formulas and units.** As in `research/protocol.md` section 4.
14. **Uncertainty method.** Descriptive only (mean, sd, range across replicates). No inference.
15. **Exclusion and stopping.** No exclusions. Stop at the first failed verification check, record it, fix it (characterise first, then change), and rerun.
16. **Anticipated failure modes.** Off-by-one in round counting; reuse of RNG streams across arms; BA edge count differing from expectation; WS generator not connected.
17. **Sensitivity tests.** None; this is a verification experiment.
18. **What would contradict the hypothesis.** Any failed check above means the engine is not ready and EXP-002 cannot run.
19. **Reproducibility commands (planned, not yet implemented).** `uv run python -m viral.cli smoke --config experiments/EXP-001/config.json` and `uv run pytest`.
