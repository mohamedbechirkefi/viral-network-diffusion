# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Relative Markdown links resolve, and references.bib matches the manuscript reference list (M6)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_relative_links_resolve():
    n, errors = check_links.check_links(check_links.tracked_markdown())
    assert n > 0
    assert errors == []


def test_bib_matches_reference_list():
    n, errors = check_links.check_references()
    assert n > 0
    assert errors == []


def test_checker_detects_broken_link_and_anchor(tmp_path):
    (tmp_path / "a.md").write_text("# Title\n\n## Second part\n", encoding="utf-8")
    doc = tmp_path / "b.md"
    doc.write_text("[ok](a.md#second-part) [bad](missing.md) [anchor](a.md#nope) "
                   "`[code](ignored.md)` [web](https://example.org)\n", encoding="utf-8")
    n, errors = check_links.check_links([doc], root=tmp_path)
    assert n == 3
    assert len(errors) == 2
    assert any("missing file" in e for e in errors)
    assert any("missing anchor" in e for e in errors)
