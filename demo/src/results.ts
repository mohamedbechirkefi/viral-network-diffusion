// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  // VIRAL extensions (all required by validateResults).
  level_display: string;
  interval_kind: string;
  kind: string;
  analysis: string;
  contrast: string;
  param_name: string;
  param: number | string;
  rejected: boolean | null;
  inside_sesoi: boolean | null;
  claim_id: string;
  printed_in: string;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface LevelPoint {
  param: number;
  param_display: string;
  mean: number;
  lo: number;
  hi: number;
  display: string;
  interval_display: string;
  replicates: number;
}

export interface LevelBlock {
  model: string;
  param_name: string;
  seed_rule: string;
  seed_count: number;
  interval: string;
  printed_in: string;
  series: { topology: string; label: string; points: LevelPoint[] }[];
}

export interface GraphStatRow {
  topology: string;
  label: string;
  edges: string;
  second_moment: string;
  p_c: string;
  clustering: string;
  giant_fraction: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  sesoi: number;
  levels: Record<string, LevelBlock>;
  graph_stats: { experiment: string; printed_in: string; rows: GraphStatRow[] };
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function boolOrNull(o: Obj, k: string, where: string): boolean | null {
  const v = o[k];
  if (v === null || typeof v === "boolean") return v;
  throw new ResultsError(`${where}.${k}: expected a boolean or null`);
}

function levelBlock(v: unknown, where: string): LevelBlock {
  const o = obj(v, where);
  const series = arr(o, "series", where).map((sv, i) => {
    const w = `${where}.series[${i}]`;
    const so = obj(sv, w);
    const points = arr(so, "points", w).map((pv, j) => {
      const pw = `${w}.points[${j}]`;
      const po = obj(pv, pw);
      const p: LevelPoint = {
        param: num(po, "param", pw) as number,
        param_display: str(po, "param_display", pw),
        mean: num(po, "mean", pw) as number,
        lo: num(po, "lo", pw) as number,
        hi: num(po, "hi", pw) as number,
        display: str(po, "display", pw),
        interval_display: str(po, "interval_display", pw),
        replicates: num(po, "replicates", pw) as number,
      };
      if (p.lo > p.hi || p.mean < 0 || p.mean > 1) throw new ResultsError(`${pw}: invalid level or interval`);
      return p;
    });
    if (points.length < 2) throw new ResultsError(`${w}.points: need at least two points`);
    return { topology: str(so, "topology", w), label: str(so, "label", w), points };
  });
  if (series.length === 0) throw new ResultsError(`${where}.series: empty`);
  return {
    model: str(o, "model", where),
    param_name: str(o, "param_name", where),
    seed_rule: str(o, "seed_rule", where),
    seed_count: num(o, "seed_count", where) as number,
    interval: str(o, "interval", where),
    printed_in: str(o, "printed_in", where),
    series,
  };
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    level_display: str(o, "level_display", where),
    interval_kind: str(o, "interval_kind", where),
    kind: str(o, "kind", where),
    analysis: str(o, "analysis", where),
    contrast: str(o, "contrast", where),
    param_name: str(o, "param_name", where),
    param: typeof o.param === "string" ? str(o, "param", where) : (num(o, "param", where) as number),
    rejected: boolOrNull(o, "rejected", where),
    inside_sesoi: boolOrNull(o, "inside_sesoi", where),
    claim_id: str(o, "claim_id", where),
    printed_in: str(o, "printed_in", where),
  };
  if (e.display === null || e.interval_display === null) {
    throw new ResultsError(`${where}: display and interval_display are required (exact manuscript text)`);
  }
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    sesoi: num(o, "sesoi", "results") as number,
    levels: Object.fromEntries(
      Object.entries(obj(o.levels, "results.levels")).map(([k, v]) => [k, levelBlock(v, `levels.${k}`)]),
    ),
    graph_stats: (() => {
      const g = obj(o.graph_stats, "results.graph_stats");
      const rows = arr(g, "rows", "graph_stats").map((rv, i) => {
        const w = `graph_stats.rows[${i}]`;
        const r = obj(rv, w);
        return {
          topology: str(r, "topology", w), label: str(r, "label", w), edges: str(r, "edges", w),
          second_moment: str(r, "second_moment", w), p_c: str(r, "p_c", w),
          clustering: str(r, "clustering", w), giant_fraction: str(r, "giant_fraction", w),
        };
      });
      if (rows.length === 0) throw new ResultsError("graph_stats.rows: empty");
      return { experiment: str(g, "experiment", "graph_stats"), printed_in: str(g, "printed_in", "graph_stats"), rows };
    })(),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
