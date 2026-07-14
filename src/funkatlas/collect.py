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
import re
import sqlite3
from pathlib import Path

from funkatlas import logsink

# stg table -> ordered payload columns (ts_utc, device_id are always prepended).
_COLUMNS: dict[str, tuple[str, ...]] = {}


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_RESERVED = ("ts_utc", "device_id")


def register_domain(table: str, columns: tuple[str, ...]) -> None:
    """Additive registration; re-registering with a different shape is a bug.

    Identifiers are validated here because they are later interpolated into
    SQL — this is the explicit trust boundary (registry membership alone would
    let a config-derived name through).
    """
    for name in (table, *columns):
        if not _IDENT_RE.fullmatch(name):
            raise ValueError(f"invalid SQL identifier: {name!r}")
    if any(c in _RESERVED for c in columns):
        raise ValueError(f"columns must not shadow reserved keys {_RESERVED}")
    known = _COLUMNS.get(table)
    if known is not None and known != columns:
        raise ValueError(f"domain {table} already registered with different columns")
    _COLUMNS[table] = columns


def insert_raw(
    conn: sqlite3.Connection, ts: str, device_id: str, source: str, payload: dict
) -> None:
    """Raw insurance: verbatim payload, never transformed.

    Commits immediately — the raw evidence must survive even when the
    subsequent parse/staging step fails (that is its whole purpose).
    """
    conn.execute(
        "INSERT INTO raw_probe (ts_utc, device_id, source, payload_json) VALUES (?, ?, ?, ?)",
        (ts, device_id, source, json.dumps(payload, ensure_ascii=False, sort_keys=True)),
    )
    conn.commit()


def insert_stg(
    conn: sqlite3.Connection, table: str, ts: str, device_id: str, parsed: dict
) -> None:
    cols = _COLUMNS[table]
    # Unknown/reserved keys would make DB row and JSONL record diverge silently
    # (logs == DB is the core invariant) — reject instead of dropping.
    unexpected = set(parsed) - set(cols)
    if unexpected:
        raise ValueError(f"unregistered/reserved keys for {table}: {sorted(unexpected)}")
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
    """DB row and JSONL record from the same dict — logs == DB by construction.

    Per-row commit BEFORE the JSONL append: measurements are independent facts,
    not a transaction. A later failure can therefore never roll back a row
    whose JSONL line already exists (which would silently break logs == DB);
    the residual window is a failing log write after commit, which raises and
    is visible to the caller.
    """
    insert_stg(conn, table, ts, device_id, parsed)
    conn.commit()
    record = {"ts_utc": ts, "device_id": device_id, **parsed}
    return logsink.write_metric(domain, record, log_dir)
