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

TOPOLOGY_CODE = {"er": 0, "ws": 1, "ba": 2}
MODEL_CODE = {"ic": 0, "lt": 1}
RULE_CODE = {"random": 0, "highest_degree": 1}
STREAM_GRAPH = 0
STREAM_CASCADE = 1


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
    try:
        jsonschema.validate(cfg, _schema("config-1.0.0.json"))
    except jsonschema.ValidationError as exc:
        raise ConfigError(f"invalid config: {exc.message} at {list(exc.absolute_path)}") from exc
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
