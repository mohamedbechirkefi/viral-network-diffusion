<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Limitations (living document, M0 2026-11-24)

No results exist yet. These are the limitations known by design.

1. **Simulation only.** All results are simulations of stylised models on synthetic graphs. They support claims only within the model assumptions. They say nothing about real social platforms, their ranking algorithms, or "guaranteed virality" (section 10 claims boundary).
2. **Content quality is not modelled.** It is held fixed through a common transmission probability or threshold. Real content differs in ways these parameters do not capture.
3. **Synthetic agents are not people.** No causal statement about human behaviour follows.
4. **Three graph families, one parameterisation each.** One WS rewiring probability (`beta = 0.1`) and one BA attachment parameter (`m = 3`). Results do not generalise to all small-world or scale-free graphs.
5. **Finite size.** `N = 1000` (planning value); asymptotic statements are not tested except in the optional S4.
6. **Mean-degree matching is approximate** (BA has 2991 edges versus 3000); S3 addresses it.
7. **No real network data.** Candidate sources had unclear licences on the pages opened (decision D-003).
8. **Literature review is not systematic.** Several sources were verified only at metadata level (see `literature_review.md`).
9. **Toolchain.** No TeX distribution; `manuscript.tex` is generated but not compiled locally (decision D-002).
10. **Protocol not frozen.** Everything in `research/protocol.md` is a draft until the owner freezes it.
