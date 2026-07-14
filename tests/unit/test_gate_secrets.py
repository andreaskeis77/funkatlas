"""Pins the exact semantics of funkatlas.gate.new_secrets: per-file matching by
hashed_secret over POSIX-normalized paths; empty dict is the only clean result.
"""

import pytest

from funkatlas.gate import new_secrets

pytestmark = [pytest.mark.unit]


def _f(hash_):
    return {"type": "Hex High Entropy String", "hashed_secret": hash_, "line_number": 1}


def test_baselined_hash_is_clean():
    scan = {"a/b.py": [_f("h1")]}
    baseline = {"a/b.py": [_f("h1")]}
    assert new_secrets(scan, baseline) == {}


def test_second_hash_in_baselined_file_is_new():
    scan = {"a/b.py": [_f("h1"), _f("h2")]}
    baseline = {"a/b.py": [_f("h1")]}
    fresh = new_secrets(scan, baseline)
    assert list(fresh) == ["a/b.py"]
    assert [f["hashed_secret"] for f in fresh["a/b.py"]] == ["h2"]


def test_hash_in_unbaselined_file_is_new():
    scan = {"new.py": [_f("h1")]}
    assert list(new_secrets(scan, {})) == ["new.py"]


def test_windows_and_posix_paths_are_equivalent():
    """Regression for the predecessor's OS-path-separator coupling: a baseline
    written on Windows (backslash keys) must match a scan on POSIX and vice versa."""
    scan = {"tests/unit/test_x.py": [_f("h1")]}
    baseline = {"tests\\unit\\test_x.py": [_f("h1")]}
    assert new_secrets(scan, baseline) == {}
    assert new_secrets({"tests\\a.py": [_f("h2")]}, {"tests/a.py": [_f("h2")]}) == {}
