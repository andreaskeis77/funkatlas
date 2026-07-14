"""YAML config with code defaults.

Defaults live in code so the app runs even when the config/ directory is
absent. YAML is an override, not the source of truth.

Merge contract (unified on purpose — the predecessor mixed key-merge and
wholesale replacement, which silently dropped unlisted defaults from partial
files): every loader key-merges the YAML mapping OVER the code defaults, so a
partial YAML file only overrides the keys it names.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def _config_dir() -> Path:
    override = os.environ.get("FUNKATLAS_CONFIG_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "config"


def _load(name: str) -> dict:
    """Best-effort YAML mapping; anything unreadable/non-dict -> {}."""
    path = _config_dir() / name
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - missing/broken config must never crash
        return {}
    return data if isinstance(data, dict) else {}


def load_merged(name: str, defaults: dict) -> dict:
    """Code defaults key-merged with the optional YAML override (YAML wins per key).

    Merges one level deep: a partial nested section (e.g. ``ping:`` naming only
    ``targets``) keeps the unlisted defaults of that section instead of
    wholesale-replacing it.
    """
    loaded = _load(name)
    merged = {**defaults}
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


# Probe defaults for LaptopAndi (circle A). Per-device overrides via
# config/probes.yaml or FUNKATLAS_CONFIG_DIR; the central per-device config
# distribution arrives with M2.
DEFAULT_PROBES: dict = {
    "ping": {
        "count": 4,
        "timeout_ms": 2000,
        "targets": {"gateway": "192.168.178.1", "internet": "1.1.1.1"},
    },
    "dns": {"names": ["example.com"]},
}


def probes() -> dict:
    return load_merged("probes.yaml", DEFAULT_PROBES)


# Light cadence by default: the probe runs on a work laptop and must not
# influence work or measurement (Grobkonzept risk list).
DEFAULT_SCHEDULER: dict = {"probe_interval_s": 60}


def scheduler() -> dict:
    return load_merged("scheduler.yaml", DEFAULT_SCHEDULER)
