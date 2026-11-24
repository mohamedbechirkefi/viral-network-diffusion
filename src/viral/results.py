# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Result documents: assembly, schema validation at export and import, run manifests."""

from __future__ import annotations

import json
import platform
import resource
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import jsonschema

from . import RESULT_SCHEMA_VERSION, __version__
from .config import ExperimentConfig, _schema


class ResultError(ValueError):
    """Raised for a malformed or missing result document."""


def _git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=10, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def cpu_description() -> str:
    if sys.platform == "darwin":
        try:
            brand = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            ncpu = subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            return f"{brand}, {ncpu} logical CPUs"
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or platform.machine()


def peak_rss_bytes() -> int | None:
    """Process peak resident set size (ru_maxrss is bytes on macOS, KiB on Linux)."""
    try:
        v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(v if sys.platform == "darwin" else v * 1024)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_run_id(experiment_id: str, started_utc: str, cfg_hash: str) -> str:
    stamp = started_utc.replace("-", "").replace(":", "")
    return f"{experiment_id}-{stamp}-{cfg_hash[:8]}"


def build_manifest(cfg: ExperimentConfig, repo: Path, started_utc: str, finished_utc: str, runtime_s: float) -> dict:
    rev = _git(repo, "rev-parse", "HEAD")
    status = _git(repo, "status", "--porcelain", "--", ".", ":(exclude)results")
    return {
        "run_id": make_run_id(cfg.experiment_id, started_utc, cfg.hash),
        "experiment_id": cfg.experiment_id,
        "mode": cfg.mode,
        "label": cfg.label,
        "config_hash": cfg.hash,
        "master_seed": cfg.master_seed,
        "engine": cfg.engine,
        "git_revision": rev or "unknown",
        "git_dirty": None if status is None else bool(status),
        "versions": {
            "python": platform.python_version(),
            "numpy": metadata.version("numpy"),
            "networkx": metadata.version("networkx"),
            "jsonschema": metadata.version("jsonschema"),
            "viral": __version__,
        },
        "os": platform.platform(),
        "cpu": cpu_description(),
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "runtime_seconds": runtime_s,
        "peak_rss_bytes": peak_rss_bytes(),
        "peak_memory_note": "process peak RSS from getrusage; includes interpreter and imports",
        "git_dirty_scope": "working tree excluding results/",
    }


def assemble(cfg: ExperimentConfig, run: dict, manifest: dict) -> dict:
    return {
        "result_schema_version": RESULT_SCHEMA_VERSION,
        "kind": "viral.result",
        "experiment_id": cfg.experiment_id,
        "run_id": manifest["run_id"],
        "mode": cfg.mode,
        "label": cfg.label,
        "config": cfg.raw,
        "config_hash": cfg.hash,
        "manifest": manifest,
        "graphs": run["graphs"],
        "cells": run["cells"],
        "failures": run["failures"],
        "verification": run["verification"],
    }


def validate_result(doc: dict) -> dict:
    try:
        jsonschema.validate(doc, _schema("result-1.0.0.json"))
    except jsonschema.ValidationError as exc:
        raise ResultError(f"invalid result: {exc.message} at {list(exc.absolute_path)}") from exc
    for cell in doc["cells"]:
        for k, v in cell["per_cascade"].items():
            if len(v) != cell["n_cascades"]:
                raise ResultError(f"cell has {len(v)} values of {k} for {cell['n_cascades']} cascades")
    return doc


def write_result(doc: dict, out_dir: Path) -> Path:
    """Validate, then write result.json and run_manifest.json into out_dir/run_id/."""
    validate_result(doc)
    run_dir = Path(out_dir) / doc["run_id"]
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "result.json").write_text(json.dumps(doc, indent=1) + "\n")
    (run_dir / "run_manifest.json").write_text(json.dumps(doc["manifest"], indent=2) + "\n")
    return run_dir


def load_result(path: str | Path) -> dict:
    p = Path(path)
    if p.is_dir():
        p = p / "result.json"
    if not p.is_file():
        raise ResultError(f"result not found: {p}")
    try:
        doc = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise ResultError(f"result is not valid JSON: {exc}") from exc
    return validate_result(doc)
