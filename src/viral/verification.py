# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""EXP-001 verification checks applied to individual cascades and graphs.

Each check returns a list of failure messages; an empty list means pass.
"""

from __future__ import annotations

import numpy as np

from .engines import Cascade
from .graphs import Graph


def seeded_components_mask(graph: Graph, labels: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    return np.isin(labels, np.unique(labels[seeds]))


def check_cascade(graph: Graph, labels: np.ndarray, c: Cascade, param: float) -> list[str]:
    fails: list[str] = []
    active = c.activation_round >= 0
    n_active = int(active.sum())
    if c.n_activation_events != n_active:
        fails.append(f"duplicate activation: {c.n_activation_events} events for {n_active} active nodes")
    if not np.all(c.activation_round[c.seeds] == 0):
        fails.append("a seed is not active at round 0")
    if np.any((c.activation_round == 0) & ~np.isin(np.arange(graph.n), c.seeds)):
        fails.append("a non-seed node is active at round 0")
    reach = seeded_components_mask(graph, labels, c.seeds)
    if np.any(active & ~reach):
        fails.append("activation crossed into an unseeded component")
    if c.model == "ic":
        nonseed = np.flatnonzero(active & (c.activation_round > 0))
        par = c.parent[nonseed]
        if np.any(par < 0):
            fails.append("a non-seed active node has no parent")
        else:
            if not np.all(c.activation_round[par] == c.activation_round[nonseed] - 1):
                fails.append("parent not activated in the previous round")
            for v, u in zip(nonseed, par):
                if u not in graph.neighbours(int(v)):
                    fails.append(f"parent {u} of {v} is not a neighbour")
                    break
        if np.any(c.parent[c.seeds] != -1):
            fails.append("a seed has a parent")
        if int(c.generation.max()) != int(c.activation_round.max()):
            fails.append("IC depth differs from duration")
        if param == 0.0 and n_active != c.seeds.size:
            fails.append("p = 0 but non-seed nodes activated")
        if param == 1.0 and not np.array_equal(active, reach):
            fails.append("p = 1 but active set differs from seeded components")
    else:
        if param == 0.0 and not np.array_equal(active, reach):
            fails.append("phi = 0 but active set differs from seeded components")
        if param > 1.0 and n_active != c.seeds.size:
            fails.append("phi > 1 but non-seed nodes activated")
    return fails


def check_graph(stats: dict, target_mean_degree: float, tolerance: float = 0.01) -> list[str]:
    fails = []
    if stats["self_loops"]:
        fails.append("self-loops present")
    if stats["multi_edges"]:
        fails.append("multi-edges present")
    if not stats["symmetric"]:
        fails.append("adjacency not symmetric")
    if abs(stats["mean_degree"] - target_mean_degree) > tolerance * target_mean_degree:
        fails.append(f"mean degree {stats['mean_degree']:.4f} outside {tolerance:.0%} of target {target_mean_degree}")
    return fails
