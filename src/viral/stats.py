# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Statistical helpers: paired cluster bootstrap, Holm adjustment, variance decomposition, sizing.

The independent unit is the graph replicate (research/protocol.md section 5).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np


class StatsError(ValueError):
    """Raised for invalid statistical inputs."""


def paired_differences(treated: Sequence[float], control: Sequence[float]) -> np.ndarray:
    t = np.asarray(treated, dtype=float)
    c = np.asarray(control, dtype=float)
    if t.shape != c.shape or t.ndim != 1 or t.size == 0:
        raise StatsError("paired arrays must be one-dimensional, non-empty and of equal length")
    return t - c


def cluster_bootstrap(diffs: Sequence[float], n_boot: int, rng: np.random.Generator, level: float = 0.95) -> dict:
    """Percentile bootstrap of the mean paired difference, resampling replicates (matched sets).

    Returns mean, interval at `level`, and a two-sided bootstrap p-value
    p = min(1, 2 min(P*(mean <= 0), P*(mean >= 0))).
    """
    d = np.asarray(diffs, dtype=float)
    if d.ndim != 1 or d.size < 2:
        raise StatsError("need at least two replicates")
    if n_boot < 1 or not (0 < level < 1):
        raise StatsError("n_boot >= 1 and 0 < level < 1 required")
    idx = rng.integers(0, d.size, size=(n_boot, d.size))
    means = d[idx].mean(axis=1)
    a = (1 - level) / 2
    lo, hi = np.quantile(means, [a, 1 - a])
    p = min(1.0, 2 * min(np.mean(means <= 0), np.mean(means >= 0)))
    return {"mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "level": level, "p_boot": float(p), "n_replicates": int(d.size), "n_boot": int(n_boot)}


def holm(pvalues: Mapping[str, float], alpha: float = 0.05) -> dict:
    """Holm step-down. Returns per hypothesis: adjusted p, the per-step level alpha/(m-i), and reject flag."""
    if not pvalues:
        raise StatsError("no p-values")
    items = sorted(pvalues.items(), key=lambda kv: (kv[1], kv[0]))
    m = len(items)
    out = {}
    running = 0.0
    still = True
    for i, (k, p) in enumerate(items):
        if not (0 <= p <= 1):
            raise StatsError(f"p-value out of range: {p}")
        adj = min(1.0, max(running, (m - i) * p))
        running = adj
        step_alpha = alpha / (m - i)
        reject = still and p <= step_alpha
        still = reject
        out[k] = {"p": p, "p_holm": adj, "step_alpha": step_alpha, "reject": reject}
    return out


def variance_decomposition(values: Mapping[str, Sequence[Sequence[float]]]) -> dict:
    """Balanced three-level decomposition of the variance of S (law of total variance).

    values[topology][replicate] is the list of per-cascade outcomes. Returns the
    population variance and the shares between topologies, between replicates
    within topology, and within graph (between cascades). Shares sum to 1.
    """
    arrays = {t: np.asarray(v, dtype=float) for t, v in values.items()}
    shapes = {a.shape for a in arrays.values()}
    if len(shapes) != 1 or len(next(iter(shapes))) != 2:
        raise StatsError("design must be balanced: same replicates x cascades per topology")
    x = np.stack(list(arrays.values()))  # topology x replicate x cascade
    total = float(x.var())
    graph_means = x.mean(axis=2)
    topo_means = x.mean(axis=(1, 2))
    within_graph = float(x.var(axis=2).mean())
    between_rep = float(graph_means.var(axis=1).mean())
    between_topo = float(topo_means.var())
    out = {"total_variance": total, "between_topology": between_topo, "between_replicate": between_rep, "within_graph": within_graph}
    if total > 0:
        out.update({"share_topology": between_topo / total, "share_replicate": between_rep / total, "share_within_graph": within_graph / total})
    else:
        out.update({"share_topology": None, "share_replicate": None, "share_within_graph": None})
    return out


def required_replicates(sd_diff: float, half_width: float, z: float = 1.959963984540054) -> int:
    """Smallest R with z sd_diff / sqrt(R) <= half_width (normal approximation, planning only)."""
    if sd_diff < 0 or half_width <= 0 or not math.isfinite(sd_diff):
        raise StatsError("sd_diff >= 0 and half_width > 0 required")
    if sd_diff == 0:
        return 2
    return max(2, math.ceil((z * sd_diff / half_width) ** 2))


def holm_bootstrap_contrasts(diffs: Mapping[str, Sequence[float]], n_boot: int, rng: np.random.Generator, alpha: float = 0.05) -> dict:
    """Confirmatory family: paired cluster bootstrap per contrast, Holm step-down, Holm-step intervals.

    research/protocol.md section 11.3 (owner-approved amendment 2026-11-24, round 2):
    - every contrast is a vector of paired replicate differences over the same R matched sets;
      one (n_boot x R) matrix of resampling indices is drawn once from `rng` and shared by all
      contrasts, so resamples stay paired across contrasts;
    - p_boot = min(1, 2 min(P*(mean <= 0), P*(mean >= 0))); a zero-variance contrast stays in
      the family (its p_boot is 1 if its constant difference is 0, else 0);
    - Holm: sort by (p_boot, contrast name); step i (0-based) is tested at alpha / (m - i);
      testing stops at the first non-rejection j*;
    - interval: percentile bootstrap interval at level 1 - alpha / (m - i) for steps i <= j*,
      and at level 1 - alpha / (m - j*) for steps after j* (every step uses its own level when
      all are rejected). These intervals are reported; decisions use the Holm p-values.
    """
    if not diffs:
        raise StatsError("no contrasts")
    arrays = {k: np.asarray(v, dtype=float) for k, v in diffs.items()}
    sizes = {a.size for a in arrays.values()}
    if len(sizes) != 1 or any(a.ndim != 1 for a in arrays.values()):
        raise StatsError("all contrasts must have the same number of paired replicates")
    r = sizes.pop()
    if r < 2 or n_boot < 1 or not (0 < alpha < 1):
        raise StatsError("need R >= 2, n_boot >= 1 and 0 < alpha < 1")
    idx = rng.integers(0, r, size=(n_boot, r))
    boot = {k: a[idx].mean(axis=1) for k, a in arrays.items()}
    pvals = {k: float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0)))) for k, b in boot.items()}
    h = holm(pvals, alpha)
    order = sorted(pvals, key=lambda k: (pvals[k], k))
    m = len(order)
    stop = next((i for i, k in enumerate(order) if not h[k]["reject"]), None)
    out = {}
    for i, k in enumerate(order):
        step = i if (stop is None or i <= stop) else stop
        level = 1 - alpha / (m - step)
        lo, hi = np.quantile(boot[k], [(1 - level) / 2, 1 - (1 - level) / 2])
        out[k] = {
            "mean": float(arrays[k].mean()), "sd": float(arrays[k].std(ddof=1)), "n_replicates": r, "n_boot": int(n_boot),
            "p_boot": pvals[k], "p_holm": h[k]["p_holm"], "holm_step": i, "step_alpha": h[k]["step_alpha"],
            "reject": h[k]["reject"], "interval_level": float(level), "lo": float(lo), "hi": float(hi),
        }
    return out


def equivalence(lo: float, hi: float, sesoi: float = 0.02) -> bool:
    """Equivalence is claimed only if the reported interval lies entirely inside [-sesoi, +sesoi]."""
    return -sesoi <= lo and hi <= sesoi
