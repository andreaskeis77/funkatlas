"""The merge gate — one command, green or red. The gate is never weakened to
make speed (iron rule).

Steps:
  (1) compileall over src/tests/tools
  (2) ruff restricted to critical classes (syntax / undefined-name only)
  (3) pytest, offline by default (``-m 'not network'``)
  (4) secret-scan vs the committed baseline (never mutates the baseline;
      a new secret is always a hard failure, not a baseline append)

A live-smoke step returns in M2 when the ingest API exists (plan decision D3).

Path normalization: baseline result keys are compared as POSIX paths
(``as_posix``), so the gate behaves identically on Windows and Linux — the
predecessor's baseline was OS-path-separator coupled.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path, PurePath

REPO_ROOT = Path(__file__).resolve().parents[2]
RUFF_CRITICAL = ["E9", "F63", "F7", "F82"]  # syntax / undefined-name classes only
BASELINE_FILE = ".secrets.baseline"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    # ruff/detect-secrets emit UTF-8 regardless of the Windows ANSI codepage —
    # decoding must never crash the gate.
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def _git_files() -> list[str] | None:
    """Files git would consider (tracked + untracked, respecting .gitignore) —
    so secrets in not-yet-committed files are caught before they enter history.

    NUL-separated (-z) so non-ASCII names arrive unquoted. Returns ``None`` on
    git failure — callers must treat that as FAIL, never as "nothing to scan"
    (fail-safe, not fail-open).
    """
    proc = _run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    if proc.returncode != 0:
        print(proc.stderr or "git ls-files failed")
        return None
    return [f for f in proc.stdout.split("\0") if f.strip()]


def step_compile() -> bool:
    proc = _run([sys.executable, "-m", "compileall", "-q", "src", "tests", "tools"])
    if proc.returncode != 0:
        print(proc.stdout or proc.stderr)
    return proc.returncode == 0


def step_ruff_critical() -> bool:
    proc = _run(
        [sys.executable, "-m", "ruff", "check", "--select", ",".join(RUFF_CRITICAL), "."]
    )
    if proc.returncode != 0:
        print(proc.stdout or proc.stderr)
    return proc.returncode == 0


def step_pytest() -> bool:
    proc = _run([sys.executable, "-m", "pytest", "-m", "not network", "-q"])
    tail = "\n".join((proc.stdout or "").splitlines()[-8:])
    print(tail)
    return proc.returncode == 0


def _posix(path: str) -> str:
    return PurePath(path.replace("\\", "/")).as_posix()


def new_secrets(scan_results: dict, baseline_results: dict) -> dict:
    """Findings in ``scan_results`` absent from ``baseline_results``.

    Pure and unit-tested: matching is per file (POSIX-normalized path) by
    ``hashed_secret``. An empty dict is the only clean result.
    """
    baseline: dict[str, set[str]] = {}
    for path, findings in baseline_results.items():
        baseline.setdefault(_posix(path), set()).update(
            f["hashed_secret"] for f in findings
        )
    fresh: dict[str, list[dict]] = {}
    for path, findings in scan_results.items():
        known = baseline.get(_posix(path), set())
        new = [f for f in findings if f["hashed_secret"] not in known]
        if new:
            fresh[_posix(path)] = new
    return fresh


def step_secret_scan() -> bool:
    listed = _git_files()
    if listed is None:
        return False  # git failure is a FAIL, not an empty scan
    files = [f for f in listed if f != BASELINE_FILE]
    if not files:
        return True
    proc = _run([sys.executable, "-m", "detect_secrets", "scan", *files])
    if proc.returncode != 0:
        print(proc.stdout or proc.stderr)
        return False
    scan = json.loads(proc.stdout).get("results", {})
    baseline_path = REPO_ROOT / BASELINE_FILE
    if baseline_path.exists():
        # utf-8-sig tolerates a BOM if some tool wrote one (Windows editors do).
        baseline = json.loads(baseline_path.read_text(encoding="utf-8-sig")).get("results", {})
    else:
        baseline = {}
    fresh = new_secrets(scan, baseline)
    if fresh:
        print("NEW potential secrets (not in baseline):")
        for path, findings in fresh.items():
            for f in findings:
                print(f"  {path}: {f.get('type')} (line {f.get('line_number')})")
        return False
    return True


STEPS = (
    ("compile", step_compile),
    ("ruff-critical", step_ruff_critical),
    ("pytest", step_pytest),
    ("secret-scan", step_secret_scan),
)


def main() -> int:
    ok = True
    for name, step in STEPS:
        passed = step()
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed
    print(f"GESAMT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
