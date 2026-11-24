# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Command-line interface: smoke, run, report, test.

  viral smoke  [--config experiments/EXP-001/config.json]
  viral run    --config PATH            (refuses a confirmatory config unless its protocol is frozen)
  viral report RESULT_DIR [--project CONFIG] [--pdf]
  viral test   [pytest args...]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from .config import ConfigError, load_config
from .protocol_gate import frozen_status
from .report import build_report
from .results import ResultError, assemble, build_manifest, utc_now, write_result
from .runner import run_experiment

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SMOKE = REPO / "experiments" / "EXP-001" / "config.json"


def _execute(config_path: Path, out_root: Path | None, quiet: bool) -> int:
    cfg = load_config(config_path)
    if cfg.mode == "confirmatory":
        ok, why = frozen_status(REPO, cfg.experiment_id)
        if not ok:
            print(f"REFUSED: {cfg.experiment_id} config is confirmatory but its protocol is not frozen: {why}.", file=sys.stderr)
            print("Freezing is the owner's decision (G-FREEZE). Use an exploratory config instead.", file=sys.stderr)
            return 3
        default_root = REPO / "results" / "confirmatory" / cfg.experiment_id
    else:
        default_root = REPO / "results" / "exploratory" / cfg.experiment_id
    started = utc_now()
    t0 = time.perf_counter()
    run = run_experiment(cfg, progress=None if quiet else (lambda s: print(s, flush=True)))
    runtime = time.perf_counter() - t0
    manifest = build_manifest(cfg, REPO, started, utc_now(), runtime)
    doc = assemble(cfg, run, manifest)
    run_dir = write_result(doc, out_root or default_root)
    v = doc["verification"]
    print(f"run {doc['run_id']} ({cfg.mode}) written to {run_dir}")
    print(f"runtime {runtime:.2f} s; graphs {v['graphs_checked']} (failures {v['graph_failures']}); cascades checked {v['cascades_checked']} (failures {v['cascade_failures']})")
    return 1 if (v["graph_failures"] or v["cascade_failures"]) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="viral", description="VIRAL diffusion simulations (all outputs are simulations).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="run the exploratory EXP-001 smoke config with verification checks")
    s.add_argument("--config", type=Path, default=DEFAULT_SMOKE)
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--quiet", action="store_true")
    r = sub.add_parser("run", help="run a config (confirmatory configs require a frozen protocol)")
    r.add_argument("--config", type=Path, required=True)
    r.add_argument("--out", type=Path, default=None)
    r.add_argument("--quiet", action="store_true")
    p = sub.add_parser("report", help="build report.md, tables and figures from a result directory")
    p.add_argument("result", type=Path)
    p.add_argument("--project", type=Path, default=None, help="config whose full-matrix runtime to project")
    p.add_argument("--pdf", action="store_true")
    t = sub.add_parser("test", help="run the test suite")
    t.add_argument("pytest_args", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "smoke":
            cfg = load_config(a.config)
            if cfg.mode != "exploratory":
                print("REFUSED: smoke only runs exploratory configs.", file=sys.stderr)
                return 3
            return _execute(a.config, a.out, a.quiet)
        if a.cmd == "run":
            return _execute(a.config, a.out, a.quiet)
        if a.cmd == "report":
            proj = load_config(a.project) if a.project else None
            path = build_report(a.result, project=proj, pdf=a.pdf)
            print(f"report written to {path}")
            return 0
        if a.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", *a.pytest_args], cwd=REPO)
    except (ConfigError, ResultError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
