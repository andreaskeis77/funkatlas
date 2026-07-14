"""Heartbeat visibility: gaps in the heartbeat trail = gaps in measurement
(sleep, crash, logoff). The morning-after check for night runs.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from funkatlas import schema

_FMT = "%Y-%m-%dT%H:%M:%SZ"


def heartbeat_stats(conn: sqlite3.Connection, hours: int = 24, now: str | None = None) -> dict:
    """Last heartbeat, count and largest gap (seconds) within the window."""
    now_ts = now or schema.now_utc_iso()
    now_dt = datetime.strptime(now_ts, _FMT).replace(tzinfo=UTC)
    since = datetime.fromtimestamp(now_dt.timestamp() - hours * 3600, tz=UTC).strftime(_FMT)
    rows = conn.execute(
        "SELECT ts_utc FROM heartbeat WHERE ts_utc >= ? ORDER BY ts_utc", (since,)
    ).fetchall()
    stamps = [datetime.strptime(r["ts_utc"], _FMT).replace(tzinfo=UTC) for r in rows]
    if not stamps:
        return {"count": 0, "last": None, "max_gap_s": None, "tail_gap_s": None}
    gaps = [(b - a).total_seconds() for a, b in zip(stamps, stamps[1:], strict=False)]
    return {
        "count": len(stamps),
        "last": stamps[-1].strftime(_FMT),
        "max_gap_s": round(max(gaps), 1) if gaps else 0.0,
        "tail_gap_s": round((now_dt - stamps[-1]).total_seconds(), 1),
    }


def last_round(conn: sqlite3.Connection) -> dict | None:
    """Timestamp/device of the newest measurement round (from wifi_status)."""
    row = conn.execute(
        "SELECT ts_utc, device_id FROM stg_wifi_status ORDER BY ts_utc DESC LIMIT 1"
    ).fetchone()
    return {"ts_utc": row["ts_utc"], "device_id": row["device_id"]} if row else None


def heartbeat_report(conn: sqlite3.Connection, hours: int = 24) -> str:
    # ASCII-safe on purpose: console codepages vary (OEM vs UTF-8).
    stats = heartbeat_stats(conn, hours=hours)
    round_ = last_round(conn)
    round_line = (
        f"Letzte Messrunde: {round_['ts_utc']} ({round_['device_id']})"
        if round_
        else "Letzte Messrunde: keine"
    )
    if stats["count"] == 0:
        return (
            f"Keine Heartbeats in den letzten {hours} h - Dauerlauf (Supervisor) lief nicht.\n"
            + round_line
        )
    return (
        f"Heartbeats letzte {hours} h: {stats['count']}\n"
        f"Letzter: {stats['last']} (vor {stats['tail_gap_s']} s)\n"
        f"Groesste Luecke: {stats['max_gap_s']} s\n" + round_line
    )
