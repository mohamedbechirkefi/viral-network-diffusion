// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Browser port of the VIRAL diffusion engine for the visitor sandbox.
//
// icCascade and ltCascade are line-by-line ports of viral.engines.ic_reference and lt_reference:
// same synchronous rounds, same attempt order (frontier ascending, neighbours ascending), one
// uniform draw per attempt. Driven by the same uniform stream they reproduce the Python engine
// exactly (src/engine.test.ts, fixture from scripts/make_sandbox_fixture.py).
//
// The graph generators below implement the same three models (ER G(n, M), Watts-Strogatz,
// Barabasi-Albert) but are not byte-identical to networkx: their random streams differ, so a
// sandbox graph is never one of the research graphs.

export type Rng = () => number;

/** mulberry32: small seeded 32-bit generator (public domain); bit-exact with the Python port. */
export function mulberry32(seed: number): Rng {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = ((t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t) >>> 0;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export interface Graph {
  n: number;
  indptr: Int32Array;
  indices: Int32Array; // neighbours of each node, ascending
}

export class EngineError extends Error {}

export function fromEdges(n: number, edges: ReadonlyArray<readonly [number, number]>): Graph {
  if (!Number.isInteger(n) || n < 1) throw new EngineError("n must be a positive integer");
  const adj: number[][] = Array.from({ length: n }, () => []);
  const seen = new Set<number>();
  for (const [u, v] of edges) {
    if (!(u >= 0 && u < n && v >= 0 && v < n) || u === v) throw new EngineError(`invalid edge (${u}, ${v})`);
    const key = Math.min(u, v) * n + Math.max(u, v);
    if (seen.has(key)) throw new EngineError(`duplicate edge (${u}, ${v})`);
    seen.add(key);
    adj[u].push(v);
    adj[v].push(u);
  }
  const indptr = new Int32Array(n + 1);
  for (let i = 0; i < n; i++) indptr[i + 1] = indptr[i] + adj[i].length;
  const indices = new Int32Array(indptr[n]);
  for (let i = 0; i < n; i++) {
    adj[i].sort((a, b) => a - b);
    indices.set(adj[i], indptr[i]);
  }
  return { n, indptr, indices };
}

export function edgeList(g: Graph): [number, number][] {
  const out: [number, number][] = [];
  for (let u = 0; u < g.n; u++) for (let j = g.indptr[u]; j < g.indptr[u + 1]; j++) if (u < g.indices[j]) out.push([u, g.indices[j]]);
  return out;
}

export function degree(g: Graph, u: number): number {
  return g.indptr[u + 1] - g.indptr[u];
}

/** Locally tree-like bond-percolation threshold estimate <k> / (<k^2> - <k>), as viral.graphs.percolation_threshold. */
export function percolationThreshold(g: Graph): number {
  let k1 = 0;
  let k2 = 0;
  for (let u = 0; u < g.n; u++) {
    const d = degree(g, u);
    k1 += d;
    k2 += d * d;
  }
  k1 /= g.n;
  k2 /= g.n;
  const denom = k2 - k1;
  return denom > 0 ? k1 / denom : Infinity;
}

function checkSeeds(g: Graph, seeds: readonly number[]): number[] {
  if (seeds.length === 0) throw new EngineError("seeds must be non-empty");
  const s = [...seeds].sort((a, b) => a - b);
  for (let i = 0; i < s.length; i++) {
    if (!Number.isInteger(s[i]) || s[i] < 0 || s[i] >= g.n) throw new EngineError("seed out of range");
    if (i > 0 && s[i] === s[i - 1]) throw new EngineError("duplicate seed nodes");
  }
  return s;
}

export interface Cascade {
  activationRound: Int32Array; // -1 never active
  parent: Int32Array; // IC only; -1 for seeds and inactive nodes
  generation: Int32Array; // LT generation; equals activationRound for IC
  size: number;
}

/** Independent cascade, port of viral.engines.ic_reference. */
export function icCascade(g: Graph, seeds: readonly number[], p: number, rng: Rng): Cascade {
  if (!Number.isFinite(p) || p < 0 || p > 1) throw new EngineError("p must be in [0, 1]");
  const s = checkSeeds(g, seeds);
  const act = new Int32Array(g.n).fill(-1);
  const parent = new Int32Array(g.n).fill(-1);
  for (const u of s) act[u] = 0;
  let frontier = s;
  let r = 0;
  const activeAtStart = new Uint8Array(g.n);
  while (frontier.length) {
    r += 1;
    for (let i = 0; i < g.n; i++) activeAtStart[i] = act[i] >= 0 ? 1 : 0;
    const next: number[] = [];
    for (const u of frontier) {
      for (let j = g.indptr[u]; j < g.indptr[u + 1]; j++) {
        const v = g.indices[j];
        if (activeAtStart[v]) continue;
        const x = rng();
        if (x < p && act[v] < 0) {
          act[v] = r;
          parent[v] = u;
          next.push(v);
        }
      }
    }
    frontier = next.sort((a, b) => a - b);
  }
  let size = 0;
  for (let i = 0; i < g.n; i++) if (act[i] >= 0) size++;
  return { activationRound: act, parent, generation: act.slice(), size };
}

/** Fractional threshold, port of viral.engines.lt_reference. Deterministic given graph and seeds. */
export function ltCascade(g: Graph, seeds: readonly number[], phi: number): Cascade {
  if (!Number.isFinite(phi) || phi < 0) throw new EngineError("phi must be >= 0");
  const s = checkSeeds(g, seeds);
  const act = new Int32Array(g.n).fill(-1);
  const gen = new Int32Array(g.n).fill(-1);
  for (const u of s) {
    act[u] = 0;
    gen[u] = 0;
  }
  let r = 0;
  for (;;) {
    r += 1;
    const snap = act.slice();
    const gsnap = gen.slice();
    const next: [number, number][] = [];
    for (let v = 0; v < g.n; v++) {
      if (snap[v] >= 0) continue;
      const d = degree(g, v);
      if (d === 0) continue;
      let count = 0;
      let maxGen = -1;
      for (let j = g.indptr[v]; j < g.indptr[v + 1]; j++) {
        const u = g.indices[j];
        if (snap[u] >= 0) {
          count++;
          if (gsnap[u] > maxGen) maxGen = gsnap[u];
        }
      }
      if (count > 0 && count / d >= phi) next.push([v, 1 + maxGen]);
    }
    if (next.length === 0) break;
    for (const [v, gv] of next) {
      act[v] = r;
      gen[v] = gv;
    }
  }
  let size = 0;
  for (let i = 0; i < g.n; i++) if (act[i] >= 0) size++;
  return { activationRound: act, parent: new Int32Array(g.n).fill(-1), generation: gen, size };
}

// ---- Sandbox graph generators (same models as the research generators; different random streams) ----

export type Family = "er" | "ws" | "ba";

function randInt(rng: Rng, n: number): number {
  return Math.min(n - 1, Math.floor(rng() * n));
}

/** G(n, M): M distinct edges drawn uniformly. */
export function erGraph(n: number, m: number, rng: Rng): Graph {
  if (m > (n * (n - 1)) / 2) throw new EngineError("too many edges");
  const seen = new Set<number>();
  const edges: [number, number][] = [];
  while (edges.length < m) {
    const u = randInt(rng, n);
    const v = randInt(rng, n);
    if (u === v) continue;
    const key = Math.min(u, v) * n + Math.max(u, v);
    if (seen.has(key)) continue;
    seen.add(key);
    edges.push([Math.min(u, v), Math.max(u, v)]);
  }
  return fromEdges(n, edges);
}

/** Watts-Strogatz: ring lattice with k neighbours, each lattice edge rewired with probability beta. */
export function wsGraph(n: number, k: number, beta: number, rng: Rng): Graph {
  if (k % 2 !== 0 || k >= n) throw new EngineError("k must be even and below n");
  const adj: Set<number>[] = Array.from({ length: n }, () => new Set<number>());
  for (let u = 0; u < n; u++)
    for (let j = 1; j <= k / 2; j++) {
      const v = (u + j) % n;
      adj[u].add(v);
      adj[v].add(u);
    }
  for (let j = 1; j <= k / 2; j++) {
    for (let u = 0; u < n; u++) {
      const v = (u + j) % n;
      if (rng() < beta && adj[u].has(v) && adj[u].size < n - 1) {
        let w = randInt(rng, n);
        while (w === u || adj[u].has(w)) w = randInt(rng, n);
        adj[u].delete(v);
        adj[v].delete(u);
        adj[u].add(w);
        adj[w].add(u);
      }
    }
  }
  const edges: [number, number][] = [];
  for (let u = 0; u < n; u++) for (const v of adj[u]) if (u < v) edges.push([u, v]);
  return fromEdges(n, edges);
}

/** Barabasi-Albert: star on m + 1 nodes, then each new node attaches to m distinct nodes by degree. m (n - m) edges. */
export function baGraph(n: number, m: number, rng: Rng): Graph {
  if (m < 1 || m >= n) throw new EngineError("m must be in [1, n)");
  const edges: [number, number][] = [];
  const repeated: number[] = [];
  for (let v = 1; v <= m; v++) {
    edges.push([0, v]);
    repeated.push(0, v);
  }
  for (let source = m + 1; source < n; source++) {
    const targets = new Set<number>();
    while (targets.size < m) targets.add(repeated[randInt(rng, repeated.length)]);
    for (const t of targets) {
      edges.push([t, source]);
      repeated.push(t, source);
    }
  }
  return fromEdges(n, edges);
}

export function makeGraph(family: Family, n: number, rng: Rng): Graph {
  // Target mean degree 6, as in the research design: ER M = 3n, WS k = 6 and beta = 0.1, BA m = 3.
  if (family === "er") return erGraph(n, 3 * n, rng);
  if (family === "ws") return wsGraph(n, 6, 0.1, rng);
  return baGraph(n, 3, rng);
}

export type SeedRule = "random" | "highest_degree";

/** Seed sets: uniform without replacement, or the highest-degree nodes with seeded tie-breaks. */
export function selectSeeds(g: Graph, rule: SeedRule, count: number, rng: Rng): number[] {
  if (!Number.isInteger(count) || count < 1 || count > g.n) throw new EngineError("seed count out of range");
  if (rule === "random") {
    const pool = Array.from({ length: g.n }, (_, i) => i);
    for (let i = 0; i < count; i++) {
      const j = i + randInt(rng, g.n - i);
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    return pool.slice(0, count).sort((a, b) => a - b);
  }
  const tie = Array.from({ length: g.n }, () => rng());
  const order = Array.from({ length: g.n }, (_, i) => i).sort((a, b) => degree(g, b) - degree(g, a) || tie[a] - tie[b]);
  return order.slice(0, count).sort((a, b) => a - b);
}

/** Positions in [0, 1] x [0, 1]: a ring for WS, a short force-directed layout otherwise. */
export function layout(g: Graph, family: Family, rng: Rng, iterations = 120): Float64Array {
  const n = g.n;
  const pos = new Float64Array(2 * n);
  if (family === "ws") {
    for (let i = 0; i < n; i++) {
      pos[2 * i] = 0.5 + 0.46 * Math.cos((2 * Math.PI * i) / n);
      pos[2 * i + 1] = 0.5 + 0.46 * Math.sin((2 * Math.PI * i) / n);
    }
    return pos;
  }
  for (let i = 0; i < 2 * n; i++) pos[i] = rng();
  const k = Math.sqrt(1 / n);
  const disp = new Float64Array(2 * n);
  let temp = 0.1;
  for (let it = 0; it < iterations; it++) {
    disp.fill(0);
    for (let i = 0; i < n; i++)
      for (let j = i + 1; j < n; j++) {
        const dx = pos[2 * i] - pos[2 * j];
        const dy = pos[2 * i + 1] - pos[2 * j + 1];
        const d2 = Math.max(dx * dx + dy * dy, 1e-9);
        const f = (k * k) / d2;
        disp[2 * i] += dx * f;
        disp[2 * i + 1] += dy * f;
        disp[2 * j] -= dx * f;
        disp[2 * j + 1] -= dy * f;
      }
    for (let u = 0; u < n; u++)
      for (let j = g.indptr[u]; j < g.indptr[u + 1]; j++) {
        const v = g.indices[j];
        if (v <= u) continue;
        const dx = pos[2 * u] - pos[2 * v];
        const dy = pos[2 * u + 1] - pos[2 * v + 1];
        const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1e-9);
        const f = d / k;
        disp[2 * u] -= dx * f;
        disp[2 * u + 1] -= dy * f;
        disp[2 * v] += dx * f;
        disp[2 * v + 1] += dy * f;
      }
    for (let i = 0; i < n; i++) {
      const dx = disp[2 * i];
      const dy = disp[2 * i + 1];
      const d = Math.max(Math.sqrt(dx * dx + dy * dy), 1e-9);
      const step = Math.min(d, temp);
      pos[2 * i] += (dx / d) * step;
      pos[2 * i + 1] += (dy / d) * step;
    }
    temp *= 0.97;
  }
  // Normalise to [0.04, 0.96].
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (let i = 0; i < n; i++) {
    x0 = Math.min(x0, pos[2 * i]); x1 = Math.max(x1, pos[2 * i]);
    y0 = Math.min(y0, pos[2 * i + 1]); y1 = Math.max(y1, pos[2 * i + 1]);
  }
  const sx = x1 - x0 || 1;
  const sy = y1 - y0 || 1;
  for (let i = 0; i < n; i++) {
    pos[2 * i] = 0.04 + (0.92 * (pos[2 * i] - x0)) / sx;
    pos[2 * i + 1] = 0.04 + (0.92 * (pos[2 * i + 1] - y0)) / sy;
  }
  return pos;
}
