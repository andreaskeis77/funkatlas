import pytest

from funkatlas.status import heartbeat_report, heartbeat_stats

pytestmark = [pytest.mark.unit]


def _seed(conn, stamps):
    for ts in stamps:
        conn.execute(
            "INSERT INTO heartbeat (ts_utc, device_id, component) VALUES (?, 'testdevice', 'probe')",
            (ts,),
        )
    conn.commit()


def test_gap_detection(tmp_db):
    _seed(
        tmp_db,
        ["2026-07-14T01:00:00Z", "2026-07-14T01:01:00Z", "2026-07-14T03:00:00Z"],
    )
    stats = heartbeat_stats(tmp_db, hours=24, now="2026-07-14T03:00:30Z")
    assert stats["count"] == 3
    assert stats["max_gap_s"] == 7140.0  # the 01:01 -> 03:00 sleep gap
    assert stats["tail_gap_s"] == 30.0
    assert stats["last"] == "2026-07-14T03:00:00Z"


def test_no_heartbeats_message(tmp_db):
    report = heartbeat_report(tmp_db, hours=24)
    assert "lief nicht" in report
    assert "Letzte Messrunde: keine" in report


def test_report_shows_last_round(tmp_db):
    tmp_db.execute(
        "INSERT INTO stg_wifi_status (ts_utc, device_id) VALUES ('2026-07-14T05:00:00Z', 'testdevice')"
    )
    tmp_db.commit()
    assert "2026-07-14T05:00:00Z (testdevice)" in heartbeat_report(tmp_db, hours=24)
