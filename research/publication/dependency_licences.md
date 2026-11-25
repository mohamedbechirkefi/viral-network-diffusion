<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Sources: Python licences from the installed `.venv` package metadata (`License-Expression`, else the `License ::` classifiers); npm licences from `demo/node_modules/*/package.json`, with the runtime or development role from `demo/package-lock.json`. Permissive list used for flags: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0 and similarly permissive licences.

**Flags: none.** Every installed dependency is under a permissive licence. Notes on licences outside the strict list: `pillow` (MIT-CMU, a permissive historical licence), `numpy` (bundled code under 0BSD, Zlib and CC0-1.0, all permissive), `hypothesis` and `lightningcss` (MPL-2.0, file-level copyleft; development and build tools only, not distributed). The build tool pandoc is GPL-2.0-or-later; it is run locally to convert Markdown and is not distributed or linked.

## Python (`uv.lock`, environment synced with `--all-groups --all-extras`)

| package | version | licence | role |
|---|---|---|---|
| networkx | 3.7 | BSD-3-Clause | runtime |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime |
| jsonschema | 4.26.0 | MIT | runtime |
| attrs | 26.1.0 | MIT | runtime (via jsonschema) |
| jsonschema-specifications | 2025.9.1 | MIT | runtime (via jsonschema) |
| referencing | 0.37.0 | MIT | runtime (via jsonschema) |
| rpds-py | 2026.9.1 | MIT | runtime (via jsonschema) |
| typing_extensions | 4.16.0 | PSF-2.0 | runtime (via referencing) |
| matplotlib | 3.11.2 | Python Software Foundation License (matplotlib licence, PSF-based) | figures group |
| contourpy | 1.4.0 | BSD-3-Clause | figures group |
| cycler | 0.12.1 | BSD | figures group |
| fonttools | 4.68.0 | MIT | figures group |
| kiwisolver | 1.5.1 | BSD | figures group |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | figures and dev groups |
| pillow | 13.0.0 | MIT-CMU | figures group |
| pyparsing | 3.3.3 | MIT | figures group |
| python-dateutil | 4.0.0 | BSD-3-Clause | figures group |
| tzdata | 2026.6 | Apache-2.0 | figures group |
| pytest | 9.2.0 | MIT | dev group |
| hypothesis | 6.170.15 | MPL-2.0 | dev group |
| iniconfig | 2.3.1 | MIT | dev group |
| pluggy | 1.7.0 | MIT | dev group |
| Pygments | 2.21.0 | BSD-2-Clause | dev group |
| sortedcontainers | 2.4.0 | Apache-2.0 | dev group |
| viral | 0.1.0 | LicenseRef-VIRAL-NC-Research-1.0 (this project; no licence field in its metadata) | project |

## npm (`demo/package-lock.json`, 84 entries)

Runtime (shipped in the built page): react 19.3.1 (MIT), react-dom 19.3.1 (MIT), scheduler 0.28.0 (MIT).

Development and build (not shipped):

| licence | packages (version) |
|---|---|
| MIT | @jridgewell/sourcemap-codec 1.6.0, @oxc-project/types 0.156.0, @rolldown/binding-darwin-arm64 1.2.19, @rolldown/pluginutils 1.1.1, @standard-schema/spec 1.1.0, @types/chai 5.2.3, @types/deep-eql 4.0.2, @types/estree 1.0.11, @types/react 19.3.0, @types/react-dom 19.3.0, @vitejs/plugin-react 6.1.2, @vitest/expect, mocker, pretty-format, runner, snapshot, spy and utils 4.1.12, assertion-error 2.0.1, chai 6.3.0, convert-source-map 2.0.0, csstype 3.2.4, es-module-lexer 2.3.2, estree-walker 3.0.3, fdir 6.5.0, fsevents 2.3.3, magic-string 0.30.21, nanoid 3.3.20, obug 2.2.1, pathe 2.0.3, picomatch 4.0.7, postcss 8.5.33, rolldown 1.2.19, stackback 0.0.2, std-env 4.3.0, tinybench 2.9.0, tinyexec 1.4.0, tinyglobby 0.2.17, tinyrainbow 3.2.0, vite 8.3.5, vitest 4.1.12, why-is-node-running 2.3.0 |
| Apache-2.0 | detect-libc 2.1.2, expect-type 1.4.0, typescript 5.9.3 |
| ISC | picocolors 1.1.1, siginfo 2.0.0 |
| BSD-3-Clause | source-map-js 1.2.4 |
| MPL-2.0 | lightningcss 1.33.0, lightningcss-darwin-arm64 1.33.0 |

The other 31 lockfile entries (84 minus the 53 installed) are optional platform binaries (other operating systems and architectures of rolldown and lightningcss, and the WebAssembly helpers @emnapi, @napi-rs, @tybys and tslib) that are not installed on this machine, so their `package.json` was not read.

## Build tools and fonts (local, not distributed with the code)

| tool | version | licence |
|---|---|---|
| uv | 0.9.5 | MIT OR Apache-2.0 |
| pandoc | 3.6.3 | GPL-2.0-or-later (used as a program; output is not a derivative of pandoc) |
| typst (Python package) | 0.15.0 | Apache-2.0 |
| pypdf | 6.20.0 | BSD-3-Clause |
| Node.js | 22.23.3 | MIT |
| Libertinus Serif (embedded in the PDFs) | bundled with typst | SIL Open Font License 1.1 (embedding permitted) |
| DejaVu Sans Mono (embedded in the PDFs) | bundled with typst | Bitstream Vera licence and public domain parts (embedding permitted) |

The licences of uv, pandoc, Node.js and the two fonts are stated from their published licence terms, not from installed metadata (the installed binaries carry no machine-readable licence field); they are labelled here as not verified in this session.
