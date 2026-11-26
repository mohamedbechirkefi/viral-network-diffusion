<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Supplementary material

Companion to `research/paper/manuscript.md` (version 0.2, M4, 2026-11-25). Independent research manuscript / preprint draft, not peer-reviewed. Author: Mohamed Bechir Kefi, independent researcher. All results are simulations. Every number below is traced by `scripts/audit_evidence.py` (`research/publication/number_trace.csv`).

## S1. Complete experimental matrix

| experiment | model | topologies | parameter grid | exposure (seed rule x count) | R | C | master seed | cascades |
|------------|------|----------|--------------------------|--------------|-----|-----|----------|------------|
| EXP-001 smoke (exploratory) | IC, LT | ER, WS, BA | IC `p` in {0, 0.05, 0.20, 1}; LT `phi` in {0, 0.18, 1.01} | random x 1 | 5 | 50 | 20261124 | 5,250 per smoke run |
| EXP-002 | IC | ER, WS, BA | `p` in {0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50} | {random, highest degree} x {1, 10} | 120 | 200 | 20261125 | 2,016,000 |
| EXP-003 | LT | ER, WS, BA | `phi` in {0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30} | {random, highest degree} x {1, 10} | 30 | 200 | 20261126 | 504,000 |
| EXP-004 S1 | IC | ER, WS, BA | `p = min(1, c p_c(G))`, `c` in {0.5, 1, 1.5, 2, 3} | random x 1 | 30 | 200 | 20261125 | 90,000 |
| EXP-004 S2 | IC | BA, ba_dpr | EXP-002 grid | random x 1 | 30 | 200 | 20261125 | 84,000 |
| EXP-004 S3 | IC | er_trim, ws_trim, BA | EXP-002 grid | random x 1 | 30 | 200 | 20261125 | 126,000 |
| EXP-004 S4 (optional) | IC | ER, WS, BA at `N` = 500 and 2000 | EXP-002 grid | random x 1 | 30 | 200 | 20261125 | 126,000 per size |
| EXP-005 | IC | real, real_er, real_dpr | `p` in {0.005806, 0.014516, 0.029031, 0.043547, 0.058062, 0.087093, 0.145155} | random x 1 | 120 | 200 | 20261128 | 504,000 |
| M4 X1 (exploratory) | IC | ER, WS, ws_dpr | EXP-002 grid | random x 1 | 30 | 200 | 20261201 | not stored per cascade |
| M4 X2 (exploratory) | IC | real, real_dpr | EXP-005 grid | random x 1 | 30 | 200 | 20261202 | not stored per cascade |
| M4 X3 (exploratory) | LT | ER, WS, ws_dpr, BA, ba_dpr | EXP-003 grid | random x 10 | 30 | 200 | 20261203 | not stored per cascade |

For EXP-003 the highest-degree rule is deterministic given the graph, so its cells repeat identical cascades; the counts above are the configured ones. The primary analysis of each experiment uses only the cells named in manuscript section 4.4.

## S2. Extended tables

### S2.1 EXP-002 absolute levels (IC, one random seed)

Mean over 120 replicates of per-graph mean `S` (`topology_means.csv`; claims EXP-002-LVL rows).

| `p` | ER | WS | BA |
|---|---|---|---|
| 0.02 | 0.0011 | 0.0011 | 0.0012 |
| 0.05 | 0.0014 | 0.0014 | 0.0017 |
| 0.10 | 0.0025 | 0.0021 | 0.0084 |
| 0.15 | 0.0079 | 0.0036 | 0.0683 |
| 0.20 | 0.0957 | 0.0073 | 0.1926 |
| 0.30 | 0.5352 | 0.1823 | 0.4769 |
| 0.50 | 0.8839 | 0.9471 | 0.8481 |

### S2.2 Grid means by exposure condition (secondary, unadjusted 95 percent)

| experiment | exposure | WS - ER | BA - ER |
|---|---|---|---|
| EXP-002 (IC) | random, single seed | -0.0547 [-0.0557, -0.0536] | +0.0099 [+0.0087, +0.0112] |
| EXP-002 (IC) | highest-degree, single seed | -0.0905 [-0.0915, -0.0895] | +0.0707 [+0.0699, +0.0714] |
| EXP-002 (IC) | highest-degree, ten seeds | -0.0794 [-0.0799, -0.0788] | +0.0451 [+0.0447, +0.0455] |
| EXP-002 (IC) | ten random seeds | -0.0740 [-0.0746, -0.0735] | +0.0421 [+0.0418, +0.0425] |
| EXP-003 (LT) | random, single seed | +0.1233 [+0.1150, +0.1316] | -0.0083 [-0.0185, +0.0021] |
| EXP-003 (LT) | highest-degree, single seed | +0.0459 [+0.0045, +0.0887] | +0.3374 [+0.2917, +0.3854] |
| EXP-003 (LT) | highest-degree, ten seeds | +0.2718 [+0.2456, +0.2963] | +0.4253 [+0.4208, +0.4305] |

The EXP-003 primary (ten random seeds) is in manuscript Table 5. All per-`p` and per-`phi` secondary estimates, including depth, time to half, Gini and large-cascade share, are in the `secondary_contrasts.csv` file of each run.

### S2.3 EXP-005 absolute levels (IC, one random seed)

| `p` | real | real_er | real_dpr |
|---|---|---|---|
| 0.005806 | 0.0030 | 0.0030 | 0.0030 |
| 0.014516 | 0.0034 | 0.0033 | 0.0034 |
| 0.029031 | 0.0048 | 0.0041 | 0.0048 |
| 0.043547 | 0.0088 | 0.0053 | 0.0096 |
| 0.058062 | 0.0180 | 0.0075 | 0.0270 |
| 0.087093 | 0.0642 | 0.0257 | 0.1330 |
| 0.145155 | 0.1996 | 0.4076 | 0.3313 |

Secondary grid means (unadjusted 95 percent): real - real_er -0.0221 [-0.0228, -0.0213]; real - real_dpr -0.0300 [-0.0308, -0.0293].

## S3. Configurations and hashes

| item | path | file SHA-256 (prefix) | canonical config hash (prefix) | run id |
|-----------|-----------------------|---------------|---------------|----------------------------------|
| study protocol v1.0 | `research/protocol.md` | d984f2f8f2fb | not applicable | not applicable |
| EXP-002 config | `experiments/EXP-002/config.json` | 3a1cd795beb8 | 2c7febb68d11 | EXP-002-20261124T233447Z-2c7febb6 |
| EXP-003 config | `experiments/EXP-003/config.json` | 728f9a314357 | a2d668abb8f1 | EXP-003-20261124T234212Z-a2d668ab |
| EXP-004 S1 | `experiments/EXP-004/S1-config.json` | 17f64abe4ef7 | de14a4b374f2 | EXP-004-20261124T233447Z-de14a4b3 |
| EXP-004 S2 | `experiments/EXP-004/S2-config.json` | 42fd53afd45e | 916e8d290508 | EXP-004-20261124T233637Z-916e8d29 |
| EXP-004 S3 | `experiments/EXP-004/S3-config.json` | 9d0aaf2b4e76 | e1d240911d90 | EXP-004-20261124T233755Z-e1d24091 |
| EXP-004 S4 N = 500 | `experiments/EXP-004/S4-n500-config.json` | 6e91910ff329 | e31dba07eb68 | EXP-004-20261124T235044Z-e31dba07 |
| EXP-004 S4 N = 2000 | `experiments/EXP-004/S4-n2000-config.json` | b9cf372f65aa | 40385ec33b30 | EXP-004-20261124T235110Z-40385ec3 |
| EXP-005 config | `experiments/EXP-005/config.json` | 06b507e45eef | d277f271e686 | EXP-005-20261124T233932Z-d277f271 |
| M4 exploratory | `scripts/exploratory_m4.py` | script constants | not applicable | code revision 4ed1942 |

Full hashes, the experiment protocol hashes and the data manifest hash are in `research/freeze.json`. All confirmatory runs used code revision `32961c3` with a clean tree.

## S4. Robustness results

### S4.1 EXP-004 S3, exact edge matching (Holm over 14; R = 30)

| `p` | ws_trim - er_trim | BA - er_trim |
|---|---|---|
| 0.02 | -0.0000 [-0.0000, +0.0000], not rejected | +0.0000 [+0.0000, +0.0000] |
| 0.05 | -0.0000 [-0.0000, -0.0000] | +0.0003 [+0.0002, +0.0004] |
| 0.10 | -0.0004 [-0.0004, -0.0003] | +0.0060 [+0.0052, +0.0068] |
| 0.15 | -0.0041 [-0.0045, -0.0037] | +0.0616 [+0.0571, +0.0664] |
| 0.20 | -0.0833 [-0.0883, -0.0785] | +0.0985 [+0.0883, +0.1074] |
| 0.30 | -0.3597 [-0.3747, -0.3434] | -0.0565 [-0.0737, -0.0402] |
| 0.50 | +0.0574 [+0.0502, +0.0643] | -0.0433 [-0.0544, -0.0319] |

Every contrast except ws_trim - er_trim at 0.02 is rejected. Claims EXP-004-S3-R01 to R14.

### S4.2 EXP-004 S4, size (optional; Holm over 14 per size; R = 30)

| `p` | WS - ER, N = 500 | BA - ER, N = 500 | WS - ER, N = 2000 | BA - ER, N = 2000 |
|---|---|---|---|---|
| 0.02 | -0.0000 [-0.0000, +0.0000] n.r. | +0.0000 [+0.0000, +0.0001] | -0.0000 [-0.0000, +0.0000] n.r. | +0.0000 [+0.0000, +0.0000] |
| 0.05 | -0.0001 [-0.0001, -0.0000] | +0.0004 [+0.0003, +0.0005] | -0.0000 [-0.0000, -0.0000] | +0.0002 [+0.0002, +0.0002] |
| 0.10 | -0.0007 [-0.0009, -0.0006] | +0.0061 [+0.0052, +0.0071] | -0.0002 [-0.0002, -0.0002] | +0.0061 [+0.0052, +0.0068] |
| 0.15 | -0.0073 [-0.0083, -0.0064] | +0.0524 [+0.0476, +0.0574] | -0.0024 [-0.0026, -0.0021] | +0.0611 [+0.0559, +0.0664] |
| 0.20 | -0.0849 [-0.0893, -0.0806] | +0.0920 [+0.0823, +0.1019] | -0.0895 [-0.0934, -0.0851] | +0.0964 [+0.0886, +0.1046] |
| 0.30 | -0.3355 [-0.3507, -0.3223] | -0.0497 [-0.0670, -0.0329] | -0.3578 [-0.3726, -0.3428] | -0.0536 [-0.0712, -0.0357] |
| 0.50 | +0.0562 [+0.0467, +0.0655] | -0.0466 [-0.0601, -0.0328] | +0.0593 [+0.0505, +0.0684] | -0.0445 [-0.0576, -0.0333] |

"n.r." means not rejected. Claims EXP-004-S4-n500 and EXP-004-S4-n2000 rows.

### S4.3 M4 exploratory checks, every row (EXPLORATORY, post hoc, unadjusted)

Source: `results/exploratory/M4/m4_exploratory_contrasts.csv` (generator `scripts/exploratory_m4.py`, revision 4ed1942, clean tree). "mean A" and "mean B" are the mean `S` (or, for X2 `S_giant_norm`, the mean over giant-seeded cascades of size divided by giant-component size) of the two arms. Claims M4-X1-01 to M4-X1-21, M4-X2-01 to M4-X2-14 and M4-X3-01 to M4-X3-42.

| check | contrast | metric | parameter | mean A | mean B | difference [95 percent, unadjusted] |
|---|---|---|---|---|---|---|
| X1 | ws - ws_dpr | S | p = 0.02 | 0.0011 | 0.0011 | +1.67e-06 [-1.33e-06, +4.83e-06] |
| X1 | ws - ws_dpr | S | p = 0.05 | 0.0014 | 0.0014 | -1.27e-05 [-2.07e-05, -4.83e-06] |
| X1 | ws - ws_dpr | S | p = 0.1 | 0.0021 | 0.0022 | -0.0001 [-0.0001, -8.95e-05] |
| X1 | ws - ws_dpr | S | p = 0.15 | 0.0036 | 0.0048 | -0.0012 [-0.0013, -0.0010] |
| X1 | ws - ws_dpr | S | p = 0.2 | 0.0073 | 0.0285 | -0.0212 [-0.0224, -0.0199] |
| X1 | ws - ws_dpr | S | p = 0.3 | 0.1870 | 0.5531 | -0.3662 [-0.3750, -0.3573] |
| X1 | ws - ws_dpr | S | p = 0.5 | 0.9433 | 0.9551 | -0.0119 [-0.0169, -0.0067] |
| X1 | ws_dpr - er | S | p = 0.02 | 0.0011 | 0.0011 | -3.33e-06 [-7.00e-06, -1.67e-07] |
| X1 | ws_dpr - er | S | p = 0.05 | 0.0014 | 0.0014 | -2.17e-05 [-3.30e-05, -1.15e-05] |
| X1 | ws_dpr - er | S | p = 0.1 | 0.0022 | 0.0024 | -0.0002 [-0.0003, -0.0002] |
| X1 | ws_dpr - er | S | p = 0.15 | 0.0048 | 0.0079 | -0.0032 [-0.0035, -0.0028] |
| X1 | ws_dpr - er | S | p = 0.2 | 0.0285 | 0.0984 | -0.0699 [-0.0742, -0.0657] |
| X1 | ws_dpr - er | S | p = 0.3 | 0.5531 | 0.5394 | +0.0137 [+0.0030, +0.0246] |
| X1 | ws_dpr - er | S | p = 0.5 | 0.9551 | 0.8842 | +0.0709 [+0.0634, +0.0779] |
| X1 | ws - er | S | p = 0.02 | 0.0011 | 0.0011 | -1.67e-06 [-4.67e-06, +1.17e-06] |
| X1 | ws - er | S | p = 0.05 | 0.0014 | 0.0014 | -3.43e-05 [-4.63e-05, -2.32e-05] |
| X1 | ws - er | S | p = 0.1 | 0.0021 | 0.0024 | -0.0003 [-0.0004, -0.0003] |
| X1 | ws - er | S | p = 0.15 | 0.0036 | 0.0079 | -0.0043 [-0.0047, -0.0040] |
| X1 | ws - er | S | p = 0.2 | 0.0073 | 0.0984 | -0.0911 [-0.0952, -0.0868] |
| X1 | ws - er | S | p = 0.3 | 0.1870 | 0.5394 | -0.3524 [-0.3619, -0.3426] |
| X1 | ws - er | S | p = 0.5 | 0.9433 | 0.8842 | +0.0590 [+0.0522, +0.0659] |
| X2 | real - real_dpr | S | p = 0.005806 | 0.0030 | 0.0029 | +8.75e-06 [+9.21e-07, +1.70e-05] |
| X2 | real - real_dpr | S | p = 0.014516 | 0.0034 | 0.0034 | +4.60e-07 [-3.73e-05, +4.01e-05] |
| X2 | real - real_dpr | S | p = 0.029031 | 0.0047 | 0.0048 | -3.04e-05 [-0.0002, +9.16e-05] |
| X2 | real - real_dpr | S | p = 0.043547 | 0.0085 | 0.0093 | -0.0008 [-0.0012, -0.0004] |
| X2 | real - real_dpr | S | p = 0.058062 | 0.0183 | 0.0264 | -0.0081 [-0.0092, -0.0070] |
| X2 | real - real_dpr | S | p = 0.087093 | 0.0620 | 0.1326 | -0.0706 [-0.0760, -0.0650] |
| X2 | real - real_dpr | S | p = 0.145155 | 0.2006 | 0.3315 | -0.1309 [-0.1387, -0.1231] |
| X2 | real - real_dpr | S_giant_norm | p = 0.005806 | 0.0033 | 0.0031 | +0.0002 [+0.0002, +0.0002] |
| X2 | real - real_dpr | S_giant_norm | p = 0.014516 | 0.0038 | 0.0036 | +0.0002 [+0.0002, +0.0003] |
| X2 | real - real_dpr | S_giant_norm | p = 0.029031 | 0.0054 | 0.0051 | +0.0003 [+0.0002, +0.0005] |
| X2 | real - real_dpr | S_giant_norm | p = 0.043547 | 0.0100 | 0.0100 | +2.07e-05 [-0.0004, +0.0005] |
| X2 | real - real_dpr | S_giant_norm | p = 0.058062 | 0.0218 | 0.0285 | -0.0067 [-0.0079, -0.0055] |
| X2 | real - real_dpr | S_giant_norm | p = 0.087093 | 0.0750 | 0.1437 | -0.0687 [-0.0748, -0.0625] |
| X2 | real - real_dpr | S_giant_norm | p = 0.145155 | 0.2405 | 0.3582 | -0.1177 [-0.1259, -0.1100] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.18 | 1.0000 | 0.9224 | +0.0776 [+0.0572, +0.1019] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.2 | 1.0000 | 0.9213 | +0.0787 [+0.0610, +0.0995] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.22 | 0.7548 | 0.0127 | +0.7420 [+0.7229, +0.7614] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.24 | 0.7634 | 0.0127 | +0.7506 [+0.7344, +0.7680] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.26 | 0.5252 | 0.0116 | +0.5137 [+0.5004, +0.5269] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.28 | 0.5397 | 0.0116 | +0.5280 [+0.5146, +0.5406] |
| X3 | ws - ws_dpr | S (LT, 10 random seeds) | phi = 0.3 | 0.2755 | 0.0111 | +0.2644 [+0.2448, +0.2841] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.18 | 0.9224 | 0.9973 | -0.0749 [-0.0991, -0.0543] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.2 | 0.9213 | 0.9974 | -0.0761 [-0.0979, -0.0582] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.22 | 0.0127 | 0.2244 | -0.2117 [-0.2351, -0.1904] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.24 | 0.0127 | 0.0643 | -0.0515 [-0.0604, -0.0434] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.26 | 0.0116 | 0.0152 | -0.0036 [-0.0038, -0.0034] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.28 | 0.0116 | 0.0153 | -0.0037 [-0.0038, -0.0035] |
| X3 | ws_dpr - er | S (LT, 10 random seeds) | phi = 0.3 | 0.0111 | 0.0147 | -0.0036 [-0.0037, -0.0035] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.18 | 1.0000 | 0.9973 | +0.0027 [+0.0021, +0.0034] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.2 | 1.0000 | 0.9974 | +0.0026 [+0.0020, +0.0031] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.22 | 0.7548 | 0.2244 | +0.5304 [+0.5011, +0.5619] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.24 | 0.7634 | 0.0643 | +0.6991 [+0.6808, +0.7179] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.26 | 0.5252 | 0.0152 | +0.5101 [+0.4971, +0.5234] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.28 | 0.5397 | 0.0153 | +0.5244 [+0.5114, +0.5370] |
| X3 | ws - er | S (LT, 10 random seeds) | phi = 0.3 | 0.2755 | 0.0147 | +0.2608 [+0.2412, +0.2806] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.18 | 0.9976 | 1.0000 | -0.0024 [-0.0040, -0.0011] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.2 | 0.9958 | 1.0000 | -0.0042 [-0.0062, -0.0024] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.22 | 0.3567 | 0.8017 | -0.4450 [-0.4761, -0.4126] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.24 | 0.1974 | 0.6664 | -0.4691 [-0.5160, -0.4238] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.26 | 0.0239 | 0.0323 | -0.0084 [-0.0090, -0.0077] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.28 | 0.0239 | 0.0324 | -0.0085 [-0.0094, -0.0077] |
| X3 | ba - ba_dpr | S (LT, 10 random seeds) | phi = 0.3 | 0.0229 | 0.0307 | -0.0079 [-0.0085, -0.0073] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.18 | 1.0000 | 0.9973 | +0.0027 [+0.0021, +0.0034] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.2 | 1.0000 | 0.9974 | +0.0026 [+0.0020, +0.0031] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.22 | 0.8017 | 0.2244 | +0.5773 [+0.5385, +0.6148] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.24 | 0.6664 | 0.0643 | +0.6022 [+0.5559, +0.6474] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.26 | 0.0323 | 0.0152 | +0.0171 [+0.0164, +0.0178] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.28 | 0.0324 | 0.0153 | +0.0171 [+0.0161, +0.0183] |
| X3 | ba_dpr - er | S (LT, 10 random seeds) | phi = 0.3 | 0.0307 | 0.0147 | +0.0160 [+0.0154, +0.0167] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.18 | 0.9976 | 0.9973 | +0.0003 [-0.0015, +0.0019] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.2 | 0.9958 | 0.9974 | -0.0016 [-0.0037, +0.0003] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.22 | 0.3567 | 0.2244 | +0.1323 [+0.1031, +0.1601] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.24 | 0.1974 | 0.0643 | +0.1331 [+0.1171, +0.1485] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.26 | 0.0239 | 0.0152 | +0.0088 [+0.0084, +0.0091] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.28 | 0.0239 | 0.0153 | +0.0086 [+0.0081, +0.0092] |
| X3 | ba - er | S (LT, 10 random seeds) | phi = 0.3 | 0.0229 | 0.0147 | +0.0082 [+0.0079, +0.0085] |

## S5. Experiment reports

| experiment | report | reproduction | status |
|---|---|---|---|
| EXP-001 | `research/experiments/EXP-001/report.md` | `research/experiments/EXP-001/reproduction.md` | exploratory, complete |
| EXP-002 | `research/experiments/EXP-002/report.md` | `research/experiments/EXP-002/reproduction.md` | confirmatory, complete |
| EXP-003 | `research/experiments/EXP-003/report.md` | `research/experiments/EXP-003/reproduction.md` | confirmatory, complete |
| EXP-004 | `research/experiments/EXP-004/report.md` | `research/experiments/EXP-004/reproduction.md` | confirmatory, complete (S4 optional, run) |
| EXP-005 | `research/experiments/EXP-005/report.md` | `research/experiments/EXP-005/reproduction.md` | confirmatory, complete |

Each report also exists as `report.pdf` in the same folder, built at M6 by `scripts/build_pdfs.py`.

## S6. Deviations from the frozen protocol and owner decisions

| id | date | what | kind | record |
|-------------|-----------|-------------------------------------------|---------------|--------------------|
| C4 | 2026-11-24 | Pilot values of the primary contrast were seen at R = 10 before the freeze; they motivated the per-`p` primary analysis, R = 120 and the EXP-003 grid | disclosure (pre-freeze) | `research/freeze.json`; D-007, D-009 |
| amendments | 2026-11-24 | Per-`p` primary family, R = 120, new master seeds, threshold grid 0.18 to 0.30, Holm interval method, real-network second test | owner-approved pre-freeze amendments | protocol section 11; D-009, D-010 |
| ratification | 2026-11-24 | Real network and the session's interval construction, per-multiplier S1 criterion and configs ratified | owner decision | D-011 |
| M3-1 | 2026-11-25 | Raw results stored in git-ignored `results/raw/confirmatory/` with SHA-256 committed | storage, not design | D-012 |
| M3-analysis | 2026-11-25 | Frozen inferential analysis produced by `scripts/analyse_confirmatory.py` rather than `viral report` (which produces the descriptive tables) | tooling, not design | D-012 |
| M3-2 | 2026-11-25 | S1 reported per multiplier, no overall verdict, no multiplier picked after the data | owner decision | D-013 |
| M3-3 | 2026-11-25 | Experiment reports written after the runs from committed files only | owner decision | D-013 |
| M4-1 | 2026-11-25 | Exploratory confounder checks X1 to X3 added after the confirmatory results were seen; they never change a frozen verdict | exploratory addition | D-014 |
| M4-2 | 2026-11-25 | Evidence-audit corrections: EXP-004 total runtime corrected to 351.1 s (version 1.0 of the report summed the rounded run times); literature verification levels stated in the reports; registry statuses updated | correction of reporting | D-014; `research/publication/evidence_audit.md` |

No confirmatory run failed, was retried or was dropped. No frozen protocol, config, seed or analysis changed after the freeze.
