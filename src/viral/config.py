# SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0
"""Experiment configuration: schema validation, canonical hashing and derived RNG streams."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import jsonschema
import numpy as np

from . import CONFIG_SCHEMA_VERSIONS

TOPOLOGY_CODE = {"er": 0, "ws": 1, "ba": 2, "er_trim": 3, "ws_trim": 4, "ba_dpr": 5, "real": 6, "real_er": 7, "real_dpr": 8}
REAL_TOPOLOGIES = ("real", "real_er", "real_dpr")
MODEL_CODE = {"ic": 0, "lt": 1}
RULE_CODE = {"random": 0, "highest_degree": 1}
STREAM_GRAPH = 0
STREAM_CASCADE = 1
STREAM_BOOTSTRAP = 2


class ConfigError(ValueError):
    """Raised for an invalid experiment configuration."""


def _schema(name: str) -> dict:
    return json.loads(resources.files("viral.schemas").joinpath(name).read_text())


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(canonical_json(cfg).encode()).hexdigest()


@dataclass(frozen=True)
class ExperimentConfig:
    raw: dict

    def __getattr__(self, name):  # convenience access to validated fields
        try:
            return self.raw[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def hash(self) -> str:
        return config_hash(self.raw)

    @property
    def engine(self) -> str:
        return self.raw.get("engine", "vectorised")

    @property
    def p_scale(self) -> str:
        return self.raw.get("p_scale", "absolute")

    @property
    def dpr_swaps_per_edge(self) -> int:
        return int(self.raw.get("dpr_swaps_per_edge", 10))

    @property
    def verify(self) -> bool:
        return bool(self.raw.get("verify", False))

    def settings(self) -> list[tuple[str, float]]:
        out = []
        for model in ("ic", "lt"):
            if model in self.raw["models"]:
                key = "p" if model == "ic" else "phi"
                out.extend((model, float(v)) for v in self.raw["models"][model][key])
        return out


def validate_config(cfg: dict) -> ExperimentConfig:
    version = cfg.get("config_schema_version") if isinstance(cfg, dict) else None
    if version not in CONFIG_SCHEMA_VERSIONS:
        raise ConfigError(f"invalid config: unknown config_schema_version {version!r}")
    try:
        jsonschema.validate(cfg, _schema(f"config-{version}.json"))
    except jsonschema.ValidationError as exc:
        raise ConfigError(f"invalid config: {exc.message} at {list(exc.absolute_path)}") from exc
    p_scale = cfg.get("p_scale", "absolute")
    if "ic" in cfg["models"] and p_scale == "absolute" and max(cfg["models"]["ic"]["p"]) > 1:
        raise ConfigError("an absolute transmission probability must lie in [0, 1]")
    uses_real = any(t in REAL_TOPOLOGIES for t in cfg["topologies"])
    if uses_real != ("real_graph" in cfg):
        raise ConfigError("real_graph is required exactly when a real, real_er or real_dpr topology is listed")
    if uses_real and any(t not in REAL_TOPOLOGIES for t in cfg["topologies"]):
        raise ConfigError("real-network topologies cannot be mixed with synthetic ones in one config")
    if max(cfg["seed_counts"]) >= cfg["n"]:
        raise ConfigError("seed count must be smaller than n")
    if cfg["mode"] == "exploratory" and "EXPLORATORY" not in cfg["label"].upper():
        raise ConfigError("an exploratory config must say EXPLORATORY in its label")
    return ExperimentConfig(cfg)


def load_config(path: str | Path) -> ExperimentConfig:
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"config not found: {p}")
    try:
        cfg = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config is not valid JSON: {exc}") from exc
    return validate_config(cfg)


def param_code(x: float) -> int:
    """Stable integer key for a parameter value (millionths)."""
    return int(round(x * 1_000_000))


def graph_rng_seed(master: int, topology: str, replicate: int) -> int:
    ss = np.random.SeedSequence(master, spawn_key=(STREAM_GRAPH, TOPOLOGY_CODE[topology], replicate))
    return int(ss.generate_state(1, dtype=np.uint32)[0])


def cascade_rng(master: int, replicate: int, model: str, param: float, rule: str, count: int) -> np.random.Generator:
    """Cascade stream keyed by replicate and setting but NOT by topology: common random numbers across topologies."""
    ss = np.random.SeedSequence(master, spawn_key=(STREAM_CASCADE, replicate, MODEL_CODE[model], param_code(param), RULE_CODE[rule], count))
    return np.random.Generator(np.random.PCG64(ss))


def bootstrap_rng(master: int) -> np.random.Generator:
    """Stream for the confirmatory bootstrap resampling indices (protocol section 11.3)."""
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(master, spawn_key=(STREAM_BOOTSTRAP,))))
