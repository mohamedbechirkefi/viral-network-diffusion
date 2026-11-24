# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Integration: config -> run -> validated result -> report; protocol gate; CLI."""

import copy
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from viral import cli
from viral.config import ConfigError, cascade_rng, config_hash, graph_rng_seed, load_config, validate_config
from viral.protocol_gate import frozen_status
from viral.report import build_report
from viral.results import ResultError, assemble, build_manifest, load_result, validate_result, write_result
from viral.runner import run_experiment
from viral.seeding import SeedingError, select_seeds
from viral.graphs import from_edges, generate

REPO = Path(__file__).resolve().parents[1]

TINY = {
    "config_schema_version": "1.0.0",
    "experiment_id": "EXP-001",
    "mode": "exploratory",
    "label": "EXPLORATORY test fixture",
    "master_seed": 42,
    "n": 400,  # BA has m (n - m) edges: n must be large enough for the 1 percent mean-degree tolerance
    "mean_degree": 4,
    "ws_beta": 0.1,
    "topologies": ["er", "ws", "ba"],
    "models": {"ic": {"p": [0.0, 0.3, 1.0]}, "lt": {"phi": [0.0, 0.3, 1.01]}},
    "seed_rules": ["random", "highest_degree"],
    "seed_counts": [1, 3],
    "replicates": 2,
    "cascades": 5,
    "verify": True,
}


def tiny_doc(cfg_raw=TINY):
    cfg = validate_config(copy.deepcopy(cfg_raw))
    run = run_experiment(cfg)
    man = build_manifest(cfg, REPO, "2026-11-24T00:00:00Z", "2026-11-24T00:00:01Z", run["wall_seconds"])
    return cfg, assemble(cfg, run, man)


def test_config_validation_errors():
    for mutate in (
        lambda c: c.pop("master_seed"),
        lambda c: c.update(mode="final"),
        lambda c: c.update(topologies=["er", "er"]),
        lambda c: c.update(models={"ic": {"p": [1.5]}}),
        lambda c: c.update(extra=1),
        lambda c: c.update(seed_counts=[400]),
        lambda c: c.update(label="smoke"),
        lambda c: c.update(experiment_id="EXP-1"),
    ):
        bad = copy.deepcopy(TINY)
        mutate(bad)
        with pytest.raises(ConfigError):
            validate_config(bad)


def test_config_hash_canonical():
    a = copy.deepcopy(TINY)
    b = dict(reversed(list(copy.deepcopy(TINY).items())))
    assert config_hash(a) == config_hash(b)
    a["master_seed"] = 43
    assert config_hash(a) != config_hash(b)


def test_rng_streams_matched_across_topologies():
    a = cascade_rng(1, 3, "ic", 0.2, "random", 1).random(5)
    b = cascade_rng(1, 3, "ic", 0.2, "random", 1).random(5)
    c = cascade_rng(1, 4, "ic", 0.2, "random", 1).random(5)
    assert np.array_equal(a, b) and not np.array_equal(a, c)
    assert graph_rng_seed(1, "er", 0) != graph_rng_seed(1, "ws", 0)


def test_seed_selection():
    g = from_edges(5, [(0, 1), (0, 2), (0, 3), (1, 2)])
    assert select_seeds(g, "highest_degree", 1, np.random.default_rng(0)).tolist() == [0]
    hd2 = {tuple(select_seeds(g, "highest_degree", 2, np.random.default_rng(s)).tolist()) for s in range(30)}
    assert hd2 == {(0, 1), (0, 2)}  # tie between nodes 1 and 2 broken by the seeded draw
    s = select_seeds(g, "random", 5, np.random.default_rng(0))
    assert s.tolist() == [0, 1, 2, 3, 4]
    for rule, k in (("random", 0), ("random", 6), ("best", 1), ("random", True)):
        with pytest.raises(SeedingError):
            select_seeds(g, rule, k, np.random.default_rng(0))


def test_run_validates_and_is_deterministic():
    cfg, doc = tiny_doc()
    validate_result(doc)
    assert doc["verification"]["cascade_failures"] == 0 and doc["verification"]["graph_failures"] == 0
    assert doc["verification"]["cascades_checked"] == 3 * 2 * 6 * 2 * 2 * 5
    _, doc2 = tiny_doc()
    assert [c["per_cascade"] for c in doc["cells"]] == [c["per_cascade"] for c in doc2["cells"]]
    # common random numbers: same replicate and setting gives the same random seed set on every topology
    firsts = {}
    for c in doc["cells"]:
        if c["seed_rule"] == "random":
            firsts.setdefault((c["replicate"], c["model"], c["param"], c["seed_count"]), set()).add(tuple(c["first_seed_set"]))
    assert all(len(v) == 1 for v in firsts.values())


def test_result_schema_rejects_malformed(tmp_path):
    _, doc = tiny_doc()
    bad = copy.deepcopy(doc)
    bad["cells"][0]["summary"]["mean_S"] = 1.5
    with pytest.raises(ResultError):
        validate_result(bad)
    bad = copy.deepcopy(doc)
    bad["cells"][0]["per_cascade"]["size"].pop()
    with pytest.raises(ResultError):
        validate_result(bad)
    bad = copy.deepcopy(doc)
    del bad["manifest"]["git_revision"]
    with pytest.raises(ResultError):
        validate_result(bad)
    p = tmp_path / "result.json"
    p.write_text("{not json")
    with pytest.raises(ResultError):
        load_result(p)
    with pytest.raises(ResultError):
        load_result(tmp_path / "missing")


def test_write_load_report_round_trip(tmp_path):
    cfg, doc = tiny_doc()
    run_dir = write_result(doc, tmp_path)
    assert load_result(run_dir) == json.loads((run_dir / "result.json").read_text())
    assert json.loads((run_dir / "run_manifest.json").read_text())["config_hash"] == cfg.hash
    report = build_report(run_dir, project=cfg)
    text = report.read_text()
    assert "EXPLORATORY RUN. Not a finding." in text
    assert (run_dir / "tables" / "cells.csv").stat().st_size > 0
    assert "Runtime projection" in text
    with pytest.raises(FileExistsError):
        write_result(doc, tmp_path)


def _fake_repo(tmp_path, proto_text="# protocol\n", recorded=None, parent="Status: FROZEN\n"):
    (tmp_path / "research" / "experiments" / "EXP-002").mkdir(parents=True)
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.write_text(proto_text)
    (tmp_path / "research" / "protocol.md").write_text(parent)
    h = recorded if recorded is not None else hashlib.sha256(proto_text.encode()).hexdigest()
    (tmp_path / "research" / "experiment_registry.csv").write_text(
        "exp_id,title,purpose,depends_on,primary_outcome,protocol_path,protocol_hash,status,report_path,planned_analysis\n"
        f"EXP-002,t,p,d,o,research/experiments/EXP-002/protocol.md,{h},frozen,r,a\n"
    )
    return tmp_path


def test_protocol_gate(tmp_path):
    assert frozen_status(_fake_repo(tmp_path / "a"), "EXP-002") == (True, "frozen")
    assert not frozen_status(_fake_repo(tmp_path / "b", recorded="none (draft)"), "EXP-002")[0]
    assert not frozen_status(_fake_repo(tmp_path / "c", recorded="0" * 64), "EXP-002")[0]
    assert not frozen_status(_fake_repo(tmp_path / "d", parent="**Status: DRAFT, NOT FROZEN.**"), "EXP-002")[0]
    assert not frozen_status(_fake_repo(tmp_path / "e"), "EXP-009")[0]
    assert not frozen_status(tmp_path / "nowhere", "EXP-002")[0]


def test_real_repo_protocols_are_not_frozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003", "EXP-004"):
        ok, why = frozen_status(REPO, exp)
        assert not ok, why


def test_cli_run_refuses_confirmatory_config(capsys, tmp_path):
    rc = cli.main(["run", "--config", str(REPO / "experiments" / "EXP-002" / "config.json"), "--out", str(tmp_path)])
    assert rc == 3
    assert "REFUSED" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_cli_smoke_refuses_confirmatory_and_reports_bad_config(tmp_path, capsys):
    assert cli.main(["smoke", "--config", str(REPO / "experiments" / "EXP-002" / "config.json")]) == 3
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    assert cli.main(["run", "--config", str(bad)]) == 2


def test_cli_run_exploratory_tiny(tmp_path):
    p = tmp_path / "tiny.json"
    p.write_text(json.dumps(TINY))
    assert cli.main(["run", "--config", str(p), "--out", str(tmp_path / "out"), "--quiet"]) == 0
    (run_dir,) = list((tmp_path / "out").iterdir())
    assert cli.main(["report", str(run_dir)]) == 0


def test_repo_configs_validate():
    for p in (REPO / "experiments").glob("EXP-*/*.json"):
        load_config(p)
