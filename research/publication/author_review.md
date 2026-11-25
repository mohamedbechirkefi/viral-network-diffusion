<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Owner review checklist

To be completed by the owner. The AI assistant does not tick these boxes.

- [ ] Protocol frozen and hash recorded (G-FREEZE).
- [ ] Authorship and affiliation metadata approved.
- [ ] AI assistance disclosure approved.
- [ ] Claims register reviewed.
- [ ] Manuscript and every experiment report reviewed.
- [ ] Publication, push or release approved (G-PUBLIC).

## Items raised at M4 (2026-11-25) for the owner

- [ ] Manuscript title (approved by the owner on 2026-11-25, D-015; the box is left for the owner to tick). The working title, "The mathematics of going viral", was replaced by a descriptive title proposed by the session: "Topology and initial exposure in simulated diffusion: preregistered matched comparisons of independent-cascade and threshold models on random, small-world and scale-free graphs". The owner may change it.
- [ ] Manuscript version 0.2 (`research/paper/manuscript.md`) and its supplementary file, including the exploratory section 5.5.
- [ ] Second review pass (`research/publication/review_pass_2.md`) and evidence audit (`research/publication/evidence_audit.md`).
- [ ] AI-assistance statement in manuscript section 11 (wording approved by the owner on 2026-11-25 together with the funding and competing-interest statements, D-015; the box is left for the owner to tick).
- [ ] Full-text review of manuscript version 0.2 (pending; M6).

## Prepared for the owner (M6, 2026-11-25)

No box above was ticked by an agent at M6, and none had been ticked before, so none was unticked. Only the owner ticks these boxes.

### What to read for each item

| item | what to read |
|---|---|
| Protocol frozen and hash recorded | `research/protocol.md` (header: version 1.0, frozen 2026-11-24) and `research/freeze.json` (protocol, config and data hashes); decision log D-009 to D-011. |
| Authorship and affiliation metadata | `research/paper/manuscript.md`, title block and section "Author and affiliation metadata"; `CITATION.cff` (`authors`); `CONTRIBUTING.md` section 4. |
| AI assistance disclosure | `research/paper/manuscript.md` section 11; decision log D-015. |
| Claims register | `research/claims_register.csv` (575 rows) and `research/publication/claims_audit.md`. |
| Manuscript and every experiment report | `research/paper/manuscript.pdf` (23 pages) and `research/paper/supplementary.pdf` (13 pages); `research/experiments/EXP-001/report.pdf` to `EXP-005/report.pdf` (4, 9, 6, 8 and 7 pages). The Markdown files next to them are canonical. |
| Publication, push or release | `research/publication/release_checklist.md`, `research/publication/reproducibility_report.md`, `research/publication/dependency_licences.md`. |
| Manuscript title | `research/paper/manuscript.md`, title; decision log D-015. `CITATION.cff` now carries the same title (M6). |
| Manuscript version 0.2 and supplementary, including section 5.5 | `research/paper/manuscript.md` section 5.5; `research/paper/supplementary.md` section S4.3. |
| Second review pass and evidence audit | `research/publication/review_pass_2.md`; `research/publication/evidence_audit.md`, including its M6 section. |
| AI-assistance statement | `research/paper/manuscript.md` section 11. |
| Full-text review of manuscript version 0.2 | `research/paper/manuscript.pdf`. M6 changed only the literature verification levels in section 2 and the reference list (`research/literature_review.md`, M6 update); no number or verdict changed. |

### Open decisions for this repository

1. Approval to push, release or publish anything, including the repository, the demo page, the PDFs and the article drafts, is open (G-PUBLIC; owner-approvals-2026-11-25e, "What it does not decide").
2. The public repository URL is an owner-only fact that is still a placeholder.
3. The demo URL is an owner-only fact that is still a placeholder.
4. The author line and the affiliation ("Mohamed Bechir Kefi (no affiliation)") stay as the owner set them and are confirmed only by the owner.
5. The funding and competing-interest statements were approved on 2026-11-25 (D-015) and are listed here only because owner-approvals-2026-11-25e names them as owner-only facts.
6. The owner's full-text review of manuscript version 0.2, the supplementary file, the five reports and the article drafts (`articles/medium.md`, `articles/linkedin.md`) is pending.
7. The `CITATION.cff` version reads `0.1.0-rc1` and has no `date-released`; at release, the owner sets the final version and re-adds the release date (owner-approvals-2026-11-25e, coordinator default).
8. The `CITATION.cff` title was set to the owner-approved manuscript title at M6 (it was the project name); the owner may prefer the project name for the software record.

### Owner placeholders remaining (file and line, at the M6 commit)

| file | line | placeholder |
|---|---|---|
| `README.md` | 12 | Demo URL: [placeholder, not published] |
| `README.md` | 90 | Repository URL: [placeholder, not published] |
| `CITATION.cff` | 12 | "Repository URL: placeholder, not published." (end of the abstract) |
| `research/paper/manuscript.md` | 357 | Public repository URL and demo URL: [placeholder, not published] (section 10) |
| `research/paper/manuscript.tex` | 1258 and 1261 | the same two placeholders (generated file) |
| `articles/medium.md` | 69 | repository link and demo link placeholders |
| `articles/linkedin.md` | 14 and 15 | repository and interactive-page placeholders |
| `demo/README.md` | 30 | Demo URL: [placeholder, not published] |
