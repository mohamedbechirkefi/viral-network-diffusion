<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# VIRAL: how every session works

VIRAL studies network diffusion: how network topology and initial exposure influence diffusion independently of content quality. `master_prompt.md` is the authority. It is never edited.

## 1. Reading order (every session, before modifying anything)

1. `master_prompt.md` (whole file; sections 2, 3, 10 and 11 are binding).
2. `roadmap.md` (milestones M0 to M6, status, blockers).
3. `progress.md` (append-only journal; read the latest entry and its "next action").
4. `research/protocol.md` (check whether it is DRAFT or FROZEN, and its hash).
5. `research/claims_register.csv` (no claim may appear anywhere without a row).

Then inspect `git status` and `git log`. Do not overwrite changes made by the owner. State the current milestone and the next bounded task before working.

## 2. Mandatory requirements (master prompt section 11)

- Maintain the publication tree of section 11.1: `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex generated, references.bib, figures/, supplementary.md, manuscript.pdf generated only after validation), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- Register every experiment before confirmatory execution (purpose, dependency, primary outcome, protocol hash, status, report location, planned analysis). Seeds and replicates are runs inside an experiment, not new experiments. A new question or a materially different protocol gets a new EXP id.
- Write `EXP-NNN/protocol.md` before each experiment (section 11.2), freeze it with a hash and the owner's recorded approval before confirmatory runs. Post-hoc changes are exploratory, dated and justified.
- Write a standalone report per registered experiment with the 12-part structure of section 11.3, including failed, null, abandoned and exploratory experiments. Never fabricate a PDF or placeholder results.
- One integrated manuscript (section 11.4), Markdown canonical, LaTeX and PDF generated with free local tools.
- Evidence-to-publication pipeline (section 11.5): figures and tables generated once from versioned results; a manifest maps every number to experiment id, run ids, metric, result path, generator, config hash and code revision. A second review pass challenges the preferred hypothesis.
- Milestone additions of section 11.6 are part of `roadmap.md` acceptance criteria.

## 3. Toolchain (zero cost, decided 2026-11-24, see decision_log D-002)

- Python 3.12.1 at `/usr/local/bin/python3`; project environment managed by uv 0.9.5 at `/Users/bechir/research/labs/.tools/py/bin/uv`, locked in `uv.lock`.
- pandoc 3.6.3 at `/Users/bechir/research/labs/.tools/pandoc`; typst 0.15.0 (Python package), pypdf and pillow in `/Users/bechir/research/labs/.tools/py/bin/python`.
- No TeX distribution. PDFs: pandoc Markdown to Typst, compiled with the typst Python package. `manuscript.tex` is generated from Markdown with pandoc and is not compiled locally.
- Node 22.23.3 at `/Users/bechir/research/helix/.tools/node/bin` may be used read-only for the demo. Never modify that folder.

## 4. Rules

### Gates
- Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
- No paid service of any kind.
- Never freeze a protocol: freezing is the owner's decision (G-FREEZE). Until the owner freezes `research/protocol.md`, every run is exploratory and labelled so.
- No confirmatory experiments before the freeze. Tiny exploratory smoke checks of the toolchain or engine are allowed and must be labelled exploratory.

### Scope
- Work only inside this repository, except read-only use of the tools listed in section 3.
- Do not touch any other folder under `/Users/bechir/research` (hive, helix, cogkt, trading, the other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs in `progress.md`.
- Anything not verified is labelled unverified. Cite only sources actually opened, with URL or DOI and access date.
- Claims boundary (section 10): no claims about real social-platform algorithms or guaranteed virality. All results are simulations and are labelled as such.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0` as a comment where the format allows; JSON and CSV are covered by `NOTICE.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).
- Do not change the licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`). Development commands may be appended to `CONTRIBUTING.md`.
- Keep large generated files out of git (`results/raw/` is ignored); provide deterministic regeneration scripts.

### Commits
- Local commits only, with the owner's git identity as given in the session brief (`git -c user.name=... -c user.email=... commit`; the address is not written in repository files), message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.

## 5. Session end

Update `progress.md` (append a dated entry: commands, actual outputs, failures, changed files, risks, next action) and `roadmap.md` statuses. Append decisions to `research/decision_log.md`. Never mark incomplete work done.
