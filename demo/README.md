<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# demo: VIRAL interactive page (M5)

A static page in TypeScript, React and Vite, built from the shared lab template (`labs/_shared/demo-template/`, pinned versions, `package-lock.json`). It has no runtime service, sends no request to any other host, collects nothing about visitors and works offline after the first load.

## What it shows

- **Overview** with the status label: simulation study, protocol v1.0 frozen 2026-11-24, manuscript version 0.2 (not peer-reviewed).
- **Published results** (labelled "measured"): every registered experiment, EXP-001 to EXP-005, and the exploratory M4 checks, each with its status, its verdict under the frozen rule and its claim ids. Every estimate is shown with its interval and interval level, as printed in the manuscript or its supplementary tables; null, negligible and not-rejected contrasts are drawn with the same weight as rejected ones. EXP-004 S1 is shown per multiplier, with no overall verdict (owner decision D-013).
- **The project's visual**: mean final cascade fraction by `p` or `phi` per topology with interval bands (EXP-002, EXP-003, EXP-005), and forest plots of the paired contrasts against the SESOI band; each chart has a plain-language description and a table.
- **Assumptions** (labelled "assumption") and **method and limitations**.
- **Sandbox** (labelled "sandbox output"): animated network cascades, seed controls and distribution plots, computed in a Web Worker from the visitor's settings (model, `p` or `phi`, seed rule and count, N, cascades, random seed; run, cancel, reset, save as JSON). Animation is off when the system asks for reduced motion and can be toggled.

## Sandbox fidelity

The IC and fractional-threshold rules in `src/engine.ts` are line-by-line ports of `viral.engines.ic_reference` and `lt_reference`. `src/engine.test.ts` runs them on graphs from the research generators and compares them with a fixture written by the Python engine (`scripts/make_sandbox_fixture.py`, driven by the same mulberry32 stream): tolerance zero for every activation round, parent, generation and size, and 1e-12 relative for the threshold estimate. The sandbox graphs, however, are generated in the browser by reimplementations of the same three models (not byte-identical to networkx), at N of at most 400 and with at most 1000 cascades. Sandbox numbers are therefore not the published numbers and are never mixed with them.

## Commands

Node 22 (`../../helix/.tools/node/bin` relative to the repository root, on the development machine).

```sh
npm ci && npm run build && npm run preview   # quick start
npm test                                      # vitest: results validation and engine port
node tools/a11y_check.mjs dist --screenshots <dir>   # offline and accessibility check
```

The data file `public/data/results.json` is written by `../scripts/export_demo_data.py` from committed results only; `../tests/test_demo_export.py` checks that it is up to date and that every displayed number is printed verbatim in the manuscript or its supplementary tables. The loader fails closed: a missing or malformed field shows an error panel and no numbers.

## Design and brand

The page has its own identity (owner request of 2026-11-26), planned in `DESIGN.md`: a field epidemiology map sheet, Archivo for map lettering and Newsreader for reading. The hero is a labelled illustration (one cascade on each of three 56-node graphs, drawn with the sandbox's own generators and cascade rule), not study data. Brand files are in `public/brand/`: `mark.svg`, `mark-mono.svg`, `mark-dark.svg`, `lockup.svg`, `lockup-mono.svg`, `lockup-dark.svg`, `favicon.svg`, `favicon-32.png` and the Open Graph image `og.png` (1200 by 630). The wordmark is Archivo (weight 760, width 78) converted to outlines.

## Third-party notes

| Component | Version | Licence | Use |
| --- | --- | --- | --- |
| Archivo (`@fontsource-variable/archivo`) | 5.3.0 | SIL Open Font License 1.1 | Display and interface face, wordmark outlines; latin weight and width file only |
| Newsreader (`@fontsource-variable/newsreader`) | 5.3.0 | SIL Open Font License 1.1 | Reading face; latin weight file only |

Both are installed from npm with exact versions (resolved with `npm_config_before=2026-11-12`), bundled into `dist/` and served from the page's own origin.

Demo: <https://viral-network-diffusion.kefimohamedbechir.workers.dev>. The built page (`dist/`) is hosted as Cloudflare Workers static assets on the free plan, configured by `wrangler.jsonc` (assets only, no Worker script). It is deployed by the lab coordinator, not by any script of this repository.

Author: Mohamed Bechir Kefi, independent researcher.
