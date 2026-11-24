<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Contributing to VIRAL

VIRAL is an independent, source-available research project maintained by Mohamed Bechir Kefi: network diffusion.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the VIRAL Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the VIRAL CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

- Install the locked environment: `uv sync --locked` (uv 0.9.5 or later).
- Refresh the lockfile after a reviewed dependency change: `uv lock`.
- Generate the manuscript LaTeX source: `pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex`.
- Build a PDF without TeX: `pandoc <file>.md -s -t typst -V mainfont="Libertinus Serif" -o <file>.typ`, then `python -c "import typst; typst.compile('<file>.typ', output='<file>.pdf')"`.
- Install with figures: `uv sync --locked --all-groups`.
- Tests: `uv run --locked pytest` or `uv run --locked viral test`.
- Exploratory smoke run: `uv run --locked viral smoke` (writes `results/exploratory/EXP-001/<run_id>/`).
- Any run: `uv run --locked viral run --config <config.json>`; confirmatory configs are refused until the protocol is frozen by the owner.
- Report: `uv run --locked viral report <run_dir> [--project <config.json>] [--pdf]`; for `--pdf` set `VIRAL_PANDOC` (pandoc binary) and `VIRAL_TYPST_PYTHON` (a Python with the typst package).
