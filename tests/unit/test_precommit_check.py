"""The pre-commit hook is the only control that stops a secret BEFORE it
enters history — its dispatch logic must be pinned.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import precommit_check  # noqa: E402

pytestmark = [pytest.mark.unit]


class _Proc:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def _scan_json(path, hash_):
    return json.dumps(
        {"results": {path: [{"type": "Hex", "hashed_secret": hash_, "line_number": 1}]}}
    )


def _with_baseline(monkeypatch, tmp_path, results):
    baseline = tmp_path / ".secrets.baseline"
    baseline.write_text(json.dumps({"results": results}), encoding="utf-8")
    monkeypatch.setattr(precommit_check, "REPO_ROOT", tmp_path)


def test_fresh_secret_blocks_commit(monkeypatch, tmp_path):
    monkeypatch.setattr(precommit_check, "_staged_files", lambda: ["a.py"])
    monkeypatch.setattr(
        precommit_check, "_run", lambda args: _Proc(stdout=_scan_json("a.py", "fresh"))
    )
    _with_baseline(monkeypatch, tmp_path, {})
    assert precommit_check.main() == 1


def test_baselined_secret_passes_and_ruff_runs_only_on_py(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(precommit_check, "_staged_files", lambda: ["a.py", "notes.md"])

    def fake_run(args):
        calls.append(args)
        if "detect_secrets" in " ".join(args):
            return _Proc(stdout=_scan_json("a.py", "known"))
        return _Proc()  # ruff green

    monkeypatch.setattr(precommit_check, "_run", fake_run)
    _with_baseline(monkeypatch, tmp_path, {"a.py": [{"hashed_secret": "known"}]})  # pragma: allowlist secret
    assert precommit_check.main() == 0
    ruff_call = next(c for c in calls if "ruff" in " ".join(c))
    assert "a.py" in ruff_call and "notes.md" not in ruff_call


def test_baseline_file_itself_excluded_from_scan(monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(
        precommit_check, "_staged_files", lambda: [precommit_check.BASELINE_FILE]
    )
    monkeypatch.setattr(
        precommit_check, "_run", lambda args: seen.setdefault("args", args) or _Proc()
    )
    _with_baseline(monkeypatch, tmp_path, {})
    assert precommit_check.main() == 0
    assert "args" not in seen  # nothing left to scan -> no subprocess at all


def test_no_staged_files_is_clean(monkeypatch):
    monkeypatch.setattr(precommit_check, "_staged_files", lambda: [])
    assert precommit_check.main() == 0


def test_git_failure_blocks_commit(monkeypatch):
    monkeypatch.setattr(precommit_check, "_staged_files", lambda: None)
    assert precommit_check.main() == 1


def test_red_ruff_blocks_commit(monkeypatch, tmp_path):
    monkeypatch.setattr(precommit_check, "_staged_files", lambda: ["a.py"])

    def fake_run(args):
        if "detect_secrets" in " ".join(args):
            return _Proc(stdout=json.dumps({"results": {}}))
        return _Proc(returncode=1)

    monkeypatch.setattr(precommit_check, "_run", fake_run)
    _with_baseline(monkeypatch, tmp_path, {})
    assert precommit_check.main() == 1
