// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Visitor sandbox: an animated cascade and cascade-size distributions computed in a Web Worker
// from the visitor's settings. Its output is labelled as sandbox output and never mixed with
// the published results. Nothing is stored or sent.
import { useCallback, useEffect, useRef, useState } from "react";
import { useWidth, seriesClass } from "./charts";
import type { Family } from "./engine";
import { BINS, LIMITS, type SandboxSettings, type ShownCascade, type TopologySummary, type WorkerReply, type WorkerRequest } from "./sandbox.worker";

const DEFAULTS: SandboxSettings = { seed: 1, model: "ic", param: 0.3, seedRule: "random", seedCount: 1, n: 200, cascades: 300, show: "ws" };
const NAMES: Record<Family, string> = { er: "ER", ws: "WS", ba: "BA" };
const f4 = (x: number) => x.toFixed(4);

function prefersReducedMotion(): boolean {
  try {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch {
    return false;
  }
}

type Result = { settings: SandboxSettings; summaries: TopologySummary[]; shown: ShownCascade };

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [form, setForm] = useState<SandboxSettings>(DEFAULTS);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [out, setOut] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [animate, setAnimate] = useState(() => !prefersReducedMotion());

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") {
        setProgress(m.fraction);
        return;
      }
      if (m.type === "done") {
        setResult({ settings: m.settings, summaries: m.summaries, shown: m.shown });
        const s = m.settings;
        const par = s.model === "ic" ? `IC, p = ${s.param}` : `LT, phi = ${s.param}`;
        setOut(
          `Sandbox output (seed ${s.seed}; ${par}; N = ${s.n}; ${s.cascades} cascades per topology; ${s.seedCount} ${s.seedRule === "random" ? "random" : "highest-degree"} seed${s.seedCount > 1 ? "s" : ""}): mean S ` +
            m.summaries.map((t) => `${NAMES[t.family]} ${f4(t.meanS)} [${f4(t.lo)}, ${f4(t.hi)}]`).join("; ") + ".",
        );
      }
      if (m.type === "error") setOut(`Sandbox run stopped: ${m.message}`);
      if (m.type === "cancelled") setOut("Sandbox run cancelled.");
      setRunning(false);
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  const start = useCallback((s: SandboxSettings) => {
    setRunning(true);
    setProgress(0);
    setOut("");
    worker.current?.postMessage({ type: "run", settings: s } satisfies WorkerRequest);
  }, []);

  // One initial run with the default settings, so the page shows a network on first load.
  useEffect(() => {
    const t = setTimeout(() => start(DEFAULTS), 0);
    return () => clearTimeout(t);
  }, [start]);

  const run = () => start(form);
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    setForm(DEFAULTS);
    start(DEFAULTS);
  };
  const set = <K extends keyof SandboxSettings>(k: K, v: SandboxSettings[K]) => setForm((f) => ({ ...f, [k]: v }));
  const clampInt = (v: string, lo: number, hi: number, d: number) => {
    const x = Math.round(Number(v));
    return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
  };

  const exportJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify({ label: "VIRAL sandbox output (not a research result)", ...result.settings, summaries: result.summaries }, null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `viral-sandbox-seed-${result.settings.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Sandbox: run cascades yourself</h2>
      <p className="label label-sandbox">Sandbox output, computed in your browser</p>
      <p className="note">
        The diffusion rules are a port of the research engine: on the same graph and random stream they reproduce its
        cascades exactly (tested). The graphs are generated in your browser by the same three models at a smaller size,
        with fewer cascades, so sandbox numbers are not the published numbers and cannot replace them. Intervals here
        are normal approximations over cascades on one graph, not the study's replicate-level intervals.
      </p>
      <form className="controls" onSubmit={(e) => { e.preventDefault(); run(); }}>
        <label>
          Model
          <select id="sb-model" value={form.model} onChange={(e) => { const model = e.target.value as "ic" | "lt"; setForm((f) => ({ ...f, model, param: model === "ic" ? 0.3 : 0.22 })); }}>
            <option value="ic">Independent cascade (p)</option>
            <option value="lt">Fractional threshold (phi)</option>
          </select>
        </label>
        <label>
          {form.model === "ic" ? "Transmission p" : "Threshold phi"}
          <input id="sb-param" type="number" min={0} max={1} step={0.01} value={form.param}
            onChange={(e) => set("param", Math.min(1, Math.max(0, Number(e.target.value) || 0)))} />
        </label>
        <label>
          Initial exposure
          <select id="sb-rule" value={form.seedRule} onChange={(e) => set("seedRule", e.target.value as SandboxSettings["seedRule"])}>
            <option value="random">Random seed nodes</option>
            <option value="highest_degree">Highest-degree nodes</option>
          </select>
        </label>
        <label>
          Seed nodes
          <input id="sb-count" type="number" min={1} max={LIMITS.seedCountMax} value={form.seedCount}
            onChange={(e) => set("seedCount", clampInt(e.target.value, 1, LIMITS.seedCountMax, 1))} />
        </label>
        <label>
          Nodes N
          <select id="sb-n" value={form.n} onChange={(e) => set("n", Number(e.target.value))}>
            {[100, 200, 400].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
        <label>
          Cascades per topology
          <select id="sb-cascades" value={form.cascades} onChange={(e) => set("cascades", Number(e.target.value))}>
            {[100, 300, 1000].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
        <label>
          Animate topology
          <select id="sb-show" value={form.show} onChange={(e) => set("show", e.target.value as Family)}>
            <option value="er">ER (random)</option>
            <option value="ws">WS (small-world)</option>
            <option value="ba">BA (scale-free)</option>
          </select>
        </label>
        <label>
          Random seed
          <input id="sb-seed" type="number" min={1} max={LIMITS.seedMax} value={form.seed}
            onChange={(e) => set("seed", clampInt(e.target.value, 1, LIMITS.seedMax, 1))} />
        </label>
        <div className="buttons">
          <button type="submit" disabled={running}>Run</button>
          <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
          <button type="button" onClick={reset} disabled={running}>Reset</button>
          <button type="button" onClick={exportJson} disabled={!result || running}>Save as JSON</button>
        </div>
      </form>
      <p aria-live="polite" className="sandbox-out">{out}</p>
      {running && <p className="note">Running: {Math.round(progress * 100)} percent.</p>}
      <label className="check">
        <input id="sb-animate" type="checkbox" checked={animate} onChange={(e) => setAnimate(e.target.checked)} /> Animate the cascade round by round
        (off by default when your system asks for reduced motion)
      </label>
      {result && (
        <div className="sandbox-grid">
          <NetworkView shown={result.shown} model={result.settings.model} animate={animate} />
          <Histograms summaries={result.summaries} />
        </div>
      )}
    </section>
  );
}

function NetworkView({ shown, model, animate }: { shown: ShownCascade; model: "ic" | "lt"; animate: boolean }) {
  const last = Math.max(0, ...shown.round);
  const [round, setRound] = useState(animate ? 0 : last);
  const [playing, setPlaying] = useState(animate);

  useEffect(() => {
    setRound(animate ? 0 : last);
    setPlaying(animate);
  }, [shown, animate, last]);

  useEffect(() => {
    if (!playing) return;
    if (round >= last) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setRound((r) => r + 1), 450);
    return () => clearTimeout(t);
  }, [playing, round, last]);

  const active = shown.round.filter((r) => r >= 0 && r <= round).length;
  const path = shown.edges.map(([u, v]) => `M${(shown.pos[2 * u] * 100).toFixed(2)} ${(shown.pos[2 * u + 1] * 100).toFixed(2)}L${(shown.pos[2 * v] * 100).toFixed(2)} ${(shown.pos[2 * v + 1] * 100).toFixed(2)}`).join("");
  const r = shown.family === "ws" ? (shown.n > 150 ? 0.7 : 1.0) : shown.n > 250 ? 0.9 : 1.3;
  return (
    <figure className="chart network">
      <figcaption id="net-cap">
        <strong>One {model.toUpperCase()} cascade on a sandbox {NAMES[shown.family]} graph.</strong> Seeds are outlined; filled nodes
        are active by the round shown; the most recent round is drawn larger. Edges are grey.
      </figcaption>
      <svg viewBox="0 0 100 100" role="img" aria-labelledby="net-cap net-state" className="net">
        <path className="edges" d={path} />
        {shown.round.map((ar, i) => {
          const on = ar >= 0 && ar <= round;
          const fresh = on && ar === round && round > 0;
          const seed = ar === 0;
          return (
            <circle key={i} cx={shown.pos[2 * i] * 100} cy={shown.pos[2 * i + 1] * 100} r={fresh ? r * 1.5 : r}
              className={seed ? "node seed" : on ? "node on" : "node"} />
          );
        })}
      </svg>
      <p id="net-state" className="meta">
        Round {round} of {last}: {active} of {shown.n} nodes active (final size {shown.size}, S = {f4(shown.size / shown.n)}).
      </p>
      <div className="buttons">
        <button type="button" onClick={() => { if (round >= last) setRound(0); setPlaying((p) => !p); }}>
          {playing ? "Pause" : "Play"}
        </button>
        <button type="button" onClick={() => { setPlaying(false); setRound((x) => Math.min(last, x + 1)); }}>Step</button>
        <button type="button" onClick={() => { setPlaying(false); setRound(0); }}>First round</button>
        <button type="button" onClick={() => { setPlaying(false); setRound(last); }}>Final state</button>
      </div>
    </figure>
  );
}

function Histograms({ summaries }: { summaries: TopologySummary[] }) {
  const [ref, width] = useWidth<HTMLDivElement>(300);
  const h = 130;
  const m = { l: 34, r: 8, t: 8, b: 26 };
  const ymax = Math.max(0.05, ...summaries.flatMap((s) => s.histogram));
  const bw = (width - m.l - m.r) / BINS;
  const y = (v: number) => m.t + (1 - v / ymax) * (h - m.t - m.b);
  return (
    <figure className="chart" ref={ref}>
      <figcaption>
        <strong>Distribution of final cascade fraction S, sandbox.</strong> Share of cascades in each S bin of width 0.05, one
        panel per topology, same vertical scale. Near threshold the distribution is often bimodal: many cascades die out
        early and others become large.
      </figcaption>
      {summaries.map((s) => (
        <div key={s.family} className={`hist ${seriesClass(s.family)}`}>
          <p className="meta">
            {NAMES[s.family]}: {s.edges} edges, p_c estimate {f4(s.pc)}; mean S {f4(s.meanS)} [{f4(s.lo)}, {f4(s.hi)}]
          </p>
          <svg width={width} height={h} role="img" aria-label={`${NAMES[s.family]} histogram of S: ` + s.histogram.map((v, i) => `${(i * 0.05).toFixed(2)} to ${((i + 1) * 0.05).toFixed(2)}: ${(v * 100).toFixed(1)} percent`).join("; ")}>
            <line className="grid" x1={m.l} x2={width - m.r} y1={y(0)} y2={y(0)} />
            <text className="tick-label" x={m.l - 4} y={y(ymax) + 4} textAnchor="end">{Math.round(ymax * 100)}%</text>
            <text className="tick-label" x={m.l - 4} y={y(0) + 4} textAnchor="end">0</text>
            {s.histogram.map((v, i) => (
              v > 0 && <rect key={i} className="bar" x={m.l + i * bw + 1} width={Math.max(1, bw - 2)} y={y(v)} height={Math.max(1, y(0) - y(v))} rx={1.5}>
                <title>{`S ${(i * 0.05).toFixed(2)} to ${((i + 1) * 0.05).toFixed(2)}: ${(v * 100).toFixed(1)} percent of cascades`}</title>
              </rect>
            ))}
            {[0, 0.5, 1].map((t) => (
              <text key={t} className="tick-label" x={m.l + t * (width - m.l - m.r)} y={h - 8} textAnchor={t === 0 ? "start" : t === 1 ? "end" : "middle"}>S = {t}</text>
            ))}
          </svg>
        </div>
      ))}
    </figure>
  );
}
