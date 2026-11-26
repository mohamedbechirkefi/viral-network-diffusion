<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
<!-- Draft for LinkedIn, written at M5 (2026-11-25) from manuscript version 0.2 only. Not published; publication is the owner's decision. -->

Same content, different network: does the structure alone change how far it spreads?

I built a small, preregistered simulation study to test this. Content quality is held fixed by one shared transmission probability; only the network changes: random (ER), small-world (WS) and hub-dominated (BA) graphs with the same size and average number of connections.

One defensible finding: in simulation, topology changes how far identical content spreads, but not in one direction. Hubs help near the take-off point (BA - ER +0.0969 [+0.0921, +0.1018] at p = 0.20) and hurt above it, and the small-world network reaches a third of the network less than the random one at p = 0.30 (-0.3529 [-0.3601, -0.3456]). Holm rejects 13 of 14 comparisons, but only 7 of 14 exceed the effect size set in advance.

Caveat: these are simulations of stylised models, not evidence about any real platform, its algorithms or real people. One planned sensitivity test gave no overall verdict, and the study replicates known structural results rather than claiming a new mechanism.

What is in the repository: frozen protocols, five experiment reports (including null and negligible results), a claims register tracing every number, a preprint draft that is not peer-reviewed, and an offline interactive page.

Repository: https://github.com/mohamedbechirkefi/viral-network-diffusion
Interactive page: https://viral-network-diffusion.kefimohamedbechir.workers.dev

Mohamed Bechir Kefi, independent researcher. Developed with an AI research and development assistant (Claude, Anthropic), disclosed; it is not an author.
