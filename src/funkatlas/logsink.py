"""Durable JSONL projection of every metric/event — the second sink besides SQLite.

Layout (becomes frozen zone with the M2 contract; until then: still additive-only):
    logs/metrics/<device_id>/<domain>/<YYYY-MM-DD>.jsonl
    logs/events/<device_id>/<kind>/<YYYY-MM-DD>.jsonl

Rules: append-only · one compact JSON object per line (sorted keys, so lines
are deterministic and diffable) · every record MUST carry ``ts_utc`` (strict
``YYYY-MM-DDTHH:MM:SSZ``) and ``device_id`` · records must already be PII-free
(pseudonymized upstream). Events partition by their OWN timestamp
(``event_ts``) when present, so a re-polled old event lands in its historical
day file.

``log_dir`` resolves lazily through the settings module attribute (honors
``reload_settings()`` in tests — never bind at import time).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from funkatlas import settings as _settings_mod

_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _require(record: dict, key: str) -> str:
    value = record.get(key)
    if not value or not isinstance(value, str):
        raise ValueError(f"record must carry a non-empty '{key}'")
    return value


def _day_from_ts(ts: str) -> str:
    if not _TS_RE.fullmatch(ts):
        raise ValueError(f"ts_utc must be YYYY-MM-DDTHH:MM:SSZ, got: {ts!r}")
    return ts[:10]


def _resolve_log_dir(log_dir: str | Path | None) -> Path:
    return Path(log_dir) if log_dir else Path(_settings_mod.settings.log_dir)


def append_jsonl(path: Path, record: dict) -> None:
    """One compact, deterministic JSON line; creates parent dirs; UTF-8, LF."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")


def metric_path(domain: str, record: dict, log_dir: str | Path | None = None) -> Path:
    day = _day_from_ts(_require(record, "ts_utc"))
    device = _require(record, "device_id")
    return _resolve_log_dir(log_dir) / "metrics" / device / domain / f"{day}.jsonl"


def write_metric(domain: str, record: dict, log_dir: str | Path | None = None) -> Path:
    path = metric_path(domain, record, log_dir)
    append_jsonl(path, record)
    return path


def event_path(kind: str, record: dict, log_dir: str | Path | None = None) -> Path:
    _day_from_ts(_require(record, "ts_utc"))  # ts_utc stays mandatory
    device = _require(record, "device_id")
    day = (record.get("event_ts") or record["ts_utc"])[:10]
    return _resolve_log_dir(log_dir) / "events" / device / kind / f"{day}.jsonl"


def write_event(kind: str, record: dict, log_dir: str | Path | None = None) -> Path:
    path = event_path(kind, record, log_dir)
    append_jsonl(path, record)
    return path
