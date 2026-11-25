# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""EXPLORATORY confounder checks for M4 (2026-11-25). Never confirmatory; never changes a frozen verdict.

Two cheap checks of competing explanations named in the protocols, run on fresh exploratory
master seeds (20261201, 20261202) that differ from every pilot and confirmatory seed.

X1  WS structure versus WS degree sequence (EXP-002 competing explanation "clustering or
    degree homogeneity"). Arms er, ws and ws_dpr (replicate r of ws after 10 M double-edge
    swaps, which keeps the WS degree sequence and destroys its clustering). R = 30, C = 200,
    EXP-002 p grid, one uniformly random seed. Contrasts ws - ws_dpr and ws_dpr - er.

X2  EXP-005 component structure (limitation 16). Arms real and real_dpr at the frozen EXP-005
    p grid, R = 30, C = 200, one random seed. Besides S, records whether the seed lies in the
    giant component and the cascade size divided by the giant-component size. Contrast
    real - real_dpr on (a) S, (b) S given a seed in the giant component, normalised by the
    giant-component size.

X3  EXP-003 competing explanation "degree heterogeneity alone" under the threshold model.
    Arms er, ws, ws_dpr, ba, ba_dpr (10 M swaps), LT, frozen EXP-003 phi grid, 10 uniformly
    random seeds, R = 30, C = 200. Contrasts ws - ws_dpr, ws_dpr - er, ba - ba_dpr, ba_dpr - er.

Intervals are unadjusted 95 percent percentile bootstrap intervals over matched replicates
(B = 10000), labelled exploratory. Writes results/exploratory/M4/m4_exploratory.json and a CSV.

Usage:  .venv/bin/python scripts/exploratory_m4.py OUT_DIR
"""

from __future__ import annotations

import csv
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from viral.config import cascade_rng, graph_rng_seed, load_config
from viral.engines import ic_vectorised, lt_vectorised
from viral.graphs import components, degree_preserving_randomisation, generate, graph_stats
from viral.realdata import load_processed
from viral.seeding import select_seeds

REPO = Path(__file__).resolve().parents[1]
R, C, B = 30, 200, 10_000
SEED_X1, SEED_X2, SEED_X3 = 20261201, 20261202, 20261203
EXP003_PHI = [0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30]
EXP002_P = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]


def dpr_seed(master: int, r: int) -> int:
    return int(np.random.SeedSequence(master, spawn_key=(9, r)).generate_state(1, dtype=np.uint32)[0])


def boot_ci(d: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    idx = rng.integers(0, d.size, size=(B, d.size))
    m = d[idx].mean(axis=1)
    lo, hi = np.quantile(m, [0.025, 0.975])
    return float(lo), float(hi)


def run_arm(graph, p_list, master, r, giant_mask=None):
    """Per p: mean S, and (if giant_mask) mean over giant-seeded cascades of size / giant size."""
    out = {}
    gsize = int(giant_mask.sum()) if giant_mask is not None else None
    for p in p_list:
        rng = cascade_rng(master, r, "ic", p, "random", 1)
        s, sg = [], []
        for _ in range(C):
            seeds = select_seeds(graph, "random", 1, rng)
            c = ic_vectorised(graph, seeds, p, rng)
            s.append(c.size / graph.n)
            if giant_mask is not None and giant_mask[seeds[0]]:
                sg.append(c.size / gsize)
        out[p] = {"S": float(np.mean(s)), "S_giant_norm": float(np.mean(sg)) if sg else float("nan"), "n_giant_seeded": len(sg)}
    return out


def giant_mask_of(graph) -> np.ndarray:
    lab = components(graph)
    return lab == np.bincount(lab).argmax()


def x1() -> dict:
    per = {t: [] for t in ("er", "ws", "ws_dpr")}
    gstats = {t: [] for t in per}
    for r in range(R):
        er = generate("er", 1000, 6, graph_rng_seed(SEED_X1, "er", r))
        ws = generate("ws", 1000, 6, graph_rng_seed(SEED_X1, "ws", r), ws_beta=0.1)
        wsd = degree_preserving_randomisation(ws, 10, dpr_seed(SEED_X1, r))
        for t, g in (("er", er), ("ws", ws), ("ws_dpr", wsd)):
            st = graph_stats(g)
            gstats[t].append({k: st[k] for k in ("second_moment_degree", "p_c", "average_clustering", "giant_component_fraction")})
            per[t].append(run_arm(g, EXP002_P, SEED_X1, r))
    return {"per_replicate": per, "graph_stats": gstats}


def x2() -> dict:
    cfg = load_config(REPO / "research/experiments/EXP-005/config.json")
    real = load_processed(REPO / cfg.raw["real_graph"]["path"], expected_sha256=cfg.raw["real_graph"]["sha256"])
    p_list = list(cfg.raw["models"]["ic"]["p"])
    real_mask = giant_mask_of(real)
    per = {"real": [], "real_dpr": []}
    gstats = {"real": [], "real_dpr": []}
    rs = graph_stats(real)
    for r in range(R):
        dpr = degree_preserving_randomisation(real, 10, dpr_seed(SEED_X2, r))
        dmask = giant_mask_of(dpr)
        st = graph_stats(dpr)
        gstats["real_dpr"].append({k: st[k] for k in ("average_clustering", "giant_component_fraction", "n_components")})
        gstats["real"].append({k: rs[k] for k in ("average_clustering", "giant_component_fraction", "n_components")})
        per["real"].append(run_arm(real, p_list, SEED_X2, r, real_mask))
        per["real_dpr"].append(run_arm(dpr, p_list, SEED_X2, r, dmask))
    return {"per_replicate": per, "graph_stats": gstats, "p": p_list}


def run_lt(graph, phis, master, r):
    out = {}
    for phi in phis:
        rng = cascade_rng(master, r, "lt", phi, "random", 10)
        s = [lt_vectorised(graph, select_seeds(graph, "random", 10, rng), phi).size / graph.n for _ in range(C)]
        out[phi] = {"S": float(np.mean(s))}
    return out


def x3() -> dict:
    per = {t: [] for t in ("er", "ws", "ws_dpr", "ba", "ba_dpr")}
    gstats = {t: [] for t in per}
    for r in range(R):
        er = generate("er", 1000, 6, graph_rng_seed(SEED_X3, "er", r))
        ws = generate("ws", 1000, 6, graph_rng_seed(SEED_X3, "ws", r), ws_beta=0.1)
        ba = generate("ba", 1000, 6, graph_rng_seed(SEED_X3, "ba", r))
        wsd = degree_preserving_randomisation(ws, 10, dpr_seed(SEED_X3, r))
        bad = degree_preserving_randomisation(ba, 10, dpr_seed(SEED_X3, 1000 + r))
        for t, g in (("er", er), ("ws", ws), ("ws_dpr", wsd), ("ba", ba), ("ba_dpr", bad)):
            st = graph_stats(g)
            gstats[t].append({k: st[k] for k in ("second_moment_degree", "average_clustering", "giant_component_fraction")})
            per[t].append(run_lt(g, EXP003_PHI, SEED_X3, r))
    return {"per_replicate": per, "graph_stats": gstats}


def contrasts(per: dict, a: str, b: str, p_list, metric: str, rng) -> list[dict]:
    rows = []
    for p in p_list:
        d = np.array([per[a][r][p][metric] - per[b][r][p][metric] for r in range(R)])
        lo, hi = boot_ci(d, rng)
        rows.append({"contrast": f"{a} - {b}", "metric": metric, "p": p, "mean_diff": float(d.mean()), "lo95": lo, "hi95": hi,
                     "mean_a": float(np.mean([per[a][r][p][metric] for r in range(R)])),
                     "mean_b": float(np.mean([per[b][r][p][metric] for r in range(R)])), "n_replicates": R})
    return rows


def main(out_dir: str) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rev = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
    t0 = time.time()
    r1 = x1()
    t1 = time.time()
    r2 = x2()
    t2 = time.time()
    r3 = x3()
    t3 = time.time()
    rng = np.random.default_rng(np.random.SeedSequence(SEED_X1, spawn_key=(2,)))
    rows = contrasts(r1["per_replicate"], "ws", "ws_dpr", EXP002_P, "S", rng)
    rows += contrasts(r1["per_replicate"], "ws_dpr", "er", EXP002_P, "S", rng)
    rows += contrasts(r1["per_replicate"], "ws", "er", EXP002_P, "S", rng)
    rng2 = np.random.default_rng(np.random.SeedSequence(SEED_X2, spawn_key=(2,)))
    rows += contrasts(r2["per_replicate"], "real", "real_dpr", r2["p"], "S", rng2)
    rows += contrasts(r2["per_replicate"], "real", "real_dpr", r2["p"], "S_giant_norm", rng2)
    for row in rows:
        row["check"] = "X1" if row["contrast"].startswith("ws") else "X2"
    rng3 = np.random.default_rng(np.random.SeedSequence(SEED_X3, spawn_key=(2,)))
    x3rows = []
    for a, b in (("ws", "ws_dpr"), ("ws_dpr", "er"), ("ws", "er"), ("ba", "ba_dpr"), ("ba_dpr", "er"), ("ba", "er")):
        x3rows += contrasts(r3["per_replicate"], a, b, EXP003_PHI, "S", rng3)
    for row in x3rows:
        row["check"] = "X3"
        row["metric"] = "S (LT, 10 random seeds)"
    rows += x3rows

    def gmean(gs):
        return {t: {k: float(np.mean([g[k] for g in v])) for k in v[0]} for t, v in gs.items()}

    doc = {
        "label": "EXPLORATORY (M4, 2026-11-25): not confirmatory, unadjusted intervals, never replaces a frozen verdict",
        "script": "scripts/exploratory_m4.py",
        "code_revision": rev, "tree_dirty_at_start": dirty,
        "master_seeds": {"X1": SEED_X1, "X2": SEED_X2, "X3": SEED_X3},
        "R": R, "C": C, "B": B, "interval": "unadjusted 95 percent percentile bootstrap over matched replicates",
        "runtime_seconds": {"X1": t1 - t0, "X2": t2 - t1, "X3": t3 - t2},
        "platform": {"python": platform.python_version(), "machine": platform.machine(), "system": platform.platform(), "numpy": np.__version__},
        "graph_means": {"X1": gmean(r1["graph_stats"]), "X2": gmean(r2["graph_stats"]), "X3": gmean(r3["graph_stats"])},
        "x2_giant_seeded_counts": {t: int(sum(v[p]["n_giant_seeded"] for v in r2["per_replicate"][t] for p in r2["p"])) for t in ("real", "real_dpr")},
        "contrasts": rows,
    }
    (out / "m4_exploratory.json").write_text(json.dumps(doc, indent=2) + "\n")
    with open(out / "m4_exploratory_contrasts.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({k: doc[k] for k in ("runtime_seconds", "graph_means", "x2_giant_seeded_counts")}, indent=1))
    for row in rows:
        print(f"{row['check']} {row['contrast']:<16} {row['metric'][:13]:<13} p={row['p']:<9} a={row['mean_a']:.4f} b={row['mean_b']:.4f} d={row['mean_diff']:+.4f} [{row['lo95']:+.4f}, {row['hi95']:+.4f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
