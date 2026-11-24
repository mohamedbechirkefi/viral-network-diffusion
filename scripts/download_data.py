# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Download the real network used by EXP-005 into data/raw/ (git-ignored) and record provenance.

Dataset: B. F. Maier's anonymized Facebook friendship network (fall 2014), as published
in the GitHub repository benmaier/BFMaierFBnetwork under the MIT License and listed in
the Netzschleuder catalogue as `facebook_friends`. Files are fetched from a pinned commit,
so the download is deterministic; the SHA-256 of every file is checked against the
values pinned in data/manifest.json when they are present.

Only the GML edge file (integer node ids, no node attributes), the LICENSE and the
README are fetched. The GraphML variant, which carries relationship descriptors, is
deliberately not downloaded.

Usage:  .venv/bin/python scripts/download_data.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw" / "maier_fb"
MANIFEST = REPO / "data" / "manifest.json"
COMMIT = "d1446af55483c98d93f72015b6238200e1a30575"
BASE = f"https://raw.githubusercontent.com/benmaier/BFMaierFBnetwork/{COMMIT}/"
FILES = ("bfmaier_anonymized_fb_network.gml", "LICENSE", "README.md")
MAX_BYTES = 5_000_000  # the three files total about 0.1 MB; anything larger is refused


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pinned_hashes() -> dict[str, str]:
    try:
        man = json.loads(MANIFEST.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    for ds in man.get("external_datasets", []):
        if ds.get("id") == "maier_fb":
            return {f["name"]: f["sha256"] for f in ds.get("files", []) if f.get("sha256")}
    return {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true", help="download again even if the files exist")
    a = ap.parse_args(argv)
    RAW.mkdir(parents=True, exist_ok=True)
    pins = pinned_hashes()
    record = {"dataset": "maier_fb", "commit": COMMIT, "accessed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "files": []}
    ok = True
    for name in FILES:
        dest = RAW / name
        url = BASE + name
        if a.force or not dest.is_file():
            with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (fixed https URL)
                data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                print(f"REFUSED: {name} is larger than {MAX_BYTES} bytes", file=sys.stderr)
                return 2
            dest.write_bytes(data)
        data = dest.read_bytes()
        digest = sha256_bytes(data)
        match = None if name not in pins else (pins[name] == digest)
        if match is False:
            ok = False
        record["files"].append({"name": name, "url": url, "bytes": len(data), "sha256": digest, "matches_manifest_pin": match})
        print(f"{name}: {len(data)} bytes, sha256 {digest}" + ("" if match is None else (" (pin OK)" if match else " (PIN MISMATCH)")))
    (RAW / "download_record.json").write_text(json.dumps(record, indent=1) + "\n")
    if not ok:
        print("ERROR: a downloaded file does not match the SHA-256 pinned in data/manifest.json", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
