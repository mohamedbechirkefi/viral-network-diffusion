# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""EXPLORATORY metric validation on known cases (M3 pre-run check; not a finding).

Checks every metric of research/protocol.md section 4 on hand-computed graphs, the
confirmatory statistics on known inputs, and the p = 0 / p = 1 cells of an EXP-001
smoke result. Writes a JSON record and exits 1 if any check fails.

Usage:  .venv/bin/python scripts/validate_metrics.py SMOKE_RESULT_DIR OUT_JSON
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from viral import metrics
from viral.engines import ic_reference, ic_vectorised, lt_reference, lt_vectorised
from viral.graphs import from_edges, percolation_threshold
from viral.results import load_result
from viral.stats import holm, holm_bootstrap_contrasts


def main(smoke_dir: str, out_json: str) -> int:
    checks: list[dict] = []

    def check(name, got, expected):
        ok = bool(np.isclose(got, expected)) if isinstance(expected, float) else got == expected
        checks.append({"check": name, "got": got, "expected": expected, "pass": ok})

    path = from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 4)])  # path 0-1-2-3-4
    star = from_edges(5, [(0, 1), (0, 2), (0, 3), (0, 4)])  # hub 0
    rng = np.random.default_rng(0)
    for eng_name, eng in (("reference", ic_reference), ("vectorised", ic_vectorised)):
        c = eng(path, [0], 1.0, rng)
        m = metrics.cascade_metrics(c)
        check(f"IC {eng_name} p=1 path from end: size", m["size"], 5)
        check(f"IC {eng_name} p=1 path from end: depth", m["depth"], 4)
        check(f"IC {eng_name} p=1 path from end: duration", m["duration"], 4)
        check(f"IC {eng_name} p=1 path from end: T50 (ceil(5/2)=3 active at round 2)", m["t50"], 2)
        check(f"IC {eng_name} p=1 path from end: structural virality (Wiener 20 / C(5,2) = 2)", m["structural_virality"], 2.0)
        check(f"IC {eng_name} p=1 path S", metrics.final_fraction(c), 1.0)
        c0 = eng(star, [0], 0.0, rng)
        check(f"IC {eng_name} p=0 star: size", metrics.final_size(c0), 1)
        check(f"IC {eng_name} p=0 star: depth", metrics.depth(c0), 0)
        c1 = eng(star, [1], 1.0, rng)
        check(f"IC {eng_name} p=1 star from leaf: depth", metrics.depth(c1), 2)
        check(f"IC {eng_name} p=1 star from leaf: structural virality (Wiener 16 / 10)", metrics.structural_virality(c1), 1.6)
    for eng_name, eng in (("reference", lt_reference), ("vectorised", lt_vectorised)):
        c = eng(star, [0], 0.5)  # every leaf has 1 of 1 neighbours active
        check(f"LT {eng_name} phi=0.5 star from hub: size", metrics.final_size(c), 5)
        c = eng(star, [1], 0.5)  # hub sees 1 of 4 = 0.25 < 0.5
        check(f"LT {eng_name} phi=0.5 star from leaf: size", metrics.final_size(c), 1)
        c = eng(path, [0], 1.0)
        check(f"LT {eng_name} phi=1 path from end: size (node 1 sees 1 of 2)", metrics.final_size(c), 1)
    check("Gini of equal sizes", metrics.gini([3, 3, 3, 3]), 0.0)
    check("Gini of [0,0,0,1] = 0.75", metrics.gini([0, 0, 0, 1]), 0.75)
    check("large-cascade share [0.05, 0.1, 0.5, 0.09]", metrics.large_cascade_share([0.05, 0.1, 0.5, 0.09]), 0.5)
    cyc = from_edges(6, [(i, (i + 1) % 6) for i in range(6)])
    k4 = from_edges(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    check("p_c of a cycle (<k>=2, <k^2>=4) = 1", percolation_threshold(cyc), 1.0)
    check("p_c of K4 (<k>=3, <k^2>=9) = 0.5", percolation_threshold(k4), 0.5)
    h = holm({"a": 0.01, "b": 0.04, "c": 0.03}, 0.05)
    check("Holm a rejected at 0.05/3", h["a"]["reject"], True)
    check("Holm c not rejected at 0.05/2 (stops)", h["c"]["reject"], False)
    check("Holm adjusted p of a = 0.03", h["a"]["p_holm"], 0.03)
    res = holm_bootstrap_contrasts({"zero": [0.0] * 5, "pos": [0.1] * 5}, 100, np.random.default_rng(1))
    check("bootstrap family: constant 0 difference p = 1", res["zero"]["p_boot"], 1.0)
    check("bootstrap family: constant 0.1 difference p = 0", res["pos"]["p_boot"], 0.0)
    check("bootstrap family: constant difference interval", (res["pos"]["lo"], res["pos"]["hi"]), (0.1, 0.1))

    doc = load_result(smoke_dir)
    n = doc["config"]["n"]
    labels_size = {}
    for c in doc["cells"]:
        if c["model"] == "ic" and c["param"] == 0.0:
            check(f"smoke IC p=0 {c['topology']} r{c['replicate']}: every S = 1/N", all(s == c["seed_count"] for s in c["per_cascade"]["size"]), True)
        if c["model"] == "ic" and c["param"] == 1.0:
            labels_size.setdefault(c["topology"], []).extend(c["per_cascade"]["size"])
    check("smoke verification failures (p=1 sizes checked against seed component inside the runner)", doc["verification"]["cascade_failures"] + doc["verification"]["graph_failures"], 0)
    check("smoke IC p=1 cascades present", sum(len(v) for v in labels_size.values()) > 0, True)
    ok = all(c["pass"] for c in checks)
    rec = {"label": "EXPLORATORY metric validation on known cases (M3 pre-run check); not a finding",
           "smoke_run_id": doc["run_id"], "n_checks": len(checks), "n_failed": sum(not c["pass"] for c in checks), "checks": checks}
    Path(out_json).write_text(json.dumps(rec, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)) + "\n")
    print(f"{len(checks)} checks, {rec['n_failed']} failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
