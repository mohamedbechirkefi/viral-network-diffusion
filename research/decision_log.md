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
