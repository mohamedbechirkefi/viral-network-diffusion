# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Fail-closed gate: a confirmatory config runs only against a frozen, hash-matched protocol.

A protocol counts as frozen only if (a) its row in research/experiment_registry.csv
carries a 64-hex sha256 in protocol_hash, (b) the file's current sha256 equals it,
and (c) research/protocol.md does not declare itself DRAFT. Freezing is the
owner's decision (G-FREEZE); this module never writes a hash.
"""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_status(repo: Path, experiment_id: str) -> tuple[bool, str]:
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
    return True, "frozen"
