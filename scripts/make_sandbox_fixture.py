# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Write the engine fixture that the demo's vitest suite compares the browser port against (M5).

The research engine's reference implementations (viral.engines.ic_reference and lt_reference)
are run on three small graphs from the research generators (viral.graphs.generate). The IC engine
is driven by a Python port of the mulberry32 generator that the browser sandbox uses, so the
TypeScript port consumes the identical uniform stream and must reproduce every activation round
and parent exactly. The LT engine is deterministic given the graph and seed set.

This is a test fixture, not an experiment: tiny, exploratory, no result is reported from it.
Compute: well under one second, one process.

Usage:  .venv/bin/python scripts/make_sandbox_fixture.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from viral.engines import ic_reference, lt_reference  # noqa: E402
from viral.graphs import generate, percolation_threshold  # noqa: E402

OUT = REPO / "demo" / "src" / "fixtures" / "engine_fixture.json"
M32 = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & M32


class Mulberry32:
    """Bit-exact Python port of the JavaScript mulberry32 used in demo/src/engine.ts."""

    def __init__(self, seed: int) -> None:
        self.a = seed & M32

    def random(self) -> float:
        self.a = (self.a + 0x6D2B79F5) & M32
        a = self.a
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296


GRAPHS = [("er", 60, 6, 11), ("ws", 60, 6, 12), ("ba", 60, 6, 13)]
IC_P = [0.1, 0.25, 0.6]
LT_PHI = [0.15, 0.25, 0.4]
IC_CASCADES = 8


def build() -> dict:
    cases = []
    for family, n, k, seed in GRAPHS:
        g = generate(family, n, k, seed)
        ic = []
        for j, p in enumerate(IC_P):
            rng = Mulberry32(1000 + 17 * seed + j)
            runs = []
            for c in range(IC_CASCADES):
                seeds = [(7 * c + seed) % n]
                cas = ic_reference(g, seeds, p, rng)
                runs.append({"seeds": seeds, "activation_round": cas.activation_round.tolist(), "parent": cas.parent.tolist(), "size": cas.size})
            ic.append({"p": p, "rng_seed": 1000 + 17 * seed + j, "cascades": runs})
        lt = []
        for phi in LT_PHI:
            seeds = sorted({(3 * i + seed) % n for i in range(6)})
            cas = lt_reference(g, seeds, phi)
            lt.append({"phi": phi, "seeds": seeds, "activation_round": cas.activation_round.tolist(), "generation": cas.generation.tolist(), "size": cas.size})
        cases.append({"family": family, "n": n, "mean_degree": k, "networkx_seed": seed, "edges": [list(e) for e in g.edge_list()],
                      "p_c": percolation_threshold(g), "ic": ic, "lt": lt})
    r = Mulberry32(1)
    return {
        "note": "Test fixture from the research engine (viral.engines ic_reference, lt_reference) on graphs from viral.graphs.generate; not a result.",
        "generator": "scripts/make_sandbox_fixture.py",
        "rng_check": {"seed": 1, "first_draws": [r.random() for _ in range(3)]},
        "cases": cases,
    }


def render(doc: dict) -> str:
    return json.dumps(doc, separators=(",", ":")) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(build()))
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
