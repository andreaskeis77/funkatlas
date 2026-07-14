import pytest

from funkatlas.probes import dns

pytestmark = [pytest.mark.unit]


def _ticker(values):
    it = iter(values)
    return lambda: next(it)


def test_successful_resolve_times_and_counts():
    result = dns.resolve(
        "example.com",
        resolver=lambda name: [("af", "sock", 6, "", ("93.184.216.34", 0))] * 3,
        timer=_ticker([1.0, 1.025]),
    )
    assert result == {
        "name": "example.com",
        "ok": 1,
        "resolve_ms": 25.0,
        "address_count": 3,
    }


def test_failed_resolve_degrades_not_raises():
    def failing(name):
        raise OSError("getaddrinfo failed")

    result = dns.resolve("nope.invalid", resolver=failing)
    assert result == {"name": "nope.invalid", "ok": 0, "resolve_ms": None, "address_count": None}
