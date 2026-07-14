import json

import pytest

from funkatlas import logsink

pytestmark = [pytest.mark.unit]

REC = {"ts_utc": "2026-07-14T01:02:03Z", "device_id": "testdevice", "value": 1}


def test_metric_path_partitions_by_device_domain_day(tmp_path):
    path = logsink.metric_path("demo", REC, log_dir=tmp_path)
    assert path == tmp_path / "metrics" / "testdevice" / "demo" / "2026-07-14.jsonl"


def test_missing_ts_utc_rejected(tmp_path):
    with pytest.raises(ValueError):
        logsink.write_metric("demo", {"device_id": "d"}, log_dir=tmp_path)


def test_missing_device_id_rejected(tmp_path):
    with pytest.raises(ValueError):
        logsink.write_metric("demo", {"ts_utc": "2026-07-14T01:02:03Z"}, log_dir=tmp_path)


def test_malformed_ts_rejected(tmp_path):
    bad = {**REC, "ts_utc": "14.07.2026 01:02"}
    with pytest.raises(ValueError):
        logsink.write_metric("demo", bad, log_dir=tmp_path)


def test_lines_are_compact_sorted_and_appended(tmp_path):
    p1 = logsink.write_metric("demo", REC, log_dir=tmp_path)
    p2 = logsink.write_metric("demo", {**REC, "value": 2}, log_dir=tmp_path)
    assert p1 == p2
    lines = p1.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0] == '{"device_id":"testdevice","ts_utc":"2026-07-14T01:02:03Z","value":1}'
    assert json.loads(lines[1])["value"] == 2


def test_event_partitions_by_own_event_ts(tmp_path):
    rec = {**REC, "event_ts": "2026-07-01T22:00:00Z"}
    path = logsink.write_event("demo_events", rec, log_dir=tmp_path)
    assert path.name == "2026-07-01.jsonl"


def test_event_without_event_ts_falls_back_to_ts_utc(tmp_path):
    path = logsink.write_event("demo_events", REC, log_dir=tmp_path)
    assert path.name == "2026-07-14.jsonl"
