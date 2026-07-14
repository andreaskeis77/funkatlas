"""Collection-round core: one round = one shared ``ts_utc`` per device.

The twin-write is the mechanism behind the ``logs == DB`` guarantee: staging
row and JSONL record are produced from the SAME parsed dict, and ``_COLUMNS``
is the single source of field names per domain — the consistency test iterates
it, so every new column is automatically covered.

Probe modules register their domain additively via ``register_domain`` (table
DDL stays in ``schema.py``; registration here only declares the payload column
order for insert + log identity).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from funkatlas import logsink

# stg table -> ordered payload columns (ts_utc, device_id are always prepended).
_COLUMNS: dict[str, tuple[str, ...]] = {}


def register_domain(table: str, columns: tuple[str, ...]) -> None:
    """Additive registration; re-registering with a different shape is a bug."""
    known = _COLUMNS.get(table)
    if known is not None and known != columns:
        raise ValueError(f"domain {table} already registered with different columns")
    _COLUMNS[table] = columns


def insert_raw(
    conn: sqlite3.Connection, ts: str, device_id: str, source: str, payload: dict
) -> None:
    """Raw insurance: verbatim payload, never transformed."""
    conn.execute(
        "INSERT INTO raw_probe (ts_utc, device_id, source, payload_json) VALUES (?, ?, ?, ?)",
        (ts, device_id, source, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
    )


def insert_stg(
    conn: sqlite3.Connection, table: str, ts: str, device_id: str, parsed: dict
) -> None:
    cols = _COLUMNS[table]
    names = ("ts_utc", "device_id", *cols)
    placeholders = ", ".join("?" for _ in names)
    values = (ts, device_id, *(parsed.get(c) for c in cols))
    conn.execute(
        f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})", values
    )


def twin_write(
    conn: sqlite3.Connection,
    domain: str,
    table: str,
    ts: str,
    device_id: str,
    parsed: dict,
    log_dir: str | Path | None = None,
) -> Path:
    """DB row and JSONL record from the same dict — logs == DB by construction."""
    insert_stg(conn, table, ts, device_id, parsed)
    record = {"ts_utc": ts, "device_id": device_id, **parsed}
    return logsink.write_metric(domain, record, log_dir)
