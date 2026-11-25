# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""M5 consistency test (master prompt 11.6): the demo shows the numbers the paper prints.

1. Re-running scripts/export_demo_data.py in memory reproduces the committed results.json exactly.
2. Every `display` and `interval_display` string of the export appears verbatim in
   research/paper/manuscript.md. Documented exceptions:
   - estimates marked `printed_in: supplementary ...` (EXP-004 S3 and S4 rows, all M4 rows) are
     checked against research/paper/supplementary.md, which prints every such row;
   - the absolute levels behind the line charts are printed by the manuscript only as figures,
     so each level is checked against its claims-register row text (EXP-xxx-LVLnn);
   - graph statistics are checked against manuscript Table 2.
3. The sandbox engine fixture is reproduced by scripts/make_sandbox_fixture.py.
"""

import csv
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


exporter = _load("export_demo_data")
COMMITTED = REPO / "demo" / "public" / "data" / "results.json"
MANUSCRIPT = (REPO / "research" / "paper" / "manuscript.md").read_text()
SUPPLEMENTARY = (REPO / "research" / "paper" / "supplementary.md").read_text()


def test_export_reproduces_committed_file():
    assert exporter.render(exporter.build()) == COMMITTED.read_text()


def test_export_has_one_entry_per_registered_experiment():
    doc = json.loads(COMMITTED.read_text())
    with (REPO / "research" / "experiment_registry.csv").open() as fh:
        registered = [r["exp_id"] for r in csv.DictReader(fh)]
    ids = [e["id"] for e in doc["experiments"]]
    assert all(r in ids for r in registered)
    assert all(e["verdict"] and e["status"] for e in doc["experiments"])
    assert "no overall verdict" in next(e for e in doc["experiments"] if e["id"] == "EXP-004")["verdict"]


def test_every_display_string_is_printed_in_the_paper():
    doc = json.loads(COMMITTED.read_text())
    missing = []
    n = 0
    for e in doc["experiments"]:
        for x in e["estimates"]:
            text = MANUSCRIPT if x["printed_in"] == "manuscript" else SUPPLEMENTARY
            assert x["printed_in"] == "manuscript" or x["printed_in"].startswith("supplementary")
            for k in ("display", "interval_display"):
                n += 1
                if x[k] not in text:
                    missing.append((e["id"], x["label"], k, x[k]))
    assert n > 300
    assert missing == []


def test_manuscript_rows_appear_jointly_where_printed_as_one_cell():
    doc = json.loads(COMMITTED.read_text())
    for e in doc["experiments"]:
        if e["id"] not in ("EXP-003", "EXP-005"):
            continue
        for x in e["estimates"]:
            assert f"{x['display']} {x['interval_display']}" in MANUSCRIPT, x["label"]


def test_levels_match_claims_register_and_graph_stats_match_table_2():
    doc = json.loads(COMMITTED.read_text())
    with (REPO / "research" / "claims_register.csv").open() as fh:
        lvl_text = "\n".join(r["text"] for r in csv.DictReader(fh) if "-LVL" in r["claim_id"])
    for key, block in doc["levels"].items():
        for s in block["series"]:
            for p in s["points"]:
                assert f"{p['display']} {p['interval_display']}" in lvl_text, (key, s["topology"], p["param"])
    for g in doc["graph_stats"]["rows"]:
        for k in ("edges", "second_moment", "p_c", "clustering", "giant_fraction"):
            assert g[k] in MANUSCRIPT, (g["topology"], k)


def test_sandbox_fixture_is_reproduced_by_the_python_engine():
    fixture = _load("make_sandbox_fixture")
    committed = (REPO / "demo" / "src" / "fixtures" / "engine_fixture.json").read_text()
    assert fixture.render(fixture.build()) == committed


def test_mulberry32_matches_known_values():
    fixture = _load("make_sandbox_fixture")
    rng = fixture.Mulberry32(1)
    # First draws of the JavaScript mulberry32 with seed 1 (also asserted by the vitest suite).
    got = [rng.random() for _ in range(3)]
    data = json.loads((REPO / "demo" / "src" / "fixtures" / "engine_fixture.json").read_text())
    assert got == data["rng_check"]["first_draws"]


def test_public_texts_use_only_numbers_printed_in_the_manuscript():
    """README, CITATION.cff, the article drafts and the demo README (master prompt 11.6, M5)."""
    import re

    bad = []
    for rel in ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        text = (REPO / rel).read_text()
        for tok in set(re.findall(r"[+-]?\d+\.\d+(?:e-\d+)?", text)):
            if tok not in MANUSCRIPT:
                bad.append((rel, tok))
    assert bad == []
