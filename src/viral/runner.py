# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Experiment runner: config -> graphs -> cascades -> per-cell records.

The runner does no I/O. It returns plain dictionaries that results.py
validates and serialises.
"""

from __future__ import annotations

import time
from collections.abc import Callable

import numpy as np

from . import metrics
from pathlib import Path

import networkx as nx

from .config import REAL_TOPOLOGIES, ConfigError, ExperimentConfig, cascade_rng, graph_rng_seed
from .engines import ENGINES
from .graphs import Graph, components, degree_preserving_randomisation, from_networkx, generate, graph_stats, percolation_threshold, trim_edges
from .seeding import select_seeds
from .verification import check_cascade, check_graph


REPO = Path(__file__).resolve().parents[2]


def load_real(cfg: ExperimentConfig, repo: Path = REPO) -> Graph:
    """The pinned processed real network of a real-network config (SHA-256 checked)."""
    from .realdata import load_processed

    rg = cfg.raw["real_graph"]
    path = Path(rg["path"])
    g = load_processed(path if path.is_absolute() else repo / path, expected_sha256=rg["sha256"])
    if g.n != cfg.n:
        raise ConfigError(f"config n = {cfg.n} but the real network has {g.n} nodes")
    return g


def build_graph(cfg: ExperimentConfig, topology: str, r: int, real: Graph | None = None) -> tuple[Graph, int]:
    """Graph of `topology` for replicate r, and the seed that identifies it.

    er, ws, ba: seeded generators. er_trim, ws_trim: replicate r of er or ws, trimmed to the
    BA edge count m (n - m) with m = mean_degree / 2 (EXP-004 S3). ba_dpr: replicate r of ba
    after dpr_swaps_per_edge * M double-edge swaps (EXP-004 S2). real: the pinned real network
    (identical for every r). real_er: G(n, M) with the real network's n and M. real_dpr: the
    real network after dpr_swaps_per_edge * M double-edge swaps (EXP-005).
    """
    seed = graph_rng_seed(cfg.master_seed, topology, r)
    if topology in ("er", "ws", "ba"):
        return generate(topology, cfg.n, cfg.mean_degree, seed, ws_beta=cfg.ws_beta), seed
    if topology in ("er_trim", "ws_trim"):
        base_t = topology.split("_")[0]
        base = generate(base_t, cfg.n, cfg.mean_degree, graph_rng_seed(cfg.master_seed, base_t, r), ws_beta=cfg.ws_beta)
        m_half = int(round(cfg.mean_degree / 2))
        g = trim_edges(base, m_half * (cfg.n - m_half), np.random.default_rng(seed))
        return Graph(g.n, g.indptr, g.indices, family=topology, params={**g.params, "trim_seed": seed}), seed
    if topology == "ba_dpr":
        base = generate("ba", cfg.n, cfg.mean_degree, graph_rng_seed(cfg.master_seed, "ba", r))
        g = degree_preserving_randomisation(base, cfg.dpr_swaps_per_edge, seed)
        return Graph(g.n, g.indptr, g.indices, family=topology, params=g.params), seed
    if topology in REAL_TOPOLOGIES:
        if real is None:
            raise ConfigError("a real-network topology needs the real graph")
        if topology == "real":
            return real, 0
        if topology == "real_er":
            g = from_networkx(nx.gnm_random_graph(real.n, real.m, seed=seed), family="real_er", params={"n": real.n, "m": real.m, "networkx_seed": seed})
            return g, seed
        g = degree_preserving_randomisation(real, cfg.dpr_swaps_per_edge, seed)
        return Graph(g.n, g.indptr, g.indices, family="real_dpr", params=g.params), seed
    raise ConfigError(f"unknown topology {topology!r}")


def run_experiment(cfg: ExperimentConfig, progress: Callable[[str], None] | None = None) -> dict:
    """Run every (topology, replicate, model, parameter, seed rule, seed count) cell of the config."""
    graphs_out: list[dict] = []
    cells: list[dict] = []
    failures: list[dict] = []
    checks = {"cascades_checked": 0, "cascade_failures": 0, "graphs_checked": 0, "graph_failures": 0}
    t_start = time.perf_counter()
    real = load_real(cfg) if "real_graph" in cfg.raw else None
    for topology in cfg.topologies:
        for r in range(cfg.replicates):
            t0 = time.perf_counter()
            graph, seed = build_graph(cfg, topology, r, real)
            gen_s = time.perf_counter() - t0
            stats = graph_stats(graph)
            labels = components(graph)
            gfails = check_graph(stats, cfg.mean_degree)
            checks["graphs_checked"] += 1
            if gfails:
                checks["graph_failures"] += 1
                failures.append({"kind": "graph", "topology": topology, "replicate": r, "messages": gfails})
            graphs_out.append({"topology": topology, "replicate": r, "networkx_seed": seed, "generation_seconds": gen_s, "params": graph.params, "stats": stats})
            p_c = percolation_threshold(graph)
            for model, param in cfg.settings():
                engine = ENGINES[(model, cfg.engine)]
                # EXP-004 S1: under p_scale = pc_multiple, param is the multiplier c and p = min(1, c p_c(G))
                p_run = min(1.0, param * p_c) if (model == "ic" and cfg.p_scale == "pc_multiple") else param
                for rule in cfg.seed_rules:
                    for count in cfg.seed_counts:
                        rng = cascade_rng(cfg.master_seed, r, model, param, rule, count)
                        rec = {k: [] for k in ("size", "depth", "duration", "t50", "structural_virality")}
                        first_seeds = None
                        t1 = time.perf_counter()
                        for _ in range(cfg.cascades):
                            seeds = select_seeds(graph, rule, count, rng)
                            if first_seeds is None:
                                first_seeds = seeds.tolist()
                            c = engine(graph, seeds, p_run, rng) if model == "ic" else engine(graph, seeds, p_run)
                            m = metrics.cascade_metrics(c)
                            for k in rec:
                                rec[k].append(m[k])
                            if cfg.verify:
                                cf = check_cascade(graph, labels, c, p_run)
                                checks["cascades_checked"] += 1
                                if cf:
                                    checks["cascade_failures"] += 1
                                    failures.append({"kind": "cascade", "topology": topology, "replicate": r, "model": model, "param": param, "seed_rule": rule, "seed_count": count, "messages": cf})
                        cell_s = time.perf_counter() - t1
                        frac = np.asarray(rec["size"], dtype=float) / cfg.n
                        cell = {
                            "topology": topology,
                            "replicate": r,
                            "model": model,
                            "param": param,
                            "seed_rule": rule,
                            "seed_count": count,
                            "n_cascades": cfg.cascades,
                            "first_seed_set": first_seeds,
                            "runtime_seconds": cell_s,
                            "per_cascade": rec,
                            "summary": {
                                "mean_S": float(frac.mean()),
                                "sd_S": float(frac.std(ddof=1)) if frac.size > 1 else 0.0,
                                "mean_depth": float(np.mean(rec["depth"])),
                                "mean_duration": float(np.mean(rec["duration"])),
                                "mean_t50": float(np.mean(rec["t50"])),
                                "gini_size": metrics.gini(rec["size"]),
                                "large_cascade_share": metrics.large_cascade_share(frac),
                            },
                        }
                        if model == "ic" and cfg.p_scale == "pc_multiple":
                            cell["p_actual"] = p_run
                        cells.append(cell)
            if progress:
                progress(f"{topology} replicate {r} done ({time.perf_counter() - t_start:.1f} s)")
    return {"graphs": graphs_out, "cells": cells, "failures": failures, "verification": checks, "wall_seconds": time.perf_counter() - t_start}
