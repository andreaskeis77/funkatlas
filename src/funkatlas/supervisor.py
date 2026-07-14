"""Long-running probe loop (harvested pattern, multi-device ready).

Single-DB-writer invariant: APScheduler with a single-worker executor => all
jobs serialize through exactly ONE thread => exactly one SQLite writer
(matches WAL). This is a PER-PROCESS guarantee — never run a second supervisor
against the same DB (see RUNBOOK).

Error isolation: every job runs inside ``_safe`` — a failing tick must not
kill the loop, and a heartbeat row is written in the ``finally`` path, so
liveness is provable in the DB even when collection fails (heartbeat presence
does NOT mean data was collected). Only the exception type name is logged —
messages can carry hosts/credentials.

job_defaults are tuned for laptop sleep/wake: ``coalesce`` merges missed runs,
``max_instances=1`` forbids overlap, ``misfire_grace_time=30`` prevents a job
stampede after resume.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from funkatlas import config, schema
from funkatlas import settings as _settings_mod
from funkatlas.probes.round import collect_probe_once

log = logging.getLogger("funkatlas.supervisor")


def _default_conn():
    conn = schema.connect()
    schema.ensure_schema(conn)
    return conn


class Supervisor:
    def __init__(
        self,
        device_id: str | None = None,
        log_dir=None,
        conn_factory=None,
        probe_cfg: dict | None = None,
        scheduler_cfg: dict | None = None,
        probe_kwargs: dict | None = None,
    ) -> None:
        self.device_id = device_id or _settings_mod.settings.device_id
        self.log_dir = log_dir
        self._conn_factory = conn_factory or _default_conn
        self.probe_cfg = probe_cfg
        self.scheduler_cfg = scheduler_cfg
        self.probe_kwargs = probe_kwargs or {}

    def _heartbeat(self, component: str) -> None:
        try:
            conn = self._conn_factory()
            try:
                conn.execute(
                    "INSERT INTO heartbeat (ts_utc, device_id, component) VALUES (?, ?, ?)",
                    (schema.now_utc_iso(), self.device_id, component),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001 - even a heartbeat failure only logs
            log.warning("heartbeat %s failed: %s", component, type(exc).__name__)

    def _safe(self, component: str, fn) -> None:
        """Run a job; never raise; always heartbeat (proves liveness on failure)."""
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - a failing tick must not kill the loop
            log.warning("job %s failed: %s", component, type(exc).__name__)
        finally:
            self._heartbeat(component)

    def job_probe(self) -> None:
        """One measurement round; fresh connection per job, closed in finally."""
        conn = self._conn_factory()
        try:
            collect_probe_once(
                conn,
                device_id=self.device_id,
                log_dir=self.log_dir,
                cfg=self.probe_cfg,
                **self.probe_kwargs,
            )
        finally:
            conn.close()

    def run(self, max_runtime_s: float | None = None, stop_event: threading.Event | None = None) -> None:
        sched_cfg = self.scheduler_cfg or config.scheduler()
        stop = stop_event or threading.Event()
        scheduler = BackgroundScheduler(
            executors={"default": ThreadPoolExecutor(max_workers=1)},  # one writer
            job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 30},
        )
        scheduler.add_job(
            lambda: self._safe("probe", self.job_probe),
            "interval",
            seconds=int(sched_cfg["probe_interval_s"]),
            next_run_time=datetime.now(),  # immediate first tick
        )
        scheduler.start()
        deadline = time.monotonic() + max_runtime_s if max_runtime_s else None
        try:
            while not stop.is_set():
                if deadline is not None and time.monotonic() >= deadline:
                    break
                time.sleep(0.5)
        finally:
            # wait=True: a job must never outlive run() — an in-flight tick
            # re-resolving settings later could write into the wrong DB
            # (second-writer risk). Jobs are seconds-bounded, so this is cheap.
            scheduler.shutdown(wait=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="funkatlas probe")
    parser.add_argument("--max-runtime", type=float, default=None, help="seconds, bounded run")
    parser.add_argument("--once", action="store_true", help="one round, then exit")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    if args.once:
        conn = _default_conn()
        try:
            summary = collect_probe_once(conn)
            print(summary)
        finally:
            conn.close()
        return 0
    Supervisor().run(max_runtime_s=args.max_runtime)
    return 0
