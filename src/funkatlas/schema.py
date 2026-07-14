"""SQLite storage: WAL connection factory + additive schema migrations.

Mechanism (harvested from the predecessor, proven): ``ensure_schema`` is
idempotent and safe to call on every process start and every job tick — it
creates only what's missing (guarded by ``table_exists``/``index_exists``),
records each schema version exactly once in ``migrations``, and NEVER drops or
alters existing tables. New tables/indexes = new ``_CREATE_*_SQL`` + registry
entry + ``SCHEMA_VERSION`` bump. Column additions to existing tables need an
explicit version-gated ``ALTER TABLE`` step (the guard alone cannot do it).

Every timestamp is ``now_utc_iso()``: strict UTC ISO-8601 with trailing Z and a
fixed field layout, so lexicographic ordering equals chronological ordering
(fixes the predecessor's predecessor's mixed-format sort fragility).

Multi-device from day one (plan decision D1): every fact table carries a
``device_id`` column; correlation key per collection round is
``(device_id, ts_utc)``.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime

from funkatlas import settings as _settings_mod

SCHEMA_VERSION = 1

# Subset a future backup count-probe verifies after restore (keep in sync on rename).
CORE_TABLES = ("raw_probe", "heartbeat")


def now_utc_iso() -> str:
    """Strict sortable UTC timestamp: YYYY-MM-DDTHH:MM:SSZ (second granularity)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(db_path: str | None = None) -> sqlite3.Connection:
    """Open SQLite in WAL mode (one writer + many readers, online-backup capable).

    Resolves the default path lazily through the settings module attribute so
    tests calling ``reload_settings()`` are honored — do NOT "optimize" this
    into ``from funkatlas.settings import settings`` (import-time binding was a
    real predecessor bug: reloads were silently ignored).
    """
    path = db_path or _settings_mod.settings.db_path  # dynamic: honors reload_settings()
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def index_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,)
    ).fetchone()
    return row is not None


_CREATE_MIGRATIONS_SQL = """
CREATE TABLE migrations (
    version     INTEGER NOT NULL,
    applied_at  TEXT NOT NULL
)
"""

_CREATE_META_SQL = """
CREATE TABLE meta (
    key   TEXT PRIMARY KEY,
    value TEXT
)
"""

# Raw insurance layer: verbatim probe payloads, never transformed.
_CREATE_RAW_PROBE_SQL = """
CREATE TABLE raw_probe (
    ts_utc       TEXT NOT NULL,
    device_id    TEXT NOT NULL,
    source       TEXT NOT NULL,
    payload_json TEXT NOT NULL
)
"""

# Liveness: written by the supervisor's safe-job wrapper in its finally block —
# a heartbeat row proves the loop is alive even when collection fails.
_CREATE_HEARTBEAT_SQL = """
CREATE TABLE heartbeat (
    ts_utc    TEXT NOT NULL,
    device_id TEXT NOT NULL,
    component TEXT NOT NULL
)
"""

_FACT_TABLES: tuple[tuple[str, str], ...] = (
    ("raw_probe", _CREATE_RAW_PROBE_SQL),
    ("heartbeat", _CREATE_HEARTBEAT_SQL),
)

_CREATE_INDEXES: tuple[tuple[str, str], ...] = (
    ("idx_raw_probe_dev_ts", "CREATE INDEX idx_raw_probe_dev_ts ON raw_probe(device_id, ts_utc)"),
    ("idx_heartbeat_dev_ts", "CREATE INDEX idx_heartbeat_dev_ts ON heartbeat(device_id, ts_utc)"),
)


def record_migration(conn: sqlite3.Connection, version: int) -> None:
    """Record a schema version exactly once."""
    row = conn.execute("SELECT 1 FROM migrations WHERE version=?", (version,)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO migrations (version, applied_at) VALUES (?, ?)",
            (version, now_utc_iso()),
        )


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotent: adds what's missing; never drops or alters existing tables."""
    if not table_exists(conn, "migrations"):
        conn.execute(_CREATE_MIGRATIONS_SQL)
        conn.execute("CREATE UNIQUE INDEX idx_migrations_version ON migrations(version)")
    if not table_exists(conn, "meta"):
        conn.execute(_CREATE_META_SQL)
    for name, sql in _FACT_TABLES:
        if not table_exists(conn, name):
            conn.execute(sql)
    for name, sql in _CREATE_INDEXES:
        if not index_exists(conn, name):
            conn.execute(sql)
    record_migration(conn, SCHEMA_VERSION)
    conn.commit()
