# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Tests of the frozen confirmatory analyses (viral.confirmatory, scripts/analyse_confirmatory.py)."""

import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from viral.analysis import confirmatory_contrasts
from viral.config import load_config
from viral.confirmatory import PLANS, grid_mean_family, per_param_family, run_plan, s1_reading
from viral.results import write_result

from test_pipeline import TINY, tiny_doc

REPO = Path(__file__).resolve().parents[1]


def _fake_doc(values: dict, master=7):
    """values[(topology, param, replicate)] = mean_S; one IC random single-seed cell each."""
    cells = []
    for (t, p, r), v in values.items():
        cells.append({"topology": t, "param": p, "replicate": r, "model": "ic", "seed_rule": "random", "seed_count": 1, "n_cascades": 1,
                      "summary": {"mean_S": v, "mean_depth": 1.0, "mean_t50": 1.0, "gini_size": 0.0, "large_cascade_share": 0.0}})
    return {"config": {"master_seed": master}, "cells": cells}


def test_plans_match_frozen_configs():
    for key, plan in PLANS.items():
        cfg = load_config(REPO / "experiments" / key)
        assert cfg.mode == "confirmatory"
        assert {x for pr in plan["pairs"] for x in pr} <= set(cfg.topologies)
        assert plan["model"] in cfg.raw["models"] and plan["rule"] in cfg.seed_rules and plan["count"] in cfg.seed_counts
    sizes = {k: len(load_config(REPO / "experiments" / k).settings()) * len(p["pairs"]) for k, p in PLANS.items() if p["kind"] == "per_param"}
    assert sizes == {"EXP-002/config.json": 14, "EXP-004/S1-config.json": 10, "EXP-004/S2-config.json": 7, "EXP-004/S3-config.json": 14,
                     "EXP-004/S4-n500-config.json": 14, "EXP-004/S4-n2000-config.json": 14, "EXP-005/config.json": 14}


def test_per_param_family_equals_existing_confirmatory_contrasts():
    _, doc = tiny_doc()
    a = per_param_family(doc, [("ws", "er"), ("ba", "er")], n_boot=500)
    b = confirmatory_contrasts(doc, ["ws", "ba"], "er", n_boot=500)
    assert [(r["contrast"], r["param"], r["mean"], r["lo"], r["hi"], r["reject"]) for r in a] == \
           [(r["contrast"], r["param"], r["mean"], r["lo"], r["hi"], r["reject"]) for r in b]


def test_known_differences_and_two_controls():
    vals = {}
    for r in range(20):
        for p in (0.1, 0.2):
            vals[("x", p, r)] = 0.5 + (0.1 if p == 0.2 else 0.0)
            vals[("a", p, r)] = 0.5
            vals[("b", p, r)] = 0.5 + 0.001 * (r % 3 - 1)
    rows = per_param_family(_fake_doc(vals), [("x", "a"), ("x", "b")], n_boot=2000)
    by = {(r["contrast"], r["param"]): r for r in rows}
    assert len(rows) == 4
    assert by[("x - a", 0.2)]["mean"] == pytest.approx(0.1) and by[("x - a", 0.2)]["reject"]
    assert by[("x - a", 0.1)]["mean"] == 0 and not by[("x - a", 0.1)]["reject"] and by[("x - a", 0.1)]["equivalent_within_sesoi"]
    assert by[("x - b", 0.2)]["reject"]


def test_grid_mean_family_known_value():
    vals = {}
    for r in range(10):
        vals[("ws", 0.1, r)], vals[("ws", 0.3, r)] = 0.25, 0.75   # grid mean 0.5
        vals[("er", 0.1, r)], vals[("er", 0.3, r)] = 0.125, 0.375   # grid mean 0.25
        vals[("ba", 0.1, r)], vals[("ba", 0.3, r)] = 0.125 + 0.0625 * (r % 2), 0.375 - 0.0625 * (r % 2)  # sums exact in binary
    rows = grid_mean_family(_fake_doc(vals), [("ws", "er"), ("ba", "er")], "ic", "random", 1, n_boot=1000)
    by = {r["contrast"]: r for r in rows}
    assert by["ws - er"]["mean"] == pytest.approx(0.25) and by["ws - er"]["reject"]
    assert by["ba - er"]["mean"] == pytest.approx(0.0) and not by["ba - er"]["reject"]
    assert all(r["n_replicates"] == 10 for r in rows)


def test_s1_reading_cases():
    e2 = [{"contrast": "ba - er", "param": 0.2, "reject": True}]
    inside = [{"contrast": "ba - er", "param": 1.0, "lo": -0.01, "hi": 0.01}]
    outside = [{"contrast": "ba - er", "param": 1.0, "lo": 0.05, "hi": 0.09}]
    assert s1_reading(e2, inside)["verdict"].startswith("mapping-invariant: every")
    assert s1_reading(e2, outside)["verdict"].startswith("mapping-invariant: no")
    assert s1_reading(e2, inside + [{**outside[0], "param": 2.0}])["verdict"].startswith("unresolved")


def test_run_plan_and_script_refusal(tmp_path):
    _, doc = tiny_doc()
    out = run_plan(doc, PLANS["EXP-002/config.json"] | {"pairs": [("ws", "er"), ("ba", "er")]})
    assert len(out["primary"]) == 3 * 2 and out["secondary"] and out["topology_means"]
    spec = importlib.util.spec_from_file_location("analyse_confirmatory", REPO / "scripts" / "analyse_confirmatory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    run_dir = write_result(doc, tmp_path)
    assert mod.analyse(run_dir, "EXP-002/config.json", tmp_path / "an") == 3  # hash differs from the frozen config
    pytest.importorskip("matplotlib")
    figs = mod.figures(out, doc, tmp_path, "EXP-TEST")
    assert all((tmp_path / f"{s}.png").is_file() for s in figs)
