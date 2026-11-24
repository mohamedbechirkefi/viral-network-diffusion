# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from viral.graphs import (
    GraphError,
    components,
    degree_preserving_randomisation,
    from_edges,
    generate,
    graph_stats,
    percolation_threshold,
    trim_edges,
)


def test_from_edges_csr_sorted_and_symmetric():
    g = from_edges(4, [(2, 0), (0, 1), (3, 2)])
    assert g.m == 3
    assert g.neighbours(0).tolist() == [1, 2]
    assert g.neighbours(2).tolist() == [0, 3]
    assert g.degrees().tolist() == [2, 1, 2, 1]


@pytest.mark.parametrize("edges", [[(0, 0)], [(0, 1), (1, 0)], [(0, 5)], [(-1, 0)], [(0, 1, 2)]])
def test_from_edges_rejects_invalid(edges):
    with pytest.raises(GraphError):
        from_edges(3, edges)


@pytest.mark.parametrize("n", [0, -1, 2.5, True])
def test_from_edges_rejects_bad_n(n):
    with pytest.raises(GraphError):
        from_edges(n, [])


def test_empty_graph_allowed():
    g = from_edges(3, [])
    assert g.m == 0 and components(g).tolist() == [0, 1, 2]


@pytest.mark.parametrize("family,m_expected", [("er", 3000), ("ws", 3000), ("ba", 2991)])
def test_generators_invariants(family, m_expected):
    g = generate(family, 1000, 6, seed=7)
    s = graph_stats(g)
    assert s["n"] == 1000
    assert s["m"] == m_expected
    assert s["self_loops"] == 0 and s["multi_edges"] == 0 and s["symmetric"]
    assert abs(s["mean_degree"] - 6) <= 0.06


@pytest.mark.parametrize("family", ["er", "ws", "ba"])
def test_generators_deterministic(family):
    a, b = generate(family, 200, 6, seed=3), generate(family, 200, 6, seed=3)
    assert np.array_equal(a.indptr, b.indptr) and np.array_equal(a.indices, b.indices)
    c = generate(family, 200, 6, seed=4)
    assert not (np.array_equal(a.indptr, c.indptr) and np.array_equal(a.indices, c.indices))


@pytest.mark.parametrize(
    "family,n,k,kw",
    [("xx", 100, 6, {}), ("er", 2, 1, {}), ("er", 101, 3, {}), ("ws", 100, 5, {}), ("ws", 100, 6, {"ws_beta": 1.5}),
     ("ba", 100, 5, {}), ("er", 100, 0, {}), ("er", 100, float("nan"), {}), ("er", 10, 9, {})],
)
def test_generators_reject_invalid(family, n, k, kw):
    with pytest.raises(GraphError):
        generate(family, n, k, seed=1, **kw)


def test_generator_rejects_negative_seed():
    with pytest.raises(GraphError):
        generate("er", 100, 6, seed=-1)


def test_components_disconnected():
    g = from_edges(6, [(0, 1), (1, 2), (3, 4)])
    assert components(g).tolist() == [0, 0, 0, 1, 1, 2]
    s = graph_stats(g)
    assert s["n_components"] == 3 and s["n_isolated"] == 1 and s["giant_component_fraction"] == 0.5


def test_percolation_threshold_hand_computed():
    # star with 3 leaves: degrees 3,1,1,1 -> <k>=1.5, <k^2>=3, p_c = 1.5/1.5 = 1
    assert percolation_threshold(from_edges(4, [(0, 1), (0, 2), (0, 3)])) == pytest.approx(1.0)
    # 3-regular (K4): <k>=3, <k^2>=9, p_c = 3/6
    k4 = from_edges(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    assert percolation_threshold(k4) == pytest.approx(0.5)
    assert percolation_threshold(from_edges(2, [(0, 1)])) == float("inf")


def test_degree_preserving_randomisation_keeps_degrees():
    g = generate("ba", 300, 6, seed=5)
    h = degree_preserving_randomisation(g, swaps_per_edge=2, seed=9)
    assert np.array_equal(np.sort(g.degrees()), np.sort(h.degrees()))
    assert np.array_equal(g.degrees(), h.degrees())
    assert h.m == g.m
    assert graph_stats(h)["multi_edges"] == 0


def test_trim_edges():
    g = generate("er", 1000, 6, seed=1)
    h = trim_edges(g, 2991, np.random.default_rng(0))
    assert h.m == 2991
    assert set(h.edge_list()) <= set(g.edge_list())
    with pytest.raises(GraphError):
        trim_edges(g, 3001, np.random.default_rng(0))


@settings(max_examples=60, deadline=None)
@given(st.integers(2, 25).flatmap(lambda n: st.tuples(st.just(n), st.sets(st.tuples(st.integers(0, n - 1), st.integers(0, n - 1)).filter(lambda e: e[0] < e[1]), max_size=60))))
def test_property_csr_round_trip(case):
    n, edges = case
    g = from_edges(n, edges)
    assert set(g.edge_list()) == set(edges)
    assert g.degrees().sum() == 2 * len(edges)
    s = graph_stats(g)
    assert s["symmetric"] and s["self_loops"] == 0 and s["multi_edges"] == 0
    lab = components(g)
    for u, v in edges:
        assert lab[u] == lab[v]
