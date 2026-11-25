# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Build the claims register and the artifact manifest from committed result files.

Rows are generated from results/confirmatory/**/analysis.json, the committed CSV tables beside them
(themselves generated from the raw result files by scripts/analyse_confirmatory.py and `viral report`)
and results/exploratory/M4/ (scripts/exploratory_m4.py, exploratory). Synthesis and external claims
are listed by hand at the end of this file, each with the result ids or the source it rests on.
Every row carries: claim, result id, config hash, figure or table, section, limit (M4 brief, task 3).
All result rows are simulations (claims boundary).

Usage:  .venv/bin/python scripts/build_records.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLAIMS = REPO / "research" / "claims_register.csv"
ARTIFACTS = REPO / "research" / "publication" / "artifact_manifest.json"
FIELDS = ["claim_id", "text", "type", "result_id", "config_hash", "figure_or_table", "section", "evidence_path_or_source", "scope", "status", "limitations"]
SCOPE = {
    "EXP-002": "simulation; IC; N = 1000, <k> = 6; ER G(n,M), WS beta = 0.1, BA m = 3; one uniformly random seed; R = 120, C = 200",
    "EXP-003": "simulation; fractional-threshold (LT); N = 1000, <k> = 6; phi 0.18 to 0.30; 10 random seeds; R = 30, C = 200",
    "EXP-004": "simulation; IC; EXP-002 graphs (replicates 0 to 29) or their S2/S3 variants, or N = 500/2000 (S4, optional); one random seed; R = 30, C = 200",
    "EXP-005": "simulation on one anonymized 362-node friendship network (maier_fb) versus G(n,M) and degree-preserving nulls; one random seed; R = 120, C = 200; conditional on this one network",
    "M4": "EXPLORATORY simulation (M4, post hoc, after the confirmatory results were seen); fresh master seeds 20261201 to 20261203; R = 30, C = 200; unadjusted 95 percent intervals",
}
# Where each analysis appears: (figure or table, manuscript and report sections)
PLACE = {
    "EXP-002": ("manuscript Table 3 and Figure 1; report EXP-002 Table 8.1 and Figure EXP-002-F1", "manuscript 5.1; EXP-002 report 8.1"),
    "EXP-003": ("manuscript Table 5 and Figure 4; report EXP-003 Table 8.1 and Figure EXP-003-F1", "manuscript 5.3; EXP-003 report 8.1"),
    "EXP-004 S1": ("manuscript Table 4 and Figure 3; report EXP-004 Table 8.1 and Figure EXP-004-F1", "manuscript 5.2; EXP-004 report 8.1"),
    "EXP-004 S2": ("manuscript Table 4; report EXP-004 Table 8.2 and Figure EXP-004-F2", "manuscript 5.2; EXP-004 report 8.2"),
    "EXP-004 S3": ("supplementary Table S4.1; report EXP-004 Table 8.3", "manuscript 5.2 (summary); supplementary S4; EXP-004 report 8.3"),
    "EXP-004 S4-n500": ("supplementary Table S4.2; report EXP-004 Table 8.4", "manuscript 5.2 (summary); supplementary S4; EXP-004 report 8.4"),
    "EXP-004 S4-n2000": ("supplementary Table S4.2; report EXP-004 Table 8.4", "manuscript 5.2 (summary); supplementary S4; EXP-004 report 8.4"),
    "EXP-005": ("manuscript Table 6 and Figure 5; report EXP-005 Table 8.1 and Figure EXP-005-F1", "manuscript 5.4; EXP-005 report 8.1"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fmt(x: float) -> str:
    return f"{x:+.4f}" if abs(x) >= 1e-4 or x == 0 else f"{x:+.2e}"


def read_csv(p: Path) -> list[dict]:
    with p.open() as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    rows, artifacts = [], []
    for path in sorted((REPO / "results" / "confirmatory").rglob("analysis.json")):
        a = json.loads(path.read_text())
        exp = a["experiment"]
        base = exp.split()[0]
        tag = exp.replace(" ", "-")
        rel = path.relative_to(REPO)
        rd = path.parent
        optional = " (optional analysis S4)" if "S4" in exp else ""
        fig, sec = PLACE[exp]
        common = {"result_id": a["run_id"], "config_hash": a["config_hash"], "scope": SCOPE[base]}
        for i, r in enumerate(a["primary"], 1):
            param = r["param"] if isinstance(r["param"], str) else f"{r['param']:g}"
            pname = "multiplier c" if "S1" in exp else ("phi grid" if base == "EXP-003" else "p")
            text = (f"Simulation{optional}: {r['contrast']} at {pname} = {param}: mean paired difference in final cascade fraction S "
                    f"{fmt(r['mean'])}, Holm-step percentile interval [{fmt(r['lo'])}, {fmt(r['hi'])}] at level {r['interval_level']:.4f}; "
                    f"Holm-adjusted p {r['p_holm']:.4g}{' (< 1e-4 resolution)' if r['p_holm'] == 0 else ''}; "
                    f"{'H0 rejected' if r['reject'] else 'H0 not rejected'}; "
                    f"{'interval inside' if r['equivalent_within_sesoi'] else 'interval not inside'} the SESOI [-0.02, 0.02]; n = {r['n_replicates']} matched sets.")
            rows.append({
                "claim_id": f"{tag}-R{i:02d}", "text": text, "type": "confirmatory result" + (" (optional)" if optional else ""), **common,
                "figure_or_table": fig, "section": sec,
                "evidence_path_or_source": f"{rel}; {rd.relative_to(REPO)}/primary_contrasts.csv (generator scripts/analyse_confirmatory.py; rev {a['git_revision'][:12]})",
                "status": "verified against raw result (recomputed by scripts/audit_evidence.py, M4)",
                "limitations": "research/limitations.md; nonrejection is not equivalence; simulation only" + ("; S1 is reported per multiplier with no overall verdict (owner, 2026-11-25, D-013)" if "S1" in exp else ""),
            })
        # secondary (unadjusted) final-size contrasts
        sec_rows = [s for s in read_csv(rd / "secondary_contrasts.csv") if s["metric"] in ("mean_S", "grid_mean_S")]
        for j, s in enumerate(sec_rows, 1):
            where = "grid mean" if s["param"] == "grid mean" else f"{'c' if 'S1' in exp else ('phi' if base == 'EXP-003' else 'p')} = {s['param']}"
            rows.append({
                "claim_id": f"{tag}-SEC{j:02d}", "type": "secondary estimate (unadjusted)", **common,
                "text": (f"Simulation: {s['contrast']}, {s['model'].upper()}, seed rule {s['seed_rule']}, seed count {s['seed_count']}, {where}: "
                         f"mean paired difference in S {fmt(float(s['mean']))}, unadjusted 95 percent interval [{fmt(float(s['lo']))}, {fmt(float(s['hi']))}]; n = {s['n_replicates']}."),
                "figure_or_table": f"{rd.relative_to(REPO)}/secondary_contrasts.csv; supplementary S2", "section": f"supplementary S2; {base} report 8 (where quoted); manuscript 5 (where quoted)",
                "evidence_path_or_source": f"{rd.relative_to(REPO)}/secondary_contrasts.csv (generator scripts/analyse_confirmatory.py)",
                "status": "verified against raw result (recomputed by scripts/audit_evidence.py, M4)",
                "limitations": "secondary, unadjusted, not used for any confirmatory decision; simulation only",
            })
        # descriptive levels (primary exposure only) and graph statistics
        prim_rule = ("random", "10") if base == "EXP-003" else ("random", "1")
        lv = [t for t in read_csv(rd / "topology_means.csv") if (t["seed_rule"], t["seed_count"]) == prim_rule]
        for j, t in enumerate(lv, 1):
            rows.append({
                "claim_id": f"{tag}-LVL{j:02d}", "type": "descriptive", **common,
                "text": f"Simulation: mean over {t['replicates']} replicates of per-graph mean S, {t['topology']}, {t['model'].upper()} parameter {t['param']}: {float(t['mean_S']):.4f} [{float(t['lo95']):.4f}, {float(t['hi95']):.4f}] (unadjusted 95 percent).",
                "figure_or_table": f"{rd.relative_to(REPO)}/topology_means.csv; report {base} 8.2; manuscript Figures 2, 4, 5 where shown",
                "section": "manuscript 5; supplementary S2", "evidence_path_or_source": f"{rd.relative_to(REPO)}/topology_means.csv",
                "status": "verified against raw result (recomputed by scripts/audit_evidence.py, M4)", "limitations": "descriptive; simulation only",
            })
        gp = rd / "tables" / "graphs.csv"
        for t in read_csv(gp):
            rows.append({
                "claim_id": f"{tag}-G-{t['topology']}", "type": "descriptive (graph statistics)", **common,
                "text": (f"Generated graphs, {t['topology']}, mean over {t['graphs']} graphs: edges {float(t['mean_m']):.1f}, <k^2> {float(t['second_moment']):.2f}, "
                         f"p_c estimate {float(t['p_c']):.4f}, giant-component fraction {float(t['giant_fraction']):.4f}, average clustering {float(t['clustering']):.4f}."),
                "figure_or_table": f"{gp.relative_to(REPO)}; manuscript Table 2 (where shown)", "section": "manuscript 4.2; experiment report 5",
                "evidence_path_or_source": f"{gp.relative_to(REPO)} (generator viral report)", "status": "generated from raw result",
                "limitations": "descriptive; p_c is the locally tree-like estimate and ignores clustering",
            })
        for f in ["primary_contrasts.csv", "secondary_contrasts.csv", "topology_means.csv", *a["figures"]]:
            p = rd / f
            artifacts.append({"id": f"{tag}/{f}", "experiment_id": base, "run_ids": [a["run_id"]], "path": str(p.relative_to(REPO)), "sha256": sha(p),
                              "metric": "final cascade fraction S (per-graph mean); paired differences; Holm-step percentile intervals (protocol 11.3)",
                              "result_path": f"results/raw/confirmatory/{base}/{a['run_id']}/result.json (git-ignored)", "result_sha256": a["result_json_sha256"],
                              "generator": "scripts/analyse_confirmatory.py", "config_hash": a["config_hash"], "code_revision": a["git_revision"]})

    # exploratory M4 checks
    m4 = REPO / "results" / "exploratory" / "M4"
    j = json.loads((m4 / "m4_exploratory.json").read_text())
    counters: dict[str, int] = {}
    for c in read_csv(m4 / "m4_exploratory_contrasts.csv"):
        counters[c["check"]] = counters.get(c["check"], 0) + 1
        k = counters[c["check"]]
        par = "phi" if c["check"] == "X3" else "p"
        rows.append({
            "claim_id": f"M4-{c['check']}-{k:02d}", "type": "exploratory result (M4, post hoc)", "result_id": f"M4 exploratory {c['check']} (master seed {j['master_seeds'][c['check']]})",
            "config_hash": f"script constants in scripts/exploratory_m4.py at rev {j['code_revision'][:12]}", "figure_or_table": "manuscript Table 7 (where shown); supplementary S4.3",
            "section": "manuscript 5.5 and 6.1; supplementary S4.3",
            "text": f"EXPLORATORY simulation: {c['contrast']}, metric {c['metric']}, {par} = {c['p']}: mean paired difference {fmt(float(c['mean_diff']))}, unadjusted 95 percent interval [{fmt(float(c['lo95']))}, {fmt(float(c['hi95']))}]; n = {c['n_replicates']}.",
            "evidence_path_or_source": "results/exploratory/M4/m4_exploratory_contrasts.csv (generator scripts/exploratory_m4.py)", "scope": SCOPE["M4"],
            "status": "exploratory; generated by script", "limitations": "post hoc and exploratory; never replaces a frozen verdict; unadjusted; one randomisation scheme",
        })
    for f in ("m4_exploratory.json", "m4_exploratory_contrasts.csv", "run.log"):
        artifacts.append({"id": f"M4/{f}", "experiment_id": "M4 exploratory (X1 to X3)", "run_ids": ["M4-exploratory"], "path": f"results/exploratory/M4/{f}", "sha256": sha(m4 / f),
                          "metric": "final cascade fraction S; giant-normalised S (X2); paired differences; unadjusted 95 percent percentile intervals",
                          "result_path": "results/exploratory/M4/m4_exploratory.json", "result_sha256": sha(m4 / "m4_exploratory.json"),
                          "generator": "scripts/exploratory_m4.py", "config_hash": "script constants", "code_revision": j["code_revision"]})

    rows += SYNTHESIS + EXTERNAL
    for r in rows:
        for k in FIELDS:
            r.setdefault(k, "")
    with CLAIMS.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    old = json.loads(ARTIFACTS.read_text()) if ARTIFACTS.exists() else {}
    doc = {"schema_version": "0.3", "updated": "2026-11-25", "note": "Artifacts generated by scripts/build_records.py; the numbers block and audits by scripts/audit_evidence.py.", "artifacts": artifacts}
    for k in ("numbers", "raw_audit", "copy_audit"):
        if k in old:
            doc[k] = old[k]
    ARTIFACTS.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(rows)} claim rows; {len(artifacts)} artifacts")
    return 0


R2 = "EXP-002-20261124T233447Z-2c7febb6"
R3 = "EXP-003-20261124T234212Z-a2d668ab"
R4S1, R4S2, R4S3 = "EXP-004-20261124T233447Z-de14a4b3", "EXP-004-20261124T233637Z-916e8d29", "EXP-004-20261124T233755Z-e1d24091"
R4N5, R4N2 = "EXP-004-20261124T235044Z-e31dba07", "EXP-004-20261124T235110Z-40385ec3"
R5 = "EXP-005-20261124T233932Z-d277f271"
C2 = "2c7febb68d111345c89d9d165dc574b107319b8b3dd4df141b4de66db64f4256"
C3 = "a2d668abb8f1dd40c442582d4276509c81040a95a47f2d00277abdc9f47a2abd"
C4S1 = "de14a4b374f26f4a688857695c225e8ed7986296f8183a0aba343ac1e4d4148d"
C4S2 = "916e8d2905088aaf46ba170cad8f894464dcb789bfdb1d759798ab5a0deb92e0"
C4S3 = "e1d240911d90b80284fd78d8ecf60ec96fd4a2f97064a066dd8d3817ee166971"
C4N5 = "e31dba07eb685936f0ea61f10455d4e7f7f358acfd1ff4906565ab288d52ba1b"
C4N2 = "40385ec33b306aa97f3df78618fead6b0f833c3f527d13b85a3eefbf7c728a73"
C5 = "d277f271e6863fba0f5a3ee24796b1e94e273c5c7f4a4276c20e8e7a651218ae"


def syn(cid, text, rid, cfg, fig, sec, ev, lim, typ="synthesis (inferred from listed results)"):
    return {"claim_id": cid, "text": text, "type": typ, "result_id": rid, "config_hash": cfg, "figure_or_table": fig, "section": sec,
            "evidence_path_or_source": ev, "scope": "simulation; as in the rows cited", "status": "checked against the cited rows (M4)", "limitations": lim}


SYNTHESIS = [
    syn("SYN-01", "In EXP-002 both topology contrasts change sign across the p grid (WS - ER negative at p 0.05 to 0.30 and positive at 0.50; BA - ER positive at 0.02 to 0.20 and negative at 0.30 and 0.50), so no single topology effect summarises the IC results.",
        R2, C2, "manuscript Table 3, Figure 1", "manuscript abstract, 5.1, 6, 9", "EXP-002-R02 to R07, R08 to R14", "simulation only; one parameterisation per family"),
    syn("SYN-02", "The EXP-002 pattern of signs and rejections is unchanged under exact edge matching (S3) and at N = 500 and N = 2000 (S4), so neither the edge-count mismatch nor finite size within that range explains it.",
        f"{R4S3}; {R4N5}; {R4N2}", f"{C4S3}; {C4N5}; {C4N2}", "supplementary Tables S4.1, S4.2", "manuscript 5.2, 6.1", "EXP-004-S3-R01 to R14; EXP-004-S4-n500-R01 to R14; EXP-004-S4-n2000-R01 to R14", "two sizes only"),
    syn("SYN-03", "The BA advantage over ER at p = 0.15 and 0.20 is carried by the degree sequence: BA and its degree-preserving randomisation are equivalent within 0.02 at those p (S2, EXP-004 protocol item 6).",
        f"{R2}; {R4S2}", f"{C2}; {C4S2}", "manuscript Table 4", "manuscript abstract, 5.2, 6.1", "EXP-002-R11, R12; EXP-004-S2-R04, R05", "one randomisation scheme (10 M swaps); R = 30"),
    syn("SYN-04", "Rescaling p by each graph's tree-like threshold estimate makes the topologies equivalent within 0.02 at c = 0.5 and 1 but not at c = 1.5, 2 and 3; per the owner's decision S1 gives no overall verdict and reclassifies no EXP-002 effect.",
        R4S1, C4S1, "manuscript Table 4, Figure 3", "manuscript 5.2, 6.1", "EXP-004-S1-R01 to R10; decision D-013", "the threshold estimate ignores clustering"),
    syn("SYN-05", "The ordering of WS against ER depends on the contagion model: WS is below ER near the IC threshold (EXP-002) and far above ER under the fractional-threshold model (EXP-003).",
        f"{R2}; {R3}", f"{C2}; {C3}", "manuscript Tables 3 and 5", "manuscript abstract, 5.3, 6", "EXP-002-R05, R06; EXP-003-R01", "EXP-003 grid mean is grid-dependent (limitation 15)"),
    syn("SYN-06", "On the one real network of EXP-005, structure beyond the degree sequence lowers IC final size wherever a difference is detectable (real - real_dpr negative at the four largest calibrated p).",
        R5, C5, "manuscript Table 6", "manuscript abstract, 5.4", "EXP-005-R11 to R14", "one network; conditional inference"),
    syn("SYN-07", "Exploratory (M4): the WS deficit at p = 0.30 is reproduced on fresh seeds and is almost entirely a structure-beyond-degree effect (WS minus its degree-preserving randomisation), while the WS advantage at p = 0.50 goes with its narrower degree sequence.",
        "M4 exploratory X1", "scripts/exploratory_m4.py constants", "manuscript Table 7", "manuscript 5.5, 6.1", "M4-X1 rows (results/exploratory/M4/m4_exploratory_contrasts.csv)", "exploratory, post hoc; clustering and ring structure are removed together", "exploratory synthesis"),
    syn("SYN-08", "Exploratory (M4): the EXP-005 real - real_dpr deficit is not explained by the smaller giant component: restricted to seeds in the giant component and normalised by its size, the deficit remains (-0.1177 at the largest calibrated p).",
        "M4 exploratory X2", "scripts/exploratory_m4.py constants", "manuscript Table 7", "manuscript 5.5, 6.1", "M4-X2 rows", "exploratory, post hoc; one network", "exploratory synthesis"),
    syn("SYN-09", "Exploratory (M4): under the threshold model, the WS advantage is carried by structure beyond the degree sequence (WS far above its randomisation, the randomisation below ER), while BA's degree-preserving randomisation spreads more than BA itself in the transition region.",
        "M4 exploratory X3", "scripts/exploratory_m4.py constants", "manuscript Table 7", "manuscript 5.5, 6.1", "M4-X3 rows", "exploratory, post hoc; R = 30", "exploratory synthesis"),
    syn("SYN-10", "With 120 matched replicates and common random numbers, differences far below the SESOI are rejected by Holm (for example 3.27e-05 in S), so a rejection does not indicate a practically important effect.",
        R2, C2, "manuscript Table 3", "manuscript 4.5, 7", "EXP-002-R02", "statistical property of this design"),
]


def ext(cid, text, src, level, sec, lim):
    return {"claim_id": cid, "text": text, "type": "external", "result_id": "", "config_hash": "", "figure_or_table": "", "section": sec,
            "evidence_path_or_source": src, "scope": "literature", "status": f"source read: {level}", "limitations": lim}


EXTERNAL = [
    ext("EXT-01", "Pastor-Satorras and Vespignani (2001) report, in their abstract, that a spreading model on scale-free networks has no epidemic threshold.",
        "doi:10.1103/PhysRevLett.86.3200; https://arxiv.org/abs/cond-mat/0010317", "abstract only (2026-11-24)", "manuscript 2, 3", "abstract-level; the SIS model of that paper differs from IC"),
    ext("EXT-02", "Newman, Strogatz and Watts (2001) develop, per their abstract, the theory of random graphs with arbitrary degree distributions, including the phase transition at which a giant component forms.",
        "doi:10.1103/PhysRevE.64.026118; https://arxiv.org/abs/cond-mat/0007235", "abstract only (2026-11-25, M4)", "manuscript 2, 3", "abstract-level; the bond-percolation threshold expression used here was not checked against the text"),
    ext("EXT-03", "Watts (2002) defines a model in which a node adopts when at least a threshold fraction of its neighbours have adopted, and describes a cascade window bounded as a function of the average degree.",
        "doi:10.1073/pnas.082090499; https://pmc.ncbi.nlm.nih.gov/articles/PMC122850/", "full text opened (2026-11-25, M4)", "manuscript 2, 3", "read through a summarising fetch; the threshold grid of this study was not derived from the paper's numbers"),
    ext("EXT-04", "Kempe, Kleinberg and Tardos study influence maximisation in social networks under several widely studied diffusion models (journal version abstract).",
        "doi:10.4086/toc.2015.v011a004; https://www.theoryofcomputing.org/articles/v011a004/", "abstract only (2026-11-25, M4)", "manuscript 2", "the abstract does not name the IC or LT model; the IC definition is stated in full in the manuscript"),
    ext("EXT-05", "Barabasi and Albert (1999) give growth with preferential attachment as a mechanism generating scale-free degree distributions (abstract).",
        "doi:10.1126/science.286.5439.509; https://arxiv.org/abs/cond-mat/9910332", "abstract only (2026-11-24)", "manuscript 2, 3", "abstract-level"),
    ext("EXT-06", "Kitsak et al. (2010) report, in their abstract, that the most efficient single spreaders are in the k-core rather than simply of highest degree.",
        "doi:10.1038/nphys1746; https://arxiv.org/abs/1001.5285", "abstract only (2026-11-24)", "manuscript 2, 9", "abstract-level; k-core seeding is not studied here"),
    ext("EXT-07", "Pastor-Satorras, Castellano, Van Mieghem and Vespignani (2015) review epidemic processes in complex networks (abstract).",
        "doi:10.1103/RevModPhys.87.925; https://arxiv.org/abs/1408.2701", "abstract only (2026-11-24)", "manuscript 2", "abstract-level"),
    ext("EXT-08", "The Watts-Strogatz model (Watts and Strogatz 1998), the threshold idea (Granovetter 1978), complex contagion (Centola and Macy 2007), structural virality (Goel et al. 2016), the artificial cultural market (Salganik et al. 2006) and the random-graph model (Gilbert 1959) are cited as attributions only.",
        "research/literature_review.md (Crossref metadata, 2026-11-24)", "metadata only; text not read", "manuscript 2", "no statement in the manuscript rests on the content of these papers"),
    ext("EXT-09", "The real network is B. F. Maier's anonymized Facebook friendship network (fall 2014), released under the MIT License; its author requests citation of Maier and Brockmann (2017).",
        "https://github.com/benmaier/BFMaierFBnetwork (README and LICENSE downloaded and hashed; data/manifest.json)", "repository files read (2026-11-24)", "manuscript 4.3, 8", "the paper itself was not read; it is cited as the data citation"),
]


if __name__ == "__main__":
    raise SystemExit(main())
