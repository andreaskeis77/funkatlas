import json

import pytest

from conftest import load_fixture_bytes
from funkatlas import collect
from funkatlas.probes import wifi_status

pytestmark = [pytest.mark.integration]

TS = "2026-07-14T02:00:00Z"


def _runner(name):
    def run(args):
        assert args[:2] == ["netsh", "wlan"]
        return load_fixture_bytes(name)

    return run


def test_collect_writes_raw_stg_and_jsonl(tmp_db, tmp_path):
    paths = wifi_status.collect_wifi_status(
        tmp_db, TS, "testdevice", _runner("netsh_interfaces_de_connected.bin"), tmp_path
    )
    assert len(paths) == 1

    raw = tmp_db.execute("SELECT * FROM raw_probe").fetchone()
    assert raw["source"] == "wifi_status"
    assert "REDACTED_SSID" in json.loads(raw["payload_json"])["text"]

    row = tmp_db.execute("SELECT * FROM stg_wifi_status").fetchone()
    assert row["ts_utc"] == TS
    assert row["device_id"] == "testdevice"
    assert row["signal_pct"] == 59

    rec = json.loads(paths[0].read_text(encoding="utf-8").splitlines()[0])
    for col in ("ts_utc", "device_id", *collect._COLUMNS["stg_wifi_status"]):
        assert rec[col] == row[col], col


def test_collect_disconnected_still_writes_row(tmp_db, tmp_path):
    wifi_status.collect_wifi_status(
        tmp_db, TS, "testdevice", _runner("netsh_interfaces_de_disconnected.bin"), tmp_path
    )
    row = tmp_db.execute("SELECT * FROM stg_wifi_status").fetchone()
    assert row["connected"] == 0
    assert row["ssid"] is None
