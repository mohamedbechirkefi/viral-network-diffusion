# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Run the frozen confirmatory analysis of one result file and write tables, figures and a SHA-256 manifest.

Usage:
  .venv/bin/python scripts/analyse_confirmatory.py RESULT_DIR --plan EXP-002/config.json --out OUT_DIR
  .venv/bin/python scripts/analyse_confirmatory.py --s1-reading EXP002_ANALYSIS_JSON S1_ANALYSIS_JSON --out OUT_DIR

The plan key names the frozen config the result was produced from (viral.confirmatory.PLANS); the script
refuses a result whose config hash differs from that config file's canonical hash. Every number written is
computed from result.json; figures are generated from the same tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

from viral.config import load_config
from viral.confirmatory import PLANS, SESOI, run_plan, s1_reading
from viral.results import load_result

REPO = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    for r in rows:
        keys += [k for k in r if k not in keys]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (";".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})


def figures(out: dict, doc: dict, fig_dir: Path, exp: str) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    made = []
    prim = out["primary"]
    contrasts = sorted({r["contrast"] for r in prim}, key=lambda c: [r["contrast"] for r in prim].index(c))
    fig, ax = plt.subplots(figsize=(7.5, 0.45 * len(prim) + 1.5))
    labels, y = [], 0
    for ci, c in enumerate(contrasts):
        for r in [r for r in prim if r["contrast"] == c]:
            col = "C0" if r["reject"] else "C7"
            ax.errorbar(r["mean"], y, xerr=[[r["mean"] - r["lo"]], [r["hi"] - r["mean"]]], fmt="o", color=col, capsize=3)
            labels.append(f"{c} @ {r['param'] if isinstance(r['param'], str) else format(r['param'], 'g')}")
            y += 1
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(-SESOI, SESOI, color="C2", alpha=0.15, label=f"SESOI [-{SESOI}, {SESOI}]")
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("paired difference in per-graph mean final cascade fraction S")
    ax.set_title(f"{exp} primary family: estimate and Holm-adjusted interval\n(blue: Holm rejects; grey: not rejected)", fontsize=9)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(fig_dir / f"fig_primary_contrasts.{ext}", dpi=150)
    plt.close(fig)
    made.append("fig_primary_contrasts")

    plan = out["plan"]
    tm = [r for r in out["topology_means"] if r["model"] == plan["model"] and r["seed_rule"] == plan["rule"] and r["seed_count"] == plan["count"]]
    topos = sorted({r["topology"] for r in tm})
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, t in enumerate(topos):
        rs = sorted([r for r in tm if r["topology"] == t], key=lambda r: r["param"])
        xs = [r["param"] for r in rs]
        ax.errorbar(xs, [r["mean_S"] for r in rs], yerr=[[r["mean_S"] - r["lo95"] for r in rs], [r["hi95"] - r["mean_S"] for r in rs]],
                    marker="o", ms=4, capsize=3, label=f"{t} (R = {rs[0]['replicates']})")
    ax.set_xlabel("p (IC transmission probability)" if plan["model"] == "ic" else "phi (LT threshold)")
    if exp.startswith("EXP-004 S1"):
        ax.set_xlabel("multiplier c (p = c p_c(G))")
    ax.set_ylabel("mean final cascade fraction S")
    ax.set_title(f"{exp}: mean S by topology ({plan['rule']} rule, {plan['count']} seed(s));\nunadjusted 95% bootstrap interval over graph replicates", fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(fig_dir / f"fig_mean_S_by_param.{ext}", dpi=150)
    plt.close(fig)
    made.append("fig_mean_S_by_param")
    return made


def analyse(result_dir: Path, plan_key: str, out_dir: Path) -> int:
    plan = PLANS[plan_key]
    cfg = load_config(REPO / "experiments" / plan_key)
    doc = load_result(result_dir)
    if doc["config_hash"] != cfg.hash:
        print(f"REFUSED: result config hash {doc['config_hash'][:12]} differs from experiments/{plan_key} ({cfg.hash[:12]})", file=sys.stderr)
        return 3
    if doc["mode"] != "confirmatory":
        print("REFUSED: not a confirmatory result", file=sys.stderr)
        return 3
    out = run_plan(doc, plan)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "figures").mkdir(exist_ok=True)
    write_csv(out["primary"], out_dir / "primary_contrasts.csv")
    write_csv(out["secondary"], out_dir / "secondary_contrasts.csv")
    write_csv(out["topology_means"], out_dir / "topology_means.csv")
    exp = doc["experiment_id"] + ("" if doc["experiment_id"] != "EXP-004" else " " + Path(plan_key).name.split("-config")[0])
    figs = figures(out, doc, out_dir / "figures", exp)
    n_casc = sum(c["n_cascades"] for c in doc["cells"])
    summary = {
        "kind": "viral.confirmatory_analysis", "experiment": exp, "plan_key": plan_key, "plan": plan,
        "run_id": doc["run_id"], "config_hash": doc["config_hash"], "git_revision": doc["manifest"]["git_revision"],
        "git_dirty": doc["manifest"]["git_dirty"], "result_json_sha256": sha256(Path(result_dir) / "result.json"),
        "graphs": len(doc["graphs"]), "cells": len(doc["cells"]), "cascades": n_casc,
        "verification": doc["verification"], "failures": len(doc["failures"]),
        "generator": "scripts/analyse_confirmatory.py (viral.confirmatory)",
        "primary": out["primary"],
        "n_rejected": sum(r["reject"] for r in out["primary"]), "n_tests": len(out["primary"]),
        "n_equivalent": sum(r["equivalent_within_sesoi"] for r in out["primary"]),
        "figures": [f"figures/{s}.png" for s in figs],
    }
    (out_dir / "analysis.json").write_text(json.dumps(summary, indent=1) + "\n")
    files = sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "sha256_manifest.json")
    manifest = {"result_json": {"path": str(Path(result_dir) / "result.json"), "sha256": summary["result_json_sha256"]},
                "run_manifest": {"path": str(Path(result_dir) / "run_manifest.json"), "sha256": sha256(Path(result_dir) / "run_manifest.json")},
                "outputs": {str(p.relative_to(out_dir)): sha256(p) for p in files}}
    (out_dir / "sha256_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{exp}: {summary['n_rejected']} of {summary['n_tests']} rejected; {summary['n_equivalent']} equivalent within SESOI; written to {out_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path, nargs="?")
    ap.add_argument("--plan")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--s1-reading", nargs=2, type=Path, metavar=("EXP002_JSON", "S1_JSON"))
    a = ap.parse_args(argv)
    if a.s1_reading:
        e2, s1 = (json.loads(p.read_text()) for p in a.s1_reading)
        res = s1_reading(e2["primary"], s1["primary"])
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "s1_reading.json").write_text(json.dumps(res, indent=1) + "\n")
        print(res["verdict"])
        return 0
    if a.result is None or a.plan not in PLANS:
        ap.error(f"give RESULT_DIR and --plan in {sorted(PLANS)}")
    return analyse(a.result, a.plan, a.out)


if __name__ == "__main__":
    sys.exit(main())
