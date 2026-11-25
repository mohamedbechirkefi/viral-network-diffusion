<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# EXP-001 reproduction (EXPLORATORY)

1. Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`, then `.venv/bin/python -m pytest` (174 passed at revision `32961c3`).
2. Smoke run: `.venv/bin/viral smoke --config experiments/EXP-001/config.json` (about 3.5 s). Expect 15 graphs, 5,250 cascades checked, 0 failures.
3. Planning probe: `.venv/bin/viral run --config experiments/EXP-001/probe-config.json` (about 115 s).
4. Metric validation: `.venv/bin/python scripts/validate_metrics.py <smoke run dir> <out json>`. Expect 54 checks with 0 failures.
5. Descriptive report: `.venv/bin/viral report <run dir>`.

Committed outputs:
- `results/exploratory/EXP-001/EXP-001-20261124T162117Z-99c548ac/` (M2 smoke)
- `results/exploratory/EXP-001/EXP-001-20261124T162121Z-d947f41d/` (probe; raw `result.json` git-ignored, SHA-256 in `result.json.sha256`)
- `results/exploratory/EXP-001/EXP-001-20261124T233106Z-99c548ac/` (M3 smoke; `result.json` SHA-256 `d299dfac6f1c89da48d7138c9fd8f125fb7e4547283fb672ad724f0e08630b36`; `metric_validation.json`)

Seeded streams make reruns on the same platform and package versions identical. All runs use the pilot seed 20261124, which is disjoint from every confirmatory seed.
