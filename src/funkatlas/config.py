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
    """Code defaults key-merged with the optional YAML override (YAML wins per key)."""
    return {**defaults, **_load(name)}
