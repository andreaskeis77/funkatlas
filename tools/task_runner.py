"""Canonical command surface — terminal, VS Code tasks and CI all dispatch
through here, so no second, divergent workflow exists. Subcommands run with the
same Python that launched the runner (sys.executable), never a bare ``python``
lookup, to avoid interpreter drift.

USAGE is generated from COMMANDS, so dispatcher and help cannot drift (the
predecessor's usage text silently omitted two commands).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PY = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[1]

COMMANDS: dict[str, tuple[str, list[str]]] = {
    "gate": ("run the quality gate (compile, ruff-critical, pytest, secret-scan)",
             [PY, "-m", "funkatlas.gate"]),
    "test": ("full offline test suite", [PY, "-m", "pytest", "-m", "not network", "-q"]),
    "test-unit": ("unit tests only", [PY, "-m", "pytest", "-m", "unit", "-q"]),
    "test-integration": ("integration tests only",
                         [PY, "-m", "pytest", "-m", "integration", "-q"]),
    "test-consistency": ("consistency tests only",
                         [PY, "-m", "pytest", "-m", "consistency", "-q"]),
    "version": ("print version", [PY, "-m", "funkatlas", "version"]),
}


def usage() -> str:
    lines = ["usage: funkatlas.cmd <command> [args...]", "", "commands:"]
    for name, (desc, _) in COMMANDS.items():
        lines.append(f"  {name:<18} {desc}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(usage())
        return 2
    _, base = COMMANDS[argv[0]]
    # cwd pinned: the wrapper is callable from anywhere, pytest must resolve
    # THIS project's rootdir.
    return subprocess.call([*base, *argv[1:]], cwd=REPO_ROOT)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
