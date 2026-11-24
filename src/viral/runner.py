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
from .config import ExperimentConfig, cascade_rng, graph_rng_seed
from .engines import ENGINES
from .graphs import components, generate, graph_stats
from .seeding import select_seeds
from .verification import check_cascade, check_graph


def run_experiment(cfg: ExperimentConfig, progress: Callable[[str], None] | None = None) -> dict:
    """Run every (topology, replicate, model, parameter, seed rule, seed count) cell of the config."""
    graphs_out: list[dict] = []
    cells: list[dict] = []
    failures: list[dict] = []
    checks = {"cascades_checked": 0, "cascade_failures": 0, "graphs_checked": 0, "graph_failures": 0}
    t_start = time.perf_counter()
    for topology in cfg.topologies:
        for r in range(cfg.replicates):
            seed = graph_rng_seed(cfg.master_seed, topology, r)
            t0 = time.perf_counter()
            graph = generate(topology, cfg.n, cfg.mean_degree, seed, ws_beta=cfg.ws_beta)
            gen_s = time.perf_counter() - t0
            stats = graph_stats(graph)
            labels = components(graph)
            gfails = check_graph(stats, cfg.mean_degree)
            checks["graphs_checked"] += 1
            if gfails:
                checks["graph_failures"] += 1
                failures.append({"kind": "graph", "topology": topology, "replicate": r, "messages": gfails})
            graphs_out.append({"topology": topology, "replicate": r, "networkx_seed": seed, "generation_seconds": gen_s, "params": graph.params, "stats": stats})
            for model, param in cfg.settings():
                engine = ENGINES[(model, cfg.engine)]
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
                            c = engine(graph, seeds, param, rng) if model == "ic" else engine(graph, seeds, param)
                            m = metrics.cascade_metrics(c)
                            for k in rec:
                                rec[k].append(m[k])
                            if cfg.verify:
                                cf = check_cascade(graph, labels, c, param)
                                checks["cascades_checked"] += 1
                                if cf:
                                    checks["cascade_failures"] += 1
                                    failures.append({"kind": "cascade", "topology": topology, "replicate": r, "model": model, "param": param, "seed_rule": rule, "seed_count": count, "messages": cf})
                        cell_s = time.perf_counter() - t1
                        frac = np.asarray(rec["size"], dtype=float) / cfg.n
                        cells.append({
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
                        })
            if progress:
                progress(f"{topology} replicate {r} done ({time.perf_counter() - t_start:.1f} s)")
    return {"graphs": graphs_out, "cells": cells, "failures": failures, "verification": checks, "wall_seconds": time.perf_counter() - t_start}
