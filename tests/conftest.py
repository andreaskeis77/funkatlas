"""Shared test fixtures — hermetic by construction.

``FUNKATLAS_DISABLE_DOTENV`` is set BEFORE importing any funkatlas module so a
stray .env with real credentials can never enter a test run. This ordering is
load-bearing: settings resolution happens at import time.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("FUNKATLAS_DISABLE_DOTENV", "1")

import pytest  # noqa: E402

from funkatlas import schema, settings as settings_mod  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """Fresh SQLite in a pytest tmp dir; the live DB is never touched."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("FUNKATLAS_DB_PATH", str(db_path))
    monkeypatch.setenv("FUNKATLAS_DEVICE_ID", "testdevice")
    settings_mod.reload_settings()
    conn = schema.connect()
    schema.ensure_schema(conn)
    yield conn
    conn.close()
    # undo the env patches BEFORE rebuilding the singleton — otherwise the
    # reload re-reads the tmp values and later tests see a stale deleted path
    monkeypatch.undo()
    settings_mod.reload_settings()


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_fixture_bytes(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()
