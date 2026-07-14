import pytest

from funkatlas import settings as settings_mod

pytestmark = [pytest.mark.unit]


def test_env_overrides_default(monkeypatch):
    monkeypatch.setenv("FUNKATLAS_DB_PATH", "x/y.sqlite3")
    s = settings_mod.reload_settings()
    assert s.db_path == "x/y.sqlite3"
    monkeypatch.delenv("FUNKATLAS_DB_PATH")
    settings_mod.reload_settings()


def test_empty_env_value_treated_as_unset(monkeypatch):
    monkeypatch.setenv("FUNKATLAS_LOG_DIR", "   ")
    s = settings_mod.reload_settings()
    assert s.log_dir == "logs"
    monkeypatch.delenv("FUNKATLAS_LOG_DIR")
    settings_mod.reload_settings()


def test_device_id_default_is_a_hostname_digest_not_pii(monkeypatch):
    """Hostnames often embed a person's name — the default must be non-reversible."""
    import re
    import socket

    monkeypatch.delenv("FUNKATLAS_DEVICE_ID", raising=False)
    s = settings_mod.reload_settings()
    assert re.fullmatch(r"dev-[0-9a-f]{8}", s.device_id)
    assert socket.gethostname().lower() not in s.device_id
    settings_mod.reload_settings()


def test_device_id_env_override(monkeypatch):
    monkeypatch.setenv("FUNKATLAS_DEVICE_ID", "laptopandi")
    s = settings_mod.reload_settings()
    assert s.device_id == "laptopandi"
    monkeypatch.delenv("FUNKATLAS_DEVICE_ID")
    settings_mod.reload_settings()
