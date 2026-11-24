<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# src

Python package `viral` (M2). Modules are separated by role:

| Module | Role |
|---|---|
| `graphs.py` | CSR graph type, seeded generators (ER, WS, BA), invariants, EXP-004 helpers |
| `engines.py` | IC and fractional-threshold engines, reference and vectorised |
| `seeding.py` | seed-set selection rules |
| `metrics.py` | S, D, T, T50, Gini, large-cascade share, structural virality |
| `stats.py` | paired cluster bootstrap, Holm, variance decomposition, replicate sizing |
| `verification.py` | EXP-001 pass/fail checks |
| `config.py` | config schema validation, hashing, random streams |
| `runner.py` | experiment runner (no I/O) |
| `results.py` | result schema validation, serialisation, run manifests |
| `protocol_gate.py` | refuses confirmatory runs before the owner's freeze |
| `analysis.py`, `report.py` | tables, figures and reports from result files |
| `cli.py` | `viral smoke`, `run`, `report`, `test` |
| `schemas/` | versioned JSON schemas (config 1.0.0, result 1.0.0) |
