"""Dispatcher and help text cannot drift: every command appears in usage()."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import task_runner  # noqa: E402

pytestmark = [pytest.mark.unit]


def test_every_command_documented_in_usage():
    text = task_runner.usage()
    for name in task_runner.COMMANDS:
        assert name in text


def test_unknown_command_prints_usage_and_fails():
    assert task_runner.main(["definitely-not-a-command"]) == 2
    assert task_runner.main([]) == 2


def test_exit_code_and_extra_args_propagate(monkeypatch):
    """The wrapper must never turn a red gate green (exit-code passthrough)."""
    captured = {}

    def fake_call(args, cwd=None):
        captured["args"], captured["cwd"] = args, cwd
        return 7

    monkeypatch.setattr(task_runner.subprocess, "call", fake_call)
    assert task_runner.main(["test", "-k", "x"]) == 7
    assert captured["args"][: len(task_runner.COMMANDS["test"][1])] == task_runner.COMMANDS["test"][1]
    assert captured["args"][-2:] == ["-k", "x"]
    assert captured["cwd"] == task_runner.REPO_ROOT
