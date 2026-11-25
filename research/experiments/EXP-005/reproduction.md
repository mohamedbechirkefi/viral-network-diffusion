<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-005 reproduction

1. Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest` (174 passed at `32961c3`).
2. Data (git-ignored, never committed):
   - `.venv/bin/python scripts/download_data.py`. Expect GML SHA-256 `cb94e2c6a02c4f8457730418fd4413d5abb75783f65c02b990eb1dade4a41aaa`.
   - `.venv/bin/python scripts/ingest_data.py`. Expect processed SHA-256 `e286957db7367d10bf401217116787ee4a7ccef0fd6a70ebbcb20e427fc529cc`.
   - `.venv/bin/python scripts/fit_calibration.py`. Expect `p_c = 0.0483851339839852`.
3. Run: `.venv/bin/viral run --config experiments/EXP-005/config.json --out results/raw/confirmatory/EXP-005`. Config file SHA-256 `06b507e45eef7d299a6579e98038aae7e69d76d4f368eaed9b5f51ebeb20f758`. The original run took 138.3 s.
4. Analysis: `.venv/bin/python scripts/analyse_confirmatory.py results/raw/confirmatory/EXP-005/<run_id> --plan EXP-005/config.json --out results/confirmatory/EXP-005/<run_id>`.

Original run `EXP-005-20261124T233932Z-d277f271`, revision `32961c3c399263ff3e39a9dbd3f78be3ff934922`.
- Raw `result.json` SHA-256: `cca5abd4e84d9d670d23e035479e3ee640a59bf5f6fc3d71b2ac377c563f055e`.
- Committed output hashes: `results/confirmatory/MANIFEST.sha256`.

Exact equality is expected on the same platform and package versions.
