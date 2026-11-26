<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
<!-- Draft for Medium, written at M5 (2026-11-25) from manuscript version 0.2 only. Not published; publication is the owner's decision. Every number is copied from the manuscript; claim ids in brackets point to research/claims_register.csv. -->

# Same content, different networks: a preregistered simulation of how far things spread

*By Mohamed Bechir Kefi, independent researcher. Draft. Independent research, not peer-reviewed. Every result below is a simulation of a stylised model; none of it describes a real social platform, its ranking algorithm, real people, or a recipe for "going viral".*

## Two identical posts

Imagine two posts of exactly the same appeal. One reaches a handful of people, the other a large share of its network. The usual explanation is the content. A second explanation is the network itself: the pattern of connections through which the content travels.

In real data the two are tangled, because content and audience co-vary. In a simulation they can be pulled apart. This project holds "content quality" fixed by construction and asks a narrow question: **how do network topology and initial exposure change diffusion when the content is the same?**

## The set-up

Content quality is a single number. Under the *independent cascade* model, every newly reached person gets one chance to pass the content to each contact, with the same probability `p` everywhere. Under the *fractional-threshold* model, a person adopts once a fraction `phi` of their contacts has adopted.

Three kinds of network were compared, all with 1000 nodes and an average of 6 connections per node:

- **Erdos-Renyi (ER):** connections placed at random. This is the baseline.
- **Watts-Strogatz (WS), "small-world":** a ring of neighbours with a few random shortcuts, so friends of friends are often friends.
- **Barabasi-Albert (BA), "scale-free":** a few hubs with very many connections.

The outcome is the final cascade fraction `S`, the share of the network that the content eventually reaches. The protocol, including the smallest difference treated as practically important (plus or minus 0.02 in `S`), was frozen and approved before any confirmatory run. The unit of analysis is the graph, not the single cascade: 120 matched sets of graphs per comparison, with intervals from a paired bootstrap and Holm control of multiple tests.

*Figure 1. Mean final cascade fraction S by transmission probability p for ER, WS and BA (manuscript Figure 2). Alt text: three rising curves; BA rises first, ER overtakes BA between p = 0.20 and 0.30, and WS stays far below both at p = 0.30 before finishing highest at p = 0.50.*

## What happened

**Network structure alone changed how far identical content spread, sometimes by a lot, but not in one direction.** In the main experiment, Holm rejected 13 of 14 comparisons with the random baseline. That sounds decisive, and it is not: only 7 of the 14 differences were larger than the 0.02 threshold set in advance. Six rejections were detectable yet negligible. With 120 matched graph sets, differences as small as 3.27e-05 in `S` are "statistically significant", which says nothing about their importance [SYN-10].

Both topology effects **change sign** as `p` grows [SYN-01]:

- **Hubs help first, then hurt.** BA spreads more than ER near the point where cascades start to take off (+0.0969 [+0.0921, +0.1018] at `p` = 0.20) and less than ER above it (-0.0583 [-0.0659, -0.0503] at `p` = 0.30).
- **Small-world clustering wastes transmissions.** WS spreads far less than ER at `p` = 0.30 (-0.3529 [-0.3601, -0.3456]), about a third of the network, and slightly more at `p` = 0.50.

**Seeding a hub amplifies the hub advantage.** Starting from the highest-degree node instead of a random one, the BA advantage at `p` = 0.15 is +0.2283 [+0.2268, +0.2298] (secondary, unadjusted). Exposure changed magnitudes more than orderings under this model.

## Trying to explain it away

A preregistered sensitivity programme tried to explain the differences with simpler causes.

- **The BA advantage near threshold is a degree-sequence effect.** A randomised version of each BA graph that keeps every node's number of connections spreads the same, within 0.02, from `p` = 0.02 to 0.20 [SYN-03].
- **Edge counts and size do not explain the pattern.** Matching edge counts exactly, or using 500 or 2000 nodes, gives the same 13-of-14 pattern [SYN-02].
- **One planned test gave no verdict.** Rescaling `p` by each graph's own threshold estimate equalises the networks below threshold but not above it. Its decision rule was ambiguous in the frozen text, so the owner decided it is reported per multiplier with no overall verdict, and no multiplier was picked after seeing the data [SYN-04].

## Change the rule, change the answer

Under the threshold model, where adoption needs several adopting contacts, the small-world ordering **reverses**: WS spreads far more than ER (+0.3664 [+0.3602, +0.3727] on the grid mean of `phi`) [SYN-05]. Clustering gives the repeated exposure that threshold adoption needs. Whether "small-world" or "scale-free" structure promotes spreading is therefore not a well-posed question without the spreading rule and the operating point.

## One real network

On one anonymized 362-node friendship network, released under an MIT licence, the real wiring spread less than a randomised version with the same connection counts wherever a difference was detectable, by up to 0.1317 [SYN-06]. This is one small network, not a sample of networks.

## Exploratory follow-ups, labelled as such

Three small checks were designed after the main results were seen, so they are exploratory and never replace a preregistered verdict. On fresh seeds, the large WS deficit at `p` = 0.30 reappears (-0.3524 [-0.3619, -0.3426]) and comes from structure beyond the connection counts (-0.3662 [-0.3750, -0.3573]) [SYN-07]. The check cannot tell clustering from ring order.

## Limits

- Simulations of stylised models only; synthetic agents are not people.
- One parameterisation per network family, one real network, and sizes from 500 to 2000 only.
- Pilot values were seen before the protocol was frozen; new seeds and a frozen analysis limit, but do not remove, that risk.
- The 0.02 threshold is a design choice, and absolute: large relative differences at small `p` count as negligible.
- The study replicates known structural results in one matched design. It does not claim a new mechanism.

## Reproduce it

Code, frozen protocols, every experiment report, the claims register and an offline interactive page are in the repository: <https://github.com/mohamedbechirkefi/viral-network-diffusion>. Interactive page: <https://viral-network-diffusion.kefimohamedbechir.workers.dev>. Manuscript: `research/paper/manuscript.md` (version 0.2).

*An AI research and development assistant (Claude, Anthropic) wrote the code, ran the experiments and drafted the text under the author's direction. It is not an author.*
