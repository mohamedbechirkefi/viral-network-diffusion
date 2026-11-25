<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# experiments

Run configurations (schema `src/viral/schemas/config-1.0.0.json`). Protocols and reports live in `research/experiments/EXP-NNN/`.

- `EXP-001/config.json`: exploratory smoke matrix of the EXP-001 protocol.
- `EXP-001/probe-config.json`: exploratory planning probe (full draft grids, 10 replicates).
- `EXP-002/config.json`, `EXP-003/config.json`, `EXP-004/S*-config.json` and `EXP-005/config.json`: confirmatory configurations, frozen at protocol v1.0 on 2026-11-24 with the owner's approval (hashes in `research/freeze.json`). `viral run` refuses any confirmatory config whose hash is not listed there. All were run at M3 (2026-11-25).
