"""URL static methods conformance tests based on WPT url-statics tests."""

from __future__ import annotations

from typing import Optional

import pytest

from pywhatwgurl import URL


CAN_PARSE_TEST_CASES = [
    ("aaa:b", None, True),
    ("aaa:/b", None, True),
    ("https://test:test", None, False),
    ("a", "https://b/", True),
    ("undefined", None, False),
    ("undefined", "aaa:b", False),
    ("undefined", "https://test:test/", False),
    ("undefined", "aaa:/b", True),
]


@pytest.mark.parametrize(
    "url,base,expected",
    CAN_PARSE_TEST_CASES,
    ids=[
        f"canParse({url!r}, {base!r})" for url, base, expected in CAN_PARSE_TEST_CASES
    ],
)
def test_url_can_parse(url: str, base: Optional[str], expected: bool) -> None:
    """Test URL.can_parse() static method."""
    if base is None:
        result = URL.can_parse(url)
    else:
        result = URL.can_parse(url, base)

    assert result == expected


@pytest.mark.parametrize(
    "url,base,expected",
    CAN_PARSE_TEST_CASES,
    ids=[f"parse({url!r}, {base!r})" for url, base, expected in CAN_PARSE_TEST_CASES],
)
def test_url_parse(url: str, base: Optional[str], expected: bool) -> None:
    """Test URL.parse() static method."""
    if base is None:
        result = URL.parse(url)
    else:
        result = URL.parse(url, base)

    if expected is False:
        assert result is None
    else:
        assert result is not None
        if base is None:
            expected_url = URL(url)
        else:
            expected_url = URL(url, base)
        assert result.href == expected_url.href


def test_url_parse_returns_unique_objects() -> None:
    """URL.parse() should return a unique object each time."""
    a = URL.parse("https://example/")
    b = URL.parse("https://example/")
    assert a is not b
