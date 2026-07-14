"""Process settings: env var > .env file > code default.

Precedence contract: an explicit process env var always wins over a .env file
(``load_dotenv(override=False)`` is critical — it lets tests and the real shell
win over a stray .env). ``FUNKATLAS_DISABLE_DOTENV=1`` skips .env entirely so
hermetic tests never see real credentials. Missing python-dotenv or an
unreadable .env must never crash startup.

Secret fields (none yet; TR-064 credentials arrive with M5) MUST use
``field(repr=False)`` so no log line can ever leak them.
"""

from __future__ import annotations

import hashlib
import os
import socket
from dataclasses import dataclass, replace


def _clean(name: str) -> str | None:
    """Env value, with empty/whitespace-only treated as unset."""
    raw = os.environ.get(name)
    if raw is None:
        return None
    raw = raw.strip()
    return raw or None


def _maybe_load_dotenv() -> None:
    if os.environ.get("FUNKATLAS_DISABLE_DOTENV"):
        return
    try:
        from dotenv import load_dotenv

        # override=False is critical: explicit process env always wins.
        load_dotenv(override=False)
    except Exception:  # noqa: BLE001 - a broken .env must never crash startup
        return


def _default_device_id() -> str:
    """Non-reversible default identity: hostnames often embed a person's name
    (PII), so the default is a hostname digest. Humans who consciously choose a
    name set FUNKATLAS_DEVICE_ID (lowercase slug, [a-z0-9_-])."""
    host = socket.gethostname().lower()
    return "dev-" + hashlib.sha256(host.encode("utf-8")).hexdigest()[:8]


@dataclass(frozen=True)
class Settings:
    db_path: str = os.path.join("data", "funkatlas.sqlite3")
    log_dir: str = "logs"
    device_id: str = "unknown-device"


def _build() -> Settings:
    _maybe_load_dotenv()
    return Settings(
        db_path=_clean("FUNKATLAS_DB_PATH") or os.path.join("data", "funkatlas.sqlite3"),
        log_dir=_clean("FUNKATLAS_LOG_DIR") or "logs",
        device_id=_clean("FUNKATLAS_DEVICE_ID") or _default_device_id(),
    )


settings = _build()


def reload_settings() -> Settings:
    """Rebuild the module singleton from the current environment (tests)."""
    global settings
    settings = _build()
    return settings


def with_overrides(**kwargs) -> Settings:
    return replace(settings, **kwargs)
