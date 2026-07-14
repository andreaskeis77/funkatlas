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
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def _staged_files() -> list[str] | None:
    """NUL-separated so non-ASCII names arrive unquoted; ACMR includes
    renamed-and-modified files. None on git failure (treated as FAIL).

    Known limitation (documented, not hidden): contents are scanned from the
    WORKING TREE, not the staged blobs — the offline gate and CI re-scan
    everything and remain the backstop.
    """
    proc = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"])
    if proc.returncode != 0:
        print(proc.stderr or "git diff --cached failed")
        return None
    return [f for f in proc.stdout.split("\0") if f.strip()]


def main() -> int:
    listed = _staged_files()
    if listed is None:
        return 1  # git failure is a FAIL, not "nothing staged"
    staged = [f for f in listed if f != BASELINE_FILE]
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
