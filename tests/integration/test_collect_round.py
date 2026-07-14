"""One fully hermetic probe round: all domains under ONE shared ts_utc, rows in
every staging table, a JSONL projection per domain, logs == DB for ping.
"""

import json

import pytest

from conftest import load_fixture_bytes
from funkatlas import collect
from funkatlas.probes.round import collect_probe_once

pytestmark = [pytest.mark.integration]

CFG = {
    "ping": {"count": 4, "timeout_ms": 2000, "targets": {"gateway": "192.0.2.1", "internet": "192.0.2.2"}},
    "dns": {"names": ["example.com"]},
}


def _fake_wifi(args):
    return load_fixture_bytes("netsh_interfaces_de_connected.bin")


def _fake_ping(args):
    return "Zeit=10ms\r\nZeit=12ms\r\nZeit=11ms\r\nZeit=13ms\r\n".encode("cp1252")


def _fake_resolver(name):
    return [("af", "s", 6, "", ("192.0.2.53", 0))]


def test_full_round_shares_one_ts(tmp_db, tmp_path):
    summary = collect_probe_once(
        tmp_db,
        device_id="testdevice",
        ts="2026-07-14T03:00:00Z",
        log_dir=tmp_path,
        wifi_runner=_fake_wifi,
        ping_runner=_fake_ping,
        dns_resolver=_fake_resolver,
        cfg=CFG,
    )
    assert summary["wifi_status"] == 1
    assert summary["ping"] == 2
    assert summary["dns"] == 1

    for table, expected in (("stg_wifi_status", 1), ("stg_ping", 2), ("stg_dns", 1)):
        rows = tmp_db.execute(f"SELECT DISTINCT ts_utc FROM {table}").fetchall()
        count = tmp_db.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"]
        assert count == expected, table
        assert [r["ts_utc"] for r in rows] == ["2026-07-14T03:00:00Z"], table

    for domain in ("wifi_status", "ping", "dns"):
        files = list((tmp_path / "metrics" / "testdevice" / domain).glob("*.jsonl"))
        assert files, domain


def test_partial_failure_keeps_sibling_domains_consistent(tmp_db, tmp_path):
    """One failing probe must not kill the round, roll back siblings, or let
    DB and JSONL diverge (the M1 review panel's major finding)."""

    def broken_ping(args):
        raise OSError("ping.exe unavailable")

    summary = collect_probe_once(
        tmp_db,
        device_id="testdevice",
        ts="2026-07-14T04:00:00Z",
        log_dir=tmp_path,
        wifi_runner=_fake_wifi,
        ping_runner=broken_ping,
        dns_resolver=_fake_resolver,
        cfg=CFG,
    )
    assert summary["errors"] == {"ping": "OSError"}
    assert summary["wifi_status"] == 1 and summary["ping"] == 0 and summary["dns"] == 1

    # committed DB rows and JSONL lines agree per domain — no divergence
    for table, domain, expected in (
        ("stg_wifi_status", "wifi_status", 1),
        ("stg_ping", "ping", 0),
        ("stg_dns", "dns", 1),
    ):
        db = tmp_db.execute(f"SELECT COUNT(*) c FROM {table}").fetchone()["c"]
        files = list((tmp_path / "metrics" / "testdevice" / domain).glob("*.jsonl"))
        lines = sum(len(f.read_text(encoding="utf-8").splitlines()) for f in files)
        assert db == expected, table
        assert lines == expected, domain

    # raw insurance of the successful domains survived
    raw = tmp_db.execute("SELECT COUNT(*) c FROM raw_probe").fetchone()["c"]
    assert raw == 2  # wifi + dns


def test_ping_logs_equal_db(tmp_db, tmp_path):
    collect_probe_once(
        tmp_db,
        device_id="testdevice",
        ts="2026-07-14T03:00:01Z",
        log_dir=tmp_path,
        wifi_runner=_fake_wifi,
        ping_runner=_fake_ping,
        dns_resolver=_fake_resolver,
        cfg=CFG,
    )
    log = tmp_path / "metrics" / "testdevice" / "ping" / "2026-07-14.jsonl"
    records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    rows = tmp_db.execute("SELECT * FROM stg_ping ORDER BY target").fetchall()
    records.sort(key=lambda r: r["target"])
    for rec, row in zip(records, rows, strict=True):
        for col in ("ts_utc", "device_id", *collect._COLUMNS["stg_ping"]):
            assert rec[col] == row[col], col
