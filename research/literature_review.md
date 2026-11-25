<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Literature review (M0, 2026-11-24)

Not a systematic review. Sources found with web search on 2026-11-24. Verification levels:

- **A (abstract opened):** the abstract page was opened and read.
- **F (full text opened):** the full text was opened and the cited statement located in it.
- **M (metadata verified):** bibliographic metadata checked against the Crossref API (`https://api.crossref.org/works/<DOI>`) on 2026-11-24; the paper text was not opened (publisher page blocked or paywalled). Statements attributed to M sources are background knowledge and are marked unverified against the text until the text is read.

| Key | Reference | DOI / URL | Level | Use in VIRAL |
|---|---|---|---|---|
| kempe2003 | D. Kempe, J. Kleinberg, E. Tardos. Maximizing the spread of influence through a social network. KDD 2003, pp. 137-146. Journal version: Theory of Computing 11(4):105-147, 2015. | doi:10.1145/956750.956769; doi:10.4086/toc.2015.v011a004; https://www.theoryofcomputing.org/articles/v011a004/ | M (KDD); A for the journal version (abstract read 2026-11-25, M4; it does not name the IC or LT model) | Context for IC and LT; the definitions used are stated in full in the protocol |
| watts1998 | D. J. Watts, S. H. Strogatz. Collective dynamics of 'small-world' networks. Nature 393:440-442, 1998. | doi:10.1038/30918 | M | WS generator |
| barabasi1999 | A.-L. Barabasi, R. Albert. Emergence of scaling in random networks. Science 286:509-512, 1999. | doi:10.1126/science.286.5439.509; https://arxiv.org/abs/cond-mat/9910332 | A | BA generator; preferential attachment |
| gilbert1959 | E. N. Gilbert. Random graphs. Annals of Mathematical Statistics 30:1141-1144, 1959. | doi:10.1214/aoms/1177706098 | M | Random-graph baseline (the G(n,M) variant is usually credited to Erdos and Renyi 1959, not verified here) |
| watts2002 | D. J. Watts. A simple model of global cascades on random networks. PNAS 99:5766-5771, 2002. | doi:10.1073/pnas.082090499; https://pmc.ncbi.nlm.nih.gov/articles/PMC122850/ | F (full text opened at PubMed Central, 2026-11-25, M4) | Fractional-threshold model, cascade window |
| granovetter1978 | M. Granovetter. Threshold models of collective behavior. American Journal of Sociology 83:1420-1443, 1978. | doi:10.1086/226707 | M | Threshold contagion origin |
| centola2007 | D. Centola, M. Macy. Complex contagions and the weakness of long ties. American Journal of Sociology 113:702-734, 2007. | doi:10.1086/521848 | M | Clustering and complex contagion |
| newman2001 | M. E. J. Newman, S. H. Strogatz, D. J. Watts. Random graphs with arbitrary degree distributions and their applications. Physical Review E 64:026118, 2001. | doi:10.1103/PhysRevE.64.026118; https://arxiv.org/abs/cond-mat/0007235 | A (abstract read 2026-11-25, M4) | Random graphs with arbitrary degree distributions; giant-component transition. The bond-percolation threshold expression used in S1 was not located in the abstract and is stated as a definition |
| pastor2001 | R. Pastor-Satorras, A. Vespignani. Epidemic spreading in scale-free networks. Physical Review Letters 86:3200-3203, 2001. | doi:10.1103/PhysRevLett.86.3200; https://arxiv.org/abs/cond-mat/0010317 | A | Absent epidemic threshold on scale-free networks |
| pastor2015 | R. Pastor-Satorras, C. Castellano, P. Van Mieghem, A. Vespignani. Epidemic processes in complex networks. Reviews of Modern Physics 87:925-979, 2015. | doi:10.1103/RevModPhys.87.925; https://arxiv.org/abs/1408.2701 | A | Review; social contagion section |
| kitsak2010 | M. Kitsak et al. Identification of influential spreaders in complex networks. Nature Physics 6:888-893, 2010. | doi:10.1038/nphys1746; https://arxiv.org/abs/1001.5285 | A | Seed selection: degree versus k-core |
| goel2016 | S. Goel, A. Anderson, J. Hofman, D. J. Watts. The structural virality of online diffusion. Management Science 62:180-196, 2016. | doi:10.1287/mnsc.2015.2158 | M | Structural virality metric (exploratory) |
| salganik2006 | M. J. Salganik, P. S. Dodds, D. J. Watts. Experimental study of inequality and unpredictability in an artificial cultural market. Science 311:854-856, 2006. | doi:10.1126/science.1121066 | M (publisher page returned 403) | Motivation: outcome inequality for comparable content (human experiment; not replicated here) |
| cheng2014 | J. Cheng, L. Adamic, P. A. Dow, J. Kleinberg, J. Leskovec. Can cascades be predicted? WWW 2014, pp. 925-936. | doi:10.1145/2566486.2567997 | M | Context only; empirical platform data, outside the claims boundary |

## Synthesis (from level A sources and model definitions only)

- Pastor-Satorras and Vespignani (2001, abstract) report that a spreading model on scale-free networks has no epidemic threshold. This predicts that BA graphs sustain spreading at transmission rates where ER graphs do not, which motivates the nondirectional H1 and sensitivity S1.
- Kitsak et al. (2010, abstract) report that the best single spreaders sit in the k-core rather than simply having the highest degree, and that spreader distance matters for multiple seeds. VIRAL uses degree as the simple targeted rule; k-core seeding is a candidate extension, not in the frozen scope.
- Barabasi and Albert (1999, abstract) give growth plus preferential attachment as the generating mechanism, which networkx `barabasi_albert_graph` implements (networkx 3.7 documentation opened 2026-11-24).

## Software and data sources consulted

| Source | URL | Accessed | Finding |
|---|---|---|---|
| networkx 3.7 generators | https://networkx.org/documentation/stable/reference/generators.html | 2026-11-24 | `gnm_random_graph`, `watts_strogatz_graph`, `connected_watts_strogatz_graph`, `barabasi_albert_graph` available |
| networkx licence | https://raw.githubusercontent.com/networkx/networkx/main/LICENSE.txt | 2026-11-24 | 3-clause BSD |
| SNAP datasets | https://snap.stanford.edu/data/ | 2026-11-24 | No licence or redistribution terms stated on the index page; only a citation request |
| Netzschleuder (example entry) | https://networks.skewed.de/net/karate | 2026-11-24 | No dataset licence stated on the page; footer shows an AGPLv3 logo with unclear scope |

## Contribution (proposed, narrow)

A small, matched, fully reproducible comparison of IC and threshold diffusion across ER, WS and BA graphs that (a) reports final size, depth, duration and outcome inequality together, (b) uses replicate-level paired inference instead of treating cascades as independent, and (c) tests in advance whether degree moments alone explain the topology effect. This is a replication and integration contribution. No novelty is claimed; the search above was not systematic.

## Verification update (M4, 2026-11-25)

During the M4 evidence audit, three sources were opened again:

- **Newman, Strogatz and Watts (2001).** The arXiv abstract page (cond-mat/0007235) was read, so the level is now A. The abstract covers the giant-component transition for arbitrary degree distributions. It does not state the bond-percolation threshold expression `p_c = <k>/(<k^2> - <k>)`, so the reports and the manuscript now present that expression as a definition, not as a result of this paper.
- **Watts (2002).** The full text was opened at PubMed Central (PMC122850), so the level is now F. It confirms the threshold rule, "at least a threshold fraction", and the cascade window bounded as a function of the average degree.
- **Kempe, Kleinberg and Tardos (2015 journal version).** The abstract was read, so the level is now A. It refers to "several of the most widely studied models" without naming IC or LT, so the IC definition rests on the protocol, not on this citation.

The fetches went through a summarising web tool. Quotations are short phrases only.

Granovetter (1978), Watts and Strogatz (1998), Centola and Macy (2007), Gilbert (1959), Goel et al. (2016), Salganik et al. (2006) and Cheng et al. (2014) remain at metadata level. The manuscript cites them as attributions only.
