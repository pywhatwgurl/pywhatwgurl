"""WPT conformance tests for percent-encoding."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pytest

from pywhatwgurl import percent_encode_after_encoding
from tests.conformance.wpt_data import load_percent_encoding_cases, make_case_id


@pytest.fixture(scope="session")
def percent_encoding_cases(wpt_test_data_dir: Path) -> list[Mapping[str, Any]]:
    return load_percent_encoding_cases(wpt_test_data_dir)


def test_percent_encoding_cases(
    percent_encoding_cases: list[Mapping[str, Any]],
) -> None:
    for index, case in enumerate(percent_encoding_cases):
        case_id = make_case_id("percent-encoding", index, case)

        input_value = case.get("input")
        expected = case.get("output")
        if not isinstance(input_value, str) or not isinstance(expected, str):
            pytest.fail(f"{case_id}: invalid schema")

        actual = percent_encode_after_encoding(input_value)
        assert actual == expected, case_id
