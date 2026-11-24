# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Real-network ingestion (EXP-005): raw GML text -> validated processed edge list.

`ingest_gml` is a pure function (text in, dictionary out, no I/O). It accepts the
GML subset used by the source file (a `graph` block with `undirected 1`, `node`
blocks carrying an integer `id`, and `edge` blocks carrying integer `source` and
`target`), validates it against that schema, and reports missingness and
exclusion counts. Nodes are relabelled 0..n-1 in ascending order of their source
id (pseudonymous integers in, pseudonymous integers out). No node attribute other
than the id is kept.

Exclusion rules (fixed before the data were inspected, research/protocol.md
section 11.2): an edge with a missing or non-integer endpoint is excluded
(missingness); an edge whose endpoint is not a declared node is excluded; a
self-loop is excluded; a repeated undirected edge is kept once. Isolated nodes
are kept (protocol section 5: isolated nodes are part of the topology).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .graphs import Graph, from_edges, graph_stats

PROCESSED_SCHEMA_VERSION = "1.0.0"
_TOKEN = re.compile(r'"[^"]*"|\[|\]|[^\s\[\]]+')


class IngestError(ValueError):
    """Raised when the raw file does not match the expected schema."""


def _parse_block(tokens: list[str], i: int) -> tuple[dict, int]:
    """Parse `key value` pairs until the matching `]`; nested blocks become lists of dicts under their key."""
    out: dict = {}
    while i < len(tokens):
        t = tokens[i]
        if t == "]":
            return out, i + 1
        if t == "[":
            raise IngestError("unexpected '[' without a key")
        if i + 1 >= len(tokens):
            raise IngestError(f"key {t!r} has no value")
        v = tokens[i + 1]
        if v == "[":
            sub, i = _parse_block(tokens, i + 2)
            out.setdefault(t, []).append(sub)
        elif v == "]":
            raise IngestError(f"key {t!r} has no value")
        else:
            out.setdefault(t, []).append(v)
            i += 2
    raise IngestError("unterminated block")


def _as_int(v) -> int | None:
    if not isinstance(v, list) or len(v) != 1 or not isinstance(v[0], str):
        return None
    try:
        return int(v[0])
    except ValueError:
        return None


def ingest_gml(text: str) -> dict:
    """Turn raw GML text into the processed form. Pure: no I/O, deterministic."""
    tokens = _TOKEN.findall(text)
    top, i = _parse_block(tokens + ["]"], 0)
    if i != len(tokens) + 1:
        raise IngestError("trailing content after the graph block")
    graphs = top.get("graph", [])
    if len(graphs) != 1 or not isinstance(graphs[0], dict):
        raise IngestError("expected exactly one graph block")
    g = graphs[0]
    directed = _as_int(g.get("directed", ["0"]))
    undirected = _as_int(g.get("undirected", ["1"]))
    if directed == 1 or undirected == 0:
        raise IngestError("graph must be undirected")
    raw_nodes = g.get("node", [])
    raw_edges = g.get("edge", [])
    counts = {
        "nodes_declared": len(raw_nodes), "edges_declared": len(raw_edges),
        "nodes_missing_id": 0, "nodes_duplicate_id": 0,
        "edges_missing_endpoint": 0, "edges_unknown_endpoint": 0,
        "edges_self_loop": 0, "edges_duplicate": 0,
    }
    ids: list[int] = []
    seen_ids: set[int] = set()
    for nd in raw_nodes:
        if not isinstance(nd, dict):
            raise IngestError("node entry is not a block")
        nid = _as_int(nd.get("id"))
        if nid is None:
            counts["nodes_missing_id"] += 1
            continue
        if nid in seen_ids:
            counts["nodes_duplicate_id"] += 1
            continue
        seen_ids.add(nid)
        ids.append(nid)
    if not ids:
        raise IngestError("no valid node")
    relabel = {nid: k for k, nid in enumerate(sorted(ids))}
    edges: set[tuple[int, int]] = set()
    for ed in raw_edges:
        if not isinstance(ed, dict):
            raise IngestError("edge entry is not a block")
        s, t = _as_int(ed.get("source")), _as_int(ed.get("target"))
        if s is None or t is None:
            counts["edges_missing_endpoint"] += 1
            continue
        if s not in relabel or t not in relabel:
            counts["edges_unknown_endpoint"] += 1
            continue
        if s == t:
            counts["edges_self_loop"] += 1
            continue
        key = (min(relabel[s], relabel[t]), max(relabel[s], relabel[t]))
        if key in edges:
            counts["edges_duplicate"] += 1
            continue
        edges.add(key)
    n = len(relabel)
    counts["nodes_kept"] = n
    counts["edges_kept"] = len(edges)
    counts["edges_excluded"] = counts["edges_declared"] - len(edges)
    edge_list = [list(e) for e in sorted(edges)]
    graph = from_edges(n, [tuple(e) for e in edge_list])
    deg = graph.degrees()
    counts["nodes_isolated"] = int((deg == 0).sum())
    return {"processed_schema_version": PROCESSED_SCHEMA_VERSION, "n": n, "m": len(edge_list), "edges": edge_list, "counts": counts}


def validate_processed(doc: dict) -> None:
    """Schema check of the processed form."""
    if not isinstance(doc, dict) or doc.get("processed_schema_version") != PROCESSED_SCHEMA_VERSION:
        raise IngestError("processed document: wrong or missing schema version")
    n, edges = doc.get("n"), doc.get("edges")
    if not isinstance(n, int) or n < 1 or not isinstance(edges, list) or doc.get("m") != len(edges):
        raise IngestError("processed document: bad n, m or edges")
    seen = set()
    for e in edges:
        if not (isinstance(e, list) and len(e) == 2 and all(isinstance(x, int) for x in e) and 0 <= e[0] < e[1] < n):
            raise IngestError(f"processed document: bad edge {e!r}")
        if tuple(e) in seen:
            raise IngestError(f"processed document: duplicate edge {e!r}")
        seen.add(tuple(e))


def processed_bytes(doc: dict) -> bytes:
    """Canonical serialisation, so the SHA-256 of the processed file is reproducible."""
    validate_processed(doc)
    return (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode()


def summary(doc: dict) -> dict:
    """Aggregate statistics only (safe to commit): no row-level data."""
    g = to_graph(doc)
    s = graph_stats(g)
    return {k: s[k] for k in ("n", "m", "mean_degree", "second_moment_degree", "max_degree", "min_degree", "p_c", "n_components", "giant_component_fraction", "n_isolated", "average_clustering")}


def to_graph(doc: dict, family: str = "real") -> Graph:
    validate_processed(doc)
    return from_edges(doc["n"], [tuple(e) for e in doc["edges"]], family=family, params={"source": "processed real network", "n": doc["n"], "m": doc["m"]})


def load_processed(path: str | Path, expected_sha256: str | None = None) -> Graph:
    """Load a processed file; refuse it if its SHA-256 differs from the pinned value."""
    p = Path(path)
    if not p.is_file():
        raise IngestError(f"processed real network not found: {p} (run scripts/ingest_data.py)")
    b = p.read_bytes()
    digest = hashlib.sha256(b).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise IngestError(f"processed real network sha256 {digest[:12]} does not match the pinned {expected_sha256[:12]}")
    g = to_graph(json.loads(b))
    return Graph(n=g.n, indptr=g.indptr, indices=g.indices, family="real", params={**g.params, "sha256": digest})
