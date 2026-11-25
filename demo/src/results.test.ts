// SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
});

describe("validateResults, VIRAL extensions (fail closed)", () => {
  it("rejects an estimate without the exact manuscript display text", () => {
    const r = good();
    const e = r.experiments.find((x: { estimates: unknown[] }) => x.estimates.length > 0);
    e.estimates[0].display = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a missing claim id on an estimate", () => {
    const r = good();
    const e = r.experiments.find((x: { estimates: unknown[] }) => x.estimates.length > 0);
    delete e.estimates[0].claim_id;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-boolean Holm decision", () => {
    const r = good();
    const e = r.experiments.find((x: { estimates: unknown[] }) => x.estimates.length > 0);
    e.estimates[0].rejected = "yes";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects missing or malformed level curves", () => {
    const r = good();
    delete r.levels;
    expect(() => validateResults(r)).toThrow(ResultsError);
    const r2 = good();
    r2.levels["EXP-002"].series[0].points[0].lo = 2;
    expect(() => validateResults(r2)).toThrow(ResultsError);
  });
  it("rejects missing graph statistics or SESOI", () => {
    const r = good();
    r.graph_stats.rows = [];
    expect(() => validateResults(r)).toThrow(ResultsError);
    const r2 = good();
    delete r2.sesoi;
    expect(() => validateResults(r2)).toThrow(ResultsError);
  });
  it("keeps every registered experiment and the S1 per-multiplier reading", () => {
    const v = validateResults(good());
    expect(v.experiments.map((e) => e.id)).toEqual(["EXP-001", "EXP-002", "EXP-003", "EXP-004", "EXP-005", "M4"]);
    const s1 = v.experiments[3].estimates.filter((x) => x.analysis === "S1");
    expect(s1.length).toBe(10);
    expect(v.experiments[3].verdict).toContain("no overall verdict");
  });
});
