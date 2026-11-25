<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Release checklist

Status at M6 (2026-11-25): release candidate prepared, awaiting the owner's review and G-PUBLIC. Every ticked item was verified in the M6 session, with the evidence given. The two owner items stay open. Nothing has been pushed, tagged or released.

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
