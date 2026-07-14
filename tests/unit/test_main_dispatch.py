"""CLI dispatch is the entry point of the autostart task and the RUNBOOK smoke
command — argument forwarding must be pinned.
"""

import pytest

import funkatlas.supervisor
from funkatlas.__main__ import main

pytestmark = [pytest.mark.unit]


def _capture(store):
    def fake_main(argv):
        store["argv"] = argv
        return 0

    return fake_main


def test_probe_once_forwards_flag(monkeypatch):
    captured = {}
    monkeypatch.setattr(funkatlas.supervisor, "main", _capture(captured))
    assert main(["probe", "--once"]) == 0
    assert captured["argv"] == ["--once"]


def test_probe_max_runtime_forwarded(monkeypatch):
    captured = {}
    monkeypatch.setattr(funkatlas.supervisor, "main", _capture(captured))
    assert main(["probe", "--max-runtime", "2"]) == 0
    assert captured["argv"] == ["--max-runtime", "2.0"]


def test_heartbeat_command_prints_report(tmp_db, capsys):
    assert main(["heartbeat"]) == 0
    out = capsys.readouterr().out
    assert "Heartbeats" in out or "lief nicht" in out


def test_version_command(capsys):
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip()
