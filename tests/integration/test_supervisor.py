"""Supervisor loop hermetically: jobs write data + heartbeat, failures still
heartbeat, and — closing a legacy coverage gap — run() itself terminates on
max_runtime after doing work.
"""

import time

import pytest

from conftest import load_fixture_bytes
from funkatlas import schema
from funkatlas.supervisor import Supervisor

pytestmark = [pytest.mark.integration]

CFG = {
    "ping": {"count": 2, "timeout_ms": 100, "targets": {"internet": "192.0.2.2"}},
    "dns": {"names": ["example.com"]},
}


def _fake_wifi(args):
    return load_fixture_bytes("netsh_interfaces_de_connected.bin")


def _fake_ping(args):
    return b"Zeit=10ms\r\nZeit=12ms\r\n"


def _fake_resolver(name):
    return [("af", "s", 6, "", ("192.0.2.53", 0))]


@pytest.fixture()
def sup(tmp_db, tmp_path):
    def conn_factory():
        return schema.connect()  # env points at the tmp DB (tmp_db fixture)

    return Supervisor(
        device_id="testdevice",
        log_dir=tmp_path,
        conn_factory=conn_factory,
        probe_cfg=CFG,
        scheduler_cfg={"probe_interval_s": 1},
        probe_kwargs={
            "wifi_runner": _fake_wifi,
            "ping_runner": _fake_ping,
            "dns_resolver": _fake_resolver,
        },
    )


def test_job_probe_writes_data_and_heartbeat(sup, tmp_db):
    sup._safe("probe", sup.job_probe)
    assert tmp_db.execute("SELECT COUNT(*) c FROM stg_wifi_status").fetchone()["c"] == 1
    assert tmp_db.execute("SELECT COUNT(*) c FROM stg_ping").fetchone()["c"] == 1
    hb = tmp_db.execute("SELECT * FROM heartbeat").fetchall()
    assert len(hb) == 1
    assert hb[0]["device_id"] == "testdevice"
    assert hb[0]["component"] == "probe"


def test_safe_always_heartbeats_even_on_failure(sup, tmp_db):
    def boom():
        raise RuntimeError("tick failed")

    sup._safe("broken", boom)  # must not raise
    hb = tmp_db.execute("SELECT component FROM heartbeat").fetchall()
    assert [r["component"] for r in hb] == ["broken"]


def test_bounded_run_terminates_and_measures(sup, tmp_db):
    start = time.monotonic()
    sup.run(max_runtime_s=2.5)
    elapsed = time.monotonic() - start
    assert elapsed < 15  # terminated, no hang
    assert tmp_db.execute("SELECT COUNT(*) c FROM heartbeat").fetchone()["c"] >= 1
    assert tmp_db.execute("SELECT COUNT(*) c FROM stg_wifi_status").fetchone()["c"] >= 1
