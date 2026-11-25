// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// The browser port against a fixture produced by the Python research engine
// (scripts/make_sandbox_fixture.py). Tolerance: exact equality for every activation round,
// parent, generation and size (integers); 1e-12 relative for the threshold estimate p_c.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  baGraph, edgeList, erGraph, fromEdges, icCascade, ltCascade, makeGraph, mulberry32,
  percolationThreshold, selectSeeds, wsGraph,
} from "./engine";

interface IcRun { seeds: number[]; activation_round: number[]; parent: number[]; size: number }
interface Case {
  family: string; n: number; edges: [number, number][]; p_c: number;
  ic: { p: number; rng_seed: number; cascades: IcRun[] }[];
  lt: { phi: number; seeds: number[]; activation_round: number[]; generation: number[]; size: number }[];
}
const fixture = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8")) as {
  rng_check: { seed: number; first_draws: number[] }; cases: Case[];
};

describe("engine port matches the Python research engine", () => {
  it("mulberry32 is bit-exact with the Python port", () => {
    const r = mulberry32(fixture.rng_check.seed);
    expect([r(), r(), r()]).toEqual(fixture.rng_check.first_draws);
  });

  for (const c of fixture.cases) {
    const g = fromEdges(c.n, c.edges);
    it(`${c.family}: graph and threshold estimate`, () => {
      expect(edgeList(g)).toEqual(c.edges);
      expect(Math.abs(percolationThreshold(g) - c.p_c)).toBeLessThanOrEqual(1e-12 * c.p_c);
    });
    it(`${c.family}: independent cascade, identical rounds and parents`, () => {
      let n = 0;
      for (const block of c.ic) {
        const rng = mulberry32(block.rng_seed);
        for (const run of block.cascades) {
          const out = icCascade(g, run.seeds, block.p, rng);
          expect(Array.from(out.activationRound)).toEqual(run.activation_round);
          expect(Array.from(out.parent)).toEqual(run.parent);
          expect(out.size).toBe(run.size);
          n++;
        }
      }
      expect(n).toBe(24);
    });
    it(`${c.family}: fractional threshold, identical rounds and generations`, () => {
      for (const t of c.lt) {
        const out = ltCascade(g, t.seeds, t.phi);
        expect(Array.from(out.activationRound)).toEqual(t.activation_round);
        expect(Array.from(out.generation)).toEqual(t.generation);
        expect(out.size).toBe(t.size);
      }
    });
  }
});

describe("engine edge cases (as in the Python test suite)", () => {
  const g = fromEdges(5, [[0, 1], [1, 2], [3, 4]]);
  it("no transmission keeps only the seed; full transmission fills the component", () => {
    expect(icCascade(g, [0], 0, mulberry32(1)).size).toBe(1);
    expect(icCascade(g, [0], 1, mulberry32(1)).size).toBe(3);
  });
  it("disconnected components are never reached", () => {
    expect(icCascade(g, [3], 1, mulberry32(2)).activationRound[0]).toBe(-1);
  });
  it("rejects invalid inputs", () => {
    expect(() => icCascade(g, [0], 1.5, mulberry32(1))).toThrow();
    expect(() => icCascade(g, [0, 0], 0.5, mulberry32(1))).toThrow();
    expect(() => fromEdges(3, [[0, 0]])).toThrow();
    expect(() => fromEdges(3, [[0, 1], [1, 0]])).toThrow();
  });
});

describe("sandbox generators keep the design invariants", () => {
  it("ER has 3n edges, WS 3n edges, BA 3(n - 3) edges; all simple", () => {
    const n = 200;
    expect(edgeList(erGraph(n, 3 * n, mulberry32(5))).length).toBe(3 * n);
    expect(edgeList(wsGraph(n, 6, 0.1, mulberry32(5))).length).toBe(3 * n);
    expect(edgeList(baGraph(n, 3, mulberry32(5))).length).toBe(3 * (n - 3));
  });
  it("generation is deterministic per seed", () => {
    expect(edgeList(makeGraph("ba", 100, mulberry32(9)))).toEqual(edgeList(makeGraph("ba", 100, mulberry32(9))));
  });
  it("highest-degree seeding picks a maximum-degree node", () => {
    const b = baGraph(100, 3, mulberry32(3));
    const [s] = selectSeeds(b, "highest_degree", 1, mulberry32(4));
    const deg = (u: number) => b.indptr[u + 1] - b.indptr[u];
    for (let u = 0; u < b.n; u++) expect(deg(u)).toBeLessThanOrEqual(deg(s));
  });
});

describe("sandbox worker logic", () => {
  it("is bounded, deterministic per seed and rejects out-of-range settings", async () => {
    const { simulate } = await import("./sandbox.worker");
    const s = { seed: 7, model: "ic" as const, param: 0.3, seedRule: "random" as const, seedCount: 1, n: 100, cascades: 50, show: "ba" as const };
    const a = await simulate(s);
    const b = await simulate(s);
    expect(a).toEqual(b);
    expect(a!.summaries.map((t) => t.family)).toEqual(["er", "ws", "ba"]);
    for (const t of a!.summaries) {
      expect(t.histogram.reduce((x, y) => x + y, 0)).toBeCloseTo(1, 12);
      expect(t.lo).toBeLessThanOrEqual(t.meanS);
      expect(t.hi).toBeGreaterThanOrEqual(t.meanS);
    }
    expect(a!.shown.family).toBe("ba");
    await expect(simulate({ ...s, n: 5000 })).rejects.toThrow();
    await expect(simulate({ ...s, param: 2 })).rejects.toThrow();
    await expect(simulate({ ...s, cascades: 10_000 })).rejects.toThrow();
  });
});
