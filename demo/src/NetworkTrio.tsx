// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Hero illustration: one independent cascade on each of three small graphs
// (random, small-world, scale-free), drawn with the sandbox's own generators,
// layout and cascade rule. Nodes light up round by round from one seed. It is a
// drawing of the mechanism on 56-node graphs and one fixed random stream, not
// study data: it shows no number, and its spread says nothing about the
// published comparisons.
import { useMemo, useState } from "react";
import { icCascade, layout, makeGraph, mulberry32, selectSeeds, type Family } from "./engine";

const N = 56;
const P = 0.32;
const STREAM = 9; // fixed illustration stream
const STEP_MS = 260;
const SHAPES: { family: Family; name: string; plain: string }[] = [
  { family: "er", name: "Random", plain: "ER" },
  { family: "ws", name: "Small-world", plain: "WS" },
  { family: "ba", name: "Scale-free", plain: "BA" },
];

interface Drawn {
  family: Family;
  pos: Float64Array;
  edges: string;
  round: Int32Array;
  parent: Int32Array;
}

function draw(family: Family): Drawn {
  const rng = mulberry32(STREAM * 101 + family.length);
  const g = makeGraph(family, N, rng);
  const seeds = selectSeeds(g, "random", 1, rng);
  const c = icCascade(g, seeds, P, rng);
  const pos = layout(g, family, mulberry32(STREAM));
  let d = "";
  for (let u = 0; u < g.n; u++)
    for (let j = g.indptr[u]; j < g.indptr[u + 1]; j++) {
      const v = g.indices[j];
      if (v > u) d += `M${(pos[2 * u] * 100).toFixed(1)} ${(pos[2 * u + 1] * 100).toFixed(1)}L${(pos[2 * v] * 100).toFixed(1)} ${(pos[2 * v + 1] * 100).toFixed(1)}`;
    }
  return { family, pos, edges: d, round: c.activationRound, parent: c.parent };
}

function Panel({ d, name, plain }: { d: Drawn; name: string; plain: string }) {
  const X = (i: number) => d.pos[2 * i] * 100;
  const Y = (i: number) => d.pos[2 * i + 1] * 100;
  const idx = Array.from(d.round, (_, i) => i);
  return (
    <div className="trio-panel">
      <svg viewBox="-6 -6 112 112" className="trio-svg" aria-hidden="true" focusable="false">
        <path className="t-edges" d={d.edges} />
        {idx.map((i) =>
          d.parent[i] >= 0 ? (
            <line key={`t${i}`} className="t-pass" x1={X(d.parent[i])} y1={Y(d.parent[i])} x2={X(i)} y2={Y(i)}
              style={{ animationDelay: `${d.round[i] * STEP_MS - 120}ms` }} />
          ) : null,
        )}
        {idx.map((i) => (
          <circle key={`n${i}`} className="t-node" cx={X(i)} cy={Y(i)} r={1.9} />
        ))}
        {idx.map((i) =>
          d.round[i] >= 0 ? (
            <g key={`h${i}`} transform={`translate(${X(i).toFixed(2)} ${Y(i).toFixed(2)})`}>
              <circle className="t-pulse" r={2.2} style={{ animationDelay: `${d.round[i] * STEP_MS}ms` }} />
              <circle className={d.round[i] === 0 ? "t-hot t-seed" : "t-hot"} r={d.round[i] === 0 ? 3 : 2.3}
                style={{ animationDelay: `${d.round[i] * STEP_MS}ms` }} />
            </g>
          ) : null,
        )}
      </svg>
      <p className="trio-name">
        {name} <span>{plain}</span>
      </p>
    </div>
  );
}

export function NetworkTrio() {
  const drawn = useMemo(() => SHAPES.map((s) => draw(s.family)), []);
  const [take, setTake] = useState(0);
  return (
    <figure className="trio">
      <div className="trio-sheet" key={take}>
        {SHAPES.map((s, k) => (
          <Panel key={s.family} d={drawn[k]} name={s.name} plain={s.plain} />
        ))}
      </div>
      <figcaption className="trio-caption">
        <span className="illus-tag">Illustration, not study data.</span>{" "}
        The same transmission rule, started from one seed, on three network shapes of the same size and mean degree.
        In this drawing, the ring carries the content around its circle step by step, while the hub-heavy graph reaches far in a few rounds.
        <span className="trio-legend" aria-hidden="true">
          <span><i className="lg lg-seed" /> seed</span>
          <span><i className="lg lg-hot" /> reached</span>
          <span><i className="lg lg-off" /> not reached</span>
        </span>
      </figcaption>
      <button type="button" className="replay" onClick={() => setTake((t) => t + 1)}>
        Replay the cascade
      </button>
    </figure>
  );
}
