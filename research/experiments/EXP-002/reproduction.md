<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-002 reproduction

1. Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`, then `.venv/bin/python -m pytest` (174 passed at `32961c3`).
2. Data: synthetic only. Generators and parameters are in `data/manifest.json`, SHA-256 `ffb8eaf7b0d0beb556649e4bbc64ee9f16de43f5eb66ff8ea81d5ec8f5e2af23`.
3. Run through the freeze guard: `.venv/bin/viral run --config experiments/EXP-002/config.json --out results/raw/confirmatory/EXP-002`. Config file SHA-256 `3a1cd795beb86e3f132f56cacb4b3ff63a08bc94848c27a5bba616cee9954ac8`. The original run took 1047.8 s on an Apple M1 Pro.
4. Frozen analysis and figures: `.venv/bin/python scripts/analyse_confirmatory.py results/raw/confirmatory/EXP-002/<run_id> --plan EXP-002/config.json --out results/confirmatory/EXP-002/<run_id>`.
5. Descriptive tables: `.venv/bin/viral report results/raw/confirmatory/EXP-002/<run_id>`. Copy `tables/{graphs,cells,variance,degenerate}.csv`.
6. Claims and artifact manifest: `.venv/bin/python scripts/build_records.py`.

Original run `EXP-002-20261124T233447Z-2c7febb6`, revision `32961c3c399263ff3e39a9dbd3f78be3ff934922`.
- Raw `result.json` SHA-256: `f6b8e03e0697e228988f01ff7130a0c9c8cafcc86fac26b43a8dac071a44af94`.
- Committed outputs and their hashes: `results/confirmatory/EXP-002/EXP-002-20261124T233447Z-2c7febb6/sha256_manifest.json` and `results/confirmatory/MANIFEST.sha256`.

Expected tolerance: exact equality on the same platform and package versions (seeded streams). On other platforms, small floating-point differences are possible in derived statistics.
