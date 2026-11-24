# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""EXP-005 calibration (research/protocol.md section 11.5), EXPLORATORY journal entry.

Computes p_c(G_real) = <k> / (<k^2> - <k>) on the processed real network and the EXP-005
transmission grid p_j = round(c_j p_c, 6), capped at 1, with c_j = 6 p_j(EXP-002).
Uses the degree sequence only: no diffusion is simulated and no EXP-002 output is read.
Writes aggregate statistics only (no row-level data) to data/real_network_calibration.json.

Usage:  .venv/bin/python scripts/fit_calibration.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from viral.realdata import summary

REPO = Path(__file__).resolve().parents[1]
PROCESSED = REPO / "data" / "processed" / "maier_fb.json"
OUT = REPO / "data" / "real_network_calibration.json"
EXP002_P = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
MULTIPLIERS = [round(6 * p, 6) for p in EXP002_P]


def main() -> int:
    b = PROCESSED.read_bytes()
    stats = summary(json.loads(b))
    p_c = stats["p_c"]
    grid = [min(1.0, round(c * p_c, 6)) for c in MULTIPLIERS]
    out = {
        "label": "EXPLORATORY calibration fit (research/protocol.md section 11.5); degree sequence only, no diffusion outcome",
        "dataset": "maier_fb",
        "processed_sha256": hashlib.sha256(b).hexdigest(),
        "method": "p_c = <k> / (<k^2> - <k>) over all nodes (viral.graphs.percolation_threshold); p_j = min(1, round(c_j p_c, 6))",
        "aggregate_statistics": stats,
        "fitted": {"p_c": p_c, "multipliers": MULTIPLIERS, "exp005_p_grid": grid},
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
