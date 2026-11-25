<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Limitations (living document, M0 2026-11-24)

No results exist yet. These are the limitations known by design.

1. **Simulation only.** All results are simulations of stylised models on synthetic graphs. They support claims only within the model assumptions. They say nothing about real social platforms, their ranking algorithms, or "guaranteed virality" (section 10 claims boundary).
2. **Content quality is not modelled.** It is held fixed through a common transmission probability or threshold. Real content differs in ways these parameters do not capture.
3. **Synthetic agents are not people.** No causal statement about human behaviour follows.
4. **Three graph families, one parameterisation each.** One WS rewiring probability (`beta = 0.1`) and one BA attachment parameter (`m = 3`). Results do not generalise to all small-world or scale-free graphs.
5. **Finite size.** `N = 1000` (planning value); asymptotic statements are not tested except in the optional S4.
6. **Mean-degree matching is approximate** (BA has 2991 edges versus 3000); S3 addresses it.
7. **One real network only, for a second test.** SNAP and Netzschleuder state no dataset licence; one network with an explicit MIT licence (an anonymized Facebook friendship network of 362 nodes, 2014) is used in EXP-005 only (D-008). Its inference is conditional on that single network, which is one person's friendship circle, not a sample of social networks; nothing generalises to other networks or to any platform.
8. **Literature review is not systematic.** Several sources were verified only at metadata level (see `literature_review.md`).
9. **Toolchain.** No TeX distribution; `manuscript.tex` is generated but not compiled locally (decision D-002).
10. **Pre-freeze exposure.** The protocol was frozen on 2026-11-24 (v1.0), after exploratory pilot values of the primary contrast had been seen at R = 10 (disclosed in `research/freeze.json`, C4). The per-`p` primary analysis and R = 120 were chosen with knowledge of those values.
11. **LT depth equals duration by construction** under the frozen definition (EXP-003 amendment); the two are not distinct outcomes in EXP-003.

## Added after the confirmatory runs (M3, 2026-11-25)

12. **High power, tiny effects.** With 120 matched replicates and common random numbers, differences far below the SESOI (for example 3e-05 in `S`) are rejected by Holm. A rejection is therefore not a practically important effect; every result is reported with whether its interval lies inside `[-0.02, 0.02]`.
13. **Sign changes with `p`.** In EXP-002 both contrasts change sign across the `p` grid, so no single "topology effect" summarises the study; the grid mean (secondary) hides this.
14. **S1 reading unresolved.** The EXP-004 S1 criterion refers to "corresponding multipliers" of each EXP-002 `p`, which the frozen texts do not define. The S1 intervals lie inside the SESOI at multipliers 0.5 and 1 and outside it at 1.5, 2 and 3, so the reading depends on the mapping. The owner decided on 2026-11-25 (D-013) that S1 is reported per multiplier with no overall verdict and no multiplier picked after the data; S1 therefore neither confirms nor refutes the "degree-heterogeneity" reading of the EXP-002 effects as a whole.
15. **Saturated and flat cells in EXP-003.** At `phi` = 0.18 and 0.20 all three topologies saturate (mean `S` above 0.99 with ten random seeds); the mean `S` values at `phi` = 0.26 and 0.28 are identical to four decimals for ER and BA and nearly so for WS (0.5247 and 0.5212), because few nodes' activation requirements change between those thresholds. The EXP-003 grid mean is driven by `phi` 0.22 to 0.30.
16. **EXP-005 is conditional on one network,** whose 14 isolated nodes and 20 components differ from its degree-preserving randomisations (giant component 0.909 versus 0.961 on average); part of the real minus `real_dpr` difference may come from component structure rather than clustering.
17. **Experiment reports written after the runs from committed files only.** The 12-part `report.md` files for EXP-001 to EXP-005 could not be written during the M3 run session (the file tool refused); the owner approved writing them on 2026-11-25 (D-013) from the committed results, tables and figures, with no recomputation. No report PDF has been built yet.
