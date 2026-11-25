# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Evidence audit (master prompt section 11.5; M4). Read-only on results; writes audit records only.

Part A, raw outputs. For every confirmatory analysis under results/confirmatory/:
  - the git-ignored raw result.json is present and its SHA-256 equals the committed value;
  - the result validates against its schema (viral.results.load_result);
  - denominators and sample counts: every cell has the configured number of cascades, the cell count
    equals topologies x replicates x settings, every per-cascade size is an integer in [1, N], and
    the cell mean_S equals mean(size) / N;
  - the frozen analysis (viral.confirmatory.run_plan with the recorded plan) is recomputed from the raw
    result and compared with analysis.json, primary_contrasts.csv, secondary_contrasts.csv and
    topology_means.csv (means, interval bounds, levels, p-values, decisions, replicate counts).

Part B, numbers in documents. Every number printed in the manuscript, the supplementary file and the
experiment reports is traced to a committed result file at its printed precision, and the trace is
written to research/publication/number_trace.csv and to the "numbers" block of
research/publication/artifact_manifest.json (experiment id, run id, metric field, result path,
generator, config hash, code revision). Numbers that are not results (design constants, counts of
tests, section numbers) are classified by rule and listed; unmatched decimals are listed for review.

Usage:  .venv/bin/python scripts/audit_evidence.py [--skip-raw]
Exit status 1 if any raw check fails or any decimal number in the audited documents is untraced.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
CONF = REPO / "results" / "confirmatory"
EXPL = REPO / "results" / "exploratory"
PUB = REPO / "research" / "publication"
DOCS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    *[f"research/experiments/EXP-00{i}/report.md" for i in range(1, 6)],
]
GEN_TABLES = {"primary_contrasts.csv": "scripts/analyse_confirmatory.py", "secondary_contrasts.csv": "scripts/analyse_confirmatory.py",
              "topology_means.csv": "scripts/analyse_confirmatory.py"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b, tol=1e-12) -> bool:
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=tol)


# ---------------------------------------------------------------- Part A
def audit_raw() -> list[dict]:
    from viral.confirmatory import run_plan
    from viral.results import load_result

    out = []
    for apath in sorted(CONF.rglob("analysis.json")):
        a = json.loads(apath.read_text())
        rd = apath.parent
        rec = {"analysis": str(apath.relative_to(REPO)), "run_id": a["run_id"], "checks": [], "failures": []}

        def chk(name, ok, detail=""):
            rec["checks"].append(name)
            if not ok:
                rec["failures"].append(f"{name}: {detail}")

        raw_line = (rd / "result.json.sha256").read_text().split()
        raw = REPO / raw_line[1]
        chk("raw result present", raw.exists(), str(raw))
        if not raw.exists():
            out.append(rec)
            continue
        chk("raw SHA-256 equals committed value", sha(raw) == raw_line[0] == a["result_json_sha256"], raw_line[0])
        doc = load_result(raw)
        cfg = doc["config"]
        n, cas = cfg["n"], cfg["cascades"]
        cells = doc["cells"]
        n_settings = sum(len(v.get("p", v.get("phi", []))) for v in cfg["models"].values()) * len(cfg["seed_rules"]) * len(cfg["seed_counts"])
        chk("cell count = topologies x replicates x settings", len(cells) == len(cfg["topologies"]) * cfg["replicates"] * n_settings == a["cells"],
            f"{len(cells)} vs {a['cells']}")
        chk("cascade count", sum(c["n_cascades"] for c in cells) == a["cascades"], str(a["cascades"]))
        bad_n = [c for c in cells if c["n_cascades"] != cas or len(c["per_cascade"]["size"]) != cas]
        chk("every cell has the configured cascades", not bad_n, f"{len(bad_n)} cells")
        bad_s = 0
        bad_mean = 0
        for c in cells:
            s = np.asarray(c["per_cascade"]["size"])
            if s.min() < 1 or s.max() > n or not np.all(s == np.round(s)):
                bad_s += 1
            if not math.isclose(float((s / n).mean()), c["summary"]["mean_S"], rel_tol=1e-12, abs_tol=1e-15):
                bad_mean += 1
        chk("per-cascade sizes are integers in [1, N]", bad_s == 0, f"{bad_s} cells")
        chk("mean_S = mean(size) / N in every cell", bad_mean == 0, f"{bad_mean} cells")
        chk("graph count", len(doc["graphs"]) == a["graphs"], str(a["graphs"]))
        re_out = run_plan(doc, a["plan"])
        prim = {(r["contrast"], str(r["param"])): r for r in re_out["primary"]}
        for r in a["primary"]:
            q = prim.get((r["contrast"], str(r["param"])))
            ok = q is not None and all(close(r[k], q[k]) for k in ("mean", "lo", "hi", "interval_level", "p_boot", "p_holm", "reject", "n_replicates", "equivalent_within_sesoi"))
            chk(f"primary {r['contrast']} {r['param']} recomputed", ok)
        with open(rd / "primary_contrasts.csv") as fh:
            rows = list(csv.DictReader(fh))
        chk("primary_contrasts.csv rows = analysis.json primary", len(rows) == len(a["primary"]) and all(
            close(float(x["mean"]), y["mean"]) and close(float(x["lo"]), y["lo"]) and close(float(x["hi"]), y["hi"]) for x, y in zip(rows, a["primary"])))
        with open(rd / "secondary_contrasts.csv") as fh:
            srows = list(csv.DictReader(fh))
        chk("secondary_contrasts.csv recomputed", len(srows) == len(re_out["secondary"]) and all(
            close(float(x["mean"]), y["mean"]) and close(float(x["lo"]), y["lo"]) and close(float(x["hi"]), y["hi"]) and int(x["n_replicates"]) == y["n_replicates"]
            for x, y in zip(srows, re_out["secondary"])))
        with open(rd / "topology_means.csv") as fh:
            trows = list(csv.DictReader(fh))
        chk("topology_means.csv recomputed", len(trows) == len(re_out["topology_means"]) and all(
            close(float(x["mean_S"]), y["mean_S"]) and close(float(x["lo95"]), y["lo95"]) and close(float(x["hi95"]), y["hi95"]) and int(x["replicates"]) == y["replicates"]
            for x, y in zip(trows, re_out["topology_means"])))
        out.append(rec)
    return out


# ---------------------------------------------------------------- Part B
NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?(?:e[-+]?\d+)?(?![\w])")
STRIP = [
    re.compile(r"EXP-\d{3}(?:-\d{8}T\d{6}Z-[0-9a-f]{8})?(?:-(?:S\d(?:-n\d+)?-)?[RFXT]\d{2})?"),  # run, claim, figure ids
    re.compile(r"\b(?:S\d(?:-n\d+)?-)?R\d{2}\b"),
    re.compile(r"\b[0-9a-f]{7,64}\b"),  # hashes
    re.compile(r"\d{4}-\d{2}-\d{2}(?:T[\d:]+Z?)?"),  # dates
    re.compile(r"\b\d{2}:\d{2}(?::\d{2})?Z?\b"),  # times
    re.compile(r"\b(?:D|DEC|M|C|R|H|A|L|S|X|F|T|B)-?\d+(?:\.\d+)?\b"),  # decision, milestone, item ids
    re.compile(r"\b\d+\.\d+\.\d+\b"),  # versions
    re.compile(r"(?:section|sections|protocol|item|items|chapter|step|steps|limitation|limitations|Table|Figure|amendment|11\.)\s*\d+(?:\.\d+)?(?:\s*(?:to|and|,)\s*\d+(?:\.\d+)?)*", re.I),
    re.compile(r"^#+\s*\d+(?:\.\d+)*\.?", re.M),  # heading numbers
    re.compile(r"spawn_key=\([^)]*\)"),
    re.compile(r"`[^`]*/[^`]*`"),  # paths in code spans
    re.compile(r"\[\^?\d+\]"),
    re.compile(r"https?://\S+"),
    re.compile(r"doi:\S+|10\.\d{4,}/\S+"),
]


def fmt_keys(v: float) -> set[str]:
    keys = set()
    if not math.isfinite(v):
        return keys
    for x in (v, -v):
        for d in range(0, 7):
            keys.add(f"{x:.{d}f}")
        for d in range(0, 4):
            keys.add(f"{x:.{d}e}")
    return keys


def norm_token(t: str) -> str:
    t = t.replace(",", "")
    if t.startswith("+"):
        t = t[1:]
    if t in ("-0", "-0.0", "-0.00", "-0.000", "-0.0000"):
        t = t[1:]
    if "e" in t:
        mant = t.split("e")[0]
        d = len(mant.split(".")[1]) if "." in mant else 0
        t = f"{float(t):.{d}e}"
    return t


def run_meta(rd: Path) -> dict:
    a = rd / "analysis.json"
    if a.exists():
        j = json.loads(a.read_text())
        return {"experiment_id": j["experiment"], "run_id": j["run_id"], "config_hash": j["config_hash"], "code_revision": j["git_revision"],
                "result_path": f"results/raw/confirmatory/{j['experiment'].split()[0]}/{j['run_id']}/result.json (git-ignored; SHA-256 {j['result_json_sha256'][:12]})"}
    m = rd / "run_manifest.json"
    if m.exists():
        j = json.loads(m.read_text())
        return {"experiment_id": j["experiment_id"], "run_id": j["run_id"], "config_hash": j["config_hash"], "code_revision": j["git_revision"],
                "result_path": str((rd / "result.json").relative_to(REPO)) if (rd / "result.json").exists() else "see result.json.sha256 / RAW_RESULT.md"}
    return {}


def build_index() -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = defaultdict(list)

    def add(v, src: dict):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return
        for k in fmt_keys(v):
            idx[k].append(src)

    def add_csv(path: Path, meta: dict, gen: str):
        with open(path) as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                rk = ";".join(f"{k}={row[k]}" for k in ("contrast", "topology", "param", "seed_rule", "seed_count", "metric", "check") if k in row and row[k] != "")
                for k, v in row.items():
                    if k in ("n_boot",):
                        continue
                    add(v, {**meta, "path": str(path.relative_to(REPO)), "field": f"row {i + 2} ({rk}) column {k}", "generator": gen})

    def add_json(path: Path, meta: dict, gen: str, prefix=""):
        def walk(o, pre):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, f"{pre}.{k}" if pre else k)
            elif isinstance(o, list) and len(o) < 400:
                for i, v in enumerate(o):
                    walk(v, f"{pre}[{i}]")
            elif isinstance(o, (int, float)) and not isinstance(o, bool):
                add(o, {**meta, "path": str(path.relative_to(REPO)), "field": pre, "generator": gen})
        walk(json.loads(path.read_text()), prefix)

    for rd in sorted({p.parent for p in CONF.rglob("analysis.json")}):
        meta = run_meta(rd)
        for f in ("primary_contrasts.csv", "secondary_contrasts.csv", "topology_means.csv"):
            add_csv(rd / f, meta, GEN_TABLES[f])
        for f in ("graphs.csv", "variance.csv", "degenerate.csv"):
            if (rd / "tables" / f).exists() and (rd / "tables" / f).stat().st_size:
                add_csv(rd / "tables" / f, meta, "viral report (src/viral/report.py)")
        add_json(rd / "analysis.json", meta, "scripts/analyse_confirmatory.py")
        add_json(rd / "run_manifest.json", meta, "viral run (src/viral/results.py)")
    for s1 in CONF.rglob("s1_reading.json"):
        add_json(s1, run_meta(s1.parent), "scripts/analyse_confirmatory.py --s1-reading")
    for rd in sorted((EXPL / "EXP-001").iterdir()):
        if not rd.is_dir():
            continue
        meta = {**run_meta(rd), "experiment_id": "EXP-001 (exploratory)"}
        for f in sorted((rd / "tables").glob("*.csv")) if (rd / "tables").exists() else []:
            if f.name != "cells.csv" and f.stat().st_size:
                add_csv(f, meta, "viral report (src/viral/report.py)")
        for f in ("run_manifest.json", "metric_validation.json"):
            if (rd / f).exists():
                add_json(rd / f, meta, "viral smoke / scripts/validate_metrics.py")
    m4 = EXPL / "M4"
    if m4.exists():
        j = json.loads((m4 / "m4_exploratory.json").read_text())
        meta = {"experiment_id": "M4 exploratory checks X1 to X3", "run_id": "M4-exploratory (master seeds 20261201 to 20261203)", "config_hash": "script constants (R = 30, C = 200, B = 10000)",
                "code_revision": j["code_revision"], "result_path": "results/exploratory/M4/m4_exploratory.json"}
        add_csv(m4 / "m4_exploratory_contrasts.csv", meta, "scripts/exploratory_m4.py")
        add_json(m4 / "m4_exploratory.json", meta, "scripts/exploratory_m4.py")
    constants = {"experiment_id": "design", "run_id": "", "code_revision": "", "result_path": ""}
    for cfg in sorted((REPO / "experiments").rglob("*.json")):
        add_json(cfg, {**constants, "config_hash": f"config file SHA-256 {sha(cfg)[:12]}"}, "frozen config")
    # Protocol constants and values derived from several sources (each derivation is stated here).
    add(1e-4, {**constants, "config_hash": "", "experiment_id": "design", "path": "research/protocol.md", "field": "section 11.3: p-value resolution 1/B with B = 10000", "generator": "protocol constant"})
    rt = [json.loads(p.read_text())["runtime_seconds"] for p in sorted((CONF / "EXP-004").rglob("run_manifest.json"))]
    add(sum(rt), {**constants, "config_hash": "", "experiment_id": "EXP-004", "path": "results/confirmatory/EXP-004/*/*/run_manifest.json",
                  "field": f"derived: sum of runtime_seconds over the {len(rt)} EXP-004 runs", "generator": "derived in scripts/audit_evidence.py"})
    add_json(REPO / "data" / "real_network_calibration.json", {**constants, "config_hash": "", "experiment_id": "EXP-005 calibration (exploratory fit)"}, "scripts/fit_calibration.py")
    return idx


CONTEXT = re.compile(r"EXP-00\d|\bX[123]\b|\bS[1-4]\b")


def pick(srcs: list[dict], ctx: list[str], line_ctx: list[str] | None = None) -> dict:
    line_ctx = line_ctx or []

    def score(s):
        e = s.get("experiment_id", "")
        sc = 0
        for c in ctx:
            if c.startswith("EXP") and e.startswith(c):
                sc += 4
            if c.startswith("S") and c in e:
                sc += 2
            if c.startswith("X") and e.startswith("M4"):
                sc += 3
        if any(c.startswith("X") for c in line_ctx) and e.startswith("M4"):
            sc += 3
        if s["path"].endswith(("primary_contrasts.csv", "topology_means.csv", "secondary_contrasts.csv")):
            sc += 1
        return -sc
    return sorted(srcs, key=score)[0]


def classify_integer(tok: str, line: str) -> str:
    v = tok.replace(",", "").lstrip("+-")
    if re.search(r"\b(tests?|passed|checks?)\b", line[line.find(tok):line.find(tok) + 40]) or re.search(r"\b\d+ (passed|tests)\b", line):
        return "test or check count (progress.md, recorded command output)"
    return "integer constant or count"


def audit_numbers(idx) -> tuple[list[dict], list[dict]]:
    trace, unmatched = [], []
    for d in DOCS:
        p = REPO / d
        if not p.exists():
            continue
        ctx_head: list[str] = []
        default_ctx = re.findall(r"EXP-00\d", d)
        for ln, line in enumerate(p.read_text().splitlines(), 1):
            if line.startswith("#"):
                ctx_head = CONTEXT.findall(line)
            if line.startswith("<!--") or line.startswith("@") or "SPDX" in line:
                continue
            clean = line
            for rx in STRIP:
                clean = rx.sub(" ", clean)
            ctx = CONTEXT.findall(line) + ctx_head + default_ctx
            for m in NUM.finditer(clean):
                tok = m.group(0)
                key = norm_token(tok)
                is_dec = "." in key or "e" in key
                srcs = idx.get(key, [])
                if not is_dec:
                    srcs = [s for s in srcs]
                if srcs:
                    s = pick(srcs, ctx, CONTEXT.findall(line))
                    digits = len(re.sub(r"[^0-9]", "", key.split("e")[0]).lstrip("0"))
                    weak = is_dec and (digits <= 2 or len(srcs) >= 5)
                    alts = "; ".join(sorted({f"{x['path']} [{x['field'][:60]}]" for x in srcs if x is not s})[:3])
                    trace.append({"document": d, "line": ln, "token": tok, "kind": "decimal" if is_dec else "integer",
                                  "status": "traced (weak: low precision or many candidate sources; read with the line context)" if weak else "traced",
                                  "n_candidate_sources": len(srcs), **{k: s.get(k, "") for k in ("experiment_id", "run_id", "path", "field", "generator", "config_hash", "code_revision", "result_path")},
                                  "other_candidates": alts})
                else:
                    status = "UNTRACED decimal" if is_dec else classify_integer(tok, line)
                    row = {"document": d, "line": ln, "token": tok, "kind": "decimal" if is_dec else "integer", "status": status, "n_candidate_sources": 0,
                           "experiment_id": "", "run_id": "", "path": "", "field": "", "generator": "", "config_hash": "", "code_revision": "", "result_path": "", "other_candidates": ""}
                    trace.append(row)
                    if is_dec:
                        unmatched.append({**row, "context": line.strip()[:160]})
    return trace, unmatched


def audit_copies() -> list[str]:
    """Part C: committed result files match MANIFEST.sha256; experiment-folder copies equal their results/ originals (no stale figure or table)."""
    fails = []
    n = 0
    for line in (CONF / "MANIFEST.sha256").read_text().splitlines():
        h, rel = line.split(maxsplit=1)
        n += 1
        if sha(CONF / rel) != h:
            fails.append(f"MANIFEST mismatch: {rel}")
    pairs = []
    for e in ("EXP-002", "EXP-003", "EXP-005"):
        rd = next((CONF / e).iterdir())
        pairs += [(REPO / f"research/experiments/{e}/metrics.csv", rd / "primary_contrasts.csv"), (REPO / f"research/experiments/{e}/config.json", REPO / f"experiments/{e}/config.json"),
                  (REPO / f"research/experiments/{e}/run_manifest.json", rd / "run_manifest.json")]
        pairs += [(REPO / f"research/experiments/{e}/figures/{f.name}", f) for f in (rd / "figures").iterdir()]
    for s_ in ("S1", "S2", "S3", "S4-n500", "S4-n2000"):
        rd = next((CONF / "EXP-004" / s_).iterdir())
        pairs += [(REPO / f"research/experiments/EXP-004/{s_}-metrics.csv", rd / "primary_contrasts.csv"), (REPO / f"research/experiments/EXP-004/{s_}-config.json", REPO / f"experiments/EXP-004/{s_}-config.json"),
                  (REPO / f"research/experiments/EXP-004/{s_}-run_manifest.json", rd / "run_manifest.json")]
        pairs += [(REPO / f"research/experiments/EXP-004/figures/{s_}-{f.name}", f) for f in (rd / "figures").iterdir()]
    for a, b in pairs:
        if not a.exists() or sha(a) != sha(b):
            fails.append(f"copy differs or missing: {a.relative_to(REPO)} vs {b.relative_to(REPO)}")
    print(f"COPIES {n} manifest entries and {len(pairs)} experiment-folder copies checked, {len(fails)} failures")
    return fails


TRIPLE = re.compile(r"([-+]?\d+\.\d+(?:e[-+]?\d+)?)\s*\|?\s*\[\s*([-+]?\d+\.\d+(?:e[-+]?\d+)?)\s*,\s*([-+]?\d+\.\d+(?:e[-+]?\d+)?)\s*\]")


def triple_rows() -> list[tuple[float, float, float, str]]:
    """(mean, lo, hi, source) for every contrast row of every committed contrast table."""
    out = []
    for f in list(CONF.rglob("primary_contrasts.csv")) + list(CONF.rglob("secondary_contrasts.csv")) + [EXPL / "M4" / "m4_exploratory_contrasts.csv"]:
        with open(f) as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                m = r.get("mean", r.get("mean_diff"))
                lo, hi = r.get("lo", r.get("lo95")), r.get("hi", r.get("hi95"))
                out.append((float(m), float(lo), float(hi), f"{f.relative_to(REPO)} row {i + 2}"))
    for f in CONF.rglob("topology_means.csv"):
        with open(f) as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                out.append((float(r["mean_S"]), float(r["lo95"]), float(r["hi95"]), f"{f.relative_to(REPO)} row {i + 2}"))
    return out


def audit_triples() -> tuple[int, list[str]]:
    """Every printed 'estimate [lo, hi]' must match one committed row jointly (all three numbers from the same row)."""
    rows = triple_rows()
    ok, bad = 0, []
    for d in DOCS:
        p = REPO / d
        if not p.exists():
            continue
        for ln, line in enumerate(p.read_text().splitlines(), 1):
            for m in TRIPLE.finditer(line):
                toks = [norm_token(t) for t in m.groups()]
                hit = None
                for v, lo, hi, src in rows:
                    if all(t in fmt_keys(x) for t, x in zip(toks, (v, lo, hi))):
                        hit = src
                        break
                if hit:
                    ok += 1
                else:
                    bad.append(f"{d}:{ln} {m.group(0)}")
    return ok, bad


def main(argv: list[str]) -> int:
    t_ok, t_bad = audit_triples()
    print(f"TRIPLES {t_ok} estimate-interval triples matched jointly to one committed row; {len(t_bad)} unmatched")
    for b in t_bad:
        print("   UNMATCHED TRIPLE", b)
    copy_fails = audit_copies()
    for f in copy_fails:
        print("   FAIL", f)
    raw = [] if "--skip-raw" in argv else audit_raw()
    idx = build_index()
    trace, unmatched = audit_numbers(idx)
    with open(PUB / "number_trace.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trace[0]))
        w.writeheader()
        w.writerows(trace)
    man_path = PUB / "artifact_manifest.json"
    man = json.loads(man_path.read_text())
    man["numbers"] = {
        "note": "Generated by scripts/audit_evidence.py: every number printed in the manuscript, supplementary file and experiment reports, with its traced source. Full table: research/publication/number_trace.csv.",
        "documents": DOCS,
        "counts": {
            "tokens": len(trace),
            "decimal_traced": sum(1 for t in trace if t["kind"] == "decimal" and t["status"].startswith("traced")),
            "decimal_traced_weak": sum(1 for t in trace if t["kind"] == "decimal" and t["status"].startswith("traced (weak")),
            "decimal_untraced": sum(1 for t in trace if t["status"] == "UNTRACED decimal"),
            "integer_traced": sum(1 for t in trace if t["kind"] == "integer" and t["status"].startswith("traced")),
            "integer_constant_or_count": sum(1 for t in trace if t["kind"] == "integer" and not t["status"].startswith("traced")),
        },
        "trace_file": "research/publication/number_trace.csv",
    }
    man["copy_audit"] = {"failures": copy_fails}
    man["triple_audit"] = {"matched": t_ok, "unmatched": t_bad, "rule": "each printed 'estimate [lo, hi]' matches the mean, lower and upper bound of one committed row jointly, at printed precision"}
    if raw:
        man["raw_audit"] = [{"analysis": r["analysis"], "run_id": r["run_id"], "n_checks": len(r["checks"]), "failures": r["failures"]} for r in raw]
    man_path.write_text(json.dumps(man, indent=1) + "\n")
    nfail = sum(len(r["failures"]) for r in raw)
    for r in raw:
        print(f"RAW {r['run_id']}: {len(r['checks'])} checks, {len(r['failures'])} failures")
        for f in r["failures"]:
            print("   FAIL", f)
    print(json.dumps(man["numbers"]["counts"]))
    for u in unmatched:
        print(f"UNTRACED {u['document']}:{u['line']} {u['token']!r} | {u['context']}")
    return 1 if (nfail or unmatched or copy_fails or t_bad) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
