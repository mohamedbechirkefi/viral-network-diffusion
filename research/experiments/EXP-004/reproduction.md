<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-004 reproduction

1. Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest` (174 passed at `32961c3`).
2. Runs, for X in S1, S2, S3, S4-n500, S4-n2000: `.venv/bin/viral run --config experiments/EXP-004/X-config.json --out results/raw/confirmatory/EXP-004`.
3. Analysis, per run: `.venv/bin/python scripts/analyse_confirmatory.py results/raw/confirmatory/EXP-004/<run_id> --plan EXP-004/X-config.json --out results/confirmatory/EXP-004/X/<run_id>`.
4. S1 reading record (pre-decision state, superseded by D-013 for reporting): `.venv/bin/python scripts/analyse_confirmatory.py --s1-reading <EXP-002 analysis.json> <S1 analysis.json> --out <S1 output dir>`.

Raw `result.json` SHA-256 values (git-ignored files):

| analysis | run id | SHA-256 |
|---|---|---|
| S1 | EXP-004-20261124T233447Z-de14a4b3 | `f43d6a7f6bbed45f8de9042e8705d2fcae95044ae795ef0c581189e2457c3e07` |
| S2 | EXP-004-20261124T233637Z-916e8d29 | `c219c59b1ec7d2bffc551be4720ed83ab6e8ecc18fbc3b31681c00f97df9be28` |
| S3 | EXP-004-20261124T233755Z-e1d24091 | `35052d8ef0e0df95f7665641536cdcaab4923f767ded1439e4d9d53b87dc3bd1` |
| S4 N = 500 | EXP-004-20261124T235044Z-e31dba07 | `6e8e0fc33f7e4c9b284d30f7a00d8cb409937f46dcaf851e8bba3cb75221a945` |
| S4 N = 2000 | EXP-004-20261124T235110Z-40385ec3 | `0cb5040b44f742ce8145ae52a0806cb42a3ead4c1ba76380a96766939b173a51` |

Revision `32961c3c399263ff3e39a9dbd3f78be3ff934922`. Committed output hashes are in `results/confirmatory/MANIFEST.sha256`. Exact equality is expected on the same platform and package versions.
