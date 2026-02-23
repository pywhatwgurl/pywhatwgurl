"""WPT conformance tests for URL property setters."""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from pywhatwgurl import URL
from tests.conformance.conftest import DATA_DIR
from tests.conformance.wpt_data import load_setters_cases


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "setter_case" not in metafunc.fixturenames:
        return

    cases = load_setters_cases(DATA_DIR)
    ids = [f"setters:{attr}[{idx}]" for attr, idx, _ in cases]
    metafunc.parametrize("setter_case", cases, ids=ids)


def test_url_setter_case(setter_case: tuple[str, int, Mapping[str, Any]]) -> None:
    attr, idx, case = setter_case

    url = URL(case["href"])
    setattr(url, attr, case["new_value"])

    for key, expected_value in case["expected"].items():
        assert getattr(url, key) == expected_value, f"setters:{attr}[{idx}]:{key}"
