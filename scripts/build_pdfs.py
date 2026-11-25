# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Build the publication PDFs (manuscript, supplementary, one per experiment report).

Uses viral.report.build_pdf (pandoc Markdown to Typst, compiled with the typst Python
package) with the repository as the Typst root, so the manuscript can include figures
from research/experiments/. Intermediate .typ files are removed unless --keep-typ.

    .venv/bin/python scripts/build_pdfs.py [--keep-typ]

Environment: VIRAL_PANDOC (pandoc binary) and VIRAL_TYPST_PYTHON (a Python with the
typst package). Defaults: the shared tools folder next to the repository (../.tools).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from viral.report import build_pdf  # noqa: E402

DEFAULT_PANDOC = str(ROOT.parent / ".tools" / "pandoc")
DEFAULT_TYPST_PYTHON = str(ROOT.parent / ".tools" / "py" / "bin" / "python")


def documents() -> list[Path]:
    docs = [ROOT / "research/paper/manuscript.md", ROOT / "research/paper/supplementary.md"]
    docs += sorted((ROOT / "research/experiments").glob("EXP-*/report.md"))
    return docs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep-typ", action="store_true", help="keep the intermediate .typ files")
    args = ap.parse_args()
    pandoc = os.environ.get("VIRAL_PANDOC", DEFAULT_PANDOC)
    typst_python = os.environ.get("VIRAL_TYPST_PYTHON", DEFAULT_TYPST_PYTHON)
    for md in documents():
        out = build_pdf(md, pandoc=pandoc, typst_python=typst_python, root=ROOT)
        if not args.keep_typ:
            md.with_suffix(".typ").unlink(missing_ok=True)
        print(f"{out.relative_to(ROOT)} {out.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
