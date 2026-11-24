<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, rationale, alternatives, consequences.

## D-001 (2026-11-24): Licence is the owner's protective non-commercial licence

- **Decided by:** the owner.
- **Decision:** All original material is licensed under the VIRAL Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-VIRAL-NC-Research-1.0`), with a CLA for contributions. The package (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/workflows/cla.yml`, `.gitignore`) was committed at the first commit.
- **Rationale:** The master prompt (section 2) asks for an "owner-approved permissive code license". On 2026-11-24 the owner instead chose this protective licence, for their own protection.
- **Alternatives:** a permissive licence such as MIT or Apache-2.0, as the prompt suggested; not chosen by the owner.
- **Consequences:** The project is source-available, not OSI open source. Third-party dependencies and data keep their own licences (recorded in `data/manifest.json` and `uv.lock`). Sessions do not modify the licence files.

## D-002 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decided by:** the session, following the M0 brief; open to owner review.
- **Decision:** No TeX distribution is installed (`which tex pdflatex xelatex` found nothing). Canonical sources are Markdown. PDFs are produced by pandoc 3.6.3 (Markdown to Typst) and compiled with the typst 0.15.0 Python package. `research/paper/manuscript.tex` is generated from Markdown with pandoc for venues that need LaTeX source, but it is not compiled locally.
- **Rationale:** Free, local, already installed, no account or service. Section 11.1 allows "an installed equivalent" of TeX Live.
- **Alternatives:** installing TeX Live (several GB, not needed); a hosted LaTeX service (excluded: external service).
- **Consequences:** The LaTeX source is not compile-checked locally; this is recorded in `research/limitations.md`. An exploratory smoke check of the chain was run on 2026-11-24 (see `progress.md`): it failed with the default pandoc Typst template (empty font list) and passed with `-V mainfont="Libertinus Serif"`.

## D-003 (2026-11-24): Synthetic graphs only; no external network dataset in the confirmatory study

- **Decided by:** the session, as a proposal; requires owner confirmation at the protocol freeze.
- **Decision:** All confirmatory experiments use synthetic graphs generated with seeded generators (Erdos-Renyi G(n,M), Watts-Strogatz, Barabasi-Albert). No real network dataset is downloaded or bundled.
- **Rationale:** Section 10 specifies synthetic graphs with matched size and mean degree. The candidate real-network sources checked (SNAP, Netzschleuder) do not state a dataset licence on the pages opened, so redistribution rights are unclear.
- **Consequences:** External validity to real networks is out of scope and listed as a limitation. Any later real-network experiment is a new EXP id and needs the owner to resolve the licence question first.

## D-004 (2026-11-24): Proposed primary design (DRAFT, awaiting owner freeze)

- **Decided by:** proposal by the session; not binding until the owner freezes `research/protocol.md`.
- **Decision:** Primary model independent cascade (IC); primary metric final cascade fraction; baseline Erdos-Renyi G(n,M) with one uniformly random seed; two primary contrasts (Watts-Strogatz minus ER, Barabasi-Albert minus ER), paired by replicate, cluster bootstrap over graph replicates, Holm adjustment. Details in `research/protocol.md`.
- **Rationale:** Final size is the outcome most directly tied to "how far diffusion goes"; ER is the simplest graph with matched size and mean degree and no imposed structure; "content quality" is held fixed by matching the transmission probability across topologies.
- **Alternatives:** depth, time or inequality as primary (kept as secondary); LT as primary (kept as a secondary experiment, EXP-003).
