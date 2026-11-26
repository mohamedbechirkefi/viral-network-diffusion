<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Release checklist

Status at M6 (2026-11-25): release candidate prepared, awaiting the owner's review and G-PUBLIC. Every ticked item was verified in the M6 session, with the evidence given. The two owner items stay open. Correction of 2026-11-26: the repository was pushed and has been public at https://github.com/mohamedbechirkefi/viral-network-diffusion since 2026-11-25 (pushed by the lab coordinator); no tag, release, DOI or preprint exists. The owner's answers of 2026-11-26 (owner, 2026-11-26, decision sheet) were applied as wording only; no box below changed.

- [x] Every registered experiment has a truthful standalone report (including failed or null). Evidence: `research/experiments/EXP-001/report.md` to `EXP-005/report.md`, all five registered experiments in `research/experiment_registry.csv`; the M6 evidence audit traced every number in them (`scripts/audit_evidence.py`: `decimal_untraced` 0).
- [x] Integrated manuscript complete; PDF compiled with the documented toolchain and visually inspected. Evidence: `research/paper/manuscript.pdf` (23 pages) and `supplementary.pdf` (13 pages) from `scripts/build_pdfs.py` (pandoc 3.6.3 to Typst 0.15.0); every page rendered to PNG and inspected; fixes in `reproducibility_report.md` section 4; PDF title metadata set, no e-mail address or local path (pypdf).
- [x] Experiment report PDFs compiled and inspected. Evidence: five `report.pdf` files (4, 9, 6, 8 and 7 pages); every page inspected, including all figure pages.
- [x] README key findings match verified results. Evidence: `tests/test_demo_export.py::test_public_texts_use_only_numbers_printed_in_the_manuscript` passes (README, `CITATION.cff`, both articles and the demo README); full suite `189 passed`.
- [x] Demo, manuscript, reports and articles use identical results and labels. Evidence: `scripts/export_demo_data.py --check` prints "results.json up to date"; demo `npm test` 30 of 30; the M5 consistency tests pass.
- [x] Medium and LinkedIn drafts checked against the claims register. Evidence: numbers by the consistency test above; claims boundary text ("simulations", no platform claim) present in both drafts; they remain drafts for the owner's review.
- [x] Reproducibility report complete. Evidence: `research/publication/reproducibility_report.md` (clean clone: 186 tests, smoke identical apart from volatile fields, `A11Y-CHECK PASS`, export deterministic; fresh clone of the M6 commit re-checked).
- [x] Links, references, manifests, secrets and licences checked. Evidence: `scripts/check_links.py` `LINKS PASS` (49 links, 14 bib entries); `data/manifest.json` 4 of 4 hashes; `artifact_manifest.json` 43 of 43 paths and hashes; scan of 366 tracked files with 0 tokens, keys or `.env` files; `dependency_licences.md` with no flag.
- [x] `CITATION.cff` prepared as a release candidate. Evidence: `date-released` removed (owner-approvals-2026-11-25e), version `0.1.0-rc1`, title equal to the manuscript title, structural check against CFF 1.2.0 keys and types passed.
- [ ] Owner sign-off of `research/publication/author_review.md` (owner only).
- [ ] Owner approval recorded before any push or publication (G-PUBLIC; owner only).

## Version and date at the release (B8, owner, 2026-11-26, decision sheet)

Until the release, `CITATION.cff` keeps version `0.1.0-rc1` and no `date-released`. At the release, the version becomes `0.1.0` and `date-released` is set to the release day. `pyproject.toml` stays at `0.0.0`, because changing it would change `uv.lock` and the recorded environments.

## Release notes (draft)

- Figures: no figure of this repository was listed with small, crowded or clipped labels (B11); every committed figure is kept as generated.
- Build and check tools: external build and check tools are used but not redistributed (B13): pandoc 3.6.3 (GPL-2.0-or-later) for Markdown conversion, Google Chrome (headless, for `demo/tools/a11y_check.mjs`), the fonts bundled with typst and embedded in the PDFs (Libertinus Serif, SIL Open Font License 1.1; DejaVu Sans Mono), and the MPL-2.0 development and build tools lightningcss and hypothesis, as listed in `research/publication/dependency_licences.md`.
- Sources: the literature verification labels (full text, abstract only, metadata only) stated in the manuscript reference list were accepted by the owner (B14); no further reading was done for this release.
- Demo: the built page is hosted as Cloudflare Workers static assets on the free plan at https://viral-network-diffusion.kefimohamedbechir.workers.dev, configured by `demo/wrangler.jsonc` and deployed by the lab coordinator.
