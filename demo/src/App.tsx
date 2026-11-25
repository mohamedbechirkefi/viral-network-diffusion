// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import { useEffect, useState } from "react";
import { ForestPlot, LevelsChart } from "./charts";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Estimate, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="wrap">
          <p className="kicker">VIRAL, a simulation study of network diffusion</p>
          <h1>How do network topology and initial exposure change how far identical content spreads?</h1>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#results">Results</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Sandbox</a>
          </nav>
        </div>
      </header>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <Sandbox />
      </main>
      <footer className="site">
        <div className="wrap">
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere. All results
            are simulations of stylised models; nothing here describes a real social platform, its algorithms, real
            people or any guarantee of virality.
          </p>
        </div>
      </footer>
    </>
  );
}

const decision = (x: Estimate) => (x.rejected === null ? "no Holm test" : x.rejected ? "rejected" : "not rejected");
const sesoiText = (x: Estimate) => (x.inside_sesoi === null ? "not assessed" : x.inside_sesoi ? "inside" : "outside");

function EstimateTable({ e, rows }: { e: Experiment; rows: Estimate[] }) {
  const long = rows.length > 16;
  return (
    <div id={`tbl-${e.id}-${rows[0].analysis.replace(/\W+/g, "-")}`} className={long ? "table-scroll tall" : "table-scroll"} role="region" aria-label={`${e.id} ${rows[0].analysis} estimates`} tabIndex={0}>
      <table className="est">
        <thead>
          <tr>
            <th scope="col">Quantity</th>
            <th scope="col">Estimate</th>
            <th scope="col">Interval (level)</th>
            <th scope="col">Holm decision</th>
            <th scope="col">SESOI</th>
            <th scope="col">Claim</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((x) => (
            <tr key={x.claim_id}>
              <th scope="row">{x.label.startsWith(x.analysis + ": ") ? x.label.slice(x.analysis.length + 2) : x.label}</th>
              <td data-label="Estimate">{fmtEstimate(x)}</td>
              <td data-label="Interval (level)">{fmtInterval(x)} ({x.level_display})</td>
              <td data-label="Holm decision">{decision(x)}</td>
              <td data-label="SESOI">{sesoiText(x)}</td>
              <td data-label="Claim"><code>{x.claim_id}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ExperimentPanel({ e, r }: { e: Experiment; r: Results }) {
  const groups = [...new Set(e.estimates.map((x) => x.analysis))];
  const forest = (a: string) => ["primary", "primary grid mean", "S1", "S2"].includes(a);
  const kinds = [...new Set(e.estimates.map((x) => x.kind))];
  return (
    <article className="panel" aria-labelledby={`h-${e.id}`}>
      <h3 id={`h-${e.id}`}>
        {e.id}: {e.title}
      </h3>
      <p>
        <span className="badge">{e.status}</span>{" "}
        <span className="label label-measured">{kinds.some((k) => k.startsWith("exploratory")) || e.id === "EXP-001" ? "measured, exploratory" : "measured, published"}</span>
      </p>
      <p className="verdict"><strong>Verdict under the frozen rule:</strong> {e.verdict}</p>
      {e.notes.map((n, i) => (
        <p key={i} className="note">{n}</p>
      ))}
      {e.id === "EXP-002" && (
        <LevelsChart block={r.levels["EXP-002"]} title="Figure B. Mean final cascade fraction S by p (EXP-002, IC, one random seed)."
          description="Each point is the mean over 120 graph replicates of the per-graph mean S. Lines join measured grid points only. BA takes off first; ER overtakes it above both thresholds; WS stays far below ER at p = 0.30 and finishes highest at p = 0.50." />
      )}
      {e.id === "EXP-003" && (
        <LevelsChart block={r.levels["EXP-003"]} title="Figure C. Mean S by threshold phi (EXP-003, LT, ten random seeds)."
          description="Mean over 30 replicates. All three saturate at phi = 0.18 and 0.20; in the transition region WS spreads far more than ER, the reverse of its IC deficit." />
      )}
      {e.id === "EXP-005" && (
        <LevelsChart block={r.levels["EXP-005"]} title="Figure D. Mean S by calibrated p (EXP-005, one real network and two nulls)."
          description="Mean over 120 batches or replicates. The real network lies below its degree-preserving null wherever a difference is detectable." />
      )}
      {groups.map((g) => {
        const rows = e.estimates.filter((x) => x.analysis === g);
        return (
          <div key={g} className="group">
            {groups.length > 1 && <h4>{g === "S1" ? "S1, per multiplier c (no overall verdict)" : g} <span className="badge">{rows[0].kind}</span></h4>}
            {forest(g) && (
              <ForestPlot rows={rows} sesoi={r.sesoi}
                title={`${e.id} ${g}: paired differences in S with ${rows[0].interval_kind}s.`}
                description={g === "S1"
                  ? "Each multiplier c is a separate test; the rows are not combined into one verdict. Hollow markers are non-rejections and carry the same weight as filled ones."
                  : "Treatment minus comparator, per parameter value. Hollow markers are non-rejections and carry the same weight as filled ones. Several intervals are narrower than the markers."} />
            )}
            <EstimateTable e={e} rows={rows} />
          </div>
        );
      })}
      <p className="meta">
        Report: <code>{e.report_path}</code>
        {e.claim_ids.length > 0 ? <> · Claims: {e.claim_ids.length} rows in <code>research/claims_register.csv</code></> : <> · No claim rows</>}
      </p>
    </article>
  );
}

function Published({ r }: { r: Results }) {
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label">{r.status_label}</p>
        <p><strong>Question.</strong> {r.question}</p>
        <p>
          Content quality is held fixed by giving every edge the same transmission probability p (independent cascade,
          IC) or every node the same adoption threshold phi (fractional threshold, LT). Watts-Strogatz (WS, small-world)
          and Barabasi-Albert (BA, scale-free) graphs are compared with Erdos-Renyi (ER) graphs of the same size and mean
          degree, under a protocol frozen before any confirmatory run.
        </p>
        <p className="lead">
          Within these models, topology effects are large but are not one effect: their sign and size depend on p and
          on the contagion rule. Holm rejects 13 of 14 IC contrasts, but only 7 of 14 lie outside the smallest effect
          size of interest; six rejections are detectable yet negligible.
        </p>
        <div className="labels-key" aria-label="How results are labelled">
          <span className="label label-measured">measured, published</span> committed simulation results, identical to the manuscript
          <span className="label label-assumption">assumption</span> a design value chosen before the runs
          <span className="label label-sandbox">sandbox output</span> computed in your browser, never mixed with the above
        </div>
      </section>

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          These numbers come from the committed results at revision <code>{r.code_revision.slice(0, 12)}</code> and are
          printed exactly as in the manuscript (version 0.2) or its supplementary tables. Every registered experiment is
          listed, including the null and negligible contrasts, together with the exploratory checks. They are separate
          from anything the sandbox below produces.
        </p>
        <figure className="chart">
          <figcaption><strong>Table A. Graph statistics of EXP-002</strong> (means over 120 graphs per topology; manuscript Table 2).</figcaption>
          <div id="tbl-graph-stats" className="table-scroll" role="region" aria-label="Graph statistics" tabIndex={0}>
            <table>
              <thead>
                <tr><th scope="col">statistic</th>{r.graph_stats.rows.map((g) => <th key={g.topology} scope="col">{g.label}</th>)}</tr>
              </thead>
              <tbody>
                <tr><th scope="row">edges</th>{r.graph_stats.rows.map((g) => <td key={g.topology}>{g.edges}</td>)}</tr>
                <tr><th scope="row">&lt;k^2&gt;</th>{r.graph_stats.rows.map((g) => <td key={g.topology}>{g.second_moment}</td>)}</tr>
                <tr><th scope="row">p_c estimate</th>{r.graph_stats.rows.map((g) => <td key={g.topology}>{g.p_c}</td>)}</tr>
                <tr><th scope="row">average clustering</th>{r.graph_stats.rows.map((g) => <td key={g.topology}>{g.clustering}</td>)}</tr>
                <tr><th scope="row">giant-component fraction</th>{r.graph_stats.rows.map((g) => <td key={g.topology}>{g.giant_fraction}</td>)}</tr>
              </tbody>
            </table>
          </div>
        </figure>
        {r.experiments.map((e) => (
          <ExperimentPanel key={e.id} e={e} r={r} />
        ))}
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions</h2>
        <p><span className="label label-assumption">assumption</span> Design values fixed in the frozen protocol before any confirmatory run.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          The independent unit is the matched graph set, not the cascade. Each contrast is the mean of paired replicate
          differences, with a paired cluster bootstrap (B = 10000) and Holm step-down control within each confirmatory
          family. A contrast counts as practically negligible only if its whole interval lies inside the SESOI of plus or
          minus 0.02. Exploratory and secondary intervals are unadjusted and labelled so. The full method is in the
          manuscript, <code>research/paper/manuscript.md</code>, and each experiment has a standalone report.
        </p>
        <h3>Limitations</h3>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary id="sum-sources">Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
