# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Tests for the number-tracing helpers of scripts/audit_evidence.py (M4)."""

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("audit_evidence", Path(__file__).resolve().parents[1] / "scripts" / "audit_evidence.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_norm_token_signs_commas_and_scientific():
    assert audit.norm_token("+0.0969") == "0.0969"
    assert audit.norm_token("-0.0000") == "0.0000"
    assert audit.norm_token("2,016,000") == "2016000"
    assert audit.norm_token("1e-4") == "1e-04"
    assert audit.norm_token("-3.27e-05") == "-3.27e-05"


def test_fmt_keys_match_printed_precision_only():
    keys = audit.fmt_keys(-0.35292)
    assert "-0.3529" in keys and "0.3529" in keys
    assert "-0.3530" not in keys
    assert "1e-04" in audit.fmt_keys(1e-4)


def test_triple_pattern_reads_text_and_table_forms():
    m = audit.TRIPLE.search("WS - ER -0.3529 [-0.3601, -0.3456] at p = 0.30")
    assert m and m.groups() == ("-0.3529", "-0.3601", "-0.3456")
    m = audit.TRIPLE.search("| -0.0884 | [-0.0910, -0.0857] | 0.9875 |")
    assert m and m.groups() == ("-0.0884", "-0.0910", "-0.0857")


def test_identifiers_are_not_numbers():
    line = "run EXP-002-20261124T233447Z-2c7febb6, claim EXP-004-S4-n500-R03, decision D-013, 2026-11-25, section 11.3"
    for rx in audit.STRIP:
        line = rx.sub(" ", line)
    assert audit.NUM.findall(line) == []
