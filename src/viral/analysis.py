# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Descriptive analysis of a validated result document (tables used by the report generator)."""

from __future__ import annotations

from collections import defaultdict
from statistics import NormalDist

import numpy as np

from .config import ExperimentConfig
from .stats import paired_differences, required_replicates, variance_decomposition

Z95 = NormalDist().inv_cdf(0.975)
Z95_HOLM_FIRST = NormalDist().inv_cdf(1 - 0.05 / 4)  # first Holm step over two contrasts


def setting_key(cell: dict) -> tuple:
    return (cell["model"], cell["param"], cell["seed_rule"], cell["seed_count"])


def graph_table(doc: dict) -> list[dict]:
    by = defaultdict(list)
    for g in doc["graphs"]:
        by[g["topology"]].append(g["stats"])
    rows = []
    for t, ss in by.items():
        def avg(k):
            return float(np.mean([s[k] for s in ss]))
        rows.append({
            "topology": t,
            "graphs": len(ss),
            "mean_m": avg("m"),
            "mean_degree": avg("mean_degree"),
            "second_moment": avg("second_moment_degree"),
            "max_degree_mean": avg("max_degree"),
            "p_c": avg("p_c"),
            "giant_fraction": avg("giant_component_fraction"),
            "clustering": avg("average_clustering") if "average_clustering" in ss[0] else None,
        })
    return rows


def cell_table(doc: dict) -> list[dict]:
    """Per (setting, topology): mean over replicates of per-graph means, and their spread across replicates."""
    by = defaultdict(list)
    for c in doc["cells"]:
        by[(*setting_key(c), c["topology"])].append(c)
    rows = []
    for key, cs in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3], kv[0][4])):
        means = np.array([c["summary"]["mean_S"] for c in cs])
        n_casc = sum(c["n_cascades"] for c in cs)
        rows.append({
            "model": key[0], "param": key[1], "seed_rule": key[2], "seed_count": key[3], "topology": key[4],
            "replicates": len(cs),
            "mean_S": float(means.mean()),
            "sd_S_between_replicates": float(means.std(ddof=1)) if len(cs) > 1 else None,
            "min_rep_S": float(means.min()), "max_rep_S": float(means.max()),
            "mean_depth": float(np.mean([c["summary"]["mean_depth"] for c in cs])),
            "mean_t50": float(np.mean([c["summary"]["mean_t50"] for c in cs])),
            "mean_gini": float(np.mean([c["summary"]["gini_size"] for c in cs])),
            "large_share": float(np.mean([c["summary"]["large_cascade_share"] for c in cs])),
            "seconds_per_cascade": float(sum(c["runtime_seconds"] for c in cs) / n_casc),
        })
    return rows


def contrasts(doc: dict, model: str = "ic", rule: str = "random", count: int = 1, params: list[float] | None = None, control: str = "er", half_width: float = 0.01) -> list[dict]:
    """Exploratory replicate-level contrasts of Sbar (mean S over the parameter grid) against the control topology.

    Descriptive only: reports the mean paired difference, sd_diff and the replicate count
    that would give the requested interval half-width. No inference is drawn.
    """
    cells = [c for c in doc["cells"] if c["model"] == model and c["seed_rule"] == rule and c["seed_count"] == count]
    grid = sorted({c["param"] for c in cells}) if params is None else sorted(params)
    sbar: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for c in cells:
        if c["param"] in grid:
            sbar[c["topology"]][c["replicate"]].append(c["summary"]["mean_S"])
    if control not in sbar:
        return []
    out = []
    reps = sorted(r for r, v in sbar[control].items() if len(v) == len(grid))
    for t in sorted(sbar):
        if t == control:
            continue
        common = [r for r in reps if len(sbar[t].get(r, [])) == len(grid)]
        if len(common) < 2:
            continue
        d = paired_differences([np.mean(sbar[t][r]) for r in common], [np.mean(sbar[control][r]) for r in common])
        sd = float(d.std(ddof=1))
        out.append({
            "contrast": f"{t} - {control}", "grid": grid, "replicates": len(common),
            "mean_diff": float(d.mean()), "sd_diff": sd, "min_diff": float(d.min()), "max_diff": float(d.max()),
            "R_needed_z95": required_replicates(sd, half_width, Z95),
            "R_needed_holm_first_step": required_replicates(sd, half_width, Z95_HOLM_FIRST),
            "half_width_at_R30_z95": float(Z95 * sd / np.sqrt(30)),
        })
    return out


def contrasts_by_param(doc: dict, model: str = "ic", rule: str = "random", count: int = 1) -> list[dict]:
    """The same descriptive contrast at each parameter value separately (shows crossings that a grid mean hides)."""
    params = sorted({c["param"] for c in doc["cells"] if c["model"] == model and c["seed_rule"] == rule and c["seed_count"] == count})
    rows = []
    for p in params:
        for row in contrasts(doc, model, rule, count, params=[p]):
            rows.append({"param": p, **{k: v for k, v in row.items() if k != "grid"}})
    return rows


def variance_table(doc: dict) -> list[dict]:
    by = defaultdict(lambda: defaultdict(dict))
    n = doc["config"]["n"]
    for c in doc["cells"]:
        by[setting_key(c)][c["topology"]][c["replicate"]] = [s / n for s in c["per_cascade"]["size"]]
    rows = []
    for key, topo in sorted(by.items()):
        try:
            vd = variance_decomposition({t: [reps[r] for r in sorted(reps)] for t, reps in topo.items()})
        except ValueError:
            continue
        rows.append({"model": key[0], "param": key[1], "seed_rule": key[2], "seed_count": key[3], **vd})
    return rows


def degenerate_cells(doc: dict) -> list[dict]:
    """Settings where outcomes carry no information: no spread at all, or every cascade stays at its seeds or saturates."""
    by = defaultdict(list)
    for c in doc["cells"]:
        by[(*setting_key(c), c["topology"])].append(c)
    out = []
    n = doc["config"]["n"]
    for key, cs in sorted(by.items()):
        sizes = np.concatenate([c["per_cascade"]["size"] for c in cs])
        reasons = []
        if np.all(sizes == key[3]):
            reasons.append("every cascade stayed at its seed set")
        if np.unique(sizes).size == 1:
            reasons.append("zero variance across all cascades")
        if np.mean(sizes >= 0.99 * n) == 1.0:
            reasons.append("every cascade reached >= 99 percent of nodes")
        elif np.mean(sizes == key[3]) >= 0.95:
            reasons.append(f"{np.mean(sizes == key[3]):.1%} of cascades stayed at the seed set")
        if reasons:
            out.append({"model": key[0], "param": key[1], "seed_rule": key[2], "seed_count": key[3], "topology": key[4], "reasons": reasons})
    return out


def project_runtime(doc: dict, target: ExperimentConfig) -> dict:
    """Project wall-clock time of a target matrix from measured seconds per cascade in `doc`.

    Each target cell uses the measured mean seconds per cascade of the same
    (model, parameter, rule, count, topology) if present, otherwise the nearest
    measured parameter of the same model, rule, count and topology (flagged).
    """
    per = defaultdict(lambda: [0.0, 0])
    for c in doc["cells"]:
        k = (*setting_key(c), c["topology"])
        per[k][0] += c["runtime_seconds"]
        per[k][1] += c["n_cascades"]
    rate = {k: v[0] / v[1] for k, v in per.items()}
    gen = defaultdict(list)
    for g in doc["graphs"]:
        gen[g["topology"]].append(g.get("generation_seconds", 0.0))
    total = 0.0
    exact = approx = missing = 0
    for t in target.topologies:
        g_s = float(np.mean(gen[t])) if gen[t] else 0.0
        total += g_s * target.replicates
        for model, param in target.settings():
            for rule in target.seed_rules:
                for count in target.seed_counts:
                    k = (model, param, rule, count, t)
                    if k in rate:
                        s = rate[k]
                        exact += 1
                    else:
                        cands = [kk for kk in rate if kk[0] == model and kk[2] == rule and kk[3] == count and kk[4] == t]
                        if not cands:
                            missing += 1
                            continue
                        s = rate[min(cands, key=lambda kk: abs(kk[1] - param))]
                        approx += 1
                    total += s * target.cascades * target.replicates
    return {"projected_seconds": total, "cells_exact": exact, "cells_nearest_param": approx, "cells_missing": missing,
            "note": "engine time plus graph generation only; graph statistics, verification and serialisation excluded"}
