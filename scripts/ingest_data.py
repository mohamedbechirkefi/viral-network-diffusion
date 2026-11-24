# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Ingest data/raw/maier_fb/*.gml into data/processed/maier_fb.json (git-ignored).

Prints the SHA-256 of the canonical processed file and the schema, missingness and
exclusion counts. It does not compute any calibration quantity (see scripts/fit_calibration.py).

Usage:  .venv/bin/python scripts/ingest_data.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from viral.realdata import ingest_gml, processed_bytes

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw" / "maier_fb" / "bfmaier_anonymized_fb_network.gml"
OUT = REPO / "data" / "processed" / "maier_fb.json"


def main() -> int:
    if not RAW.is_file():
        print(f"ERROR: {RAW} missing; run scripts/download_data.py first", file=sys.stderr)
        return 2
    doc = ingest_gml(RAW.read_text())
    b = processed_bytes(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(b)
    print(json.dumps({"processed_path": str(OUT.relative_to(REPO)), "processed_sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "counts": doc["counts"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
