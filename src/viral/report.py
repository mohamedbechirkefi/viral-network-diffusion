# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Report generator: tables and figures built only from a validated result file.

Writes report.md, tables/*.csv and figures/*.{png,svg} next to the result.
With pdf=True it converts report.md to PDF with pandoc (Markdown to Typst,
-V mainfont="Libertinus Serif") and the typst Python package.
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import analysis
from .config import ExperimentConfig
from .results import load_result

EXPLORATORY_BANNER = (
    "**EXPLORATORY RUN. Not a finding.** The protocol is not frozen. These numbers are "
    "simulation outputs used for engine checks and planning (runtime, seed spread, degenerate "
    "cells). They must not be cited as results."
)


def _fmt(x, nd=4):
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def _md_table(rows: list[dict], cols: list[tuple[str, str]], nd=4) -> str:
    if not rows:
        return "_No rows._\n"
    head = "| " + " | ".join(h for _, h in cols) + " |\n"
    sep = "|" + "|".join("---" for _ in cols) + "|\n"
    body = "".join("| " + " | ".join(_fmt(r.get(k), nd) for k, _ in cols) + " |\n" for r in rows)
    return head + sep + body


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (";".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})


def _figures(doc: dict, fig_dir: Path) -> list[tuple[str, str, str]]:
    """Return (file stem, caption, alt text). Requires matplotlib (dependency group 'figures')."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []
    import numpy as np

    figs = []
    n = doc["config"]["n"]
    ic = [c for c in doc["cells"] if c["model"] == "ic" and c["seed_rule"] == "random" and c["seed_count"] == 1]
    params = sorted({c["param"] for c in ic if 0 < c["param"] < 1})
    topos = [t for t in ("er", "ws", "ba") if any(c["topology"] == t for c in ic)]
    if params and topos:
        fig, axes = plt.subplots(1, len(params), figsize=(3.2 * len(params), 3.2), squeeze=False)
        for ax, p in zip(axes[0], params):
            data = [np.array([s / n for c in ic if c["topology"] == t and c["param"] == p for s in c["per_cascade"]["size"]]) for t in topos]
            ax.boxplot(data, tick_labels=[t.upper() for t in topos], showfliers=True, flierprops={"markersize": 2})
            ax.set_title(f"IC, p = {p}")
            ax.set_ylabel("final cascade fraction S")
        fig.suptitle("EXPLORATORY: per-cascade S, one random seed")
        fig.tight_layout()
        stem = "fig_exploratory_S_distribution"
        for ext in ("png", "svg"):
            fig.savefig(fig_dir / f"{stem}.{ext}", dpi=150)
        plt.close(fig)
        figs.append((stem, "Exploratory distribution of the final cascade fraction S per cascade, by topology and transmission probability p (IC, one uniformly random seed). Boxes pool all cascades over all graph replicates; cascades on one graph are correlated.",
                     "Box plots of final cascade fraction for ER, WS and BA graphs at each tested transmission probability."))
        fig, axes = plt.subplots(1, len(params), figsize=(3.2 * len(params), 3.2), squeeze=False)
        for ax, p in zip(axes[0], params):
            for i, t in enumerate(topos):
                ms = [c["summary"]["mean_S"] for c in ic if c["topology"] == t and c["param"] == p]
                ax.plot([i] * len(ms), ms, "o", alpha=0.7)
            ax.set_xticks(range(len(topos)), [t.upper() for t in topos])
            ax.set_title(f"IC, p = {p}")
            ax.set_ylabel("per-graph mean S")
        fig.suptitle("EXPLORATORY: replicate means (unit of analysis)")
        fig.tight_layout()
        stem = "fig_exploratory_replicate_means"
        for ext in ("png", "svg"):
            fig.savefig(fig_dir / f"{stem}.{ext}", dpi=150)
        plt.close(fig)
        figs.append((stem, "Exploratory per-graph mean of S (one point per graph replicate, the independent unit) by topology and p.",
                     "Dot plots of per-graph mean cascade fraction for each topology at each transmission probability."))
    return figs


def build_report(result_path: str | Path, project: ExperimentConfig | None = None, pdf: bool = False,
                 pandoc: str | None = None, typst_python: str | None = None) -> Path:
    doc = load_result(result_path)
    run_dir = Path(result_path)
    run_dir = run_dir if run_dir.is_dir() else run_dir.parent
    tables = run_dir / "tables"
    figs_dir = run_dir / "figures"
    tables.mkdir(exist_ok=True)
    figs_dir.mkdir(exist_ok=True)

    g_rows = analysis.graph_table(doc)
    c_rows = analysis.cell_table(doc)
    k_rows = analysis.contrasts(doc)
    kp_rows = analysis.contrasts_by_param(doc)
    v_rows = analysis.variance_table(doc)
    d_rows = analysis.degenerate_cells(doc)
    for name, rows in (("graphs", g_rows), ("cells", c_rows), ("contrasts", k_rows), ("contrasts_by_param", kp_rows), ("variance", v_rows), ("degenerate", d_rows)):
        _write_csv(rows, tables / f"{name}.csv")
    figs = _figures(doc, figs_dir)

    m = doc["manifest"]
    ver = doc["verification"]
    lines = [
        "<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->",
        f"# {doc['experiment_id']} run report: {doc['run_id']}",
        "",
        EXPLORATORY_BANNER if doc["mode"] == "exploratory" else "**Confirmatory run against a frozen protocol.**",
        "",
        f"Label: {doc['label']}",
        "",
        "Generated by `viral report` from `result.json` only; every number below is computed from that file.",
        "",
        "## Run record",
        "",
        f"- Config hash: `{doc['config_hash']}`",
        f"- Master seed: {m['master_seed']}; engine: {m.get('engine')}",
        f"- Git revision: `{m['git_revision']}` (dirty: {m['git_dirty']})",
        f"- Started / finished (UTC): {m['started_utc']} / {m['finished_utc']}",
        f"- Runtime: {m['runtime_seconds']:.2f} s; process peak RSS: {m['peak_rss_bytes']} bytes",
        f"- Versions: {', '.join(f'{k} {v}' for k, v in m['versions'].items())}",
        f"- OS: {m['os']}; CPU: {m['cpu']}",
        f"- Graphs: {len(doc['graphs'])}; cells: {len(doc['cells'])}; cascades: {sum(c['n_cascades'] for c in doc['cells'])}",
        "",
        "## Verification checks",
        "",
        f"- Graphs checked: {ver['graphs_checked']}, failures: {ver['graph_failures']}",
        f"- Cascades checked: {ver['cascades_checked']}, failures: {ver['cascade_failures']}",
        "",
        "## Graphs (means over replicates)",
        "",
        _md_table(g_rows, [("topology", "topology"), ("graphs", "graphs"), ("mean_m", "edges"), ("mean_degree", "<k>"), ("second_moment", "<k^2>"), ("max_degree_mean", "max k"), ("p_c", "p_c"), ("giant_fraction", "giant comp."), ("clustering", "clustering")], 3),
        "## Cells (mean over replicates of per-graph mean S; spread across replicates)",
        "",
        _md_table(c_rows, [("model", "model"), ("param", "p or phi"), ("seed_rule", "rule"), ("seed_count", "seeds"), ("topology", "topology"), ("replicates", "R"), ("mean_S", "mean S"), ("sd_S_between_replicates", "sd between R"), ("min_rep_S", "min"), ("max_rep_S", "max"), ("mean_depth", "depth"), ("mean_t50", "T50"), ("mean_gini", "Gini"), ("large_share", "P(S>=0.1)"), ("seconds_per_cascade", "s/cascade")], 4),
        "## Replicate-level spread of the primary-style contrast (descriptive, not inference)",
        "",
        "Sbar is the mean of per-graph mean S over the parameter values present in this run (IC, one random seed). "
        "`R needed` is the replicate count for a 95 percent half-width of 0.01 under a normal approximation; the Holm column uses the first Holm step over two contrasts (z = 2.24).",
        "",
        _md_table(k_rows, [("contrast", "contrast"), ("replicates", "R"), ("mean_diff", "mean diff"), ("sd_diff", "sd_diff"), ("min_diff", "min"), ("max_diff", "max"), ("half_width_at_R30_z95", "half-width at R=30"), ("R_needed_z95", "R needed"), ("R_needed_holm_first_step", "R needed (Holm)")], 4),
        "Per parameter value (same contrast, one p at a time; descriptive):",
        "",
        _md_table(kp_rows, [("param", "p"), ("contrast", "contrast"), ("replicates", "R"), ("mean_diff", "mean diff"), ("sd_diff", "sd_diff"), ("min_diff", "min"), ("max_diff", "max")], 4),
        "## Variance decomposition of S (shares of total variance)",
        "",
        _md_table(v_rows, [("model", "model"), ("param", "p or phi"), ("seed_rule", "rule"), ("seed_count", "seeds"), ("total_variance", "total var"), ("share_topology", "topology"), ("share_replicate", "replicate"), ("share_within_graph", "within graph")], 4),
        "## Degenerate cells",
        "",
        _md_table([{**d, "reasons": "; ".join(d["reasons"])} for d in d_rows], [("model", "model"), ("param", "p or phi"), ("seed_rule", "rule"), ("seed_count", "seeds"), ("topology", "topology"), ("reasons", "reasons")]),
    ]
    if project is not None:
        pr = analysis.project_runtime(doc, project)
        lines += [
            f"## Runtime projection for {project.experiment_id} (config hash `{project.hash[:12]}`)",
            "",
            f"- Projected: {pr['projected_seconds']:.1f} s ({pr['projected_seconds'] / 3600:.3f} h) on this machine, single process.",
            f"- Cells with an exact measured rate: {pr['cells_exact']}; nearest-parameter rate: {pr['cells_nearest_param']}; no rate: {pr['cells_missing']}.",
            f"- Scope: {pr['note']}.",
            "",
        ]
    if figs:
        lines += ["## Figures", ""]
        for stem, cap, alt in figs:
            lines += [f"![{alt}](figures/{stem}.png)", "", f"*{cap}*", ""]
    if doc["failures"]:
        lines += ["## Failures", ""] + [f"- {f['kind']}: {f}" for f in doc["failures"][:50]] + [""]
    report = run_dir / "report.md"
    report.write_text("\n".join(lines) + "\n")
    if pdf:
        build_pdf(report, pandoc=pandoc, typst_python=typst_python)
    return report


# Tables may break across pages, so a long table follows its caption instead of floating to
# the next page and leaving a blank half page; table cells are not justified, so narrow
# columns do not show wide word gaps (M6 visual inspection). pandoc runs with --wrap=none: a wrapped line that starts with
# "2." would otherwise be read by Typst as a numbered list item.
_TYPST_HEADER = ("#show figure.where(kind: table): set block(breakable: true)\n"
                 "#show table: set par(justify: false)\n"
                 "#show table: set text(size: 0.9em)")

# Drop a level-1 heading that repeats the metadata title (the title block already prints it).
# A document without a metadata title takes its first level-1 heading as the title, so the
# PDF title metadata is always set.
_DROP_TITLE_HEADING_LUA = """
function Pandoc(doc)
  local title = pandoc.utils.stringify(doc.meta.title or "")
  for i, b in ipairs(doc.blocks) do
    if b.t == "Header" and b.level == 1 then
      if title == "" then
        doc.meta.title = pandoc.MetaInlines(b.content)
        table.remove(doc.blocks, i)
      elseif pandoc.utils.stringify(b) == title then
        table.remove(doc.blocks, i)
      end
      break
    end
  end
  return doc
end
"""


def build_pdf(md: Path, pandoc: str | None = None, typst_python: str | None = None,
              root: Path | None = None) -> Path:
    """Compile md to PDF. root is the Typst project root (default: md's folder); pass the
    repository root when the Markdown references figures outside its own folder."""
    pandoc = pandoc or os.environ.get("VIRAL_PANDOC") or shutil.which("pandoc")
    typst_python = typst_python or os.environ.get("VIRAL_TYPST_PYTHON")
    if not pandoc:
        raise RuntimeError("pandoc not found; set VIRAL_PANDOC")
    if not typst_python:
        raise RuntimeError("no Python with the typst package; set VIRAL_TYPST_PYTHON")
    typ = md.with_suffix(".typ")
    out = md.with_suffix(".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        lua = Path(tmp) / "drop_title_heading.lua"
        lua.write_text(_DROP_TITLE_HEADING_LUA)
        subprocess.run([pandoc, md.name, "-s", "-t", "typst", "--wrap=none", "-V", 'mainfont=Libertinus Serif',
                        "-V", f"header-includes={_TYPST_HEADER}", "--lua-filter", str(lua),
                        "-o", typ.name], cwd=md.parent, check=True)
    root_arg = f", root={str(Path(root).resolve())!r}" if root is not None else ""
    subprocess.run([typst_python, "-c", f"import typst; typst.compile({typ.name!r}, output={out.name!r}{root_arg})"], cwd=md.parent, check=True)
    return out
