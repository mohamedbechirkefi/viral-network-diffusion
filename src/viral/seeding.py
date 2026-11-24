# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Seed-set selection rules (initial exposure)."""

from __future__ import annotations

import numpy as np

from .graphs import Graph

RULES = ("random", "highest_degree")


class SeedingError(ValueError):
    """Raised for invalid seeding parameters."""


def select_seeds(graph: Graph, rule: str, count: int, rng: np.random.Generator) -> np.ndarray:
    """Return `count` distinct seed nodes, sorted.

    random: uniform without replacement over node indices.
    highest_degree: the `count` nodes of highest degree; ties broken by a seeded uniform draw.
    """
    if rule not in RULES:
        raise SeedingError(f"unknown seed rule {rule!r}")
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or not (1 <= count <= graph.n):
        raise SeedingError(f"count must be an integer in [1, {graph.n}], got {count!r}")
    if rule == "random":
        return np.sort(rng.choice(graph.n, size=int(count), replace=False).astype(np.int64))
    tie = rng.random(graph.n)
    order = np.lexsort((tie, -graph.degrees()))
    return np.sort(order[: int(count)].astype(np.int64))
