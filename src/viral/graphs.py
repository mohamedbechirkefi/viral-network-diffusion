# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Graph representation, seeded generators and graph invariants.

A graph is undirected, simple (no self-loops, no multi-edges) and stored in
compressed sparse row (CSR) form with each node's neighbours sorted ascending.
Nodes are the integers 0..n-1. Units: degree in edges per node.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterable

import networkx as nx
import numpy as np

FAMILIES = ("er", "ws", "ba")


class GraphError(ValueError):
    """Raised for an invalid graph or invalid generator parameters."""


@dataclass(frozen=True)
class Graph:
    """Immutable undirected simple graph in CSR form."""

    n: int
    indptr: np.ndarray  # int64, shape (n + 1,)
    indices: np.ndarray  # int64, shape (2 m,), sorted within each row
    family: str = "custom"
    params: dict = field(default_factory=dict)

    @property
    def m(self) -> int:
        return int(self.indices.size // 2)

    def degrees(self) -> np.ndarray:
        return np.diff(self.indptr)

    def neighbours(self, u: int) -> np.ndarray:
        return self.indices[self.indptr[u] : self.indptr[u + 1]]

    def edge_list(self) -> list[tuple[int, int]]:
        out = []
        for u in range(self.n):
            for v in self.neighbours(u):
                if u < int(v):
                    out.append((u, int(v)))
        return out


def from_edges(n: int, edges: Iterable[tuple[int, int]], family: str = "custom", params: dict | None = None) -> Graph:
    """Build a Graph from an edge list. Rejects self-loops, duplicates and out-of-range nodes."""
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n < 1:
        raise GraphError(f"n must be a positive integer, got {n!r}")
    n = int(n)
    seen: set[tuple[int, int]] = set()
    for e in edges:
        if len(e) != 2:
            raise GraphError(f"edge must have two endpoints, got {e!r}")
        u, v = int(e[0]), int(e[1])
        if not (0 <= u < n and 0 <= v < n):
            raise GraphError(f"edge ({u}, {v}) out of range for n={n}")
        if u == v:
            raise GraphError(f"self-loop at node {u}")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise GraphError(f"duplicate edge {key}")
        seen.add(key)
    if seen:
        arr = np.array(sorted(seen), dtype=np.int64)
        src = np.concatenate([arr[:, 0], arr[:, 1]])
        dst = np.concatenate([arr[:, 1], arr[:, 0]])
    else:
        src = np.empty(0, dtype=np.int64)
        dst = np.empty(0, dtype=np.int64)
    order = np.lexsort((dst, src))
    src, dst = src[order], dst[order]
    counts = np.bincount(src, minlength=n)
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(counts, out=indptr[1:])
    return Graph(n=n, indptr=indptr, indices=dst.astype(np.int64), family=family, params=dict(params or {}))


def from_networkx(g: nx.Graph, family: str = "custom", params: dict | None = None) -> Graph:
    n = g.number_of_nodes()
    if set(g.nodes()) != set(range(n)):
        raise GraphError("networkx graph nodes must be exactly 0..n-1")
    if g.is_directed() or g.is_multigraph():
        raise GraphError("graph must be undirected and simple")
    return from_edges(n, g.edges(), family=family, params=params)


def to_networkx(graph: Graph) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(graph.n))
    g.add_edges_from(graph.edge_list())
    return g


def generate(family: str, n: int, mean_degree: float, seed: int, ws_beta: float = 0.1) -> Graph:
    """Generate a graph of the given family with target mean degree.

    er: networkx.gnm_random_graph(n, M) with M = n * mean_degree / 2 (must be an integer).
    ws: networkx.watts_strogatz_graph(n, k, beta) with k = mean_degree (even integer).
    ba: networkx.barabasi_albert_graph(n, m) with m = mean_degree / 2 (integer); m (n - m) edges.
    `seed` is a non-negative integer passed to networkx.
    """
    if family not in FAMILIES:
        raise GraphError(f"unknown family {family!r}; expected one of {FAMILIES}")
    if not isinstance(n, int) or isinstance(n, bool) or n < 3:
        raise GraphError(f"n must be an integer >= 3, got {n!r}")
    if not np.isfinite(mean_degree) or mean_degree <= 0 or mean_degree >= n - 1:
        raise GraphError(f"mean_degree must be in (0, n-1), got {mean_degree!r}")
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise GraphError(f"seed must be a non-negative integer, got {seed!r}")
    seed = int(seed)
    if family == "er":
        m2 = n * mean_degree
        if abs(m2 - round(m2)) > 1e-9 or round(m2) % 2:
            raise GraphError("er: n * mean_degree must be an even integer")
        m_edges = int(round(m2)) // 2
        g = nx.gnm_random_graph(n, m_edges, seed=seed)
        params = {"n": n, "m": m_edges}
    elif family == "ws":
        if abs(mean_degree - round(mean_degree)) > 1e-9 or int(round(mean_degree)) % 2:
            raise GraphError("ws: mean_degree must be an even integer")
        if not (0.0 <= ws_beta <= 1.0):
            raise GraphError(f"ws: beta must be in [0, 1], got {ws_beta!r}")
        k = int(round(mean_degree))
        g = nx.watts_strogatz_graph(n, k, ws_beta, seed=seed)
        params = {"n": n, "k": k, "beta": ws_beta}
    else:
        half = mean_degree / 2
        if abs(half - round(half)) > 1e-9:
            raise GraphError("ba: mean_degree / 2 must be an integer")
        m = int(round(half))
        g = nx.barabasi_albert_graph(n, m, seed=seed)
        params = {"n": n, "m": m}
    params["networkx_seed"] = seed
    return from_networkx(g, family=family, params=params)


def components(graph: Graph) -> np.ndarray:
    """Component label per node (labels 0..c-1 in order of smallest node)."""
    label = np.full(graph.n, -1, dtype=np.int64)
    c = 0
    for s in range(graph.n):
        if label[s] >= 0:
            continue
        label[s] = c
        q = deque([s])
        while q:
            u = q.popleft()
            for v in graph.neighbours(u):
                if label[v] < 0:
                    label[v] = c
                    q.append(int(v))
        c += 1
    return label


def percolation_threshold(graph: Graph) -> float:
    """Bond-percolation threshold estimate p_c = <k> / (<k^2> - <k>) (locally tree-like approximation).

    Returns inf when <k^2> - <k> <= 0 (no node of degree >= 2).
    """
    k = graph.degrees().astype(float)
    k1 = k.mean()
    k2 = (k**2).mean()
    denom = k2 - k1
    return float(k1 / denom) if denom > 0 else float("inf")


def graph_stats(graph: Graph) -> dict:
    """Invariants and descriptive statistics recorded for every generated graph."""
    deg = graph.degrees()
    labels = components(graph)
    sizes = np.bincount(labels)
    src = np.repeat(np.arange(graph.n), deg)
    self_loops = int(np.sum(src == graph.indices))
    pairs = src * graph.n + graph.indices
    multi = int(pairs.size - np.unique(pairs).size)
    symmetric = bool(np.array_equal(np.sort(pairs), np.sort(graph.indices * graph.n + src)))
    return {
        "n": graph.n,
        "m": graph.m,
        "mean_degree": float(deg.mean()),
        "second_moment_degree": float((deg.astype(float) ** 2).mean()),
        "max_degree": int(deg.max()) if graph.n else 0,
        "min_degree": int(deg.min()) if graph.n else 0,
        "p_c": percolation_threshold(graph),
        "n_components": int(sizes.size),
        "giant_component_fraction": float(sizes.max() / graph.n),
        "n_isolated": int(np.sum(deg == 0)),
        "self_loops": self_loops,
        "multi_edges": multi,
        "symmetric": symmetric,
        "average_clustering": float(nx.average_clustering(to_networkx(graph))),
    }


def degree_preserving_randomisation(graph: Graph, swaps_per_edge: int, seed: int) -> Graph:
    """Randomise a graph with networkx.double_edge_swap (degree sequence preserved). EXP-004 S2."""
    if swaps_per_edge < 0:
        raise GraphError("swaps_per_edge must be >= 0")
    g = to_networkx(graph)
    nswap = swaps_per_edge * graph.m
    if nswap:
        nx.double_edge_swap(g, nswap=nswap, max_tries=100 * nswap, seed=int(seed))
    return from_networkx(g, family=graph.family + "-dpr", params={**graph.params, "swaps_per_edge": swaps_per_edge, "swap_seed": int(seed)})


def trim_edges(graph: Graph, target_m: int, rng: np.random.Generator) -> Graph:
    """Remove uniformly chosen edges until the graph has target_m edges. EXP-004 S3."""
    edges = graph.edge_list()
    if not (0 <= target_m <= len(edges)):
        raise GraphError(f"target_m must be in [0, {len(edges)}], got {target_m}")
    keep = np.sort(rng.choice(len(edges), size=target_m, replace=False))
    return from_edges(graph.n, [edges[i] for i in keep], family=graph.family + "-trim", params={**graph.params, "trimmed_to": target_m})
