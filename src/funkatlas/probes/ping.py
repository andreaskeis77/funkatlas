"""System-ping probe -> rtt/jitter/loss. Harvested — encodes the predecessor's
most expensive bug fix: NEVER use ``text=True`` on a localized Windows CLI
(cp1252 decode fails -> false 100% loss). Output is read as raw BYTES and
parsed with a bytes regex matching English/German per-reply times, ``<1ms``
sub-millisecond replies and comma decimals.

Targets come from config (``config.probes()``) — fixes the predecessor's
drift where ``probes.yaml`` existed but was ignored by the code.
"""

from __future__ import annotations

import math
import os
import platform
import re
import sqlite3
import subprocess
from collections.abc import Callable
from pathlib import Path

from funkatlas import collect, config

DOMAIN = "ping"
TABLE = "stg_ping"
COLUMNS = ("target", "host", "rtt_ms", "jitter_ms", "loss_pct")
collect.register_domain(TABLE, COLUMNS)

Runner = Callable[[list[str]], bytes]

# Matches per-reply time in English/German output, '<1ms', comma decimals.
_TIME_RE = re.compile(rb"(?:time|zeit)\s*[=<]\s*(\d+(?:[.,]\d+)?)\s*ms", re.IGNORECASE)

# Hard child-process cap: a stalled ping.exe must never block the supervisor's
# single worker thread (which would also stop heartbeats). TimeoutExpired
# propagates into the round's per-domain isolation.
SUBPROCESS_TIMEOUT_S = 90

# Sanity clamps for config-derived values (defense in depth).
MAX_COUNT = 20
MIN_TIMEOUT_MS, MAX_TIMEOUT_MS = 100, 10_000


def _system32(exe: str) -> str:
    """Absolute path: bare names would search the (user-writable) cwd first —
    a binary-planting vector for the autostart task."""
    root = os.environ.get("SystemRoot", r"C:\Windows")
    return os.path.join(root, "System32", exe)


def _ping_cmd(host: str, count: int, timeout_ms: int) -> list[str]:
    host = str(host)
    if host.startswith("-"):
        raise ValueError(f"ping target must not start with '-': {host!r}")
    if platform.system() == "Windows":
        return [_system32("ping.exe"), "-n", str(count), "-w", str(timeout_ms), host]
    return ["ping", "-c", str(count), "-W", str(math.ceil(timeout_ms / 1000)), host]


def _default_runner(args: list[str]) -> bytes:
    # capture_output WITHOUT text=True -> raw bytes (localized codepages vary)
    proc = subprocess.run(args, capture_output=True, timeout=SUBPROCESS_TIMEOUT_S)
    return proc.stdout + proc.stderr


def parse(output: bytes, count: int) -> dict:
    """Pure: reply times from raw bytes -> {rtt_ms, jitter_ms, loss_pct}.

    ``count`` must equal the number of requests actually sent — loss is
    computed as count minus matched replies.
    """
    times = [float(m.group(1).replace(b",", b".")) for m in _TIME_RE.finditer(output)]
    times = times[:count]
    if not times:
        return {"rtt_ms": None, "jitter_ms": None, "loss_pct": 100.0}
    rtt = sum(times) / len(times)
    diffs = [abs(b - a) for a, b in zip(times, times[1:], strict=False)]
    jitter = sum(diffs) / len(diffs) if diffs else 0.0
    loss = 100.0 * (count - len(times)) / count
    return {"rtt_ms": round(rtt, 1), "jitter_ms": round(jitter, 1), "loss_pct": round(loss, 1)}


def ping(host: str, count: int, timeout_ms: int, runner: Runner | None = None) -> dict:
    run = runner or _default_runner
    output = run(_ping_cmd(host, count, timeout_ms))
    return parse(output, count)


def _clamped(ping_cfg: dict) -> tuple[int, int]:
    count = max(1, min(int(ping_cfg["count"]), MAX_COUNT))
    timeout_ms = max(MIN_TIMEOUT_MS, min(int(ping_cfg["timeout_ms"]), MAX_TIMEOUT_MS))
    return count, timeout_ms


def collect_ping(
    conn: sqlite3.Connection,
    ts: str,
    device_id: str,
    runner: Runner | None = None,
    log_dir: str | Path | None = None,
    cfg: dict | None = None,
) -> list[Path]:
    """One row per configured target under the shared round timestamp."""
    ping_cfg = (cfg or config.probes())["ping"]
    count, timeout_ms = _clamped(ping_cfg)
    run = runner or _default_runner
    paths = []
    for label, host in ping_cfg["targets"].items():
        output = run(_ping_cmd(host, count, timeout_ms))
        # Raw insurance is the RAW output — a parser gap (unknown locale) must
        # stay re-parseable after the fact; the parsed dict alone is not that.
        collect.insert_raw(
            conn, ts, device_id, DOMAIN,
            {"target": label, "host": host, "text": output.decode("cp850", errors="replace")},
        )
        parsed = {"target": label, "host": host, **parse(output, count)}
        paths.append(collect.twin_write(conn, DOMAIN, TABLE, ts, device_id, parsed, log_dir))
    return paths
