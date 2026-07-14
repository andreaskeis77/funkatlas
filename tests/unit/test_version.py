import re

import pytest

import funkatlas

pytestmark = [pytest.mark.unit]


def test_version_is_semver_like():
    assert re.fullmatch(r"\d+\.\d+\.\d+", funkatlas.__version__)
