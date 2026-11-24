# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from viral.engines import ic_vectorised, lt_vectorised
from viral.graphs import from_edges
from viral.metrics import MetricError, final_fraction, gini, large_cascade_share, structural_virality, time_to_half
from viral.stats import StatsError, cluster_bootstrap, holm, paired_differences, required_replicates, variance_decomposition

PATH3 = from_edges(3, [(0, 1), (1, 2)])
STAR3 = from_edges(4, [(0, 1), (0, 2), (0, 3)])


def r():
    return np.random.default_rng(0)


def test_gini_hand_computed():
    assert gini([1, 1, 1]) == pytest.approx(0.0)
    # |1-3| twice / (2 * 4 * 2) = 4 / 16
    assert gini([1, 3]) == pytest.approx(0.25)
    assert gini([5]) == pytest.approx(0.0)
    # brute force on a small set
    x = np.array([1.0, 2.0, 7.0, 7.0, 30.0])
    brute = np.abs(x[:, None] - x[None, :]).sum() / (2 * x.size**2 * x.mean())
    assert gini(x) == pytest.approx(brute)


@pytest.mark.parametrize("bad", [[], [0, 0], [-1, 2], [np.nan, 1], [[1, 2]]])
def test_gini_invalid(bad):
    with pytest.raises(MetricError):
        gini(bad)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.integers(1, 1000), min_size=1, max_size=40))
def test_property_gini_bounds_and_scale_invariance(xs):
    g = gini(xs)
    assert -1e-12 <= g <= 1 - 1 / len(xs) + 1e-12
    assert gini([3 * x for x in xs]) == pytest.approx(g)


def test_time_to_half_and_fraction():
    c = ic_vectorised(PATH3, [0], 1.0, r())  # rounds 0,1,2; target ceil(3/2) = 2 reached at round 1
    assert time_to_half(c) == 1
    assert final_fraction(c) == pytest.approx(1.0)
    c = ic_vectorised(STAR3, [0], 1.0, r())  # 4 nodes, target 2, reached at round 1
    assert time_to_half(c) == 1
    c = ic_vectorised(STAR3, [0], 0.0, r())
    assert time_to_half(c) == 0


def test_structural_virality_hand_computed():
    # path seeded at an end: distances 1, 1, 2 -> mean 4/3
    assert structural_virality(ic_vectorised(PATH3, [0], 1.0, r())) == pytest.approx(4 / 3)
    # star from centre: 3 pairs at distance 1, 3 at distance 2 -> 9/6
    assert structural_virality(ic_vectorised(STAR3, [0], 1.0, r())) == pytest.approx(1.5)
    assert structural_virality(ic_vectorised(STAR3, [0], 0.0, r())) is None
    assert structural_virality(ic_vectorised(STAR3, [0, 1], 1.0, r())) is None
    assert structural_virality(lt_vectorised(STAR3, [0], 0.0)) is None


def test_large_cascade_share():
    assert large_cascade_share([0.05, 0.1, 0.5, 0.001]) == 0.5
    with pytest.raises(MetricError):
        large_cascade_share([])


def test_bootstrap_basic_and_degenerate():
    d = paired_differences([0.3, 0.4, 0.5, 0.6], [0.1, 0.1, 0.1, 0.1])
    out = cluster_bootstrap(d, 2000, r())
    assert out["mean"] == pytest.approx(0.35)
    assert out["lo"] <= out["mean"] <= out["hi"]
    assert out["p_boot"] == 0.0
    z = cluster_bootstrap([0.0, 0.0, 0.0], 500, r())
    assert z["lo"] == z["hi"] == 0.0 and z["p_boot"] == 1.0
    a = cluster_bootstrap(d, 500, np.random.default_rng(7))
    b = cluster_bootstrap(d, 500, np.random.default_rng(7))
    assert a == b


@pytest.mark.parametrize("args", [([1.0], 10), ([1.0, 2.0], 0)])
def test_bootstrap_invalid(args):
    with pytest.raises(StatsError):
        cluster_bootstrap(args[0], args[1], r())


def test_paired_differences_invalid():
    with pytest.raises(StatsError):
        paired_differences([1, 2], [1])


def test_holm_hand_computed():
    out = holm({"ws": 0.03, "ba": 0.01})
    assert out["ba"]["p_holm"] == pytest.approx(0.02) and out["ba"]["reject"]
    assert out["ws"]["p_holm"] == pytest.approx(0.03) and out["ws"]["reject"]
    out = holm({"ws": 0.04, "ba": 0.03})
    assert not out["ba"]["reject"] and not out["ws"]["reject"]
    assert out["ws"]["p_holm"] == pytest.approx(0.06)
    with pytest.raises(StatsError):
        holm({})


def test_variance_decomposition_sums_to_total():
    rng = np.random.default_rng(3)
    vals = {t: (rng.random((4, 6)) + i).tolist() for i, t in enumerate(["er", "ws", "ba"])}
    vd = variance_decomposition(vals)
    assert vd["between_topology"] + vd["between_replicate"] + vd["within_graph"] == pytest.approx(vd["total_variance"])
    assert vd["share_topology"] + vd["share_replicate"] + vd["share_within_graph"] == pytest.approx(1.0)
    flat = variance_decomposition({"er": [[1, 1], [1, 1]], "ws": [[1, 1], [1, 1]]})
    assert flat["total_variance"] == 0 and flat["share_topology"] is None
    with pytest.raises(StatsError):
        variance_decomposition({"er": [[1, 2]], "ws": [[1, 2, 3]]})


def test_required_replicates():
    # 1.96 * 0.028 / sqrt(30) = 0.01002 -> R = 31
    assert required_replicates(0.028, 0.01) == 31
    assert required_replicates(0.0, 0.01) == 2
    with pytest.raises(StatsError):
        required_replicates(0.1, 0.0)
