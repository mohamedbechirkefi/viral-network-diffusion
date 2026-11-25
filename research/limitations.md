<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Limitations (living document, M0 2026-11-24; updated M4 2026-11-25)

Items 1 to 11 were known by design (M0 to M2); items 12 to 17 were added after the confirmatory runs (M3); items 18 to 24 were added at M4.

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
17. **Experiment reports written after the runs from committed files only.** The 12-part `report.md` files for EXP-001 to EXP-005 could not be written during the M3 run session (the file tool refused); the owner approved writing them on 2026-11-25 (D-013) from the committed results, tables and figures, with no recomputation. Report PDFs were built from these files at M6 (`scripts/build_pdfs.py`).

## Added at interpretation (M4, 2026-11-25)

18. **Item 16 narrowed (exploratory).** The exploratory check X2 conditions on giant-component seeds and normalises by giant-component size. The real - real_dpr deficit at the largest calibrated `p` remains -0.1177 [-0.1259, -0.1100], against -0.1309 for `S` on the same seeds. Component structure explains only a small part of the deficit. The remainder is not attributed to clustering rather than to degree correlations or other structure.
19. **WS deficit not attributable within the design.** No confirmatory analysis tests whether the WS deficit is a degree effect, because S2 tests BA only. The exploratory check X1 finds it is almost entirely structure beyond the degree sequence at `p = 0.30`. Its randomisation removes clustering and ring order together, so it cannot say which matters.
20. **Absolute SESOI.** The SESOI of 0.02 is absolute. At small `p` it classifies large relative differences as negligible: at `p = 0.10`, BA reaches 0.0084 against 0.0025 for ER.
21. **Per-family error control.** Holm controls each of the 8 confirmatory families (89 tests) separately. There is no study-wide correction, and the secondary and exploratory intervals are unadjusted.
22. **Confirmatory results replicate the pilot pattern.** The confirmatory values are close to the pre-freeze pilot values (item 10): for WS - ER at `p = 0.30`, -0.3529 against -0.3564 in the pilot. They are a replication on new seeds with a frozen analysis, not a blind test of a prediction.
23. **S2 and S3 share graphs and cascade streams with EXP-002** (replicates 0 to 29), so their agreement with EXP-002 is partly built in. S4 and the exploratory X1 check use new graphs.
24. **Exploratory checks are post hoc.** X1 to X3 were designed after the confirmatory results were seen. They use R = 30, one randomisation scheme (`10 M` double-edge swaps) and unadjusted intervals, and they never change a frozen verdict.
