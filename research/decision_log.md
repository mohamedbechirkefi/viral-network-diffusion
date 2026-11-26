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

## D-005 (2026-11-24): M2 implementation choices

- **Decided by:** the session (M2); open to owner review. Not a protocol change.
- **Decision:**
  - The project is now an installable package (`src/viral`, build backend `uv_build` 0.9.x, console script `viral`).
  - Engines are synchronous. IC draws one uniform per attempt, in the order (source ascending, neighbour ascending), on neighbours inactive at the start of the round; the parent of a newly active node is its first successful attempt in that order. This makes the reference loop and the vectorised engine consume identical random streams, so they are compared for exact equality, not only in distribution.
  - LT activates a node when it has at least one active neighbour and the active fraction is at least `phi` (so `phi = 0` spreads exactly over seeded components).
  - Random streams: `SeedSequence(master, spawn_key=...)`. Graph streams are keyed by (topology, replicate); cascade streams by (replicate, model, parameter, seed rule, seed count) and not by topology, which gives the common random numbers of protocol section 5.
  - WS uses `networkx.watts_strogatz_graph` (not the connected variant); the giant-component fraction is recorded per graph.
  - `viral run` refuses a confirmatory config unless the registry carries a 64-hex protocol hash that matches the protocol file and `research/protocol.md` is not marked DRAFT (fail closed).
- **Rationale:** exact differential testing; matched comparisons as drafted; no possibility of a confirmatory run before the owner's freeze.

## D-006 (2026-11-24): Large raw result files stay out of git

- **Decided by:** the session (M2), following CLAUDE.md section 4 ("keep large generated files out of git").
- **Decision:** A `result.json` above a few MB is moved to `results/raw/...` (git-ignored). The committed run folder keeps `run_manifest.json`, the report, tables, figures and `result.json.sha256` with the regeneration command. The EXP-001 smoke `result.json` (0.3 MB) is committed; the planning-probe one (14 MB) is not.
- **Consequence:** the full EXP-002 matrix (about 504,000 cascades) will produce a result file of roughly 25 MB (extrapolated from the probe, not measured); it will follow the same rule.

## D-007 (2026-11-24): Proposed protocol amendments for the owner (NOT applied)

- **Decided by:** nobody yet. These are proposals from the M2 exploratory runs; the protocol files were not edited. Freezing and amending are the owner's decisions (G-FREEZE).
- **Disclosure:** proposals A1 and A3 are informed by exploratory pilot data (EXP-001 planning probe, run `EXP-001-20261124T162121Z-d947f41d`). If the owner adopts them, the protocol must say so, so that no reader mistakes them for choices made blind.
- **A1, primary estimand averages over a crossing.** In the probe (R = 10, exploratory) the per-p mean differences change sign: BA minus ER is positive for p up to 0.20 and negative at 0.30 and 0.50; WS minus ER is negative up to 0.30 and positive at 0.50. The grid-mean estimand `Delta_T` therefore partly cancels (probe values: BA minus ER 0.0092, WS minus ER -0.0560). Options for the owner: (a) keep the grid mean as drafted and report per-p contrasts as secondary; (b) make the per-p contrasts primary with Holm over 14 tests; (c) make S1 (matched `p / p_c`) the primary scale. Option (b) needs more replicates, see A2.
- **A2, replicate count.** For the drafted grid-mean estimand, the probe sd_diff is 0.0076 (BA minus ER) and 0.0072 (WS minus ER), far below the 0.028 planning bound, so `R = 30` is adequate (normal-approximation half-width about 0.003). For per-p contrasts the largest sd_diff is 0.037 (WS minus ER at p = 0.30), which gives a half-width of 0.013 at `R = 30`; the 0.01 target would need `R = 53` unadjusted, or `R = 116` at the first Holm step over 14 tests. Estimates from 10 replicates are themselves imprecise.
- **A3, EXP-003 threshold grid is mostly saturated.** In the probe, `phi` in {0.10, 0.14} reached at least 99 percent of nodes in almost every cell, and with 10 seeds every topology saturated up to `phi = 0.18`; one random seed at `phi = 0.26` almost never spreads. The proposed EXP-003 baseline (ER, random seeds, 10 seeds) is degenerate for three of the five grid values. Proposal: move the grid into the transition region, for example {0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30}, and re-check it with an exploratory probe before freezing.
- **A4, LT depth equals duration by construction.** With synchronous updates and the planning definition (generation = 1 + max generation of the active neighbours), `D = T` for every LT cascade (proof by induction on rounds; a test asserts it). EXP-003 item 14 expects them to differ. Proposal: report one of them, or define LT depth as 1 + the minimum generation among active neighbours (shortest exposure chain), which can differ from `T`.
- **A5, "Holm-adjusted bootstrap interval" is not yet operational.** The code implements Holm on bootstrap p-values and per-step levels `alpha / (m - i)`; the protocol should state the exact construction (for example: interval for the contrast at Holm step i at level `1 - alpha / (m - i)`) before the freeze.
- **A6, compute budget.** Projected EXP-002 engine time is about 142 s on this machine (from measured per-cell rates, all 84 cells measured), against a 4-hour planning budget. The budget can be lowered, or the spare capacity used for A2, or for S4 at no risk to the schedule.
- **A7, master seed.** The pilot used master seed 20261124. The confirmatory master seed should be a different value, fixed by the owner at the freeze, so that confirmatory graphs are not the pilot graphs.

## D-008 (2026-11-24): Real-data licence recheck; one real network adopted for a second test (EXP-005)

- **Decided by:** the owner ("Approve all", second round, 2026-11-24: "SNAP or Netzschleuder networks with an explicit licence that permits research use", fallback "Stay synthetic"); the licence check and the choice of network by the session under that rule.
- **Licence check (accessed 2026-11-24).** SNAP, https://snap.stanford.edu/data/: no dataset licence stated on the pages opened (index, ego-Facebook, email-Enron). Netzschleuder, https://networks.skewed.de/ and https://networks.skewed.de/about: no dataset licence; site code AGPLv3; data offered "with the belief that this is not only permitted, but the expressed intent of the original authors"; the JSON API entries opened (karate, email_enron, facebook_friends, dolphins) have no licence field. Neither source is adopted as such. The Netzschleuder entry `facebook_friends` points to its upstream, https://github.com/benmaier/BFMaierFBnetwork, which carries the MIT License (Copyright (c) 2014 Benjamin F. Maier), an explicit licence that clearly permits non-commercial research use.
- **Decision.** Adopt that network (362 nodes, 1988 edges, pinned commit `d1446af55483c98d93f72015b6238200e1a30575`, about 0.1 MB in total) for EXP-005 only: one calibration that uses the degree sequence only (the transmission grid at fixed multiples of `p_c`) and a second test against G(n, M) and degree-preserving nulls. EXP-001 to EXP-004 stay synthetic. Protocol section 11.5 fixed the method before the fit.
- **Personal data.** Real friendships under pseudonymous ids. Only the GML file (no attributes) is downloaded; `data/raw/` and `data/processed/` are git-ignored; only provenance, SHA-256 values and aggregate statistics are committed. Although MIT permits redistribution, the files are not redistributed.
- **Alternatives.** Stay fully synthetic (the fallback; not needed because one network passed the check); larger SNAP networks (no licence).
- **Consequences.** D-003 is superseded for EXP-005 only. New scripts `download_data.py`, `ingest_data.py`, `fit_calibration.py`; new module `viral.realdata`; new topologies `real`, `real_er`, `real_dpr`. External validity remains limited to one network (limitations item 7).

## D-009 (2026-11-24): Owner-approved amendments applied (round 2)

- **Decided by:** the owner ("yes for all others", applied with the second round "Approve all"): "Per-probability contrasts are primary, R = 120, with Holm. Threshold grid 0.18 to 0.30. A new master seed. Specify the Holm interval method."
- **Applied.** Protocol section 11 and the EXP-002 to EXP-004 amendment sections: 14 per-`p` contrasts in one Holm family; `R = 120` in EXP-002; `phi` grid {0.18, ..., 0.30} in EXP-003; master seeds 20261125 (EXP-002 and EXP-004), 20261126 (EXP-003), 20261128 (EXP-005), all different from the pilot seed 20261124; Holm interval method of section 11.3 implemented in `viral.stats.holm_bootstrap_contrasts`.
- **Choices made by the session at the freeze, before any confirmatory value was seen.** The interval construction of section 11.3 (the approval asked that it be specified, not how); the per-multiplier reading of the EXP-004 S1 criterion (a consequence of the per-`p` primary analysis); EXP-004 on the EXP-002 master seed so that its graphs are the EXP-002 graphs; the configs for EXP-003 and EXP-004 S1 to S4, which did not exist before.
- **Not applied (not on the approved list).** D-007 A4 (LT depth definition): EXP-003 keeps the planning definition, under which `D = T` by construction, and says so. D-007 A6 (lower compute budget): the 4-hour budget stays.

## D-010 (2026-11-24): Protocol v1.0 frozen (G-FREEZE, owner-approved 2026-11-24)

- **Decided by:** the owner ("yes for all others"; "Approve all").
- **Decision.** `research/protocol.md` and the EXP-001 to EXP-005 protocols are frozen at version 1.0; the confirmatory configs of EXP-002 to EXP-005 are frozen. Hashes, the git revision, the data manifest hash, C1 to C4 and the C4 disclosure are in `research/freeze.json`. `viral run` accepts exactly the frozen configs and refuses changed ones (tested).
- **Consequences.** Registry statuses are "frozen (owner-approved 2026-11-24), not yet run". M3 confirmatory runs are scheduled by the coordinator; none was run in this session. Any later change is a dated post-freeze amendment.

## D-011 (2026-11-24): Owner ratification of the real network and the D-009 session choices (round 3)

- **Decided by:** the owner, "Approve all" (2026-11-24, round 3; `../_shared/owner-approvals-2026-11-24c.md` section 3, outside this repository).
- **Items ratified, quoted from the approvals file:**
  - "Keep the MIT-licensed real friendship graph for EXP-005. It is pseudonymous and git-ignored." (D-008; protocol section 11.5.)
  - "Ratify the session choices recorded in D-009: the interval construction, the per-multiplier S1 criterion, and the new EXP-003 and EXP-004 configs." (Protocol section 11.3; EXP-004 protocol; `experiments/EXP-003/config.json` and `experiments/EXP-004/S1` to `S4` configs.)
- **Effect.** Ratification only. The frozen protocol texts and configs already contain these choices, so no frozen file changed and no hash changed. The items are listed under `ratifications` in `research/freeze.json`. The choices made by the session at the freeze (D-009) are now owner decisions.
- **Consequences.** None for the M3 schedule. No confirmatory run was made.

## D-012 (2026-11-25): M3 confirmatory runs, execution notes and open items

- **Decided by:** the session (M3), under the coordinator's M3 brief ("Start next", the owner, 2026-11-25). No owner decision is taken here.
- **Executed.** Every frozen confirmatory config ran once, in full, through the freeze guard at revision `32961c3` (clean tree): EXP-002, EXP-003, EXP-004 S1, S2, S3 and the optional S4 (N = 500, N = 2000), EXP-005. Eight runs, exit status 0, no graph-check failure, no retry, no dropped run. Wall clock 23:34:46Z to 23:52:52Z on 2026-11-24 (UTC), two worker processes under `nice`.
- **Analysis code.** `viral.confirmatory` and `scripts/analyse_confirmatory.py` transcribe the frozen analysis plans. They were written, tested and committed (`32961c3`) before any confirmatory output existed and were not changed afterwards. Secondary (unadjusted) estimates use a separate stream `SeedSequence(master, spawn_key=(2, 1))` so they never consume the primary resampling matrix; this stream is a session choice for secondary estimates only.
- **Storage (not a protocol deviation).** Raw `result.json` files were written to the git-ignored `results/raw/confirmatory/` rather than the default `results/confirmatory/`, because every experiment's raw results exceed 20 MB (EXP-002 100 MB, EXP-003 23 MB, EXP-004 28 MB in total, EXP-005 24 MB). Their SHA-256 values, the run manifests, logs, analysis tables and figures are committed.
- **Open item for the owner: S1 cross-reading.** The frozen EXP-004 S1 criterion (per-multiplier reading, ratified in D-011) refers to the multipliers "corresponding" to each EXP-002 `p`, which the frozen texts do not define. All S1 Holm intervals lie inside the SESOI at c = 0.5 and 1 and outside at c = 1.5, 2 and 3, so the reading depends on the mapping. The session did not choose one; `results/confirmatory/EXP-004/S1/EXP-004-20261124T233447Z-de14a4b3/s1_reading.json` records "unresolved".
- **Open item: experiment reports.** The file tool refused to create `research/experiments/EXP-00N/report.md`; following the coordinator's instruction, the reports were left unwritten and not produced by any other means.
- **Reproducibility commands.** The EXP protocols list `viral report` for analysis; the frozen inferential analysis is produced by `scripts/analyse_confirmatory.py`, and `viral report` produces the descriptive tables (`tables/`). Recorded, not a design change.

## D-013 (2026-11-25): Owner decisions closing M3 (S1 reading; experiment reports)

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (`../_shared/owner-approvals-2026-11-25.md`, outside this repository, items 4 and 12).
- **S1 (item 12, resolves the open item of D-012), quoted:** "S1 is reported separately for each multiplier, consistent with the round-3 ratified per-multiplier criterion." "S1 gets no single overall verdict, and no multiplier is picked after the data."
- **Effect.** EXP-004 S1 is reported per multiplier: Holm-adjusted intervals inside the SESOI at c = 0.5 and 1, outside at c = 1.5, 2 and 3 (`results/confirmatory/EXP-004/S1/EXP-004-20261124T233447Z-de14a4b3/primary_contrasts.csv`). No overall S1 verdict is stated, and no EXP-002 effect is reclassified as a degree-heterogeneity effect through S1. The committed `s1_reading.json` ("unresolved") is kept as the record of the pre-decision state.
- **Experiment reports (item 4), quoted:** "The owner approves writing the missing 11.3/11.6 experiment reports (`report.md`, and `reproduction.md` where the repo uses it). They are written from the committed results, tables and figures only." "Nothing is recomputed and no numbers change."
- **Effect.** The 12-part reports and `reproduction.md` files of EXP-001 to EXP-005 are written with the file tool from committed files only. This closes the second open item of D-012.

## D-014 (2026-11-25): M4 interpretation, exploratory confounder checks and evidence-audit corrections

- **Decided by:** the session (M4), under the coordinator's M4 brief. The owner said "Approve all recommendations, push then next" on 2026-11-25 (`../_shared/owner-approvals-2026-11-25b.md`, outside this repository), which starts M4. No owner decision is taken here. The proposed manuscript title is the session's, and the owner may change it.
- **Exploratory confounder checks (X1 to X3).**
  - *Why.* Three competing explanations named in the protocols were left open by the confirmatory design:
    - degree homogeneity versus structure for the WS deficit (EXP-002 item 4a; S2 tests BA only);
    - component structure in EXP-005 (limitation 16);
    - degree heterogeneity under LT (EXP-003 item 4).
  - *Design and labelling.* `scripts/exploratory_m4.py` ran one cheap exploratory simulation for each of the three. Each used fresh master seeds 20261201, 20261202 and 20261203, R = 30, C = 200, B = 10000 and unadjusted 95 percent intervals. The checks were designed after the confirmatory results were seen. They are labelled exploratory everywhere and never change or replace a frozen verdict.
  - *Execution.* One process. Total runtime about 162 s. Outputs are in `results/exploratory/M4/`.
  - *Superseded executions.* The script was executed three times. The first execution ran X1 and X2 only, before X3 was added. The second ran with the untracked outputs of the first in the tree. Both sets of outputs were deleted by the session that created them. The committed outputs come from the third execution, at revision `4ed1942` with a clean tree. The checks are deterministic, and the X1 and X2 values of the first and third executions agree.
- **Claims register schema.** New columns: `result_id`, `config_hash`, `figure_or_table` and `section`. New row types: secondary (unadjusted), descriptive levels, graph statistics, exploratory, synthesis and external. `scripts/build_records.py` generates every row except the synthesis and external rows, which are listed in that script with the result ids or sources they rest on (575 rows).
- **Evidence audit.** `scripts/audit_evidence.py` does four things:
  - recomputes every confirmatory table from the raw results;
  - checks committed copies against their originals;
  - traces every number in the manuscript, the supplementary file and the five reports to a committed file;
  - checks every printed "estimate [lo, hi]" jointly against one committed row.
  Findings are in `research/publication/evidence_audit.md`.
- **Corrections made (reporting only; no frozen file, number of a verdict or analysis changed).**
  - (1) The EXP-004 report's total runtime is now 351.1 s. Version 1.0 summed the rounded run times.
  - (2) The literature sentences of the EXP-001 to EXP-004 reports now state the verification level of each source. Three sources were re-read (Newman et al. 2001 abstract; Watts 2002 full text; Kempe et al. 2015 abstract), and the threshold expression is presented as a definition.
  - (3) The registry statuses still said "report.md not written" and "S1 unresolved". They now reflect M3 closure and D-013.
  - (4) `research/publication/claims_audit.md` was an M0 checklist and is now completed.
- **Second review pass** (`research/publication/review_pass_2.md`). Eight challenges hold in full or in part. The manuscript changed from version 0.1 to 0.2 accordingly: descriptive title, SESOI-first counts, the pilot-replication caveat, the S2 bound, the S2 and S3 reuse note, a narrower WS mechanism statement, a narrower generalisation and per-family error control.
- **Consequences.** M4 is closed if the gate holds (`progress.md`). The owner may revise the manuscript title and the authorship metadata. Report PDFs and the manuscript PDF remain for M6.

## D-015 (2026-11-25): Owner approval of the manuscript title and of the funding, competing-interest and AI-use wording (post-M4)

- **Decided by:** the owner, 2026-11-25, "Approve all" (post-M4) (`../_shared/owner-approvals-2026-11-25c.md`, items 1 and 2). Applied by the AI assistant under the shared post-M4 brief.
- **Item 1, title.** The title proposed in M4 (D-014; `research/publication/review_pass_2.md`, challenge A1), "Topology and initial exposure in simulated diffusion: preregistered matched comparisons of independent-cascade and threshold models on random, small-world and scale-free graphs", is approved. It was already the manuscript title; the status line now records the approval. `manuscript.tex` was regenerated with the CONTRIBUTING pandoc command; the only difference is that sentence. No PDF was built (M6). The owner review checklist (`research/publication/author_review.md`) is left for the owner to tick.
- **Item 2, statements.** The wording of `research/paper/manuscript.md` section 11 (funding, competing interests and AI assistance) is owner-approved as drafted, including "No funding." and "No competing interests." No wording was changed. The remaining placeholders that need a fact only the owner knows are listed in `progress.md` under "Owner placeholders for M5".
- **Unchanged.** No frozen protocol, config, seed, result or number was touched. The evidence audit still passes with 0 untraced numbers.

## D-016 (2026-11-25): M5 interactive page, stack, sandbox fidelity and text consistency

- **Decided by:** the owner started M5: owner, 2026-11-25, "Next" (`../_shared/owner-approvals-2026-11-25d.md`, outside this repository). That record names the stack: "The master prompt's default stack is used: TypeScript, React and Vite. Versions are pinned and come from the shared template, `labs/_shared/demo-template/`, which was verified on 2026-11-25." It also states what "Next" does not decide: no push, no freeze, and no owner-only fact. The choices below are the session's, under the coordinator's M5 brief.
- **Stack.** `demo/` is a copy of the shared template (without `node_modules`), installed with `npm ci --prefer-offline`, with its `.npmrc` and pinned versions unchanged. No dependency was added; charts are hand-written SVG.
- **Exported data.** `scripts/export_demo_data.py` writes `demo/public/data/results.json` (`lab-demo-results` 1.0.0) from committed results, the registry, the claims register and the artifact manifest only. It holds one entry per registered experiment (EXP-001 to EXP-005) plus the exploratory M4 checks, each with status, verdict under the frozen rule and claim ids. Display strings follow the manuscript's print rules (four decimals; e-notation for the two EXP-002 rows that Table 3 prints so; the claims-register format for the M4 rows of supplementary S4.3). Extension keys: `sesoi`, `levels` (EXP-002, EXP-003, EXP-005 curves) and `graph_stats` (manuscript Table 2); `validateResults` checks them and fails closed. `code_revision` is the last commit touching any source file; there are no timestamps.
- **S1.** EXP-004 S1 is shown per multiplier, each with its own row and Holm-step interval, and the page states that it has no overall verdict (owner, D-013).
- **Sandbox fidelity.** The IC and LT rules (`demo/src/engine.ts`) are line-by-line ports of `ic_reference` and `lt_reference`. `scripts/make_sandbox_fixture.py` runs the Python engine on three 60-node graphs from the research generators, driving IC with a Python port of mulberry32 (the browser generator), and `demo/src/engine.test.ts` requires exact agreement (tolerance zero for every activation round, parent, generation and size; 1e-12 relative for `p_c`): 72 IC cascades and 9 LT cascades agree. The sandbox graphs are produced in the browser by reimplementations of the same three models, not byte-identical to networkx, at N of at most 400. The page therefore labels sandbox output as computed in the browser, not the published numbers, with intervals that are normal approximations over cascades on one graph. The engine is faithful; the sandbox as a whole is not the research matrix and is labelled so.
- **Text consistency (11.6, M5).** README (stale since M0), `CITATION.cff` abstract, `experiments/README.md`, `results/README.md`, `articles/README.md`, `demo/README.md`, the release and reproducibility checklist status lines and the supplementary version line (0.1 to 0.2) were brought up to date. `articles/medium.md` and `articles/linkedin.md` did not exist and were drafted from manuscript version 0.2. Manuscript section 10 gained one sentence describing the demo, on the same line, so no traced line number moved; `manuscript.tex` was regenerated and `scripts/audit_evidence.py` refreshed `number_trace.csv` (0 untraced numbers). No number in the manuscript changed.
- **Owner checklist.** No box in `research/publication/author_review.md` had been ticked by an agent, so none was unticked. Notes were added beside the title and AI-statement items recording the owner approval of D-015, with the boxes left for the owner, and an open item was added for the full-text review (M6).
- **Placeholders kept.** Repository URL and demo URL stay "[placeholder, not published]" in the manuscript, README, CITATION.cff, articles and demo README. The author line and affiliation ("Mohamed Bechir Kefi (no affiliation)") and the funding and competing-interest statements are unchanged as the owner set or approved them (D-015).
- **Unchanged.** No frozen protocol, config, seed or result was touched. No confirmatory run. Nothing was pushed.

## D-017 (2026-11-25): M6 release candidate, PDF builder fixes, literature levels and CITATION.cff

- **Decided by:** the owner started M6: owner, 2026-11-25, "Next" (second) (`../_shared/owner-approvals-2026-11-25e.md`, outside this repository). That record says: "M6 is local work: a clean clone, PDFs, checks, and a release candidate prepared for the owner's review." It applies one coordinator default: "`CITATION.cff` `date-released`: the field is removed until a release exists, because no release has been made." It does not decide any push, release, licence change or publication, any `author_review.md` box, or any owner-only fact (repository and demo URL, funding, competing interests, author line, affiliation). The choices below are the session's, under the coordinator's M6 brief.
- **PDF builder.** `viral.report.build_pdf` gains a `root` argument (the manuscript includes figures from `research/experiments/`, outside its folder, which Typst refused), runs pandoc with `--wrap=none` (a wrapped "2." became a list item), drops a level-1 heading that repeats the title and otherwise takes the first heading as the title (PDF title metadata), and adds three Typst rules: breakable tables, unjustified table cells, table text at 0.9 em. `scripts/build_pdfs.py` builds the seven PDFs. Why: visual inspection showed a duplicated title, half-blank pages, overlapping columns and one false list; the fixes are in the builder and the Markdown sources, never in a PDF.
- **Source edits for layout only.** Column widths of four pipe tables (supplementary S1, S3 and S6; EXP-001 and EXP-004 execution records) and a blank line before three lists (EXP-002 sections 11 and 12, EXP-005 section 11). No number, verdict or sentence changed in the reports; their line shifts were absorbed by re-running `scripts/audit_evidence.py` (number trace refreshed, `decimal_untraced` 0).
- **PDFs committed.** No `.gitignore` rule or decision excludes them; each is under 5 MB (largest 618 KB).
- **Literature levels.** Free arXiv or author copies of Kempe et al. 2003, Newman et al. 2001, Barabasi and Albert 1999 and Pastor-Satorras et al. 2015 (section IV.C) were read. Manuscript section 2 now cites Pastor-Satorras et al. 2015, Eq. 18, for `p_c = <k>/(<k^2> - <k>)`, and Kempe et al. 2003 for the IC model; the reference list and `references.bib` carry the new levels. Why: the brief asks to open free legal full texts for sources a claim depends on. Seven entries remain at metadata level, each an attribution or a data citation.
- **CITATION.cff.** `date-released` removed (owner-approvals-2026-11-25e). Version `0.1.0-rc1` (the package version is 0.1.0; "rc1" marks the first release candidate). Title set to the owner-approved manuscript title (D-015) so that the citation and the manuscript agree; the owner may prefer the project name for the software record (open item in `author_review.md`).
- **Paths and headers.** Absolute home-directory paths in `CLAUDE.md` and `demo/README.md` replaced by paths relative to the repository root; `research/protocol.md` (frozen) and `progress.md` (append-only) keep theirs, noted in `progress.md`. SPDX headers added to `demo/.npmrc` (a change to the template copy noted in D-016 as unchanged) and to `manuscript.tex` through pandoc `header-includes`; raw `run.log` files are not edited.
- **New checks.** `scripts/check_links.py` and `tests/test_links.py` (relative links and anchors; bib entries against the manuscript reference list).
- **Status.** M6 is "release candidate prepared, awaiting owner review and G-PUBLIC". It is not done until the owner signs off. No frozen protocol, config, seed or result changed; no confirmatory run; nothing pushed, tagged or released.

## D-018 (2026-11-26): owner answers to the decision sheet applied (wording and configuration only)

- **Decided by:** owner, 2026-11-26, decision sheet (`../_shared/owner-decision-sheet-2026-11-26.md`, answers in `../_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied under the coordinator's brief `../_shared/OWNER-ANSWERS-brief.md`.
- **A1.** Out-of-date "nothing pushed" sentences corrected in the README status, `release_checklist.md`, `reproducibility_report.md` and the open decisions of `author_review.md`: the repository has been public at https://github.com/mohamedbechirkefi/viral-network-diffusion since 2026-11-25. Append-only records (`progress.md`, this log, the experiment journal) are not edited.
- **B1.** Repository URL filled in the README, manuscript section 10, both articles and `CITATION.cff` (`repository-code`; the placeholder sentence removed from the abstract).
- **B2.** Demo URL https://viral-network-diffusion.kefimohamedbechir.workers.dev filled in the README, manuscript section 10, both articles and `demo/README.md`. `demo/wrangler.jsonc` added: assets only (`./dist`, the folder `vite build` writes), no Worker script; deployed by the coordinator, not by any script here. The built page loads nothing from another origin (a11y check "no request leaves the local origin").
- **B3.** Author line "Mohamed Bechir Kefi, independent researcher" in the manuscript title block, the manuscript metadata section ("Author: Mohamed Bechir Kefi. Affiliation: Independent researcher."), the supplementary status paragraph, the five report identification lines, `CITATION.cff` (`affiliation: "Independent researcher"`), the README, both articles, the demo footer and the demo README. `pyproject.toml` has no authors field. The frozen record `research/freeze.json` (item C3, "no affiliation") is not edited.
- **B4.** Manuscript section 11: "No funding was received. The author declares no competing interests."
- **B7, B8, B9, B10, B11, B13, B14.** `CITATION.cff` already carried the manuscript title. Version `0.1.0-rc1` and no `date-released` kept; the release step is recorded in `release_checklist.md`. No home path remained in editable files; the two kept files (`research/protocol.md`, frozen; `progress.md`, append-only) are listed in `reproducibility_report.md` section 7. PDFs stay committed. "Release notes (draft)" added to `release_checklist.md` (no small-label figure here; build tools not redistributed). Source labels accepted.
- **Not applicable here.** B5, B6, B12 and every single-repository answer (they name other repositories).
- **Edits placed on existing lines.** Every change in the manuscript, supplementary file and reports was made within an existing line, so the number trace keeps its line numbers: `scripts/audit_evidence.py` gives the same counts (`decimal_untraced` 0) and leaves `number_trace.csv` and `artifact_manifest.json` unchanged.
- **Unchanged.** No result, figure, config, seed, frozen protocol, hash or checksummed output. No box in `author_review.md` ticked. Nothing pushed or deployed by this session.
