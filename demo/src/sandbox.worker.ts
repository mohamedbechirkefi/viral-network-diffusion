// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Bounded, cancellable sandbox runs in a Web Worker. Everything here is computed from the
// visitor's settings with the ported engine (engine.ts); nothing is sent anywhere.
import {
  type Family, icCascade, layout, ltCascade, makeGraph, mulberry32, percolationThreshold,
  type SeedRule, selectSeeds, edgeList,
} from "./engine";

export interface SandboxSettings {
  seed: number;
  model: "ic" | "lt";
  param: number;
  seedRule: SeedRule;
  seedCount: number;
  n: number;
  cascades: number;
  show: Family;
}

export interface TopologySummary {
  family: Family;
  edges: number;
  pc: number;
  meanS: number;
  lo: number; // normal-approximation 95 percent interval over cascades on this one graph
  hi: number;
  histogram: number[]; // fraction of cascades per S bin, BINS bins over [0, 1]
}

export interface ShownCascade {
  family: Family;
  n: number;
  edges: [number, number][];
  pos: number[];
  round: number[]; // activation round per node, -1 never active
  seeds: number[];
  size: number;
}

export type WorkerRequest = { type: "run"; settings: SandboxSettings } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; settings: SandboxSettings; summaries: TopologySummary[]; shown: ShownCascade }
  | { type: "cancelled" }
  | { type: "error"; message: string };

export const BINS = 20;
export const LIMITS = { nMin: 50, nMax: 400, cascadesMin: 20, cascadesMax: 1000, seedCountMax: 10, seedMax: 1_000_000 };
const FAMILIES: Family[] = ["er", "ws", "ba"];
let cancelled = false;

export function checkSettings(s: SandboxSettings): void {
  const int = (x: number, lo: number, hi: number) => Number.isInteger(x) && x >= lo && x <= hi;
  if (!int(s.seed, 1, LIMITS.seedMax)) throw new Error("seed must be an integer from 1 to 1,000,000");
  if (!int(s.n, LIMITS.nMin, LIMITS.nMax)) throw new Error("N is out of range");
  if (!int(s.cascades, LIMITS.cascadesMin, LIMITS.cascadesMax)) throw new Error("cascade count is out of range");
  if (!int(s.seedCount, 1, LIMITS.seedCountMax)) throw new Error("seed count is out of range");
  if (!Number.isFinite(s.param) || s.param < 0 || s.param > 1) throw new Error("parameter must be in [0, 1]");
  if (s.model !== "ic" && s.model !== "lt") throw new Error("unknown model");
  if (!FAMILIES.includes(s.show)) throw new Error("unknown topology");
  if (s.seedRule !== "random" && s.seedRule !== "highest_degree") throw new Error("unknown seed rule");
}

export async function simulate(s: SandboxSettings, onProgress?: (f: number) => void, isCancelled = () => false):
  Promise<{ summaries: TopologySummary[]; shown: ShownCascade } | null> {
  checkSettings(s);
  const summaries: TopologySummary[] = [];
  let shown: ShownCascade | null = null;
  for (let f = 0; f < FAMILIES.length; f++) {
    const family = FAMILIES[f];
    // Independent streams per topology, all derived from the visitor's seed.
    const gRng = mulberry32((s.seed * 7919 + f * 104729) >>> 0);
    const cRng = mulberry32((s.seed * 15485863 + f * 32452843 + 1) >>> 0);
    const g = makeGraph(family, s.n, gRng);
    const hist = new Array<number>(BINS).fill(0);
    let sum = 0;
    let sum2 = 0;
    for (let c = 0; c < s.cascades; c++) {
      const seeds = selectSeeds(g, s.seedRule, s.seedCount, cRng);
      const cas = s.model === "ic" ? icCascade(g, seeds, s.param, cRng) : ltCascade(g, seeds, s.param);
      const S = cas.size / g.n;
      sum += S;
      sum2 += S * S;
      hist[Math.min(BINS - 1, Math.floor(S * BINS))] += 1;
      if (c === 0 && family === s.show) {
        shown = { family, n: g.n, edges: edgeList(g), pos: Array.from(layout(g, family, gRng)), round: Array.from(cas.activationRound), seeds, size: cas.size };
      }
      if (c % 50 === 49) {
        await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
        if (isCancelled()) return null;
        onProgress?.((f + c / s.cascades) / FAMILIES.length);
      }
    }
    const mean = sum / s.cascades;
    const sd = Math.sqrt(Math.max(0, sum2 / s.cascades - mean * mean) * (s.cascades / Math.max(1, s.cascades - 1)));
    const half = (1.96 * sd) / Math.sqrt(s.cascades);
    summaries.push({ family, edges: edgeList(g).length, pc: percolationThreshold(g), meanS: mean, lo: Math.max(0, mean - half), hi: Math.min(1, mean + half), histogram: hist.map((h) => h / s.cascades) });
  }
  return { summaries, shown: shown as ShownCascade };
}

if (typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope) {
  onmessage = async (ev: MessageEvent<WorkerRequest>) => {
    const m = ev.data;
    if (m.type === "cancel") {
      cancelled = true;
      return;
    }
    cancelled = false;
    try {
      const out = await simulate(m.settings, (fraction) => postMessage({ type: "progress", fraction } satisfies WorkerReply), () => cancelled);
      postMessage((out === null ? { type: "cancelled" } : { type: "done", settings: m.settings, ...out }) satisfies WorkerReply);
    } catch (e) {
      postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
    }
  };
}
