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

1. Approval to push, release or publish anything, including the repository, the demo page, the PDFs and the article drafts, is open (G-PUBLIC; owner-approvals-2026-11-25e, "What it does not decide"). Update of 2026-11-26: the repository was pushed and has been public since 2026-11-25, and the demo deploy was granted on 2026-11-26; the release and the articles stay open (section below).
2. The public repository URL was an owner-only placeholder; filled on 2026-11-26 (B1).
3. The demo URL was an owner-only placeholder; filled on 2026-11-26 (B2).
4. The author line and the affiliation ("Mohamed Bechir Kefi (no affiliation)") stay as the owner set them and are confirmed only by the owner. Superseded on 2026-11-26 (B3): "Mohamed Bechir Kefi, independent researcher".
5. The funding and competing-interest statements were approved on 2026-11-25 (D-015) and are listed here only because owner-approvals-2026-11-25e names them as owner-only facts.
6. The owner's full-text review of manuscript version 0.2, the supplementary file, the five reports and the article drafts (`articles/medium.md`, `articles/linkedin.md`) is pending.
7. The `CITATION.cff` version reads `0.1.0-rc1` and has no `date-released`; at release, the owner sets the final version and re-adds the release date (owner-approvals-2026-11-25e, coordinator default).
8. The `CITATION.cff` title was set to the owner-approved manuscript title at M6 (it was the project name); the owner may prefer the project name for the software record. Settled on 2026-11-26 (B7): the manuscript title.

### Owner placeholders remaining (file and line, at the M6 commit; all filled on 2026-11-26, see the next section)

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

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`../_shared/owner-decision-sheet-2026-11-26.md` and `../_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied as wording and configuration only (decision log D-018). No box in this file was ticked by an agent.

| id | answer | applied in this repository |
|---|---|---|
| A1 | correct the out-of-date "not pushed / no remote" sentences | README status, `release_checklist.md` and `reproducibility_report.md` status lines, open decisions 1 to 4 above; append-only records unchanged |
| B1 | repository URL `https://github.com/mohamedbechirkefi/viral-network-diffusion` | README, `CITATION.cff` (`repository-code`), manuscript section 10, both articles |
| B2 | demo hosted on Cloudflare Workers, free plan, at `https://viral-network-diffusion.kefimohamedbechir.workers.dev` | README, manuscript section 10, both articles, `demo/README.md`; `demo/wrangler.jsonc` added (assets only, `./dist`); deployed by the coordinator |
| B3 | "Mohamed Bechir Kefi, independent researcher" | manuscript (title block and metadata section), supplementary, five experiment reports, `CITATION.cff` (`affiliation: "Independent researcher"`), README, both articles, demo footer and demo README; `pyproject.toml` has no authors field; the frozen record `research/freeze.json` is not edited |
| B4 | no funding, no competing interests | manuscript section 11: "No funding was received. The author declares no competing interests." |
| B5, B6 | no item for this repository (title and AI statement were approved on 2026-11-25, D-015) | none |
| B7 | `CITATION.cff` carries the manuscript title | already so since M6; unchanged |
| B8 | `0.1.0-rc1` kept, no `date-released`; at release `0.1.0` and the release day; `pyproject.toml` stays `0.0.0` | recorded in `release_checklist.md` |
| B9 | scrub local home paths from editable files, no history rewrite | none remained in editable files; the two kept files are listed in `reproducibility_report.md` section 7 |
| B10 | committed PDFs stay and are attached to the release | PDFs rebuilt for the changed sources |
| B11, B13 | release-note sentences | "Release notes (draft)" in `release_checklist.md` |
| B12 | no item for this repository | none |
| B14 | literature verification labels accepted | recorded; no text change needed |

### What remains open (owner only)

- B15: the article drafts (`articles/medium.md`, `articles/linkedin.md`) and their titles, before any posting.
- B16: the full-text review of the manuscript, the supplementary file and the five reports, then the sign-off of every box in this file.
- B18: the release, tag, and any DOI or preprint.
- Freezes: none open in this repository (the protocol was frozen on 2026-11-24).

### Owner placeholders remaining (2026-11-26)

None. The repository and demo URLs are filled everywhere they appeared; no author, affiliation, funding or competing-interest placeholder remains.
