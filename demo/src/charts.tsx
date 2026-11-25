// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
// Hand-written SVG charts. Colours come from CSS tokens (style.css); text uses text tokens.
// Every chart has a plain-language description and a table with the same numbers.
import { useEffect, useRef, useState, type RefObject } from "react";
import type { Estimate, LevelBlock } from "./results";

export function useWidth<T extends HTMLElement>(fallback = 640): [RefObject<T | null>, number] {
  const ref = useRef<T | null>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => setW(Math.max(240, Math.floor(el.getBoundingClientRect().width)));
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

const SERIES_CLASS: Record<string, string> = { er: "s1", ws: "s2", ba: "s3", real: "s1", real_er: "s2", real_dpr: "s3" };
export const seriesClass = (t: string) => SERIES_CLASS[t] ?? "s1";

function ticks(lo: number, hi: number, count = 6): number[] {
  const span = hi - lo || 1;
  const raw = span / count;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10, 20].map((m) => m * mag).find((s) => span / s <= count) ?? 20 * mag;
  const out: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-12; t += step) out.push(Math.abs(t) < 1e-12 ? 0 : t);
  return out;
}

const tickText = (t: number) => (t === 0 ? "0" : `${t > 0 ? "+" : ""}${Number(t.toPrecision(3))}`);

/** Forest plot: one row per contrast, Holm-step interval as a line, SESOI as a band. */
export function ForestPlot({ rows, sesoi, title, description }: { rows: Estimate[]; sesoi: number; title: string; description: string }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const labelW = Math.min(150, Math.round(width * 0.38));
  const rowH = 24;
  const top = 8;
  const axisH = 28;
  const height = top + rows.length * rowH + axisH;
  const lo = Math.min(-sesoi, ...rows.map((r) => r.ci_low ?? r.estimate));
  const hi = Math.max(sesoi, ...rows.map((r) => r.ci_high ?? r.estimate));
  const pad = (hi - lo) * 0.06;
  const d0 = lo - pad;
  const d1 = hi + pad;
  const x0 = labelW + 8;
  const x1 = width - 12;
  const x = (v: number) => x0 + ((v - d0) / (d1 - d0)) * (x1 - x0);
  const id = title.replace(/\W+/g, "-");
  return (
    <figure className="chart" ref={ref}>
      <figcaption id={`${id}-cap`}>
        <strong>{title}</strong> {description}
      </figcaption>
      <svg width={width} height={height} role="img" aria-labelledby={`${id}-cap`}>
        <rect className="sesoi" x={x(-sesoi)} y={top} width={x(sesoi) - x(-sesoi)} height={rows.length * rowH} rx={2} />
        <line className="zero" x1={x(0)} x2={x(0)} y1={top} y2={top + rows.length * rowH} />
        {rows.map((r, i) => {
          const y = top + i * rowH + rowH / 2;
          const filled = r.rejected === true;
          return (
            <g key={r.label}>
              <text className="tick-label" x={labelW} y={y + 4} textAnchor="end">
                {typeof r.param === "string" ? `${r.contrast}, ${r.param}` : `${r.contrast}, ${r.param_name} = ${r.param}`}
              </text>
              {r.ci_low !== null && r.ci_high !== null && (
                <line className="ci" x1={x(r.ci_low)} x2={x(r.ci_high)} y1={y} y2={y} />
              )}
              <circle className={filled ? "pt" : "pt hollow"} cx={x(r.estimate)} cy={y} r={5}>
                <title>
                  {`${r.contrast}, ${r.param_name} = ${r.param}: ${r.display} ${r.interval_display} (level ${r.level_display}); ${r.rejected ? "rejected" : "not rejected"}; ${r.inside_sesoi ? "inside" : "outside"} the SESOI`}
                </title>
              </circle>
            </g>
          );
        })}
        {ticks(d0, d1).map((t) => (
          <g key={t}>
            <line className="grid" x1={x(t)} x2={x(t)} y1={top + rows.length * rowH} y2={top + rows.length * rowH + 5} />
            <text className="tick-label" x={x(t)} y={top + rows.length * rowH + 18} textAnchor="middle">
              {tickText(t)}
            </text>
          </g>
        ))}
      </svg>
      <p className="legend">
        <span className="key"><svg width="14" height="14" aria-hidden="true"><circle className="pt" cx="7" cy="7" r="5" /></svg> Holm rejects H0</span>
        <span className="key"><svg width="14" height="14" aria-hidden="true"><circle className="pt hollow" cx="7" cy="7" r="5" /></svg> H0 not rejected</span>
        <span className="key"><svg width="18" height="12" aria-hidden="true"><rect className="sesoi" x="0" y="1" width="18" height="10" /></svg> SESOI band, plus or minus {sesoi}</span>
      </p>
    </figure>
  );
}

/** Mean final cascade fraction by parameter, one line per topology, interval as a band. */
export function LevelsChart({ block, title, description }: { block: LevelBlock; title: string; description: string }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const height = 260;
  const m = { l: 44, r: 64, t: 10, b: 36 };
  const xs = block.series[0].points.map((p) => p.param);
  const d0 = Math.min(...xs);
  const d1 = Math.max(...xs);
  const x = (v: number) => m.l + ((v - d0) / (d1 - d0)) * (width - m.l - m.r);
  const y = (v: number) => m.t + (1 - v) * (height - m.t - m.b);
  const id = title.replace(/\W+/g, "-");
  const [open, setOpen] = useState(false);
  // Direct labels at the right end, nudged apart so they never overlap.
  const ends = block.series.map((s) => ({ s, y: y(s.points[s.points.length - 1].mean) })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 14) ends[i].y = ends[i - 1].y + 14;
  const over = ends.length ? ends[ends.length - 1].y - (y(0) - 8) : 0;
  if (over > 0) for (const e of ends) e.y -= over;
  return (
    <figure className="chart" ref={ref}>
      <figcaption id={`${id}-cap`}>
        <strong>{title}</strong> {description}
      </figcaption>
      <svg width={width} height={height} role="img" aria-labelledby={`${id}-cap`}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <g key={t}>
            <line className="grid" x1={m.l} x2={width - m.r} y1={y(t)} y2={y(t)} />
            <text className="tick-label" x={m.l - 6} y={y(t) + 4} textAnchor="end">{t}</text>
          </g>
        ))}
        {xs.map((t) => (
          <text key={t} className="tick-label" x={x(t)} y={height - m.b + 16} textAnchor="middle">
            {width < 420 && xs.length > 5 && xs.indexOf(t) % 2 === 1 ? "" : block.series[0].points[xs.indexOf(t)].param_display}
          </text>
        ))}
        <text className="tick-label" x={(m.l + width - m.r) / 2} y={height - 4} textAnchor="middle">{block.param_name}</text>
        {block.series.map((s) => {
          const band = s.points.map((p) => `${x(p.param)},${y(p.hi)}`).concat([...s.points].reverse().map((p) => `${x(p.param)},${y(p.lo)}`)).join(" ");
          return (
            <g key={s.topology} className={seriesClass(s.topology)}>
              <polygon className="band" points={band} />
              <polyline className="line" points={s.points.map((p) => `${x(p.param)},${y(p.mean)}`).join(" ")} />
              {s.points.map((p) => (
                <circle key={p.param} className="dot" cx={x(p.param)} cy={y(p.mean)} r={4}>
                  <title>{`${s.label}, ${block.param_name} = ${p.param_display}: mean S ${p.display} ${p.interval_display}`}</title>
                </circle>
              ))}
            </g>
          );
        })}
        {ends.map(({ s, y: yy }) => (
          <text key={s.topology} className="direct-label" x={width - m.r + 8} y={yy + 4}>{s.label}</text>
        ))}
      </svg>
      <p className="legend">
        {block.series.map((s) => (
          <span key={s.topology} className={`key ${seriesClass(s.topology)}`}>
            <svg width="18" height="10" aria-hidden="true"><line className="line" x1="0" x2="18" y1="5" y2="5" /></svg> {s.label}
          </span>
        ))}
        <span className="key">Shaded: {block.interval}</span>
      </p>
      <details onToggle={(ev) => setOpen((ev.currentTarget as HTMLDetailsElement).open)}>
        <summary id={`${id}-sum`}>Table of the plotted values</summary>
        {open && <div id={`${id}-tbl`} className="table-scroll" role="region" aria-label={`${title} values`} tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">{block.param_name}</th>
                {block.series.map((s) => <th key={s.topology} scope="col">{s.label}: mean S [95 percent]</th>)}
              </tr>
            </thead>
            <tbody>
              {block.series[0].points.map((p, i) => (
                <tr key={p.param}>
                  <th scope="row">{p.param_display}</th>
                  {block.series.map((s) => <td key={s.topology}>{s.points[i].display} {s.points[i].interval_display}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>}
      </details>
    </figure>
  );
}
