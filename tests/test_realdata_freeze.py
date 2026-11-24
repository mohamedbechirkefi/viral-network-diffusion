# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Real-network ingestion, new topologies, Holm intervals and the freeze-record guard.

The GML fixture below is synthetic (invented rows in the schema of the source file);
no real row is committed anywhere in the repository.
"""

import copy
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from viral import cli
from viral.config import ConfigError, validate_config
from viral.graphs import from_edges, generate, percolation_threshold
from viral.protocol_gate import frozen_status, sha256_file
from viral.realdata import IngestError, ingest_gml, load_processed, processed_bytes, summary, to_graph, validate_processed
from viral.results import validate_result, assemble, build_manifest
from viral.runner import build_graph, run_experiment
from viral.stats import StatsError, equivalence, holm_bootstrap_contrasts

REPO = Path(__file__).resolve().parents[1]


def _gml(nodes, edges, header="  undirected 1\n"):
    body = "".join(f"  node [\n    id {i}\n    label {i}\n  ]\n" for i in nodes)
    body += "".join("  edge [\n" + "".join(f"    {k} {v}\n" for k, v in e.items()) + "  ]\n" for e in edges)
    return f'graph [\n  name "synthetic fixture"\n{header}{body}]\n'


# 14 declared nodes with non-contiguous ids; node 90 is isolated
FIX_NODES = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 90]
RING = [(10 + i, 10 + (i + 1) % 13) for i in range(13)]  # ring over ids 10..22
CHORDS = [(10, 13), (11, 15), (12, 17), (14, 19), (16, 21), (18, 22), (20, 12), (13, 17)]
FIX_EDGES = [{"source": s, "target": t} for s, t in RING + CHORDS] + [
    {"source": 11, "target": 10},  # duplicate of (10, 11)
    {"source": 12, "target": 12},  # self-loop
    {"source": 13},  # missing target
    {"source": 13, "target": 77},  # unknown endpoint
    {"source": "x", "target": 14},  # non-integer endpoint (missing)
]
FIXTURE = _gml(FIX_NODES, FIX_EDGES)


def test_ingest_counts_and_relabelling():
    doc = ingest_gml(FIXTURE)
    c = doc["counts"]
    assert (doc["n"], doc["m"]) == (14, 21)
    assert c == {"nodes_declared": 14, "edges_declared": 26, "nodes_missing_id": 0, "nodes_duplicate_id": 0,
                 "edges_missing_endpoint": 2, "edges_unknown_endpoint": 1, "edges_self_loop": 1, "edges_duplicate": 1,
                 "nodes_kept": 14, "edges_kept": 21, "edges_excluded": 5, "nodes_isolated": 1}
    assert [0, 1] in doc["edges"] and all(13 not in e for e in doc["edges"])  # id 90 -> 13, isolated
    validate_processed(doc)
    assert ingest_gml(FIXTURE) == doc  # pure and deterministic
    assert processed_bytes(doc) == processed_bytes(ingest_gml(FIXTURE))
    s = summary(doc)
    assert s["n_isolated"] == 1 and s["m"] == 21 and "edges" not in s


def test_ingest_rejects_bad_schema():
    for bad in (
        FIXTURE.replace("undirected 1", "directed 1"),
        "graph [ node [ id 1 ] ",  # unterminated
        "node [ id 1 ]",  # no graph block
        "graph [ ]",  # no node
        "graph [ node [ id 1 ] ] graph [ node [ id 2 ] ]",
        "graph [ node [ id ] ]",
    ):
        with pytest.raises(IngestError):
            ingest_gml(bad)
    dup = ingest_gml(_gml([1, 1, 2], [{"source": 1, "target": 2}]))
    assert dup["counts"]["nodes_duplicate_id"] == 1 and dup["n"] == 2


def test_validate_processed_rejects_malformed():
    good = ingest_gml(FIXTURE)
    for mutate in (
        lambda d: d.update(processed_schema_version="0"),
        lambda d: d["edges"].append([3, 3]),
        lambda d: d["edges"].append(list(d["edges"][0])) or d.update(m=d["m"] + 1),
        lambda d: d["edges"].__setitem__(0, [5, 2]),
        lambda d: d.update(m=1),
        lambda d: d["edges"].__setitem__(0, [0, 99]),
    ):
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(IngestError):
            validate_processed(bad)


def _write_fixture(tmp_path):
    p = tmp_path / "fixture.json"
    p.write_bytes(processed_bytes(ingest_gml(FIXTURE)))
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


def test_load_processed_pins_sha(tmp_path):
    p, h = _write_fixture(tmp_path)
    g = load_processed(p, h)
    assert g.n == 14 and g.m == 21 and g.family == "real"
    with pytest.raises(IngestError):
        load_processed(p, "0" * 64)
    with pytest.raises(IngestError):
        load_processed(tmp_path / "missing.json")


REAL_TINY = {
    "config_schema_version": "1.1.0", "experiment_id": "EXP-005", "mode": "exploratory",
    "label": "EXPLORATORY test fixture (synthetic network in the real-data schema)",
    "master_seed": 7, "n": 14, "mean_degree": 3, "ws_beta": 0.0,
    "topologies": ["real", "real_er", "real_dpr"], "models": {"ic": {"p": [0.0, 0.4, 1.0]}},
    "seed_rules": ["random"], "seed_counts": [1], "replicates": 3, "cascades": 4, "verify": True, "dpr_swaps_per_edge": 2,
}


def test_real_topologies_run(tmp_path):
    p, h = _write_fixture(tmp_path)
    cfg = validate_config({**copy.deepcopy(REAL_TINY), "real_graph": {"path": str(p), "sha256": h}})
    run = run_experiment(cfg)
    assert run["verification"]["cascade_failures"] == 0 and run["verification"]["graph_failures"] == 0
    real = to_graph(ingest_gml(FIXTURE))
    graphs = {(g["topology"], g["replicate"]): g for g in run["graphs"]}
    for r in range(3):
        assert graphs[("real", r)]["stats"]["m"] == 21
        assert graphs[("real_er", r)]["stats"]["m"] == 21 and graphs[("real_er", r)]["stats"]["n"] == 14
        g_dpr, _ = build_graph(cfg, "real_dpr", r, real)
        assert sorted(g_dpr.degrees().tolist()) == sorted(real.degrees().tolist())
    # common random numbers: same replicate gives the same first seed set in every arm
    firsts = {}
    for c in run["cells"]:
        firsts.setdefault((c["replicate"], c["param"]), set()).add(tuple(c["first_seed_set"]))
    assert all(len(v) == 1 for v in firsts.values())
    man = build_manifest(cfg, REPO, "2026-11-24T00:00:00Z", "2026-11-24T00:00:01Z", run["wall_seconds"])
    validate_result(assemble(cfg, run, man))
    bad = {**copy.deepcopy(REAL_TINY), "n": 15, "real_graph": {"path": str(p), "sha256": h}}
    with pytest.raises(ConfigError):
        run_experiment(validate_config(bad))


def test_real_config_rules():
    with pytest.raises(ConfigError):  # real topology without real_graph
        validate_config(copy.deepcopy(REAL_TINY))
    mixed = {**copy.deepcopy(REAL_TINY), "topologies": ["real", "er"], "real_graph": {"path": "x", "sha256": "0" * 64}}
    with pytest.raises(ConfigError):
        validate_config(mixed)
    stray = {**copy.deepcopy(REAL_TINY), "topologies": ["er"], "n": 100, "mean_degree": 4, "real_graph": {"path": "x", "sha256": "0" * 64}}
    with pytest.raises(ConfigError):
        validate_config(stray)
    over = {**copy.deepcopy(REAL_TINY), "topologies": ["er"], "n": 100, "mean_degree": 4, "models": {"ic": {"p": [1.5]}}}
    with pytest.raises(ConfigError):
        validate_config(over)
    old = {**copy.deepcopy(over), "config_schema_version": "1.0.0", "p_scale": "pc_multiple"}
    with pytest.raises(ConfigError):  # new fields are not part of schema 1.0.0
        validate_config(old)


SYN = {
    "config_schema_version": "1.1.0", "experiment_id": "EXP-004", "mode": "exploratory", "label": "EXPLORATORY test fixture",
    "master_seed": 11, "n": 300, "mean_degree": 4, "ws_beta": 0.1, "topologies": ["er_trim", "ws_trim", "ba", "ba_dpr"],
    "models": {"ic": {"p": [0.5, 1.0, 50.0]}}, "p_scale": "pc_multiple", "dpr_swaps_per_edge": 2,
    "seed_rules": ["random"], "seed_counts": [1], "replicates": 2, "cascades": 3, "verify": True,
}


def test_sensitivity_topologies_and_pc_scale():
    cfg = validate_config(copy.deepcopy(SYN))
    for r in range(2):
        er_t, _ = build_graph(cfg, "er_trim", r)
        ws_t, _ = build_graph(cfg, "ws_trim", r)
        ba, _ = build_graph(cfg, "ba", r)
        dpr, _ = build_graph(cfg, "ba_dpr", r)
        assert er_t.m == ws_t.m == ba.m == 2 * (300 - 2)
        er, _ = build_graph(cfg, "er", r)
        assert set(er_t.edge_list()) <= set(er.edge_list())  # trimmed from the same ER replicate
        assert np.array_equal(np.sort(dpr.degrees()), np.sort(ba.degrees())) and set(dpr.edge_list()) != set(ba.edge_list())
    run = run_experiment(cfg)
    assert run["verification"]["cascade_failures"] == 0
    pc = {(g["topology"], g["replicate"]): g["stats"]["p_c"] for g in run["graphs"]}
    for c in run["cells"]:
        assert c["p_actual"] == pytest.approx(min(1.0, c["param"] * pc[(c["topology"], c["replicate"])]))
    assert any(c["p_actual"] == 1.0 for c in run["cells"])  # c = 50 is capped at 1
    man = build_manifest(cfg, REPO, "2026-11-24T00:00:00Z", "2026-11-24T00:00:01Z", run["wall_seconds"])
    validate_result(assemble(cfg, run, man))


def test_holm_bootstrap_contrasts_rule():
    rng = np.random.default_rng(0)
    diffs = {"big": rng.normal(1.0, 0.1, 40), "mid": rng.normal(0.05, 0.1, 40), "null": rng.normal(0.0, 0.1, 40), "zero": np.zeros(40)}
    res = holm_bootstrap_contrasts(diffs, 4000, np.random.default_rng(1))
    again = holm_bootstrap_contrasts(diffs, 4000, np.random.default_rng(1))
    assert res == again
    m = 4
    order = sorted(res, key=lambda k: res[k]["holm_step"])
    assert order[0] == "big" and res["big"]["reject"] and res["big"]["interval_level"] == pytest.approx(1 - 0.05 / m)
    assert res["zero"]["p_boot"] == 1.0 and not res["zero"]["reject"] and res["zero"]["lo"] == res["zero"]["hi"] == 0.0
    stop = next(res[k]["holm_step"] for k in order if not res[k]["reject"])
    for k in order:
        step = min(res[k]["holm_step"], stop)
        assert res[k]["interval_level"] == pytest.approx(1 - 0.05 / (m - step))
        assert res[k]["lo"] <= res[k]["mean"] <= res[k]["hi"] or res[k]["sd"] == 0
    const = holm_bootstrap_contrasts({"c": np.full(5, 0.3), "d": np.full(5, -0.1)}, 100, np.random.default_rng(0))
    assert const["c"]["p_boot"] == 0.0 and const["c"]["reject"] and const["d"]["reject"]
    assert equivalence(-0.01, 0.019) and not equivalence(-0.03, 0.0)
    with pytest.raises(StatsError):
        holm_bootstrap_contrasts({"a": [1, 2], "b": [1, 2, 3]}, 10, np.random.default_rng(0))
    with pytest.raises(StatsError):
        holm_bootstrap_contrasts({}, 10, np.random.default_rng(0))


# ---- freeze-record guard -------------------------------------------------

def _frozen_fake_repo(tmp_path, cfg_text='{"a": 1}\n'):
    (tmp_path / "research" / "experiments" / "EXP-002").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.write_text("# protocol\n")
    parent = tmp_path / "research" / "protocol.md"
    parent.write_text("Status: FROZEN\n")
    (tmp_path / "data" / "manifest.json").write_text("{}\n")
    cfg = tmp_path / "config.json"
    cfg.write_text(cfg_text)
    (tmp_path / "research" / "experiment_registry.csv").write_text(
        "exp_id,title,purpose,depends_on,primary_outcome,protocol_path,protocol_hash,status,report_path,planned_analysis\n"
        f"EXP-002,t,p,d,o,research/experiments/EXP-002/protocol.md,{sha256_file(proto)},frozen,r,a\n")
    rec = {"study_protocol": {"path": "research/protocol.md", "sha256": sha256_file(parent)},
           "data_manifest": {"path": "data/manifest.json", "sha256": sha256_file(tmp_path / "data" / "manifest.json")},
           "experiments": {"EXP-002": {"protocol_path": "research/experiments/EXP-002/protocol.md", "protocol_sha256": sha256_file(proto),
                                       "configs": [{"path": "config.json", "file_sha256": sha256_file(cfg)}]}}}
    (tmp_path / "research" / "freeze.json").write_text(json.dumps(rec))
    return tmp_path, cfg


def test_guard_accepts_frozen_and_refuses_changed(tmp_path):
    repo, cfg = _frozen_fake_repo(tmp_path / "a")
    assert frozen_status(repo, "EXP-002", cfg) == (True, "frozen")
    cfg.write_text('{"a": 2}\n')
    ok, why = frozen_status(repo, "EXP-002", cfg)
    assert not ok and "not a frozen" in why
    repo, cfg = _frozen_fake_repo(tmp_path / "b")
    (repo / "data" / "manifest.json").write_text('{"changed": true}\n')
    assert not frozen_status(repo, "EXP-002", cfg)[0]
    repo, cfg = _frozen_fake_repo(tmp_path / "c")
    (repo / "research" / "protocol.md").write_text("Status: FROZEN\nedited\n")
    assert not frozen_status(repo, "EXP-002", cfg)[0]
    repo, cfg = _frozen_fake_repo(tmp_path / "d")
    (repo / "research" / "freeze.json").unlink()
    assert not frozen_status(repo, "EXP-002", cfg)[0]
    repo, cfg = _frozen_fake_repo(tmp_path / "e")
    assert not frozen_status(repo, "EXP-003", cfg)[0]


FROZEN_CONFIGS = {
    "EXP-002": ["experiments/EXP-002/config.json"],
    "EXP-003": ["experiments/EXP-003/config.json"],
    "EXP-004": ["experiments/EXP-004/S1-config.json", "experiments/EXP-004/S2-config.json", "experiments/EXP-004/S3-config.json",
                "experiments/EXP-004/S4-n500-config.json", "experiments/EXP-004/S4-n2000-config.json"],
    "EXP-005": ["experiments/EXP-005/config.json"],
}


@pytest.mark.skipif(not (REPO / "research" / "freeze.json").is_file(), reason="freeze record not written yet")
def test_real_repo_guard_accepts_frozen_configs_and_refuses_changed(tmp_path, capsys):
    for exp, paths in FROZEN_CONFIGS.items():
        for rel in paths:
            ok, why = frozen_status(REPO, exp, REPO / rel)
            assert ok, (rel, why)
            changed = tmp_path / f"{exp}-{Path(rel).name}"
            raw = json.loads((REPO / rel).read_text())
            raw["replicates"] += 1
            changed.write_text(json.dumps(raw, indent=2) + "\n")
            ok, why = frozen_status(REPO, exp, changed)
            assert not ok and "not a frozen" in why
    # the CLI refuses the changed copy before running anything (no confirmatory run happens here)
    out = tmp_path / "out"
    assert cli.main(["run", "--config", str(tmp_path / "EXP-002-config.json"), "--out", str(out)]) == 3
    assert "REFUSED" in capsys.readouterr().err and not out.exists()
    assert not frozen_status(REPO, "EXP-001", REPO / "experiments/EXP-001/config.json")[0]  # exploratory, never frozen configs
