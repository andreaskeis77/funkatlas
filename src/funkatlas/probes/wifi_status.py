"""WLAN client-interface status via ``netsh wlan show interfaces``.

Encoding discipline (the predecessor's most expensive bug class): the netsh
output encoding VARIES by Windows build/console codepage — observed UTF-8 on
Win11 (2026-07) and CP850 on older builds. Output is therefore captured as raw
BYTES (never ``text=True``) and decoded with a fallback chain
utf-8 -> cp850 -> cp1252.

Locale robustness: field keys are matched by German AND English needles
("Bereich"/"Band", "Kanal"/"Channel", ...); numeric values accept comma AND
dot decimals ("2,4 GHz", "43.3"). Win11 labels the AP as "AP BSSID", older
builds as "BSSID" — matched by suffix.

Privacy (E11): SSID/BSSID land in clear text only in the LOCAL DB/logs (they
are the household's own infrastructure and the key of roaming diagnosis);
repo fixtures are pseudonymized.
"""

from __future__ import annotations

import os
import re
import sqlite3
import subprocess
from collections.abc import Callable
from pathlib import Path

from funkatlas import collect

DOMAIN = "wifi_status"
TABLE = "stg_wifi_status"
COLUMNS = (
    "interface",
    "connected",
    "ssid",
    "bssid",
    "band",
    "channel",
    "signal_pct",
    "rssi_dbm",
    "rx_mbps",
    "tx_mbps",
    "radio_type",
)
collect.register_domain(TABLE, COLUMNS)

Runner = Callable[[list[str]], bytes]

_LINE_RE = re.compile(r"^\s{4}(\S[^:]*?)\s*:\s?(.*)$")

# A wedged WLAN AutoConfig service can hang netsh (typically after
# sleep/resume — exactly the night-run scenario); the cap keeps the
# supervisor's single worker and its heartbeats alive.
SUBPROCESS_TIMEOUT_S = 30


def _default_runner(args: list[str]) -> bytes:
    # Absolute System32 path: a bare name would search the (user-writable)
    # cwd first — binary-planting vector for the autostart task.
    root = os.environ.get("SystemRoot", r"C:\Windows")
    resolved = [os.path.join(root, "System32", args[0] + ".exe"), *args[1:]]
    proc = subprocess.run(  # bytes on purpose, no text=True
        resolved, capture_output=True, timeout=SUBPROCESS_TIMEOUT_S
    )
    return proc.stdout + proc.stderr


def _decode(raw: bytes) -> str:
    for encoding in ("utf-8", "cp850"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("cp1252", errors="replace")


def _num(value: str) -> float | None:
    match = re.search(r"-?\d+(?:[.,]\d+)?", value)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def _int(value: str) -> int | None:
    num = _num(value)
    return int(num) if num is not None else None


def _band(value: str) -> str | None:
    num = _num(value)
    if num is None:
        return None
    return f"{num:g}GHz"


def _empty_interface() -> dict:
    return dict.fromkeys(COLUMNS) | {"connected": 0}


def parse(raw: bytes) -> list[dict]:
    """All interfaces in the output; unknown keys are ignored, missing fields stay None."""
    interfaces: list[dict] = []
    current: dict | None = None
    for line in _decode(raw).splitlines():
        match = _LINE_RE.match(line)
        if not match:
            continue
        key, value = match.group(1).strip(), match.group(2).strip()
        if key == "Name":
            current = _empty_interface()
            current["interface"] = value
            interfaces.append(current)
            continue
        if current is None:
            continue
        if key in ("Status", "State"):
            current["connected"] = int(value.lower() in ("verbunden", "connected"))
        elif key == "SSID":
            current["ssid"] = value or None
        elif key.endswith("BSSID"):
            current["bssid"] = value.lower() or None
        elif key in ("Bereich", "Band"):
            current["band"] = _band(value)
        elif key in ("Kanal", "Channel"):
            current["channel"] = _int(value)
        elif key == "Signal":
            current["signal_pct"] = _int(value)
        elif key == "RSSI":
            current["rssi_dbm"] = _int(value)
        elif "Empfangsrate" in key or "Receive rate" in key:
            current["rx_mbps"] = _num(value)
        elif "bertragungsrate" in key or "Transmit rate" in key:
            # substring skips the leading Ü, which decode fallbacks may mangle
            current["tx_mbps"] = _num(value)
        elif key in ("Funktyp", "Radio type"):
            current["radio_type"] = value or None
    return interfaces


def collect_wifi_status(
    conn: sqlite3.Connection,
    ts: str,
    device_id: str,
    runner: Runner | None = None,
    log_dir: str | Path | None = None,
) -> list[Path]:
    """One measurement: raw insurance + one staging row + JSONL line per interface."""
    run = runner or _default_runner
    raw = run(["netsh", "wlan", "show", "interfaces"])
    text = _decode(raw)
    collect.insert_raw(conn, ts, device_id, DOMAIN, {"text": text})
    paths = []
    for parsed in parse(raw):
        paths.append(collect.twin_write(conn, DOMAIN, TABLE, ts, device_id, parsed, log_dir))
    return paths
