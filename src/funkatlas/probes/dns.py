"""DNS resolve-time probe: how long does the system resolver take?

Resolver and timer are injectable so tests run hermetically (no network in the
gate); the default resolver is ``socket.getaddrinfo`` against the system DNS.
"""

from __future__ import annotations

import sqlite3
import socket
import time
from collections.abc import Callable
from pathlib import Path

from funkatlas import collect, config

DOMAIN = "dns"
TABLE = "stg_dns"
COLUMNS = ("name", "ok", "resolve_ms", "address_count")
collect.register_domain(TABLE, COLUMNS)

Resolver = Callable[[str], list]
Timer = Callable[[], float]


def _default_resolver(name: str) -> list:
    return socket.getaddrinfo(name, None)


def resolve(name: str, resolver: Resolver | None = None, timer: Timer | None = None) -> dict:
    res = resolver or _default_resolver
    clock = timer or time.perf_counter
    start = clock()
    try:
        addresses = res(name)
    except OSError:
        return {"name": name, "ok": 0, "resolve_ms": None, "address_count": None}
    elapsed_ms = (clock() - start) * 1000.0
    return {
        "name": name,
        "ok": 1,
        "resolve_ms": round(elapsed_ms, 1),
        "address_count": len(addresses),
    }


def collect_dns(
    conn: sqlite3.Connection,
    ts: str,
    device_id: str,
    resolver: Resolver | None = None,
    timer: Timer | None = None,
    log_dir: str | Path | None = None,
    cfg: dict | None = None,
) -> list[Path]:
    names = (cfg or config.probes())["dns"]["names"]
    paths = []
    for name in names:
        parsed = resolve(name, resolver, timer)
        collect.insert_raw(conn, ts, device_id, DOMAIN, parsed)
        paths.append(collect.twin_write(conn, DOMAIN, TABLE, ts, device_id, parsed, log_dir))
    return paths
