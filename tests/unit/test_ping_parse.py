"""Harvested regression guards for the predecessor's costliest bug: localized
Windows ping output as raw bytes (cp1252/cp850), never text=True.
"""

import pytest

from funkatlas.probes import ping

pytestmark = [pytest.mark.unit]

GERMAN_OK = (
    "Ping wird ausgeführt für 1.1.1.1 mit 32 Bytes Daten:\r\n"
    "Antwort von 1.1.1.1: Bytes=32 Zeit=10ms TTL=57\r\n"
    "Antwort von 1.1.1.1: Bytes=32 Zeit=12ms TTL=57\r\n"
    "Antwort von 1.1.1.1: Bytes=32 Zeit<1ms TTL=57\r\n"
    "Antwort von 1.1.1.1: Bytes=32 Zeit=13,5ms TTL=57\r\n"
).encode("cp1252")

GERMAN_TIMEOUT = (
    "Ping wird ausgeführt für 10.0.0.1 mit 32 Bytes Daten:\r\n"
    "Zeitüberschreitung der Anforderung.\r\n"
    "Zeitüberschreitung der Anforderung.\r\n"
).encode("cp1252")

ENGLISH_OK = (
    b"Pinging 1.1.1.1 with 32 bytes of data:\r\n"
    b"Reply from 1.1.1.1: bytes=32 time=12.5 ms TTL=57\r\n"
    b"Reply from 1.1.1.1: bytes=32 time=14 ms TTL=57\r\n"
)


def test_german_cp1252_bytes_parse_without_false_loss():
    result = ping.parse(GERMAN_OK, count=4)
    assert result["loss_pct"] == 0.0
    assert result["rtt_ms"] == round((10 + 12 + 1 + 13.5) / 4, 1)
    assert result["jitter_ms"] > 0


def test_sub_millisecond_and_comma_decimals_are_replies():
    result = ping.parse("Zeit<1ms\r\nZeit=2,5ms\r\n".encode("cp1252"), count=2)
    assert result["loss_pct"] == 0.0
    assert result["rtt_ms"] == round((1 + 2.5) / 2, 1)


def test_english_decimal_times():
    result = ping.parse(ENGLISH_OK, count=2)
    assert result["loss_pct"] == 0.0
    assert result["rtt_ms"] == round((12.5 + 14) / 2, 1)


def test_total_timeout_is_100_percent_loss_with_none_rtt():
    result = ping.parse(GERMAN_TIMEOUT, count=4)
    assert result == {"rtt_ms": None, "jitter_ms": None, "loss_pct": 100.0}


def test_partial_loss():
    two_of_four = b"Zeit=10ms\r\nZeit=20ms\r\n"
    result = ping.parse(two_of_four, count=4)
    assert result["loss_pct"] == 50.0
    assert result["rtt_ms"] == 15.0


def test_more_matches_than_count_never_negative_loss():
    result = ping.parse(b"Zeit=1ms\r\nZeit=2ms\r\nZeit=3ms\r\n", count=2)
    assert result["loss_pct"] == 0.0


def test_ping_cmd_windows_flags():
    cmd = ping._ping_cmd("1.1.1.1", 4, 2000)
    assert cmd[0] == "ping"
    assert "1.1.1.1" in cmd
