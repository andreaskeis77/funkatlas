"""Pins the gate's fail-any-step-means-red aggregation and the secret-scan
wiring — the two spots where the iron rule 'gate never weakened' would
regress silently.
"""

import json

import pytest

from funkatlas import gate

pytestmark = [pytest.mark.unit]


def test_main_red_if_any_step_fails_and_all_steps_still_run(monkeypatch, capsys):
    ran = []

    def step(name, ok):
        def _run():
            ran.append(name)
            return ok

        return _run

    monkeypatch.setattr(
        gate, "STEPS", (("a", step("a", True)), ("b", step("b", False)), ("c", step("c", True)))
    )
    assert gate.main() == 1
    assert ran == ["a", "b", "c"]  # a later PASS must not overwrite the FAIL
    assert "GESAMT: FAIL" in capsys.readouterr().out


def test_main_green_only_when_all_pass(monkeypatch, capsys):
    monkeypatch.setattr(gate, "STEPS", (("a", lambda: True), ("b", lambda: True)))
    assert gate.main() == 0
    assert "GESAMT: PASS" in capsys.readouterr().out


def _scan_json(path, hash_):
    return json.dumps(
        {"results": {path: [{"type": "Hex", "hashed_secret": hash_, "line_number": 1}]}}
    )


class _Proc:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def test_secret_scan_fails_on_fresh_secret_and_excludes_baseline(monkeypatch, tmp_path):
    seen_args = {}
    monkeypatch.setattr(gate, "_git_files", lambda: ["a.py", gate.BASELINE_FILE])

    def fake_run(args):
        seen_args["args"] = args
        return _Proc(stdout=_scan_json("a.py", "fresh"))

    monkeypatch.setattr(gate, "_run", fake_run)
    baseline = tmp_path / gate.BASELINE_FILE
    # BOM on purpose: baseline read must be utf-8-sig tolerant
    baseline.write_text(json.dumps({"results": {}}), encoding="utf-8-sig")
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)

    assert gate.step_secret_scan() is False
    assert gate.BASELINE_FILE not in seen_args["args"]


def test_secret_scan_green_when_hash_baselined(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "_git_files", lambda: ["a.py"])
    monkeypatch.setattr(gate, "_run", lambda args: _Proc(stdout=_scan_json("a.py", "known")))
    baseline = tmp_path / gate.BASELINE_FILE
    baseline.write_text(
        json.dumps({"results": {"a.py": [{"hashed_secret": "known"}]}}),  # pragma: allowlist secret
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    assert gate.step_secret_scan() is True


def test_secret_scan_fails_when_git_fails(monkeypatch):
    """git failure must be FAIL — never 'nothing to scan' (fail-safe)."""
    monkeypatch.setattr(gate, "_git_files", lambda: None)
    assert gate.step_secret_scan() is False


def test_git_files_none_on_git_error(monkeypatch):
    monkeypatch.setattr(gate, "_run", lambda args: _Proc(returncode=128))
    assert gate._git_files() is None


def test_git_files_handles_non_ascii_names(monkeypatch):
    monkeypatch.setattr(gate, "_run", lambda args: _Proc(stdout="a.py\0config/geräte.md\0"))
    assert gate._git_files() == ["a.py", "config/geräte.md"]
