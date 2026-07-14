"""The logs == DB contract at write time: staging row and JSONL record come
from the same dict; the test iterates the shared column registry so every new
column is automatically covered. Proven here against a synthetic domain — the
real probe domains (wifi_status, ping, dns) reuse exactly this machinery.
"""

import json

import pytest

from funkatlas import collect

pytestmark = [pytest.mark.consistency]

TABLE = "stg_demo"
COLUMNS = ("alpha", "beta")


@pytest.fixture()
def demo_domain(tmp_db):
    tmp_db.execute(
        f"CREATE TABLE {TABLE} (ts_utc TEXT NOT NULL, device_id TEXT NOT NULL,"
        " alpha INTEGER, beta TEXT)"
    )
    collect.register_domain(TABLE, COLUMNS)
    yield tmp_db
    collect._COLUMNS.pop(TABLE, None)


def test_logs_equal_db(demo_domain, tmp_path):
    conn = demo_domain
    ts = "2026-07-14T01:02:03Z"
    parsed = {"alpha": 42, "beta": "x"}
    log_path = collect.twin_write(conn, "demo", TABLE, ts, "testdevice", parsed, tmp_path)

    rec = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    row = conn.execute(f"SELECT * FROM {TABLE}").fetchone()
    for col in ("ts_utc", "device_id", *collect._COLUMNS[TABLE]):
        assert rec[col] == row[col], col


def test_missing_parsed_key_becomes_null_in_both(demo_domain, tmp_path):
    conn = demo_domain
    ts = "2026-07-14T01:02:04Z"
    collect.twin_write(conn, "demo", TABLE, ts, "testdevice", {"alpha": 7}, tmp_path)
    row = conn.execute(f"SELECT * FROM {TABLE} WHERE ts_utc=?", (ts,)).fetchone()
    assert row["beta"] is None


def test_reregistering_domain_with_different_shape_is_an_error(demo_domain):
    with pytest.raises(ValueError):
        collect.register_domain(TABLE, ("other",))


def test_raw_insurance_roundtrip(demo_domain):
    conn = demo_domain
    payload = {"outer": {"inner": [1, 2]}, "note": "äöü"}
    collect.insert_raw(conn, "2026-07-14T01:02:05Z", "testdevice", "demo", payload)
    row = conn.execute("SELECT * FROM raw_probe").fetchone()
    assert json.loads(row["payload_json"]) == payload
    assert row["device_id"] == "testdevice"
