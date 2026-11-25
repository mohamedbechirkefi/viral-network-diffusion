# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Export the published results for the static demo page (M5).

Writes demo/public/data/results.json in the shared template schema (lab-demo-results 1.0.0).
Inputs are committed files only: the confirmatory analysis tables under results/confirmatory/,
the exploratory EXP-001 and M4 outputs under results/exploratory/, the frozen configs under
experiments/, the experiment registry, the claims register and the artifact manifest.
Nothing is recomputed; numbers are copied and formatted with the print rules of the manuscript:

- four decimals with an explicit sign (manuscript Tables 3 to 6, supplementary S2, S4.1, S4.2);
- the two EXP-002 rows WS - ER at p = 0.02 and 0.05 are printed in e-notation (manuscript Table 3);
- the M4 exploratory rows use the claims-register format (four decimals, or e-notation below 1e-4;
  manuscript Table 7 and supplementary S4.3).

The output is deterministic (no timestamps). `code_revision` is the last commit that touched any
source file. tests/test_demo_export.py re-runs the export in memory and compares it with the
committed file, and checks every display string against the manuscript or the supplementary.

Usage:  .venv/bin/python scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "demo" / "public" / "data" / "results.json"
CONF = REPO / "results" / "confirmatory"
RUN = {
    "EXP-002": CONF / "EXP-002" / "EXP-002-20261124T233447Z-2c7febb6",
    "EXP-003": CONF / "EXP-003" / "EXP-003-20261124T234212Z-a2d668ab",
    "S1": CONF / "EXP-004" / "S1" / "EXP-004-20261124T233447Z-de14a4b3",
    "S2": CONF / "EXP-004" / "S2" / "EXP-004-20261124T233637Z-916e8d29",
    "S3": CONF / "EXP-004" / "S3" / "EXP-004-20261124T233755Z-e1d24091",
    "S4-n500": CONF / "EXP-004" / "S4-n500" / "EXP-004-20261124T235044Z-e31dba07",
    "S4-n2000": CONF / "EXP-004" / "S4-n2000" / "EXP-004-20261124T235110Z-40385ec3",
    "EXP-005": CONF / "EXP-005" / "EXP-005-20261124T233932Z-d277f271",
}
EXP001 = REPO / "results" / "exploratory" / "EXP-001" / "EXP-001-20261124T233106Z-99c548ac"
M4 = REPO / "results" / "exploratory" / "M4"
REGISTRY = REPO / "research" / "experiment_registry.csv"
CLAIMS = REPO / "research" / "claims_register.csv"
MANIFEST = REPO / "research" / "publication" / "artifact_manifest.json"
SESOI = 0.02
# Rows that manuscript Table 3 prints in e-notation (also quoted in claim SYN-10).
E_NOTATION = {("EXP-002", "ws - er", 0.02), ("EXP-002", "ws - er", 0.05)}
NAMES = {"er": "ER", "ws": "WS", "ba": "BA"}


def f4(x: float) -> str:
    return f"{x:+.4f}"


def fclaim(x: float) -> str:
    """Claims-register format (scripts/build_records.py)."""
    return f"{x:+.4f}" if abs(x) >= 1e-4 or x == 0 else f"{x:+.2e}"


def fe(x: float) -> str:
    return f"{x:+.2e}"


def contrast_label(c: str) -> str:
    parts = [p.strip() for p in c.split(" - ")]
    return " - ".join(NAMES.get(p, p) for p in parts)


class Reader:
    """Reads committed files and records each one with its SHA-256."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def _note(self, p: Path) -> bytes:
        b = p.read_bytes()
        self.files[str(p.relative_to(REPO))] = hashlib.sha256(b).hexdigest()
        return b

    def csv(self, p: Path) -> list[dict]:
        text = self._note(p).decode()
        return list(csv.DictReader(text.splitlines()))

    def json(self, p: Path):
        return json.loads(self._note(p).decode())


def git_revision(paths: list[str]) -> str:
    out = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", *paths], capture_output=True, text=True, check=True)
    rev = out.stdout.strip()
    if not rev:
        raise SystemExit("no commit found for the source files (are they committed?)")
    return rev


def primary_estimates(rd: Reader, key: str, claim_prefix: str, pname: str, printed_in: str, analysis: str) -> list[dict]:
    exp = "EXP-004" if key.startswith("S") else key
    rows = rd.csv(RUN[key] / "primary_contrasts.csv")
    out = []
    for i, r in enumerate(rows, 1):
        mean, lo, hi, lvl = float(r["mean"]), float(r["lo"]), float(r["hi"]), float(r["interval_level"])
        param = r["param"]
        try:
            pval = float(param)
        except ValueError:
            pval = None
        fmt = fe if (exp, r["contrast"], pval) in E_NOTATION else f4
        reject = r["reject"] == "True"
        inside = r["equivalent_within_sesoi"] == "True"
        pdisp = param if pval is None else (f"{pval:g}" if key != "EXP-005" else param)
        out.append({
            "label": f"{analysis}: {contrast_label(r['contrast'])}, {pname} = {pdisp}" if pval is not None else f"{analysis}: {contrast_label(r['contrast'])}, {param}",
            "estimate": mean, "ci_low": lo, "ci_high": hi, "ci_level": lvl,
            "unit": "difference in final cascade fraction S",
            "display": fmt(mean), "interval_display": f"[{fmt(lo)}, {fmt(hi)}]",
            "level_display": f"{lvl:.4f}",
            "interval_kind": "Holm-step percentile interval",
            "kind": "confirmatory" + (" (optional analysis)" if key.startswith("S4") else ""),
            "analysis": analysis, "contrast": contrast_label(r["contrast"]), "param_name": pname, "param": pval if pval is not None else param,
            "rejected": reject, "inside_sesoi": inside,
            "claim_id": f"{claim_prefix}-R{i:02d}", "printed_in": printed_in,
        })
    return out


def secondary_phi(rd: Reader) -> list[dict]:
    rows = [r for r in rd.csv(RUN["EXP-003"] / "secondary_contrasts.csv") if r["seed_rule"] == "random" and r["seed_count"] == "10" and r["metric"] == "mean_S"]
    claims = {r["text"]: r["claim_id"] for r in rd.csv(CLAIMS) if r["claim_id"].startswith("EXP-003-SEC")}
    out = []
    for r in rows:
        mean, lo, hi = float(r["mean"]), float(r["lo"]), float(r["hi"])
        cid = next((c for t, c in claims.items() if f"{r['contrast']}, LT, seed rule random, seed count 10, phi = {r['param']}:" in t), None)
        if cid is None:
            raise SystemExit(f"no claim row for EXP-003 secondary {r['contrast']} phi {r['param']}")
        out.append({
            "label": f"per-phi secondary, unadjusted: {contrast_label(r['contrast'])}, phi = {r['param']}",
            "estimate": mean, "ci_low": lo, "ci_high": hi, "ci_level": float(r["level"]),
            "unit": "difference in final cascade fraction S", "display": f4(mean), "interval_display": f"[{f4(lo)}, {f4(hi)}]",
            "level_display": f"{float(r['level']):.4f}", "interval_kind": "unadjusted percentile interval",
            "kind": "secondary (unadjusted)", "analysis": "per-phi secondary, unadjusted", "contrast": contrast_label(r["contrast"]),
            "param_name": "phi", "param": float(r["param"]), "rejected": None, "inside_sesoi": None,
            "claim_id": cid, "printed_in": "manuscript",
        })
    return out


def m4_estimates(rd: Reader) -> list[dict]:
    out, counters = [], {}
    for c in rd.csv(M4 / "m4_exploratory_contrasts.csv"):
        counters[c["check"]] = counters.get(c["check"], 0) + 1
        par = "phi" if c["check"] == "X3" else "p"
        mean, lo, hi = float(c["mean_diff"]), float(c["lo95"]), float(c["hi95"])
        metric = c["metric"].split(" (")[0]
        out.append({
            "label": f"{c['check']}: {contrast_label(c['contrast'])}, {metric}, {par} = {c['p']}",
            "estimate": mean, "ci_low": lo, "ci_high": hi, "ci_level": 0.95,
            "unit": "difference in final cascade fraction S" if metric == "S" else "difference in giant-normalised S",
            "display": fclaim(mean), "interval_display": f"[{fclaim(lo)}, {fclaim(hi)}]", "level_display": "0.95",
            "interval_kind": "unadjusted 95 percent percentile interval", "kind": "exploratory (post hoc)",
            "analysis": c["check"], "contrast": contrast_label(c["contrast"]), "param_name": par, "param": float(c["p"]),
            "rejected": None, "inside_sesoi": None, "claim_id": f"M4-{c['check']}-{counters[c['check']]:02d}",
            "printed_in": "supplementary S4.3",
        })
    return out


def counts(est: list[dict]) -> tuple[int, int, int]:
    return sum(e["rejected"] for e in est), len(est), sum(not e["inside_sesoi"] for e in est)


def levels(rd: Reader, key: str, rule: tuple[str, str], printed_in: str) -> dict:
    rows = [t for t in rd.csv(RUN[key] / "topology_means.csv") if (t["seed_rule"], t["seed_count"]) == rule]
    model = rows[0]["model"]
    series: dict[str, list] = {}
    for t in rows:
        series.setdefault(t["topology"], []).append({
            "param": float(t["param"]), "param_display": t["param"], "mean": float(t["mean_S"]), "lo": float(t["lo95"]), "hi": float(t["hi95"]),
            "display": f"{float(t['mean_S']):.4f}", "interval_display": f"[{float(t['lo95']):.4f}, {float(t['hi95']):.4f}]",
            "replicates": int(t["replicates"]),
        })
    for v in series.values():
        v.sort(key=lambda d: d["param"])
    return {"model": model, "param_name": "phi" if model == "lt" else "p", "seed_rule": rule[0], "seed_count": int(rule[1]),
            "interval": "unadjusted 95 percent percentile bootstrap interval over replicates", "printed_in": printed_in,
            "series": [{"topology": k, "label": NAMES.get(k, k), "points": series[k]} for k in sorted(series, key=lambda k: ("er", "ws", "ba", "real", "real_er", "real_dpr").index(k))]}


def build() -> dict:
    rd = Reader()
    registry = {r["exp_id"]: r for r in rd.csv(REGISTRY)}
    claim_ids = [r["claim_id"] for r in rd.csv(CLAIMS)]
    manifest = rd.json(MANIFEST)
    manifest_paths = {a["path"] for a in manifest["artifacts"]}

    cfg2 = rd.json(REPO / "experiments" / "EXP-002" / "config.json")
    cfg3 = rd.json(REPO / "experiments" / "EXP-003" / "config.json")
    cfg5 = rd.json(REPO / "experiments" / "EXP-005" / "config.json")
    a2 = rd.json(RUN["EXP-002"] / "analysis.json")
    a3 = rd.json(RUN["EXP-003"] / "analysis.json")
    a5 = rd.json(RUN["EXP-005"] / "analysis.json")
    for k in ("S1", "S2", "S3", "S4-n500", "S4-n2000"):
        rd.json(RUN[k] / "analysis.json")
    smoke = rd.json(EXP001 / "result.json")["verification"]
    mval = rd.json(EXP001 / "metric_validation.json")
    m4meta = rd.json(M4 / "m4_exploratory.json")

    e2 = primary_estimates(rd, "EXP-002", "EXP-002", "p", "manuscript", "primary")
    e3 = primary_estimates(rd, "EXP-003", "EXP-003", "phi", "manuscript", "primary grid mean") + secondary_phi(rd)
    s1 = primary_estimates(rd, "S1", "EXP-004-S1", "c", "manuscript", "S1")
    s2 = primary_estimates(rd, "S2", "EXP-004-S2", "p", "manuscript", "S2")
    s3 = primary_estimates(rd, "S3", "EXP-004-S3", "p", "supplementary S4.1", "S3")
    s4a = primary_estimates(rd, "S4-n500", "EXP-004-S4-n500", "p", "supplementary S4.2", "S4, N = 500")
    s4b = primary_estimates(rd, "S4-n2000", "EXP-004-S4-n2000", "p", "supplementary S4.2", "S4, N = 2000")
    e5 = primary_estimates(rd, "EXP-005", "EXP-005", "p", "manuscript", "primary")
    m4 = m4_estimates(rd)

    r2, n2, o2 = counts(e2)
    ba = [e for e in e2 if e["contrast"] == "BA - ER"]
    ws = [e for e in e2 if e["contrast"] == "WS - ER"]
    rb, nb, ob = counts(ba)
    rw, nw, ow = counts(ws)
    ws_null = [e for e in ws if not e["rejected"]]
    r3, n3, o3 = counts([e for e in e3 if e["kind"] == "confirmatory"])
    r5, n5, o5 = counts(e5)
    nonrej5_inside = all(e["inside_sesoi"] for e in e5 if not e["rejected"])
    c = {k: counts(v) for k, v in {"S1": s1, "S2": s2, "S3": s3, "S4a": s4a, "S4b": s4b}.items()}

    def reg(exp: str) -> str:
        return registry[exp]["report_path"]

    experiments = [
        {
            "id": "EXP-001", "title": registry["EXP-001"]["title"], "status": "exploratory, complete",
            "verdict": f"pass (exploratory gate): {smoke['cascade_failures']} failures over {smoke['cascades_checked']:,} checked cascades; {mval['n_checks'] - mval['n_failed']} of {mval['n_checks']} metric checks",
            "estimates": [], "claim_ids": [], "report_path": reg("EXP-001"),
            "notes": ["Engine verification only; no effect estimate is reported and nothing here is a finding.",
                      "No claim-register row: the verification counts are reported in manuscript Table 8 and in the EXP-001 report."],
        },
        {
            "id": "EXP-002", "title": registry["EXP-002"]["title"], "status": "confirmatory, complete",
            "verdict": (f"Holm rejects {r2} of {n2}; {o2} of {n2} intervals lie outside the SESOI. BA - ER: H1 supported at {rb} of {nb} p, {ob} of {nb} outside the SESOI. "
                        f"WS - ER: H1 supported at {rw} of {nw} p ({ow} outside the SESOI); not supported at {ws_null[0]['param']:.2f}, equivalence within {SESOI} there."),
            "estimates": e2, "claim_ids": [e["claim_id"] for e in e2], "report_path": reg("EXP-002"),
            "notes": ["A rejection inside the SESOI is detectable but negligible: six of the thirteen rejections are of this kind.",
                      f"R = {a2['primary'][0]['n_replicates']} matched graph sets; {a2['cascades']:,} cascades; {a2['failures']} failed runs."],
        },
        {
            "id": "EXP-003", "title": registry["EXP-003"]["title"], "status": "confirmatory, complete",
            "verdict": f"H1 supported for both contrasts ({r3} of {n3} Holm rejections); both outside the SESOI.",
            "estimates": e3, "claim_ids": [e["claim_id"] for e in e3], "report_path": reg("EXP-003"),
            "notes": ["The primary estimand is the grid mean over phi; the per-phi rows are secondary and unadjusted.",
                      f"R = {a3['primary'][0]['n_replicates']} matched sets, ten random seeds; {a3['cascades']:,} cascades."],
        },
        {
            "id": "EXP-004", "title": registry["EXP-004"]["title"], "status": "confirmatory, complete (S4 optional, run)",
            "verdict": (f"S1: reported per multiplier, no overall verdict (owner decision D-013); {c['S1'][0]} of {c['S1'][1]} rejected. "
                        f"S2: {c['S2'][0]} of {c['S2'][1]} rejected; the BA advantage near threshold is a degree-sequence effect. "
                        f"S3: {c['S3'][0]} of {c['S3'][1]} rejected; the edge-count mismatch does not explain the pattern. "
                        f"S4 (optional): {c['S4a'][0]} of {c['S4a'][1]} at N = 500 and {c['S4b'][0]} of {c['S4b'][1]} at N = 2000; size in this range does not explain it."),
            "estimates": s1 + s2 + s3 + s4a + s4b, "claim_ids": [e["claim_id"] for e in s1 + s2 + s3 + s4a + s4b], "report_path": reg("EXP-004"),
            "notes": ["S1 has no single overall verdict: each multiplier c is reported on its own, and no multiplier was picked after the data (owner, 2026-11-25, D-013).",
                      "S2 and S3 reuse EXP-002 replicates 0 to 29 and their cascade streams, so their agreement with EXP-002 is partly built in.",
                      "S3 and S4 rows are printed in supplementary Tables S4.1 and S4.2."],
        },
        {
            "id": "EXP-005", "title": registry["EXP-005"]["title"], "status": "confirmatory, complete",
            "verdict": f"H1 supported for {r5} of {n5}; the {n5 - r5} non-rejections lie inside the SESOI." if nonrej5_inside else f"H1 supported for {r5} of {n5}.",
            "estimates": e5, "claim_ids": [e["claim_id"] for e in e5], "report_path": reg("EXP-005"),
            "notes": ["Conditional on one anonymized 362-node friendship network; its real arm is the same graph in every replicate, so it is not a sample of networks.",
                      f"R = {a5['primary'][0]['n_replicates']} matched sets; {a5['cascades']:,} cascades."],
        },
        {
            "id": "M4", "title": "Exploratory confounder checks X1 to X3 (post hoc, not a registered experiment)", "status": "exploratory, post hoc",
            "verdict": "No verdict: exploratory checks designed after the confirmatory results were seen; they never replace a frozen verdict.",
            "estimates": m4, "claim_ids": [e["claim_id"] for e in m4], "report_path": "research/paper/manuscript.md section 5.5; results/exploratory/M4/",
            "notes": [f"Fresh master seeds {min(m4meta['master_seeds'].values())} to {max(m4meta['master_seeds'].values())}, 30 matched replicates, unadjusted 95 percent intervals.",
                      "All rows are printed in supplementary Table S4.3; manuscript Table 7 quotes a selection."],
        },
    ]
    for e in experiments:
        missing = [cid for cid in e["claim_ids"] if cid not in claim_ids]
        if missing:
            raise SystemExit(f"{e['id']}: claim ids not in the claims register: {missing[:3]}")
    for key in RUN:
        p = str((RUN[key] / "primary_contrasts.csv").relative_to(REPO))
        if p not in manifest_paths:
            raise SystemExit(f"{p} is not in the artifact manifest")

    graphs = [{"topology": t["topology"], "label": NAMES[t["topology"]], "edges": f"{float(t['mean_m']):.1f}", "second_moment": f"{float(t['second_moment']):.2f}",
               "p_c": f"{float(t['p_c']):.4f}", "clustering": f"{float(t['clustering']):.4f}", "giant_fraction": f"{float(t['giant_fraction']):.4f}"}
              for t in rd.csv(RUN["EXP-002"] / "tables" / "graphs.csv")]
    graphs.sort(key=lambda g: ("er", "ws", "ba").index(g["topology"]))

    assumptions = [
        {"name": "Graph size and density", "value": f"N = {cfg2['n']} nodes, target mean degree {cfg2['mean_degree']} (ER G(n, M) with M = 3000; WS k = 6, beta = {cfg2['ws_beta']}; BA m = 3, 2991 edges)", "source": "experiments/EXP-002/config.json; manuscript section 3"},
        {"name": "Content quality", "value": "Not modelled: held fixed by one shared transmission probability p (IC) or threshold phi (LT)", "source": "manuscript section 1"},
        {"name": "IC transmission grid", "value": "p in {" + ", ".join(f"{x:.2f}" for x in cfg2["models"]["ic"]["p"]) + "}", "source": "experiments/EXP-002/config.json"},
        {"name": "LT threshold grid", "value": "phi in {" + ", ".join(f"{x:.2f}" for x in cfg3["models"]["lt"]["phi"]) + "}", "source": "experiments/EXP-003/config.json"},
        {"name": "EXP-005 calibrated grid", "value": "p in {" + ", ".join(f"{x}" for x in cfg5["models"]["ic"]["p"]) + "}", "source": "experiments/EXP-005/config.json"},
        {"name": "Replicates and cascades", "value": f"R = {cfg2['replicates']} matched graph sets (EXP-002, EXP-005), R = {cfg3['replicates']} (EXP-003, EXP-004); C = {cfg2['cascades']} cascades per graph and cell", "source": "frozen configs"},
        {"name": "Independent unit", "value": "the matched graph set, not the cascade; paired cluster bootstrap with B = 10000", "source": "manuscript section 4.5"},
        {"name": "Error control", "value": "Holm step-down at familywise level 0.05 within each confirmatory family; secondary and exploratory intervals unadjusted", "source": "manuscript section 4.5"},
        {"name": "Smallest effect size of interest", "value": f"plus or minus {SESOI} in final cascade fraction (absolute); a design choice", "source": "manuscript section 4.4"},
        {"name": "Threshold estimate", "value": "p_c = <k> / (<k^2> - <k>), locally tree-like; ignores clustering", "source": "manuscript section 3"},
    ]
    limitations = [
        "All results are simulations of stylised models. They say nothing about real social platforms, their ranking algorithms or guaranteed virality.",
        "Content quality is not modelled; synthetic agents are not people.",
        "One parameterisation per family (one mean degree, one WS beta, one BA m) and N = 1000, with S4 at 500 and 2000 only.",
        "Pilot values at 10 replicates were seen before the freeze and informed the per-p analysis, R and the EXP-003 grid (freeze record C4).",
        "With high power, Holm rejects differences of order 1e-05; practical importance is judged only by the absolute SESOI, a design choice.",
        "Holm controls error within each of the 8 confirmatory families (89 tests); there is no study-wide correction.",
        "S1 has no overall verdict (owner decision D-013), so the degree-heterogeneity reading of the EXP-002 effects as a whole is neither confirmed nor refuted.",
        "EXP-005 rests on one small, pseudonymous friendship network; it is not a sample of networks.",
        "The M4 checks X1 to X3 are post hoc and exploratory, with 30 replicates and unadjusted intervals.",
        "The literature review is not systematic; several sources were read at metadata or abstract level only.",
        "The manuscript (version 0.2) is not peer-reviewed; the owner's full-text review is pending (M6).",
    ]

    sources = [{"path": p, "sha256": h} for p, h in sorted(rd.files.items())]
    return {
        "schema": "lab-demo-results", "schema_version": "1.0.0", "project": "VIRAL",
        "question": "How do network topology and initial exposure influence diffusion independently of content quality?",
        "status_label": "Simulation study. Confirmatory results under protocol v1.0, frozen 2026-11-24 with the owner's approval. Manuscript version 0.2, a preprint draft that is not peer-reviewed.",
        "code_revision": git_revision([s["path"] for s in sources]),
        "sources": sources, "experiments": experiments, "assumptions": assumptions, "limitations": limitations,
        "sesoi": SESOI,
        "levels": {
            "EXP-002": levels(rd, "EXP-002", ("random", "1"), "manuscript Figure 2; supplementary S2.1"),
            "EXP-003": levels(rd, "EXP-003", ("random", "10"), "manuscript Figure 4"),
            "EXP-005": levels(rd, "EXP-005", ("random", "1"), "manuscript Figure 5; supplementary S2.3"),
        },
        "graph_stats": {"experiment": "EXP-002", "printed_in": "manuscript Table 2", "rows": graphs},
    }


def render(doc: dict) -> str:
    return json.dumps(doc, indent=1, sort_keys=False, ensure_ascii=True) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text() == text
        print("results.json up to date" if same else "results.json differs from a fresh export")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
