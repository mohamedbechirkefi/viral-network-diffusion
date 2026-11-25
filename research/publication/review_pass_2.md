<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Second review pass: arguing against the preferred reading (M4, 2026-11-25)

**Scope.** This pass reviews manuscript version 0.1 (M4 draft), the five experiment reports (version 1.1) and the M4 exploratory checks. It is internal quality control by the AI assistant, not peer review. It does not polish the writing. It tries to break the preferred reading of the study.

**The preferred reading under challenge.** At matched size, density and `p`, topology changes IC final size. The sign depends on where each graph's threshold sits relative to `p`. The BA advantage near threshold is a degree-sequence effect, and the WS ordering reverses under a threshold rule.

Each challenge below gives the strongest alternative, the evidence, a judgement (**holds**, **holds in part** or **does not hold**) and the change it caused. Section B lists the changes made to the manuscript.

## A. Challenges

### A1. The title and abstract assert a mechanism the study did not test

- **Challenge.** The draft title, "Where the threshold sits", and the abstract's last sentence present a threshold-location mechanism as the finding.
- **Evidence against that mechanism.** S1 tested it and produced no overall verdict (D-013). Above threshold, rescaling by `p_c(G)` leaves large differences (BA - ER -0.6147 at `c = 3`). The largest WS effect is not a degree-moment effect in the exploratory X1 check. Under LT, the WS ordering reverses.
- **Judgement: holds.** The threshold-location account fits BA near threshold only.
- **Change.** The title is now descriptive. The abstract's conclusion names `p` and the contagion rule, not a mechanism. Section 6.2 labels the threshold-location account as a model-dependent reading and states where it fails.

### A2. "13 of 14 rejected" is a power artefact, not a finding

- **Challenge.** With 120 matched sets and common random numbers, the design rejects differences as small as 3.27e-05. Leading with the rejection count overstates the evidence.
- **Evidence.** 6 of the 13 rejections have intervals inside the SESOI.
- **Judgement: holds.** The defensible count is 7 of 14 contrasts outside the SESOI.
- **Change.** The abstract and conclusion now lead with "7 of 14 exceed the SESOI" and give the rejection count second.

### A3. An absolute SESOI hides large relative effects at small `p`

- **Challenge.** A SESOI of 0.02 in `S` calls every difference at small `p` negligible, even a large relative one. For example, at `p = 0.10`, mean `S` is 0.0084 for BA against 0.0025 for ER, yet the contrast lies "inside the SESOI".
- **Judgement: holds.** This is a property of the frozen SESOI, not an error, but readers must be told.
- **Change.** A sentence in section 5.1 and a limitation bullet now say that "inside the SESOI" means small in absolute terms only.

### A4. The confirmatory run largely re-observed a pattern already seen in the pilot

- **Challenge.** The per-`p` primary analysis and `R = 120` were chosen after pilot values had been seen (freeze record C4), and the confirmatory values are close to them. For WS - ER at `p = 0.30`, the pilot gave -0.3564 and the confirmatory run -0.3529. The test therefore did not confirm a prediction made blind. It replicated a known pattern with a new seed.
- **Judgement: holds.** New seeds protect against seed-specific noise, not against design choices informed by the pilot.
- **Change.** Section 7 and section 6.5 now say that the confirmatory results replicate the pilot pattern on new seeds, and that the frozen design was informed by it.

### A5. S3 and S2 are not independent replications of EXP-002

- **Challenge.** S2 and S3 reuse EXP-002 replicates 0 to 29 (BA graphs as-is; ER and WS graphs trimmed) and share the cascade streams, so their agreement with EXP-002 is partly built in. S4 uses new graphs.
- **Judgement: holds in part.**
  - S3 still answers its question: does removing 9 edges matter?
  - The agreement is not independent evidence that the pattern is robust. S4, and X1 on fresh seeds, are the closer replications.
- **Change.** Section 5.2 now states that S2 and S3 reuse the EXP-002 graphs, and that S4 and X1 are the independent replications.

### A6. "Carried by the degree sequence" may overstate S2

- **Challenge.** S2 shows that BA and `ba_dpr` are within 0.02 at `p` 0.15 and 0.20. It does not show that `ba_dpr` and ER differ by the full EXP-002 amount, and its intervals are wide (R = 30).
- **Evidence.** Because `BA - ER = (BA - ba_dpr) + (ba_dpr - ER)`, the S2 interval bounds the part of the BA advantage not carried by the degree sequence. At `p = 0.20` that part is at most +0.0158, the upper S2 bound, against an EXP-002 effect of +0.0969.
- **Judgement: does not hold** as a refutation. The wording is supported within the SESOI.
- **Change.** The bound is now stated in section 5.2.

### A7. The WS mechanism is over-read

- **Challenge.** The draft said that "the clustered ring structure delays the IC outbreak". X1 removes clustering and ring order together, it is exploratory, and the study measured no outbreak timing as a mechanism.
- **Judgement: holds.**
- **Change.** Section 6.2 now says that the X1 deficit comes from structure beyond the degree sequence, which X1 cannot attribute to clustering or to ring order.

### A8. Overgeneralisation of the model-dependence result

- **Challenge.** The draft's "practical lesson for anyone modelling diffusion" generalises from one `beta`, one `m`, one mean degree and one threshold rule.
- **Judgement: holds.**
- **Change.** The statement is now restricted to the families and parameters tested, and phrased as a caution, not a rule.

### A9. The real-network test is narrower than its replicate count suggests

- **Challenge.** EXP-005's 120 "replicates" of the real arm are cascade batches on one fixed graph. The intervals carry cascade and null-graph variation, not uncertainty about the network. "11 of 14 rejected" is a statement about one 362-node friendship circle.
- **Judgement: does not hold** against the manuscript, which already states this in sections 5.4 and 7. No change beyond the abstract's "one real 362-node friendship network".

### A10. The EXP-005 deficit could be a component artefact

- **Challenge.** The real network has a smaller giant component than its randomisations (0.9088 against 0.9608).
- **Evidence.** The exploratory X2 check keeps most of the deficit (-0.1177) after conditioning on giant-component seeds and normalising.
- **Judgement: does not hold** as an explanation of the whole deficit. The remainder is still not attributed to clustering specifically; degree correlations are an alternative, and X2 cannot separate them.
- **Change.** Section 5.5 names degree correlations as an alternative.

### A11. Multiplicity across the study

- **Challenge.** Holm controls the error rate within each family (8 families, 89 primary tests including the optional S4). There is no study-wide correction, and the secondary and exploratory estimates are unadjusted.
- **Evidence.** Almost every rejection has Holm p < 1e-4, so a study-wide correction would change few decisions. That was not computed, however.
- **Judgement: holds in part.**
- **Change.** A limitation bullet states that control is per family only.

### A12. Stale figures, leakage and missing runs

- **Stale figures.** `scripts/audit_evidence.py` checked all 129 committed result files against `MANIFEST.sha256`. It checked 56 experiment-folder copies (figures, metrics, configs and run manifests) against their originals. It found 0 mismatches, and the manuscript figures point at those files. **Does not hold.**
- **Leakage.** No held-out data exist in this design. The EXP-005 calibration uses the degree sequence only, and the analysis code was committed before any confirmatory output. The pilot exposure is challenge A4. **Does not hold** beyond A4.
- **Missing failed runs.** No confirmatory run failed, was retried or was dropped (run manifests, exit status 0). The exploratory M4 script was executed three times. The first two executions were superseded: one before X3 was added, and one with untracked outputs of the first in the tree. The committed outputs come from the third execution on a clean tree at revision `4ed1942`. **Holds in part:** this is now disclosed in the journal and in the evidence audit.

### A13. Content quality is still not separated from structure in any real sense

- **Challenge.** Holding `p` fixed makes "content quality" a constant by construction. The study cannot say anything about how quality and structure interact.
- **Judgement: does not hold** against the manuscript. Section 1 states that quality is held fixed and not modelled, and limitations repeat it. No change.

## B. Changes made to the manuscript (version 0.1 to 0.2)

| challenge | location | change |
|---|---|---|
| A1 | title; abstract; 6.2 | Descriptive title. The abstract conclusion no longer names a threshold-location mechanism. 6.2 labels that account as model-dependent and states where it fails. |
| A2 | abstract; 9 | The count outside the SESOI (7 of 14) leads; the rejection count follows. |
| A3 | 5.1; 7 | "Inside the SESOI" is explained as small in absolute terms only, with the `p = 0.10` example. |
| A4 | 6.5; 7 | States that the confirmatory results replicate the pilot pattern on new seeds. |
| A5 | 5.2 | States that S2 and S3 reuse EXP-002 graphs and streams; S4 and X1 are the independent replications. |
| A6 | 5.2 | Bound on the non-degree part of the BA advantage at `p = 0.20` (at most +0.0158). |
| A7 | 6.2 | The WS mechanism sentence is replaced by what X1 can and cannot attribute. |
| A8 | 6.3 | The general lesson is restricted to the tested families and parameters. |
| A10 | 5.5 | Degree correlations named as an alternative for the X2 remainder. |
| A11 | 7 | Limitation on per-family error control. |
| A12 | journal; evidence audit | Superseded exploratory executions disclosed. |

No frozen verdict changed. No number changed, except the EXP-004 runtime correction recorded in `research/publication/evidence_audit.md`.
