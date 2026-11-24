<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# tests

Run with `uv run --locked pytest`. Files: `test_graphs.py` (generators, invariants, invalid inputs, property tests), `test_engines.py` (hand-computed examples, no-transmission and all-transmission cases, disconnected components, exact reference-versus-vectorised equality, Monte Carlo against exact enumeration, LT checks), `test_metrics_stats.py` (metric and statistics golden values), `test_pipeline.py` (config to validated result to report, schema rejection, protocol gate, CLI refusal of confirmatory configs).
