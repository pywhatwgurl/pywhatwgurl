"""Unit tests for Python-specific API contracts not covered by WPT conformance."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from pywhatwgurl import URL, URLSearchParams, percent_encode_after_encoding
from pywhatwgurl import parser as parser_module


@pytest.fixture()
def example_url() -> URL:
    return URL("https://user:pass@example.com:8080/path?q=1#frag")


class TestURLRepr:
    def test_repr(self, example_url: URL) -> None:
        assert (
            repr(example_url)
            == "URL('https://user:pass@example.com:8080/path?q=1#frag')"
        )

    def test_repr_roundtrip(self) -> None:
        url = URL("https://例え.jp/")
        assert repr(url) == f"URL({url.href!r})"

    def test_str_equals_href(self, example_url: URL) -> None:
        assert str(example_url) == example_url.href


class TestURLEquality:
    @pytest.mark.parametrize(
        "a, b, expected",
        [
            pytest.param(
                "https://example.com/", "https://example.com/", True, id="same-href"
            ),
            pytest.param(
                "HTTPS://EXAMPLE.COM/", "https://example.com/", True, id="normalized"
            ),
            pytest.param(
                "https://example.com/", "https://other.com/", False, id="different-href"
            ),
        ],
    )
    def test_url_equality(self, a: str, b: str, expected: bool) -> None:
        assert (URL(a) == URL(b)) is expected

    @pytest.mark.parametrize(
        "other",
        [
            pytest.param("https://example.com/", id="string"),
            pytest.param(None, id="none"),
            pytest.param(42, id="int"),
        ],
    )
    def test_not_equal_to_non_url(self, other: object) -> None:
        assert URL("https://example.com/") != other

    def test_unhashable(self) -> None:
        with pytest.raises(TypeError, match="unhashable"):
            hash(URL("https://example.com/"))


class TestURLErrors:
    @pytest.mark.parametrize(
        "url, base, match",
        [
            pytest.param("not a url", None, "Invalid URL", id="invalid-url"),
            pytest.param("/path", "not a base", "Invalid base URL", id="invalid-base"),
            pytest.param("/relative/path", None, "Invalid URL", id="relative-no-base"),
        ],
    )
    def test_constructor_raises(self, url: str, base: str | None, match: str) -> None:
        with pytest.raises(ValueError, match=match):
            URL(url, base) if base else URL(url)

    def test_href_setter_rejects_invalid(self) -> None:
        url = URL("https://example.com/")
        with pytest.raises(ValueError, match="Invalid URL"):
            url.href = "not valid"

    @pytest.mark.parametrize(
        "url, base",
        [
            pytest.param("not a url", None, id="invalid-url"),
            pytest.param("/path", "bad base", id="invalid-base"),
        ],
    )
    def test_parse_returns_none(self, url: str, base: str | None) -> None:
        assert URL.parse(url, base) is None

    @pytest.mark.parametrize(
        "url, expected",
        [
            pytest.param("https://example.com/", True, id="valid"),
            pytest.param("not a url", False, id="invalid"),
        ],
    )
    def test_can_parse(self, url: str, expected: bool) -> None:
        assert URL.can_parse(url) is expected


class TestParserReuse:
    def test_thread_local_parser_reused_per_thread(self) -> None:
        barrier = Barrier(2)

        def get_parser_id(_: int) -> int:
            first = parser_module._get_parser()
            barrier.wait()
            second = parser_module._get_parser()
            assert first is second
            return id(first)

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_id, second_id = executor.map(get_parser_id, range(2))

        assert first_id != second_id


class TestPercentEncodeAfterEncoding:
    @pytest.mark.parametrize(
        "input_str, expected",
        [
            pytest.param("hello", "hello", id="ascii-passthrough"),
            pytest.param("abc123", "abc123", id="alphanumeric"),
            pytest.param(" ", "%20", id="space"),
            pytest.param('"', "%22", id="double-quote"),
            pytest.param("ä", "%C3%A4", id="latin-umlaut"),
            pytest.param("€", "%E2%82%AC", id="euro-sign"),
            pytest.param("", "", id="empty"),
            pytest.param("\x00", "%00", id="null-byte"),
            pytest.param("\x1f", "%1F", id="us-control"),
        ],
    )
    def test_encoding(self, input_str: str, expected: str) -> None:
        assert percent_encode_after_encoding(input_str) == expected


class TestURLSearchParamsConstructor:
    def test_from_string(self) -> None:
        params = URLSearchParams("a=1&b=2")
        assert params.get("a") == "1"
        assert params.get("b") == "2"

    def test_leading_question_mark_stripped(self) -> None:
        assert URLSearchParams("?a=1").get("a") == "1"

    @pytest.mark.parametrize(
        "init",
        [
            pytest.param(None, id="none"),
            pytest.param(None, id="no-args"),
        ],
    )
    def test_empty(self, init: None) -> None:
        assert len(URLSearchParams(init)) == 0

    def test_copy_is_independent(self) -> None:
        original = URLSearchParams("x=1&y=2")
        copy = URLSearchParams(original)
        assert copy.get("x") == "1"
        copy.set("x", "changed")
        assert original.get("x") == "1"

    def test_from_dict(self) -> None:
        params = URLSearchParams({"key": "value", "foo": "bar"})
        assert params.get("key") == "value"

    def test_from_dict_with_sequence_values(self) -> None:
        params = URLSearchParams({"tags": ["a", "b", "c"]})
        assert params.get_all("tags") == ("a", "b", "c")

    def test_from_iterable_of_pairs(self) -> None:
        params = URLSearchParams([("a", "1"), ["b", "2"]])
        assert params.get("a") == "1"
        assert params.get("b") == "2"

    @pytest.mark.parametrize(
        "bad_pair",
        [
            pytest.param(["a", "b", "c"], id="too-many"),
            pytest.param(["a"], id="too-few"),
        ],
    )
    def test_invalid_pair_length_raises(self, bad_pair: list[str]) -> None:
        with pytest.raises(TypeError, match="exactly two elements"):
            URLSearchParams([bad_pair])
