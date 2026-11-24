# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Fail-closed gate: a confirmatory config runs only against a frozen, hash-matched protocol.

A protocol counts as frozen only if (a) its row in research/experiment_registry.csv
carries a 64-hex sha256 in protocol_hash, (b) the file's current sha256 equals it,
(c) research/protocol.md does not declare itself DRAFT, and (d) the freeze record
research/freeze.json lists the same hashes for research/protocol.md, the experiment
protocol and data/manifest.json. A config is accepted only if (e) its file sha256
is one of the configs the freeze record lists for that experiment. Freezing is the
owner's decision (G-FREEZE); this module never writes a hash.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


FREEZE_RECORD = Path("research") / "freeze.json"


def _freeze_record_check(repo: Path, experiment_id: str, config_path: Path | None) -> tuple[bool, str]:
    rec_path = repo / FREEZE_RECORD
    if not rec_path.is_file():
        return False, "freeze record research/freeze.json not found"
    try:
        rec = json.loads(rec_path.read_text())
    except json.JSONDecodeError:
        return False, "freeze record is not valid JSON"
    study = rec.get("study_protocol", {})
    parent = repo / study.get("path", "research/protocol.md")
    if not parent.is_file() or sha256_file(parent) != study.get("sha256"):
        return False, "research/protocol.md differs from the hash in the freeze record; treat as amended"
    data = rec.get("data_manifest")
    if data is not None:
        dpath = repo / data.get("path", "data/manifest.json")
        if not dpath.is_file() or sha256_file(dpath) != data.get("sha256"):
            return False, "data/manifest.json differs from the hash in the freeze record; treat as amended"
    exp = rec.get("experiments", {}).get(experiment_id)
    if exp is None:
        return False, f"{experiment_id} is not in the freeze record"
    proto = repo / exp.get("protocol_path", "")
    if not proto.is_file() or sha256_file(proto) != exp.get("protocol_sha256"):
        return False, f"{experiment_id} protocol differs from the freeze record"
    if config_path is not None:
        cfg_hash = sha256_file(Path(config_path))
        if cfg_hash not in {c.get("file_sha256") for c in exp.get("configs", [])}:
            return False, f"config sha256 {cfg_hash[:12]} is not a frozen {experiment_id} config (changed or never frozen)"
    return True, "frozen"


def frozen_status(repo: Path, experiment_id: str, config_path: Path | None = None) -> tuple[bool, str]:
    repo = Path(repo)
    registry = repo / "research" / "experiment_registry.csv"
    if not registry.is_file():
        return False, "experiment registry not found"
    with registry.open(newline="") as fh:
        rows = {row["exp_id"]: row for row in csv.DictReader(fh)}
    row = rows.get(experiment_id)
    if row is None:
        return False, f"{experiment_id} is not registered"
    recorded = (row.get("protocol_hash") or "").strip().lower()
    if not HEX64.match(recorded):
        return False, f"{experiment_id} protocol has no recorded hash ({row.get('protocol_hash')!r}); not frozen"
    proto = repo / row["protocol_path"]
    if not proto.is_file():
        return False, f"protocol file missing: {row['protocol_path']}"
    actual = sha256_file(proto)
    if actual != recorded:
        return False, f"protocol hash mismatch (recorded {recorded[:12]}, actual {actual[:12]}); treat as amended"
    parent = repo / "research" / "protocol.md"
    if parent.is_file() and re.search(r"Status:\s*DRAFT", parent.read_text()):
        return False, "research/protocol.md is marked DRAFT"
    return _freeze_record_check(repo, experiment_id, config_path)
