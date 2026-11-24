# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Per-cascade and per-cell metrics. Definitions follow research/protocol.md section 4."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from .engines import Cascade


class MetricError(ValueError):
    """Raised when a metric is undefined for its input."""


def final_size(c: Cascade) -> int:
    """|A_final|: number of nodes ever active (nodes)."""
    return c.size


def final_fraction(c: Cascade) -> float:
    """S = |A_final| / N (fraction of nodes, in [0, 1])."""
    return c.size / c.activation_round.size


def depth(c: Cascade) -> int:
    """D: maximum generation (edges from a seed in the activation structure)."""
    return int(c.generation.max())


def duration(c: Cascade) -> int:
    """T: number of synchronous rounds with at least one new activation (rounds).

    Rounds with activations are contiguous from 1 because the process stops at
    the first round without a new activation, so T equals the last activation round.
    """
    return int(c.activation_round.max())


def time_to_half(c: Cascade) -> int:
    """T50: first round at which at least ceil(|A_final| / 2) nodes are active (rounds)."""
    rounds = c.activation_round[c.activation_round >= 0]
    target = math.ceil(rounds.size / 2)
    cum = np.cumsum(np.bincount(rounds))
    return int(np.argmax(cum >= target))


def structural_virality(c: Cascade) -> float | None:
    """Mean pairwise distance in the IC activation tree (Goel et al. 2016).

    Defined only for IC cascades with a single seed and at least two active nodes;
    returns None otherwise. Computed with the Wiener index identity
    W = sum over tree edges of s (n - s), where s is the subtree size below the edge.
    """
    if c.model != "ic" or c.seeds.size != 1:
        return None
    active = np.flatnonzero(c.activation_round >= 0)
    n = active.size
    if n < 2:
        return None
    order = active[np.argsort(-c.activation_round[active], kind="stable")]
    sub = np.zeros(c.activation_round.size, dtype=np.int64)
    sub[active] = 1
    w = 0
    for v in order:
        par = c.parent[v]
        if par >= 0:
            w += int(sub[v]) * (n - int(sub[v]))
            sub[par] += sub[v]
    return 2.0 * w / (n * (n - 1))


def gini(values: Sequence[float]) -> float:
    """G = sum_i sum_j |x_i - x_j| / (2 n^2 xbar) for non-negative values (dimensionless)."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size == 0:
        raise MetricError("gini needs a non-empty one-dimensional sequence")
    if not np.all(np.isfinite(x)) or np.any(x < 0):
        raise MetricError("gini needs finite non-negative values")
    total = x.sum()
    if total == 0:
        raise MetricError("gini is undefined when all values are zero")
    n = x.size
    xs = np.sort(x)
    i = np.arange(1, n + 1)
    return float(2.0 * np.sum(i * xs) / (n * total) - (n + 1) / n)


def large_cascade_share(fractions: Sequence[float], threshold: float = 0.10) -> float:
    """Share of cascades with S >= threshold (planning threshold 0.10)."""
    f = np.asarray(fractions, dtype=float)
    if f.size == 0:
        raise MetricError("no cascades")
    return float(np.mean(f >= threshold))


def cascade_metrics(c: Cascade) -> dict:
    return {
        "size": final_size(c),
        "depth": depth(c),
        "duration": duration(c),
        "t50": time_to_half(c),
        "structural_virality": structural_virality(c),
    }
