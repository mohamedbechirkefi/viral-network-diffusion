<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Raw result location (EXPLORATORY)

`result.json` of this run is 14 MB and is kept out of git in `results/raw/exploratory/EXP-001/EXP-001-20261124T162121Z-d947f41d/` (`results/raw/` is ignored). Its SHA-256 is in `result.json.sha256`.

Regenerate it with `uv run --locked viral run --config experiments/EXP-001/probe-config.json` at the git revision in `run_manifest.json`. Per-cascade outputs are deterministic given the config (verified for the smoke config on 2026-11-24: a rerun gave identical per-cascade outputs and graph statistics); timings differ between runs.
