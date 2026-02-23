"""WPT conformance tests for toascii.json.

Tests the domain_to_ascii() function against the WHATWG URL Standard
ToASCII test suite, which validates IDNA processing for URL hosts.
"""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from pywhatwgurl import URL, domain_to_ascii
from tests.conformance.conftest import DATA_DIR
from tests.conformance.wpt_data import load_toascii_cases, make_case_id


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "toascii_case" not in metafunc.fixturenames:
        return

    cases = load_toascii_cases(DATA_DIR)
    ids = [make_case_id("toascii", i, c) for i, c in enumerate(cases)]
    metafunc.parametrize("toascii_case", cases, ids=ids)


def test_toascii_case(toascii_case: Mapping[str, Any]) -> None:
    """Test domain_to_ascii against toascii.json test vector."""
    input_value = toascii_case["input"]
    expected_output = toascii_case.get("output")
    comment = toascii_case.get("comment", "")

    actual = domain_to_ascii(input_value)

    if expected_output is None:
        assert actual is None, f"Expected failure but got {actual!r} ({comment})"
    else:
        assert actual == expected_output, (
            f"Expected {expected_output!r} but got {actual!r} ({comment})"
        )


def test_toascii_via_host_setter(toascii_case: Mapping[str, Any]) -> None:
    """Test toascii.json via URL.host setter.

    Per WPT toascii.window.js: setting url.host should process IDNA domains.
    Invalid hosts should leave the URL unchanged.
    """
    input_value = toascii_case["input"]
    expected_output = toascii_case.get("output")
    comment = toascii_case.get("comment", "")

    url = URL("https://x/path")
    url.host = input_value

    if expected_output is None:
        assert url.host == "x", (
            f"Invalid host {input_value!r} should not modify URL ({comment})"
        )
    else:
        assert url.host == expected_output, (
            f"host setter: expected {expected_output!r} but got {url.host!r} ({comment})"
        )


def test_toascii_via_hostname_setter(toascii_case: Mapping[str, Any]) -> None:
    """Test toascii.json via URL.hostname setter.

    Per WPT toascii.window.js: setting url.hostname should process IDNA domains.
    Invalid hosts should leave the URL unchanged.
    """
    input_value = toascii_case["input"]
    expected_output = toascii_case.get("output")
    comment = toascii_case.get("comment", "")

    url = URL("https://x/path")
    url.hostname = input_value

    if expected_output is None:
        assert url.hostname == "x", (
            f"Invalid hostname {input_value!r} should not modify URL ({comment})"
        )
    else:
        assert url.hostname == expected_output, (
            f"hostname setter: expected {expected_output!r} but got {url.hostname!r} ({comment})"
        )
