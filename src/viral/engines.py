# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Diffusion engines: independent cascade (IC) and fractional threshold (LT).

All engines are synchronous. Round 0 is the seed set. In round r >= 1:

IC: every node that became active in round r-1 makes one attempt on each
neighbour that was inactive at the start of round r; each attempt succeeds
independently with probability p. A node activated in round r has as parent
the first successful attempt in the order (source node ascending, neighbour
ascending). One uniform draw is consumed per attempt, in that order, so the
reference and vectorised implementations consume identical random streams.

LT (fractional threshold, Watts 2002 style): an inactive node activates in
round r if it has at least one active neighbour at the start of round r and
the fraction of its neighbours active at the start of round r is >= phi.
Generation: seeds 0; otherwise 1 + max generation among neighbours active at
the start of the activation round (planning definition, EXP-003 item 14).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .graphs import Graph


class EngineError(ValueError):
    """Raised for invalid engine inputs."""


@dataclass(frozen=True)
class Cascade:
    model: str  # "ic" or "lt"
    seeds: np.ndarray  # sorted unique node ids
    activation_round: np.ndarray  # int64 per node, -1 never active
    generation: np.ndarray  # int64 per node, -1 never active
    parent: np.ndarray  # int64 per node; -1 for seeds, inactive nodes and all LT nodes
    n_activation_events: int  # number of times the engine activated a node

    @property
    def size(self) -> int:
        return int(np.count_nonzero(self.activation_round >= 0))


def validate_seeds(graph: Graph, seeds) -> np.ndarray:
    arr = np.asarray(seeds)
    if arr.ndim != 1 or arr.size == 0:
        raise EngineError("seeds must be a non-empty one-dimensional sequence")
    if not np.issubdtype(arr.dtype, np.integer):
        raise EngineError(f"seeds must be integers, got dtype {arr.dtype}")
    arr = arr.astype(np.int64)
    if arr.min() < 0 or arr.max() >= graph.n:
        raise EngineError(f"seed out of range for n={graph.n}")
    if np.unique(arr).size != arr.size:
        raise EngineError("duplicate seed nodes")
    return np.sort(arr)


def _validate_p(p: float) -> float:
    if isinstance(p, bool) or not isinstance(p, (int, float, np.floating)) or not math.isfinite(p) or not (0.0 <= p <= 1.0):
        raise EngineError(f"transmission probability p must be a finite number in [0, 1], got {p!r}")
    return float(p)


def _validate_phi(phi: float) -> float:
    if isinstance(phi, bool) or not isinstance(phi, (int, float, np.floating)) or not math.isfinite(phi) or phi < 0.0:
        raise EngineError(f"threshold phi must be a finite number >= 0, got {phi!r}")
    return float(phi)


def ic_reference(graph: Graph, seeds, p: float, rng: np.random.Generator) -> Cascade:
    """Reference IC implementation: plain loops, written for readability."""
    p = _validate_p(p)
    s = validate_seeds(graph, seeds)
    n = graph.n
    act = [-1] * n
    parent = [-1] * n
    for u in s:
        act[int(u)] = 0
    events = len(s)
    frontier = [int(u) for u in s]
    r = 0
    while frontier:
        r += 1
        active_at_start = [a >= 0 for a in act]
        new = []
        for u in frontier:
            for v in graph.neighbours(u):
                v = int(v)
                if active_at_start[v]:
                    continue
                x = rng.random()
                if x < p and act[v] < 0:
                    act[v] = r
                    parent[v] = u
                    events += 1
                    new.append(v)
        frontier = sorted(new)
    act_arr = np.array(act, dtype=np.int64)
    return Cascade("ic", s, act_arr, act_arr.copy(), np.array(parent, dtype=np.int64), events)


def ic_vectorised(graph: Graph, seeds, p: float, rng: np.random.Generator) -> Cascade:
    """Vectorised IC with frontier expansion; identical output to ic_reference for the same rng state."""
    p = _validate_p(p)
    s = validate_seeds(graph, seeds)
    indptr, indices = graph.indptr, graph.indices
    act = np.full(graph.n, -1, dtype=np.int64)
    parent = np.full(graph.n, -1, dtype=np.int64)
    act[s] = 0
    events = int(s.size)
    frontier = s
    r = 0
    while frontier.size:
        r += 1
        starts = indptr[frontier]
        counts = indptr[frontier + 1] - starts
        total = int(counts.sum())
        if total == 0:
            break
        src = np.repeat(frontier, counts)
        offsets = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
        tgt = indices[np.repeat(starts, counts) + offsets]
        mask = act[tgt] < 0
        if not mask.any():
            break
        src, tgt = src[mask], tgt[mask]
        ok = rng.random(tgt.size) < p
        if not ok.any():
            break
        new, first = np.unique(tgt[ok], return_index=True)
        act[new] = r
        parent[new] = src[ok][first]
        events += int(new.size)
        frontier = new
    return Cascade("ic", s, act, act.copy(), parent, events)


def lt_reference(graph: Graph, seeds, phi: float) -> Cascade:
    """Reference fractional-threshold implementation with plain loops."""
    phi = _validate_phi(phi)
    s = validate_seeds(graph, seeds)
    n = graph.n
    act = [-1] * n
    gen = [-1] * n
    for u in s:
        act[int(u)] = 0
        gen[int(u)] = 0
    events = len(s)
    r = 0
    while True:
        r += 1
        snapshot = list(act)
        gsnap = list(gen)
        new = []
        for v in range(n):
            if snapshot[v] >= 0:
                continue
            nb = graph.neighbours(v)
            if nb.size == 0:
                continue
            active_nb = [int(u) for u in nb if snapshot[int(u)] >= 0]
            if active_nb and len(active_nb) / nb.size >= phi:
                new.append((v, 1 + max(gsnap[u] for u in active_nb)))
        if not new:
            break
        for v, g in new:
            act[v] = r
            gen[v] = g
            events += 1
    return Cascade("lt", s, np.array(act, dtype=np.int64), np.array(gen, dtype=np.int64), np.full(n, -1, dtype=np.int64), events)


def lt_vectorised(graph: Graph, seeds, phi: float) -> Cascade:
    """Vectorised fractional-threshold engine; identical output to lt_reference."""
    phi = _validate_phi(phi)
    s = validate_seeds(graph, seeds)
    n = graph.n
    deg = graph.degrees()
    row = np.repeat(np.arange(n), deg)
    act = np.full(n, -1, dtype=np.int64)
    gen = np.full(n, -1, dtype=np.int64)
    act[s] = 0
    gen[s] = 0
    events = int(s.size)
    r = 0
    while True:
        r += 1
        active = act >= 0
        edge_active = active[graph.indices]
        nb_count = np.bincount(row[edge_active], minlength=n)
        with np.errstate(divide="ignore", invalid="ignore"):
            frac = np.where(deg > 0, nb_count / np.maximum(deg, 1), 0.0)
        cand = (~active) & (nb_count > 0) & (frac >= phi)
        if not cand.any():
            break
        max_gen = np.full(n, -1, dtype=np.int64)
        np.maximum.at(max_gen, row[edge_active], gen[graph.indices[edge_active]])
        idx = np.flatnonzero(cand)
        act[idx] = r
        gen[idx] = max_gen[idx] + 1
        events += int(idx.size)
    return Cascade("lt", s, act, gen, np.full(n, -1, dtype=np.int64), events)


ENGINES = {
    ("ic", "reference"): ic_reference,
    ("ic", "vectorised"): ic_vectorised,
    ("lt", "reference"): lt_reference,
    ("lt", "vectorised"): lt_vectorised,
}
