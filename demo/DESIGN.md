<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# VIRAL demo: design plan (owner request, 2026-11-26)

## Subject, audience, job

- **Subject.** How far identical content travels when only the network changes. Content quality is fixed by one transmission probability `p` (independent cascade) or one threshold `phi`; random (ER), small-world (WS) and scale-free (BA) graphs of the same size and mean degree are compared.
- **Audience.** A curious technical reader, an admissions committee looking for method, a researcher checking intervals, Holm decisions and the SESOI.
- **Primary job.** Put the question and the one-sentence answer first, show the crossing curves of Figure B as the study's picture, then the full evidence, the sandbox and the reproduction path.

## Palette (light only)

A field epidemiologist's map sheet: what has been reached is marked in red on a pale survey sheet. One scheme only, because the map metaphor depends on a paper ground.

| Name | Hex | Role |
| --- | --- | --- |
| Map paper | `#EDF1EE` | Page background, a cool sage grey (never cream) |
| Survey ink | `#14262B` | Text, wordmark, seed nodes, primary buttons |
| Contour grey | `#8FA39E` | Edges and nodes not reached (graphics only, never text) |
| Incidence red | `#C2361F` | Reached nodes, transmission edges, the brand mark, focus ring, forest points |
| Fresh-case amber | `#E9A23B` | The pulse of the newest round (graphics only) |
| Harbour blue | `#2B6A8E` | Links, the graticule, the ER series |

Series in charts: ER harbour blue, WS moss `#5F7F12`, BA heather `#8A3F8F`, always with direct labels and a legend, so colour is never the only carrier.

## Type

- **Archivo** (variable, width 74 to 88, weight 500 to 760): map lettering. Condensed and heavy for the hero question and headings, as on a surveyed sheet; regular width for navigation, controls, tables, figure captions and chart labels, with tabular figures.
- **Newsreader** (variable weight): the reading face for paragraphs, verdicts and notes, like a public-health bulletin.

Scale: 18 px body; headings 22, 28 to 38 (fluid); hero 34 to 62 (fluid). Body measure capped at 68 characters.

## Layout

```
+---------------------------------------------------------------------+
| [mark] Viral                         Result  Evidence  Sandbox  Method |  sticky, 58 px
+---------------------------------------------------------------------+
| HOW DO NETWORK TOPOLOGY AND        |  Answer in one sentence        |
| INITIAL EXPOSURE CHANGE HOW FAR    |  (Newsreader, 20 px)           |
| IDENTICAL CONTENT SPREADS?         |  byline                        |
| (Archivo condensed 760)            |                                |
+---------------------------------------------------------------------+
| map sheet with graticule                                             |
|  [ Random ER ]      [ Small-world WS ]      [ Scale-free BA ]        |
|  cascade lights up round by round from one seed in each              |
| "Illustration, not study data." caption, legend      [Replay]        |
+---------------------------------------------------------------------+
| Same content, three reaches: Figure B (S by p, curves cross)         |
| Overview: status, question, lead, label key                          |
| Published results: graph statistics, experiment panels (ink rule)    |
| Assumptions | Method and limitations | Sandbox (dashed red border)   |
| Reproduce: commands                                                  |
| footer: lockup, links, notes, licence, AI use, fonts                 |
+---------------------------------------------------------------------+
```

Left aligned. The three networks stay side by side at every width (on a phone each panel is about a third of the screen, with the names on two lines). Experiment panels carry a heavy ink rule on top, like a map's neatline, rather than a soft card shadow.

## Motion

- **One orchestrated hero moment.** One independent cascade per network shape, drawn with the sandbox's own generators, layout and cascade rule on 56-node graphs and one fixed random stream: each reached node scales in and an amber ring pulses outward at its activation round (260 ms per round), and the transmission edge to it fades in. The ring visibly crawls; the hub graph jumps. A "Replay the cascade" button restarts it. CSS keyframes on transform and opacity only, per-node delays.
- **Motion that answers the visitor.** Figure series fade in one after another and forest points and intervals settle once when scrolled into view; the sandbox result line fades in; buttons press (scale 0.97). The sandbox's round-by-round animation stays as before (off under reduced motion).
- **Reduced motion.** The hero shows its final state with no animation and no pulses; reveals are opacity only; no transform anywhere.
- Hover only inside `(hover: hover) and (pointer: fine)`. No `transition: all`.

## The one memorable thing

Three network shapes side by side on a surveyed sheet, lighting up from one seed at different speeds: the study's question made visible before a single number appears.

## Review against the generated-page tells, and what changed

- A dark "situation room" map was considered first, with glowing red nodes; that is the near-black with one hot accent tell; moved to a pale survey sheet where red reads as incidence on paper.
- The old page had an uppercase tracked kicker and uppercase result labels. Removed: the study name is in the lockup, and labels are sentence case.
- Setting the hero numbers (13 of 14, 7 of 14) in large type was considered and dropped: a big number with a small label is the default hero; the numbers stay in the text where they are qualified.
- No mono data labels: figures use Archivo with tabular figures; monospace is kept only for commands, paths and claim ids, which are code.
- No section numbering (the sections are not a sequence) and no fade-up on every section; the only scroll-triggered motion is the chart reveal.
- Distinct from the other labs: MATCH is a card table, HERD a line of people, FLOW a transit map; VIRAL is a field epidemiology sheet with three graphs.
