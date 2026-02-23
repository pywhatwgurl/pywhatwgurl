"""WPT conformance tests for URL parsing via urltestdata.json.

Corresponds conceptually to WPT:
- url/url-constructor.any.js (parsing logic)
- url/url-origin.any.js (origin logic)

Note: This test suite checks `origin` (like url-origin.any.js) along with other properties
(like url-constructor.any.js) in a single pass, as `urltestdata.json` provides all this data.
"""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from pywhatwgurl import URL
from tests.conformance.conftest import DATA_DIR
from tests.conformance.wpt_data import load_urltestdata_cases, make_case_id


def _expected_fields() -> tuple[str, ...]:
    return (
        "href",
        "origin",
        "protocol",
        "username",
        "password",
        "host",
        "hostname",
        "port",
        "pathname",
        "search",
        "hash",
    )


def _make_url(input_value: str, base: object) -> URL:
    if base is None:
        return URL(input_value)

    if isinstance(base, str):
        return URL(input_value, base)

    pytest.fail(f"Unexpected base type in urltestdata: {type(base).__name__}")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "urltestdata_case" not in metafunc.fixturenames:
        return

    cases = load_urltestdata_cases(DATA_DIR)
    ids = [make_case_id("urltestdata", i, c) for i, c in enumerate(cases)]
    metafunc.parametrize("urltestdata_case", cases, ids=ids)


def test_urltestdata_case(urltestdata_case: Mapping[str, Any]) -> None:
    input_value = urltestdata_case.get("input")
    base = urltestdata_case.get("base")
    if not isinstance(input_value, str):
        pytest.fail("missing/invalid 'input'")

    failure = urltestdata_case.get("failure") is True

    if failure:
        with pytest.raises(ValueError):
            _make_url(input_value, base)
        return

    url = _make_url(input_value, base)

    for field in _expected_fields():
        expected = urltestdata_case.get(field)
        if expected is None:
            continue
        if not isinstance(expected, str):
            pytest.fail(f"invalid expected value for {field}")
        actual = getattr(url, field)
        assert actual == expected, f"{field}: expected {expected!r}, got {actual!r}"

    expected_search_params = urltestdata_case.get("searchParams")
    if expected_search_params is not None:
        if not isinstance(expected_search_params, str):
            pytest.fail("invalid expected value for searchParams")
        actual_search_params = url.search_params.to_string()
        assert actual_search_params == expected_search_params, (
            f"searchParams: expected {expected_search_params!r}, got {actual_search_params!r}"
        )
