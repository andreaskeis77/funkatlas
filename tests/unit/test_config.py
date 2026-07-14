"""Unified merge contract: a PARTIAL YAML file only overrides the keys it
names — unlisted defaults survive. (The predecessor's thresholds/probes loaders
replaced defaults wholesale; that silent-drop behavior is the bug pinned here.)
"""

import pytest

from funkatlas import config

pytestmark = [pytest.mark.unit]

DEFAULTS = {"a": 1, "b": 2, "c": 3}


def test_partial_yaml_keeps_unlisted_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("FUNKATLAS_CONFIG_DIR", str(tmp_path))
    (tmp_path / "demo.yaml").write_text("b: 99\n", encoding="utf-8")
    merged = config.load_merged("demo.yaml", DEFAULTS)
    assert merged == {"a": 1, "b": 99, "c": 3}


def test_missing_file_yields_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("FUNKATLAS_CONFIG_DIR", str(tmp_path))
    assert config.load_merged("absent.yaml", DEFAULTS) == DEFAULTS


def test_malformed_yaml_yields_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("FUNKATLAS_CONFIG_DIR", str(tmp_path))
    (tmp_path / "bad.yaml").write_text("key: [unclosed\n  broken: {", encoding="utf-8")
    assert config.load_merged("bad.yaml", DEFAULTS) == DEFAULTS


def test_non_dict_yaml_yields_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("FUNKATLAS_CONFIG_DIR", str(tmp_path))
    (tmp_path / "list.yaml").write_text("- 1\n- 2\n", encoding="utf-8")
    assert config.load_merged("list.yaml", DEFAULTS) == DEFAULTS


def test_partial_nested_section_keeps_sibling_defaults(tmp_path, monkeypatch):
    """A partial ping: section naming only targets must not drop count/timeout
    (would kill every supervisor tick with KeyError while heartbeats look fine)."""
    monkeypatch.setenv("FUNKATLAS_CONFIG_DIR", str(tmp_path))
    (tmp_path / "probes.yaml").write_text(
        "ping:\n  targets:\n    printer: 192.0.2.9\n", encoding="utf-8"
    )
    merged = config.probes()
    assert merged["ping"]["targets"] == {"printer": "192.0.2.9"}
    assert merged["ping"]["count"] == config.DEFAULT_PROBES["ping"]["count"]
    assert merged["ping"]["timeout_ms"] == config.DEFAULT_PROBES["ping"]["timeout_ms"]
    assert merged["dns"] == config.DEFAULT_PROBES["dns"]
