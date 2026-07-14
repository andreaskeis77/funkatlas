"""One measurement round: all probe domains under ONE shared ``ts_utc`` per
device — the correlation key ``(device_id, ts_utc)`` joins the domains.
Commits once at the end; every external boundary is injectable.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from funkatlas import config, schema
from funkatlas import settings as _settings_mod
from funkatlas.probes import dns as dns_probe
from funkatlas.probes import ping as ping_probe
from funkatlas.probes import wifi_status


def collect_probe_once(
    conn: sqlite3.Connection,
    device_id: str | None = None,
    ts: str | None = None,
    log_dir: str | Path | None = None,
    wifi_runner=None,
    ping_runner=None,
    dns_resolver=None,
    dns_timer=None,
    cfg: dict | None = None,
) -> dict:
    """Returns per-domain row counts (for logging/tests)."""
    device = device_id or _settings_mod.settings.device_id
    round_ts = ts or schema.now_utc_iso()  # one timestamp shared by every domain
    probe_cfg = cfg or config.probes()

    wifi_paths = wifi_status.collect_wifi_status(conn, round_ts, device, wifi_runner, log_dir)
    ping_paths = ping_probe.collect_ping(conn, round_ts, device, ping_runner, log_dir, probe_cfg)
    dns_paths = dns_probe.collect_dns(
        conn, round_ts, device, dns_resolver, dns_timer, log_dir, probe_cfg
    )
    conn.commit()
    return {
        "ts_utc": round_ts,
        "device_id": device,
        "wifi_status": len(wifi_paths),
        "ping": len(ping_paths),
        "dns": len(dns_paths),
    }
