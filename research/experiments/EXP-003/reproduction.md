<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-003 reproduction

1. Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest` (174 passed at `32961c3`).
2. Run: `.venv/bin/viral run --config experiments/EXP-003/config.json --out results/raw/confirmatory/EXP-003`. Config file SHA-256 `728f9a31435777ffce283aa282ab8ee1c45eb5ef93b0bf865ff12012a4a6b659`. The original run took 502.4 s.
3. Analysis: `.venv/bin/python scripts/analyse_confirmatory.py results/raw/confirmatory/EXP-003/<run_id> --plan EXP-003/config.json --out results/confirmatory/EXP-003/<run_id>`.
4. Descriptive tables: `.venv/bin/viral report <raw run dir>`.

Original run `EXP-003-20261124T234212Z-a2d668ab`, revision `32961c3c399263ff3e39a9dbd3f78be3ff934922`.
- Raw `result.json` SHA-256: `3f9b6c0b74a86c3f08c5d0538dd93e4b3cc30c5b57aceec4808a92a82e1a5778` (git-ignored).
- Committed output hashes: `sha256_manifest.json` in the output folder and `results/confirmatory/MANIFEST.sha256`.

Exact equality is expected on the same platform and package versions.
