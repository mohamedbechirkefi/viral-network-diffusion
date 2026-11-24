# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import itertools

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from viral.engines import EngineError, ic_reference, ic_vectorised, lt_reference, lt_vectorised
from viral.graphs import components, from_edges, generate
from viral.metrics import depth, duration
from viral.verification import check_cascade

IC = [ic_reference, ic_vectorised]
LT = [lt_reference, lt_vectorised]

PATH4 = from_edges(4, [(0, 1), (1, 2), (2, 3)])
STAR4 = from_edges(5, [(0, 1), (0, 2), (0, 3), (0, 4)])
TRIANGLE = from_edges(3, [(0, 1), (1, 2), (0, 2)])
TWO_PARTS = from_edges(7, [(0, 1), (1, 2), (3, 4), (4, 5)])  # node 6 isolated


def rng(s=0):
    return np.random.default_rng(s)


def test_numpy_stream_scalar_equals_vector():
    """The exact differential test relies on this property of numpy's Generator."""
    a = rng(11)
    b = rng(11)
    assert np.array_equal([a.random() for _ in range(50)], b.random(50))


# ---------- hand-computed golden examples (IC) ----------

@pytest.mark.parametrize("engine", IC)
def test_ic_path_p1(engine):
    c = engine(PATH4, [0], 1.0, rng())
    assert c.activation_round.tolist() == [0, 1, 2, 3]
    assert c.parent.tolist() == [-1, 0, 1, 2]
    assert depth(c) == 3 and duration(c) == 3


@pytest.mark.parametrize("engine", IC)
def test_ic_star_center_and_leaf(engine):
    c = engine(STAR4, [0], 1.0, rng())
    assert c.activation_round.tolist() == [0, 1, 1, 1, 1]
    c = engine(STAR4, [3], 1.0, rng())
    assert c.activation_round.tolist() == [1, 2, 2, 0, 2]
    assert c.parent.tolist() == [3, 0, 0, -1, 0]


@pytest.mark.parametrize("engine", IC)
def test_ic_triangle_parents(engine):
    c = engine(TRIANGLE, [0], 1.0, rng())
    assert c.activation_round.tolist() == [0, 1, 1]
    assert c.parent.tolist() == [-1, 0, 0]


@pytest.mark.parametrize("engine", IC)
def test_ic_no_transmission(engine):
    g = generate("ba", 300, 6, seed=1)
    c = engine(g, [5, 9], 0.0, rng())
    assert c.size == 2 and depth(c) == 0 and duration(c) == 0
    assert np.flatnonzero(c.activation_round >= 0).tolist() == [5, 9]


@pytest.mark.parametrize("engine", IC)
def test_ic_all_transmission_disconnected(engine):
    c = engine(TWO_PARTS, [1], 1.0, rng())
    assert (c.activation_round >= 0).tolist() == [True, True, True, False, False, False, False]
    c = engine(TWO_PARTS, [6], 1.0, rng())
    assert c.size == 1
    c = engine(TWO_PARTS, [0, 5], 1.0, rng())
    assert c.size == 6 and c.activation_round[6] == -1


@pytest.mark.parametrize("engine", IC)
@pytest.mark.parametrize("bad", [-0.1, 1.1, float("nan"), float("inf"), "0.5", None, True])
def test_ic_invalid_p(engine, bad):
    with pytest.raises(EngineError):
        engine(PATH4, [0], bad, rng())


@pytest.mark.parametrize("engine", IC + [lambda g, s, p, r: lt_vectorised(g, s, p)])
@pytest.mark.parametrize("bad", [[], [0, 0], [4], [-1], [0.5], [[0]]])
def test_invalid_seeds(engine, bad):
    with pytest.raises(EngineError):
        engine(PATH4, bad, 0.5, rng())


# ---------- exact expected value (differential test against enumeration) ----------

def exact_expected_size(graph, seed, p):
    """E|A| by enumerating all live-edge subgraphs (IC equals reachability in the live-edge graph)."""
    edges = graph.edge_list()
    total = 0.0
    for keep in itertools.product([0, 1], repeat=len(edges)):
        w = np.prod([p if k else 1 - p for k in keep])
        live = from_edges(graph.n, [e for e, k in zip(edges, keep) if k])
        lab = components(live)
        total += w * np.sum(lab == lab[seed])
    return total


@pytest.mark.parametrize("graph,seed", [(PATH4, 0), (STAR4, 3), (TRIANGLE, 0), (from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 0), (1, 3), (3, 4)]), 0)])
def test_ic_matches_exact_expectation(graph, seed):
    p = 0.4
    assert exact_expected_size(PATH4, 0, 0.5) == pytest.approx(1 + 0.5 + 0.25 + 0.125)
    exact = exact_expected_size(graph, seed, p)
    r = rng(123)
    sizes = np.array([ic_vectorised(graph, [seed], p, r).size for _ in range(20000)])
    se = sizes.std() / np.sqrt(sizes.size)
    assert abs(sizes.mean() - exact) < 4 * se + 1e-9


# ---------- reference versus vectorised (exact) ----------

@pytest.mark.parametrize("family", ["er", "ws", "ba"])
@pytest.mark.parametrize("p", [0.0, 0.05, 0.2, 0.5, 1.0])
def test_ic_reference_equals_vectorised(family, p):
    g = generate(family, 300, 6, seed=2)
    for s in range(5):
        seeds = np.random.default_rng(s).choice(300, size=1 + s % 3, replace=False)
        a = ic_reference(g, seeds, p, rng(1000 + s))
        b = ic_vectorised(g, seeds, p, rng(1000 + s))
        assert np.array_equal(a.activation_round, b.activation_round)
        assert np.array_equal(a.parent, b.parent)
        assert a.n_activation_events == b.n_activation_events


@settings(max_examples=60, deadline=None)
@given(
    st.integers(2, 20).flatmap(lambda n: st.tuples(st.just(n), st.sets(st.tuples(st.integers(0, n - 1), st.integers(0, n - 1)).filter(lambda e: e[0] < e[1]), max_size=50), st.integers(0, n - 1))),
    st.floats(0, 1), st.integers(0, 2**32 - 1), st.floats(0, 1.2),
)
def test_property_engines_agree_and_invariants(case, p, seed, phi):
    n, edges, s0 = case
    g = from_edges(n, edges)
    lab = components(g)
    a = ic_reference(g, [s0], p, rng(seed))
    b = ic_vectorised(g, [s0], p, rng(seed))
    assert np.array_equal(a.activation_round, b.activation_round) and np.array_equal(a.parent, b.parent)
    assert check_cascade(g, lab, b, p) == []
    la, lb = lt_reference(g, [s0], phi), lt_vectorised(g, [s0], phi)
    assert np.array_equal(la.activation_round, lb.activation_round) and np.array_equal(la.generation, lb.generation)
    assert check_cascade(g, lab, lb, phi) == []
    # monotone bound: the IC active set lies inside the seeded component
    assert set(np.flatnonzero(b.activation_round >= 0)) <= set(np.flatnonzero(lab == lab[s0]))


# ---------- LT ----------

@pytest.mark.parametrize("engine", LT)
def test_lt_path_half(engine):
    c = engine(PATH4, [0], 0.5)
    assert c.activation_round.tolist() == [0, 1, 2, 3]
    assert c.generation.tolist() == [0, 1, 2, 3]


@pytest.mark.parametrize("engine", LT)
def test_lt_star(engine):
    assert engine(STAR4, [0], 1.0).activation_round.tolist() == [0, 1, 1, 1, 1]
    # leaf seed: centre sees 1/4 active
    assert engine(STAR4, [1], 0.25).activation_round.tolist() == [1, 0, 2, 2, 2]
    assert engine(STAR4, [1], 0.26).activation_round.tolist() == [-1, 0, -1, -1, -1]


@pytest.mark.parametrize("engine", LT)
def test_lt_needs_two_exposures(engine):
    # node 2 has neighbours 0 and 1; with phi = 1 it needs both active
    g = from_edges(3, [(0, 2), (1, 2)])
    assert engine(g, [0], 1.0).size == 1
    assert engine(g, [0, 1], 1.0).activation_round.tolist() == [0, 0, 1]


@pytest.mark.parametrize("engine", LT)
def test_lt_phi_zero_and_above_one(engine):
    c = engine(TWO_PARTS, [4], 0.0)
    assert (c.activation_round >= 0).tolist() == [False, False, False, True, True, True, False]
    g = generate("er", 300, 6, seed=4)
    assert engine(g, [0, 1, 2], 1.01).size == 3


@pytest.mark.parametrize("bad", [-0.1, float("nan"), float("inf"), "x", None, True])
def test_lt_invalid_phi(bad):
    with pytest.raises(EngineError):
        lt_vectorised(PATH4, [0], bad)


@pytest.mark.parametrize("family", ["er", "ws", "ba"])
@pytest.mark.parametrize("phi", [0.0, 0.1, 0.18, 0.26, 1.01])
def test_lt_reference_equals_vectorised(family, phi):
    g = generate(family, 300, 6, seed=8)
    for s in range(4):
        seeds = np.random.default_rng(s).choice(300, size=1 + 4 * s, replace=False)
        a, b = lt_reference(g, seeds, phi), lt_vectorised(g, seeds, phi)
        assert np.array_equal(a.activation_round, b.activation_round)
        assert np.array_equal(a.generation, b.generation)


def test_lt_depth_equals_duration_under_planning_definition():
    """Finding recorded for the owner: with synchronous updates and generation = 1 + max
    generation of active neighbours, D == T for every LT cascade (induction on rounds)."""
    for fam in ("er", "ws", "ba"):
        g = generate(fam, 500, 6, seed=1)
        for phi in (0.0, 0.1, 0.18, 0.3):
            for s in range(5):
                seeds = np.random.default_rng(s).choice(500, size=10, replace=False)
                c = lt_vectorised(g, seeds, phi)
                assert depth(c) == duration(c)


# ---------- determinism and extreme parameters ----------

def test_ic_deterministic_given_seed():
    g = generate("ws", 500, 6, seed=1)
    a = ic_vectorised(g, [0], 0.3, rng(5))
    b = ic_vectorised(g, [0], 0.3, rng(5))
    assert np.array_equal(a.activation_round, b.activation_round)


def test_extreme_all_seeds_and_single_node():
    g = generate("er", 100, 6, seed=1)
    c = ic_vectorised(g, np.arange(100), 1.0, rng())
    assert c.size == 100 and duration(c) == 0
    one = from_edges(1, [])
    assert ic_vectorised(one, [0], 1.0, rng()).size == 1
    assert lt_vectorised(one, [0], 0.0).size == 1


def test_ic_p1_large_graph_reaches_component():
    g = generate("er", 1000, 6, seed=3)
    lab = components(g)
    c = ic_vectorised(g, [0], 1.0, rng())
    assert c.size == int(np.sum(lab == lab[0]))
