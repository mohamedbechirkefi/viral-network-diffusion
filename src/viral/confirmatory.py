# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Frozen confirmatory analyses (research/protocol.md sections 5, 11.1 to 11.5; EXP protocols).

Written in session M3 on 2026-11-25 before any confirmatory output existed, as a direct
transcription of the frozen plans. Nothing here may change once confirmatory output exists.

Primary families (Holm, interval method of protocol section 11.3, viral.stats.holm_bootstrap_contrasts,
bootstrap stream viral.config.bootstrap_rng(master_seed)):

- EXP-002: ws - er and ba - er at each p, IC, random rule, 1 seed: 14 tests.
- EXP-003: ws - er and ba - er on the grid mean over phi, LT, random rule, 10 seeds: 2 tests.
- EXP-004 S1: ws - er and ba - er at each multiplier c: 10 tests.
- EXP-004 S2: ba - ba_dpr at each p: 7 tests.
- EXP-004 S3: ws_trim - er_trim and ba - er_trim at each p: 14 tests.
- EXP-004 S4 (optional): ws - er and ba - er at each p, per size: 14 tests.
- EXP-005: real - real_er and real - real_dpr at each calibrated p: 14 tests.

Secondary estimates (labelled secondary, unadjusted 95 percent percentile intervals) use a
separate stream SeedSequence(master_seed, spawn_key=(2, 1)) so that they never consume the
primary resampling matrix.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .config import STREAM_BOOTSTRAP, bootstrap_rng
from .stats import cluster_bootstrap, equivalence, holm_bootstrap_contrasts

SESOI = 0.02
N_BOOT = 10000
ALPHA = 0.05

# (experiment id, config label key) -> plan. The key is the config file name below experiments/<EXP>/.
PLANS: dict[str, dict] = {
    "EXP-002/config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ws", "er"), ("ba", "er")]},
    "EXP-003/config.json": {"kind": "grid_mean", "model": "lt", "rule": "random", "count": 10, "pairs": [("ws", "er"), ("ba", "er")]},
    "EXP-004/S1-config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ws", "er"), ("ba", "er")]},
    "EXP-004/S2-config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ba", "ba_dpr")]},
    "EXP-004/S3-config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ws_trim", "er_trim"), ("ba", "er_trim")]},
    "EXP-004/S4-n500-config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ws", "er"), ("ba", "er")], "optional": True},
    "EXP-004/S4-n2000-config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("ws", "er"), ("ba", "er")], "optional": True},
    "EXP-005/config.json": {"kind": "per_param", "model": "ic", "rule": "random", "count": 1, "pairs": [("real", "real_er"), ("real", "real_dpr")]},
}

SECONDARY_METRICS = ("mean_S", "mean_depth", "mean_t50", "gini_size", "large_cascade_share")


def secondary_rng(master: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(master, spawn_key=(STREAM_BOOTSTRAP, 1))))


def _index(doc: dict, model: str, rule: str, count: int, metric: str = "mean_S") -> tuple[dict, list[float], list[int]]:
    cells = [c for c in doc["cells"] if c["model"] == model and c["seed_rule"] == rule and c["seed_count"] == count]
    s = {(c["topology"], c["param"], c["replicate"]): c["summary"][metric] for c in cells}
    params = sorted({c["param"] for c in cells})
    reps = sorted({c["replicate"] for c in cells})
    return s, params, reps


def contrast_name(t: str, c: str, p: float | None = None) -> str:
    return f"{t} - {c}" if p is None else f"{t} - {c} @ {p:g}"


def _complete(s: dict, topos: set[str], params: list[float], reps: list[int]) -> list[int]:
    return [r for r in reps if all((t, p, r) in s for t in topos for p in params)]


def per_param_family(doc: dict, pairs: list[tuple[str, str]], model: str = "ic", rule: str = "random", count: int = 1,
                     n_boot: int = N_BOOT, alpha: float = ALPHA, sesoi: float = SESOI) -> list[dict]:
    """One Holm family over every (pair, parameter): treatment minus control of per-graph mean S."""
    s, params, reps = _index(doc, model, rule, count)
    topos = {x for pr in pairs for x in pr}
    reps = _complete(s, topos, params, reps)
    diffs = {contrast_name(t, c, p): [s[(t, p, r)] - s[(c, p, r)] for r in reps] for t, c in pairs for p in params}
    res = holm_bootstrap_contrasts(diffs, n_boot, bootstrap_rng(doc["config"]["master_seed"]), alpha)
    rows = []
    for t, c in pairs:
        for p in params:
            k = contrast_name(t, c, p)
            rows.append({"contrast": contrast_name(t, c), "param": p, **res[k], "equivalent_within_sesoi": equivalence(res[k]["lo"], res[k]["hi"], sesoi)})
    return rows


def grid_mean_family(doc: dict, pairs: list[tuple[str, str]], model: str, rule: str, count: int,
                     n_boot: int = N_BOOT, alpha: float = ALPHA, sesoi: float = SESOI) -> list[dict]:
    """One Holm family over the pairs: treatment minus control of Sbar_r, the mean over the parameter grid."""
    s, params, reps = _index(doc, model, rule, count)
    topos = {x for pr in pairs for x in pr}
    reps = _complete(s, topos, params, reps)
    sbar = {(t, r): float(np.mean([s[(t, p, r)] for p in params])) for t in topos for r in reps}
    diffs = {contrast_name(t, c): [sbar[(t, r)] - sbar[(c, r)] for r in reps] for t, c in pairs}
    res = holm_bootstrap_contrasts(diffs, n_boot, bootstrap_rng(doc["config"]["master_seed"]), alpha)
    return [{"contrast": contrast_name(t, c), "param": "grid mean", "grid": params, **res[contrast_name(t, c)],
             "equivalent_within_sesoi": equivalence(res[contrast_name(t, c)]["lo"], res[contrast_name(t, c)]["hi"], sesoi)} for t, c in pairs]


def secondary_contrasts(doc: dict, pairs: list[tuple[str, str]], n_boot: int = N_BOOT) -> list[dict]:
    """SECONDARY, unadjusted 95 percent percentile intervals: every pair, setting and secondary metric, plus grid means of S."""
    rng = secondary_rng(doc["config"]["master_seed"])
    settings = sorted({(c["model"], c["seed_rule"], c["seed_count"]) for c in doc["cells"]})
    rows = []
    for model, rule, count in settings:
        for metric in SECONDARY_METRICS:
            s, params, reps = _index(doc, model, rule, count, metric)
            topos = {x for pr in pairs for x in pr}
            reps_ok = _complete(s, topos, params, reps)
            if len(reps_ok) < 2:
                continue
            for t, c in pairs:
                for p in params:
                    d = [s[(t, p, r)] - s[(c, p, r)] for r in reps_ok]
                    b = cluster_bootstrap(d, n_boot, rng)
                    rows.append({"label": "secondary, unadjusted", "model": model, "seed_rule": rule, "seed_count": count, "metric": metric,
                                 "contrast": contrast_name(t, c), "param": p, "mean": b["mean"], "lo": b["lo"], "hi": b["hi"],
                                 "level": b["level"], "p_boot": b["p_boot"], "n_replicates": b["n_replicates"]})
                if metric == "mean_S":
                    d = [float(np.mean([s[(t, p, r)] for p in params]) - np.mean([s[(c, p, r)] for p in params])) for r in reps_ok]
                    b = cluster_bootstrap(d, n_boot, rng)
                    rows.append({"label": "secondary, unadjusted", "model": model, "seed_rule": rule, "seed_count": count, "metric": "grid_mean_S",
                                 "contrast": contrast_name(t, c), "param": "grid mean", "mean": b["mean"], "lo": b["lo"], "hi": b["hi"],
                                 "level": b["level"], "p_boot": b["p_boot"], "n_replicates": b["n_replicates"]})
    return rows


def topology_means(doc: dict, n_boot: int = N_BOOT) -> list[dict]:
    """Descriptive: mean over replicates of per-graph mean S per cell, with an unadjusted 95 percent percentile bootstrap interval over replicates."""
    rng = secondary_rng(doc["config"]["master_seed"] + 1)
    by = defaultdict(list)
    for c in doc["cells"]:
        by[(c["model"], c["param"], c["seed_rule"], c["seed_count"], c["topology"])].append(c["summary"]["mean_S"])
    rows = []
    for k in sorted(by):
        v = np.asarray(by[k])
        if v.size >= 2:
            idx = rng.integers(0, v.size, size=(n_boot, v.size))
            lo, hi = np.quantile(v[idx].mean(axis=1), [0.025, 0.975])
        else:
            lo = hi = float(v[0])
        rows.append({"model": k[0], "param": k[1], "seed_rule": k[2], "seed_count": k[3], "topology": k[4], "replicates": int(v.size),
                     "mean_S": float(v.mean()), "lo95": float(lo), "hi95": float(hi), "sd_between_replicates": float(v.std(ddof=1)) if v.size > 1 else 0.0})
    return rows


def run_plan(doc: dict, plan: dict) -> dict:
    if plan["kind"] == "per_param":
        primary = per_param_family(doc, plan["pairs"], plan["model"], plan["rule"], plan["count"])
    elif plan["kind"] == "grid_mean":
        primary = grid_mean_family(doc, plan["pairs"], plan["model"], plan["rule"], plan["count"])
    else:
        raise ValueError(f"unknown plan kind {plan['kind']!r}")
    return {"plan": plan, "primary": primary, "secondary": secondary_contrasts(doc, plan["pairs"]), "topology_means": topology_means(doc)}


def s1_reading(exp002_primary: list[dict], s1_primary: list[dict], sesoi: float = SESOI) -> dict:
    """EXP-004 S1 criterion (per-multiplier reading, D-009/D-011), evaluated only where it does not depend on a p-to-c mapping.

    The frozen text says the EXP-002 effect at p is a degree-heterogeneity effect if EXP-002 rejects at p and all
    S1 Holm-adjusted intervals at the corresponding multipliers lie inside [-sesoi, sesoi]. The frozen texts do not
    define which multipliers correspond to which p. If all S1 intervals lie inside, or none does, the reading is the
    same under every mapping; otherwise it is reported as unresolved and left to the owner.
    """
    inside = {f"{r['contrast']} @ c={r['param']:g}": equivalence(r["lo"], r["hi"], sesoi) for r in s1_primary}
    rejected = [f"{r['contrast']} @ p={r['param']:g}" for r in exp002_primary if r["reject"]]
    if all(inside.values()):
        verdict = "mapping-invariant: every S1 interval lies inside the SESOI; every rejected EXP-002 effect reads as a degree-heterogeneity effect"
    elif not any(inside.values()):
        verdict = "mapping-invariant: no S1 interval lies inside the SESOI; no rejected EXP-002 effect is reclassified as a degree-heterogeneity effect"
    else:
        verdict = "unresolved: some S1 intervals lie inside the SESOI and some do not; the reading depends on the p-to-c mapping, which the frozen texts do not define (owner decision)"
    return {"s1_inside_sesoi": inside, "exp002_rejected": rejected, "verdict": verdict}
