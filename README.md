<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# VIRAL: network topology, initial exposure and diffusion

**Question.** How do network topology and initial exposure influence diffusion independently of content quality?

**Status: M0 (bootstrap and feasibility), 2026-11-24.** No code, no experiments, no findings yet. The research protocol is a draft awaiting the owner's freeze. Everything planned here is a simulation on synthetic graphs; nothing in this repository is a claim about real social platforms or their algorithms.

## Research navigation

| Item | Location | Status |
|---|---|---|
| Protocol (draft) | [research/protocol.md](research/protocol.md) | DRAFT, not frozen |
| Experiment registry | [research/experiment_registry.csv](research/experiment_registry.csv) | 4 experiments planned |
| Literature review | [research/literature_review.md](research/literature_review.md) | M0 search, not systematic |
| Limitations | [research/limitations.md](research/limitations.md) | design-level only |
| Manuscript | [research/paper/manuscript.md](research/paper/manuscript.md) | headings only |
| Roadmap / progress | [roadmap.md](roadmap.md), [progress.md](progress.md) | |

| Experiment | Purpose | Status |
|---|---|---|
| EXP-001 | Engine verification and smoke matrix (exploratory) | exploratory run (engine checks; not a finding) |
| EXP-002 | Independent cascade: topology x transmission x initial exposure (primary) | planned |
| EXP-003 | Fractional threshold: topology x threshold x initial exposure (secondary) | planned |
| EXP-004 | Sensitivity analyses for EXP-002 | planned |

## Quick start (development environment)

```sh
uv sync --locked --all-groups   # installs the locked dependencies (uv.lock)
uv run --locked viral test       # test suite
uv run --locked viral smoke      # EXP-001 exploratory smoke run with verification checks
uv run --locked viral report results/exploratory/EXP-001/<run_id> --project experiments/EXP-002/config.json
```

`viral run --config <file>` refuses a confirmatory configuration until the owner has frozen its protocol. Every output so far is exploratory and is not a finding.

## Data

Synthetic graphs only, generated from recorded parameters and seeds. No external dataset is used; see [data/manifest.json](data/manifest.json).

## Licence

VIRAL Source-Available Non-Commercial Research License v1.0 (`LicenseRef-VIRAL-NC-Research-1.0`). See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). This is not an OSI-approved open-source licence. Third-party dependencies keep their own licences.

## Citation

See [CITATION.cff](CITATION.cff).
