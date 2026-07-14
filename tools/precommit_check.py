"""Pre-commit logic: secret-scan + ruff-critical on STAGED files only.

Kept in Python (not inline shell) so it is robust on Windows sh and
unit-testable. Reuses ``funkatlas.gate.new_secrets`` and ``RUFF_CRITICAL`` —
one definition of "a new secret" and one critical-lint selection.
Requires an editable install (``pip install -e .[dev]``).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from funkatlas.gate import BASELINE_FILE, RUFF_CRITICAL, new_secrets  # noqa: E402


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)


def _staged_files() -> list[str]:
    proc = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    return [line for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    staged = [f for f in _staged_files() if f != BASELINE_FILE]
    if not staged:
        return 0

    proc = _run([sys.executable, "-m", "detect_secrets", "scan", *staged])
    if proc.returncode != 0:
        print(proc.stdout or proc.stderr)
        return 1
    scan = json.loads(proc.stdout).get("results", {})
    baseline_path = REPO_ROOT / BASELINE_FILE
    baseline = (
        json.loads(baseline_path.read_text(encoding="utf-8-sig")).get("results", {})
        if baseline_path.exists()
        else {}
    )
    fresh = new_secrets(scan, baseline)
    if fresh:
        print("pre-commit: NEW potential secrets in staged files:")
        for path, findings in fresh.items():
            for f in findings:
                print(f"  {path}: {f.get('type')} (line {f.get('line_number')})")
        return 1

    py_files = [f for f in staged if f.endswith(".py")]
    if py_files:
        proc = _run(
            [sys.executable, "-m", "ruff", "check", "--select", ",".join(RUFF_CRITICAL), *py_files]
        )
        if proc.returncode != 0:
            print(proc.stdout or proc.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
