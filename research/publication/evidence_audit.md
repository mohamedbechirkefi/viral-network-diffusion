<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Evidence audit (master prompt section 11.5; M4, 2026-11-25)

**Command.** `.venv/bin/python scripts/audit_evidence.py` (exit status 0), run after `scripts/build_records.py`. The full output is in `progress.md` (M4 entry). The script reads results and writes only these records:

- `research/publication/number_trace.csv`;
- the `numbers`, `raw_audit`, `copy_audit` and `triple_audit` blocks of `research/publication/artifact_manifest.json`.

## 1. Raw outputs against committed tables

For each of the eight confirmatory runs, the script checks:

- that the git-ignored raw `result.json` is present and its SHA-256 equals the committed value;
- that the result validates against its schema;
- denominators and sample counts:
  - cell count equals topologies x replicates x settings;
  - every cell has the configured 200 cascades;
  - total cascades equal the count in `analysis.json`;
  - every per-cascade size is an integer in `[1, N]`;
  - each cell's `mean_S` equals mean size divided by `N`;
- precision and uncertainty: the frozen analysis is recomputed from the raw result (`viral.confirmatory.run_plan` with the recorded plan) and compared with `analysis.json`, `primary_contrasts.csv`, `secondary_contrasts.csv` and `topology_means.csv`. The comparison covers means, interval bounds, interval levels, bootstrap and Holm p-values, decisions, SESOI flags and replicate counts, at relative tolerance 1e-12.

| run | checks | failures |
|---|---|---|
| EXP-002-20261124T233447Z-2c7febb6 | 25 | 0 |
| EXP-003-20261124T234212Z-a2d668ab | 13 | 0 |
| EXP-004-20261124T233447Z-de14a4b3 (S1) | 21 | 0 |
| EXP-004-20261124T233637Z-916e8d29 (S2) | 18 | 0 |
| EXP-004-20261124T233755Z-e1d24091 (S3) | 25 | 0 |
| EXP-004-20261124T235044Z-e31dba07 (S4, N = 500) | 25 | 0 |
| EXP-004-20261124T235110Z-40385ec3 (S4, N = 2000) | 25 | 0 |
| EXP-005-20261124T233932Z-d277f271 | 25 | 0 |

Total: 177 checks, 0 failures. The confirmatory tables are exactly the frozen analysis of the raw results.

**Units.** Every contrast is a difference in the final cascade fraction `S`, which is unitless and lies in `[0, 1]`. Every "n" is a count of matched sets (graph replicates), never of cascades. These are stated in every table caption.

## 2. Stale artifacts

- **Result files.** All 129 entries of `results/confirmatory/MANIFEST.sha256` match their files.
- **Experiment-folder copies.** All 56 copies match their originals in `results/confirmatory/`: figures, `metrics.csv`, configs and run manifests.
- **Figure paths.** The manuscript figures point at the experiment-folder copies, which are byte-identical to the generated figures.
- **Result:** 0 stale figures or tables.

## 3. Numbers in the manuscript and reports

Every number token in `research/paper/manuscript.md`, `research/paper/supplementary.md` and the five `report.md` files was traced. Hashes, run ids, claim ids, dates, versions and section numbers are excluded. Each number was matched to a committed result file at its printed precision (sign-insensitive, so that "BA is below ER by 0.3194" traces). The script prefers a source of the experiment named on the line or in the section heading. Each trace row in `number_trace.csv` records:

- the document and line;
- the experiment id and run id;
- the file and the row and column of the match;
- the generator;
- the config hash;
- the code revision;
- the raw result path;
- up to three other candidate sources.

| class | tokens |
|---|---|
| decimal numbers traced | 2217 |
| of which weak (two or fewer significant digits, or five or more candidate sources; read with the line context) | 1392 |
| decimal numbers untraced | 0 |
| integers traced to a result or config | 556 |
| integers classified as constants or counts | 180 |

**Joint check of intervals.** Each printed "estimate [lo, hi]", in running text or across table columns, must match the mean, lower bound and upper bound of one committed row jointly. A weak single-number trace cannot pass this check by coincidence. Result: 370 triples matched, 0 unmatched.

**Integers not traced to a result file** fall into these categories:

- the "256" of SHA-256;
- the "95" of 95 percent;
- bibliographic years, volumes and pages;
- the suffixes of claim ids;
- test and check counts recorded in `progress.md` (174 tests; 54 checks);
- smoke and probe counts recorded in `progress.md` and the EXP-001 run records (5,250 cascades; 288,000 probe cascades; 210 graphs checked against EXP-002);
- planning numbers of the frozen protocol (116, 142);
- derived counts stated as derived:
  - 19,880 swaps = 10 x 1988 edges;
  - 552,000 = the sum of the five EXP-004 cascade counts;
  - 89 tests = the number of primary claim rows.

None of these is a result that should have come from a results table.

## 4. Mismatches found and fixed

| # | where | finding | fix |
|---|---|---|---|
| 1 | EXP-004 report, section 5 | "total runtime 351.2 s" is the sum of the rounded run times. The sum of the five unrounded `runtime_seconds` in the run manifests is 351.1 s. | Corrected to 351.1 s, with a note (report version 1.1). |
| 2 | EXP-002 and EXP-004 reports, section 3 | `p_c = <k>/(<k^2> - <k>)` was attributed to Newman, Strogatz and Watts (2001), then metadata only, and Pastor-Satorras et al. (2015), abstract only. The Newman abstract, read at M4, covers the giant-component transition but does not state the expression. | Expression presented as a definition; citations qualified with their verification levels. |
| 3 | EXP-001 report, section 3 | "The IC and LT definitions follow Kempe, Kleinberg and Tardos (2003)." The journal-version abstract, read at M4, does not name IC or LT. | Qualified; the definitions rest on the protocol. Watts (2002) full text opened at M4 (level F). |
| 4 | EXP-003 report, section 3 | Granovetter (1978) and Centola and Macy (2007), both metadata only, were cited as support for the LT background. | Restated as attributions; the threshold rule is now quoted from Watts (2002). |
| 5 | `research/experiment_registry.csv` | Statuses still said "report.md not written (tool refusal)" and, for EXP-004, "S1 cross-reading unresolved (owner)". Both were stale after D-013. | Statuses updated. |
| 6 | `research/claims_register.csv` | No result id, figure or table, or section columns. No rows for the secondary, descriptive, synthesis or external claims used in the reports. | Schema extended and rows generated (575 rows; `claims_audit.md`). |
| 7 | `research/publication/claims_audit.md` | Still the unchecked M0 checklist. | Completed. |
| 8 | `research/literature_review.md` | Verification levels predated the M4 re-reads. | Levels updated (Newman 2001: A; Watts 2002: F; Kempe 2015: A), with an M4 verification section. |

No frozen protocol, config, seed, raw result or confirmatory table changed. No verdict changed.

## 5. External claims

| source | level actually read | what the manuscript uses it for | status |
|---|---|---|---|
| Pastor-Satorras and Vespignani 2001 | abstract | no epidemic threshold on scale-free networks (context) | supported at abstract level |
| Newman, Strogatz and Watts 2001 | abstract (M4) | theory of random graphs with arbitrary degree distributions | supported at abstract level; threshold expression not attributed |
| Pastor-Satorras et al. 2015 | abstract | review (context) | supported at abstract level |
| Barabasi and Albert 1999 | abstract | preferential attachment generates heavy tails | supported at abstract level |
| Kitsak et al. 2010 | abstract | k-core spreaders (future work) | supported at abstract level |
| Kempe et al. 2015 (journal version of 2003) | abstract (M4) | influence maximisation under widely studied models | supported; IC definition does not rest on it |
| Watts 2002 | full text (M4) | fractional threshold rule; cascade window and average degree | supported |
| Watts and Strogatz 1998; Gilbert 1959; Granovetter 1978; Centola and Macy 2007; Goel et al. 2016; Salganik et al. 2006 | metadata only | attributions only | labelled "metadata only" in the manuscript references |
| Maier and Brockmann 2017 | not read (data citation requested by the data set's author) | data citation | labelled |
| networkx 3.7 documentation; BFMaierFBnetwork repository files | opened (M0, M1) | generators; data licence | supported |

The re-reads used a summarising web fetch. Quotations are limited to short phrases.

## 6. Strength and scope of evidence for each conclusion

| conclusion | evidence | strength | scope |
|---|---|---|---|
| Topology changes IC final size at matched `N`, `<k>` and `p`, by more than 0.02 in 7 of 14 conditions | EXP-002, frozen, R = 120, Holm | strong within the model (intervals far from the SESOI bounds) | `N = 1000`, `<k> = 6`, WS `beta = 0.1`, BA `m = 3`, one random seed, simulation |
| The sign of both contrasts changes with `p` | EXP-002; S3, S4 | strong within the model | same |
| The BA advantage at `p` 0.15 and 0.20 is a degree-sequence effect | S2 equivalence, R = 30 | moderate (one randomisation scheme; upper bound +0.0158 at `p = 0.20`) | BA, `m = 3` |
| Edge mismatch and size 500 to 2000 do not explain the pattern | S3, S4 | strong for these factors; S3 shares graphs with EXP-002 | the tested range only |
| Rescaling by `p_c(G)` equalises the topologies only at `c` <= 1 | S1, per multiplier | descriptive only (no overall verdict, D-013) | tree-like estimate |
| The WS ordering reverses under LT | EXP-003 grid mean | strong for the grid mean; grid-dependent | `phi` 0.18 to 0.30, ten random seeds |
| On one real network, structure beyond the degree sequence lowers IC spread | EXP-005 | strong conditional on this network | one 362-node network; not a sample |
| WS deficit at `p = 0.30` is structural beyond degree; component structure explains little of the EXP-005 deficit; BA restrains LT cascades relative to its randomisation | X1 to X3 | exploratory, post hoc | R = 30, unadjusted |

## 7. Gate assessment (M4)

- **Numerical claims.** Every numerical claim in the manuscript, supplementary file and reports maps to a result id, a config hash and a figure or table: the claims register plus `number_trace.csv`, with 0 untraced decimals.
- **External claims.** Every external claim maps to a source actually opened, at the level stated.
- **Unsupported claims.** Unsupported external attributions were qualified (section 4, items 2 to 4).

The M4 gate holds.

## 8. M6 update (2026-11-25): literature levels, references and links

Free arXiv or author copies of four sources were downloaded and their text extracted locally with pypdf (no paid access, no login). Levels in section 5 change as follows; the manuscript section 2, its reference list, `references.bib` and `research/literature_review.md` (M6 update) record them.

| source | level now | what was checked | where |
|---|---|---|---|
| Kempe, Kleinberg and Tardos 2003 (conference version) | full text | the Independent Cascade model: a newly active node "is given a single chance to activate each currently inactive neighbor" with a given probability; matches the study's IC with one common `p` | section 1, page 2 |
| Pastor-Satorras et al. 2015 | section IV.C in full, rest at abstract level | `p_c = <k>/(<k^2> - <k>)` for bond percolation on degree-uncorrelated networks without loops; the manuscript now cites this section for the expression | Eq. (18), page 15 of the arXiv preprint |
| Newman, Strogatz and Watts 2001 | full text | giant component exists if and only if the sum of `k(k - 2) p_k` is positive; the paper does not state the bond-percolation threshold, so the expression is not attributed to it | section II.D, Eq. (33), page 6 of the arXiv preprint |
| Barabasi and Albert 1999 | full text (arXiv preprint) | preferential attachment gives a power-law degree distribution, exponent 2.9 plus or minus 0.1 | page 5, Fig. 2A |

Unchanged: Watts 2002 (full text); Pastor-Satorras and Vespignani 2001 and Kitsak et al. 2010 (abstract); Watts and Strogatz 1998, Gilbert 1959 (Project Euclid returned no text to the fetch tool), Granovetter 1978, Centola and Macy 2007, Goel et al. 2016 and Salganik et al. 2006 (metadata only, attributions); Maier and Brockmann 2017 (not read, data citation). Totals for the 14 entries of `references.bib`: 5 read in full (one of them for the cited section only), 2 abstract only, 7 metadata only or not read (unverified for content). No claim depends on an unverified source beyond attribution.

`scripts/check_links.py` checks that every `references.bib` entry is in the manuscript reference list and the reverse (14 of 14), and that every relative Markdown link resolves (49 links, 0 broken). After the manuscript edits, `scripts/audit_evidence.py` traced every number again: `decimal_untraced` 0. An arXiv identifier written in the reference list was first reported as an untraced decimal and was replaced by a pointer to `references.bib`.
