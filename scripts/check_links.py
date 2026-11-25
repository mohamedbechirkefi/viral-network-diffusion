# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Check relative links in tracked Markdown files and the manuscript reference list.

1. Every relative Markdown link `[text](target)` or `![alt](target)` in a tracked .md file
   resolves to an existing file or folder; a `#fragment` must match a heading slug
   (GitHub style) of the target file. External links (http, https, mailto) are skipped,
   and links inside code spans or fenced code blocks are ignored.
2. Every entry of research/paper/references.bib is listed in the manuscript reference
   list (first author surname and year), and every reference-list item has a bib entry.

    .venv/bin/python scripts/check_links.py      # exit 0 and "LINKS PASS" when clean
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def tracked_markdown(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "*.md"], capture_output=True,
                         text=True, check=True).stdout.split()
    return [root / p for p in out if "node_modules/" not in p]


def slug(heading: str) -> str:
    """GitHub-style anchor: lowercase, drop punctuation except hyphens and spaces, spaces to hyphens."""
    h = re.sub(r"[`*_]", "", heading.strip()).lower()
    h = unicodedata.normalize("NFKD", h)
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    seen: dict[str, int] = {}
    out: set[str] = set()
    in_fence = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        m = None if in_fence else re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            out.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
    return out


def links(md: Path) -> list[tuple[int, str]]:
    found = []
    in_fence = False
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        found += [(i, m.group(1)) for m in LINK.finditer(line)]
    return found


def check_links(files: list[Path], root: Path = ROOT) -> tuple[int, list[str]]:
    errors, n = [], 0
    for md in files:
        for line, target in links(md):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            n += 1
            path, _, frag = target.partition("#")
            dest = (md.parent / path).resolve() if path else md
            where = f"{md.relative_to(root)}:{line}: {target}"
            if not dest.exists():
                errors.append(f"{where} (missing file)")
            elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                errors.append(f"{where} (missing anchor)")
    return n, errors


def check_references(root: Path = ROOT) -> tuple[int, list[str]]:
    bib = (root / "research/paper/references.bib").read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S):
        body = m.group(2)
        author = re.search(r"author\s*=\s*\{(.*?)\}\s*,", body, re.S).group(1)
        first = re.sub(r"[{}\\']", "", author.split(" and ")[0].split(",")[0]).strip()
        year = re.search(r"year\s*=\s*\{?(\d{4})", body).group(1)
        entries.append((m.group(1), first, year))
    ms = (root / "research/paper/manuscript.md").read_text(encoding="utf-8")
    refs = ms.split("\n## References", 1)[1].split("\n## ", 1)[0]
    items = [ln for ln in refs.splitlines() if ln.startswith("- ")]
    errors = []

    def fold(s: str) -> str:
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

    matched = set()
    for key, first, year in entries:
        hits = [i for i, it in enumerate(items) if fold(it).startswith(f"- {fold(first)}") and f"({year})" in it]
        if not hits:
            errors.append(f"bib entry {key} ({first} {year}) is not in the manuscript reference list")
        matched.update(hits)
    for i, it in enumerate(items):
        if i not in matched:
            errors.append(f"reference-list item without a bib entry: {it[:70]}")
    return len(entries), errors


def main() -> int:
    n_links, link_errors = check_links(tracked_markdown())
    n_bib, ref_errors = check_references()
    for e in link_errors + ref_errors:
        print("FAIL", e)
    print(f"{n_links} relative links checked, {len(link_errors)} broken; "
          f"{n_bib} bib entries checked, {len(ref_errors)} reference mismatches")
    ok = not link_errors and not ref_errors
    print("LINKS PASS" if ok else "LINKS FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
