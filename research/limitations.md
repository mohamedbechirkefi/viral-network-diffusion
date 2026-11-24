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
