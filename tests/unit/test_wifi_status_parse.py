"""Parser contract against recorded/synthetic netsh output (DE + EN, UTF-8 +
CP850). Golden values of the DE fixture come from a real capture on LaptopAndi
(2026-07-14, sanitized): 2.4 GHz / channel 6 / 59% — the B2 finding live.
"""

import pytest

from conftest import load_fixture_bytes
from funkatlas.probes import wifi_status

pytestmark = [pytest.mark.unit]


def test_german_utf8_connected_golden_values():
    rows = wifi_status.parse(load_fixture_bytes("netsh_interfaces_de_connected.bin"))
    assert len(rows) == 1
    row = rows[0]
    assert row["interface"] == "WLAN"
    assert row["connected"] == 1
    assert row["ssid"] == "REDACTED_SSID"
    assert row["bssid"] == "aa:bb:cc:00:00:01"
    assert row["band"] == "2.4GHz"
    assert row["channel"] == 6
    assert row["signal_pct"] == 59
    assert row["rssi_dbm"] == -69
    assert row["rx_mbps"] == 43.3
    assert row["tx_mbps"] == 52.0
    assert row["radio_type"] == "802.11n"


def test_german_cp850_decodes_via_fallback_to_same_values():
    """The encoding varies by Windows build — CP850 bytes must parse identically."""
    utf8 = wifi_status.parse(load_fixture_bytes("netsh_interfaces_de_connected.bin"))
    cp850 = wifi_status.parse(load_fixture_bytes("netsh_interfaces_de_connected_cp850.bin"))
    assert cp850 == utf8


def test_english_connected():
    rows = wifi_status.parse(load_fixture_bytes("netsh_interfaces_en_connected.bin"))
    assert len(rows) == 1
    row = rows[0]
    assert row["connected"] == 1
    assert row["band"] == "5GHz"
    assert row["channel"] == 52
    assert row["signal_pct"] == 84
    assert row["rx_mbps"] == 866.7
    assert row["radio_type"] == "802.11ac"
    assert row["rssi_dbm"] is None  # not present in this build's output


def test_german_disconnected_degrades_to_none_fields():
    rows = wifi_status.parse(load_fixture_bytes("netsh_interfaces_de_disconnected.bin"))
    assert len(rows) == 1
    row = rows[0]
    assert row["connected"] == 0
    assert row["ssid"] is None
    assert row["band"] is None
    assert row["channel"] is None


def test_garbage_output_yields_no_interfaces():
    assert wifi_status.parse(b"") == []
    assert wifi_status.parse(b"\xff\xfe garbage \x00") == []
