"""One measurement round: all probe domains under ONE shared ``ts_utc`` per
device — the correlation key ``(device_id, ts_utc)`` joins the domains.

Graceful degradation: one failing probe must not kill the round or roll back
sibling domains — each domain is isolated, failures land in the returned
summary (``errors``) and in the log. Persistence is per-row-committed inside
the collect core, so DB and JSONL never diverge on a partial failure.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from funkatlas import config, schema
from funkatlas import settings as _settings_mod
from funkatlas.probes import dns as dns_probe
from funkatlas.probes import ping as ping_probe
from funkatlas.probes import wifi_status

log = logging.getLogger("funkatlas.round")


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
    """Returns per-domain row counts plus an ``errors`` map (for logging/tests)."""
    device = device_id or _settings_mod.settings.device_id
    round_ts = ts or schema.now_utc_iso()  # one timestamp shared by every domain
    probe_cfg = cfg or config.probes()

    counts: dict[str, int] = {}
    errors: dict[str, str] = {}

    def _domain(name: str, fn) -> None:
        try:
            counts[name] = len(fn())
        except Exception as exc:  # noqa: BLE001 - one failing probe must not kill the round
            counts[name] = 0
            errors[name] = type(exc).__name__
            log.warning("probe %s failed: %s", name, type(exc).__name__)

    _domain(
        "wifi_status",
        lambda: wifi_status.collect_wifi_status(conn, round_ts, device, wifi_runner, log_dir),
    )
    _domain(
        "ping",
        lambda: ping_probe.collect_ping(conn, round_ts, device, ping_runner, log_dir, probe_cfg),
    )
    _domain(
        "dns",
        lambda: dns_probe.collect_dns(
            conn, round_ts, device, dns_resolver, dns_timer, log_dir, probe_cfg
        ),
    )
    return {"ts_utc": round_ts, "device_id": device, "errors": errors, **counts}
