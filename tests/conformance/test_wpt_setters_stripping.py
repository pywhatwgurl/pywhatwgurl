"""WPT conformance tests for URL setters stripping behavior.

Tests that Tab (U+0009), LF (U+000A), and CR (U+000D) are correctly stripped
from URL components during setter operations, as per WHATWG URL Standard.

Based on WPT url-setters-stripping.any.js.
"""

from __future__ import annotations


import pytest

from pywhatwgurl import URL


STRIPPED_CHARS = [
    (0x09, "TAB"),
    (0x0A, "LF"),
    (0x0D, "CR"),
]

NON_STRIPPED_EDGE_CASES = [
    (0x00, "NUL"),
    (0x1F, "US"),
]


def _url_string(
    scheme: str = "https",
    username: str = "username",
    password: str = "password",  # noqa: S107
    host: str = "host",
    port: str = "8000",
    pathname: str = "path",
    search: str = "query",
    hash_: str = "fragment",
) -> str:
    """Build a URL string with the given components."""
    return f"{scheme}://{username}:{password}@{host}:{port}/{pathname}?{search}#{hash_}"


def _url_record(scheme: str = "https") -> URL:
    """Create a URL object with standard test components."""
    return URL(_url_string(scheme=scheme))


class TestProtocolSetterStripping:
    """Test protocol setter stripping behavior."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    def test_leading_stripped(self, code_point: int, name: str, scheme: str) -> None:
        """Leading stripped character allows protocol change."""
        url = _url_record(scheme)
        new_scheme = "http" if scheme == "https" else "wpt--"
        url.protocol = chr(code_point) + new_scheme

        assert url.protocol == new_scheme + ":", (
            f"Leading {name} in protocol setter should be stripped ({scheme})"
        )

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    def test_before_colon_stripped(
        self, code_point: int, name: str, scheme: str
    ) -> None:
        """Stripped character before inserted colon allows protocol change."""
        url = _url_record(scheme)
        new_scheme = "http" if scheme == "https" else "wpt--"
        url.protocol = new_scheme + chr(code_point)

        assert url.protocol == new_scheme + ":", (
            f"{name} before colon in protocol setter should be stripped ({scheme})"
        )


class TestCredentialsSetterNoStripping:
    """Test username/password setters - no stripping, only encoding."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize(
        "code_point,name", STRIPPED_CHARS + NON_STRIPPED_EDGE_CASES
    )
    @pytest.mark.parametrize("property_name", ["username", "password"])
    @pytest.mark.parametrize("position", ["leading", "middle", "trailing"])
    def test_encoding_not_stripping(
        self, code_point: int, name: str, property_name: str, position: str, scheme: str
    ) -> None:
        """Username/password setters percent-encode, don't strip."""
        cp_str = chr(code_point)
        encoded = f"%{code_point:02X}"

        if position == "leading":
            input_val = cp_str + "test"
            expected = encoded + "test"
        elif position == "middle":
            input_val = "te" + cp_str + "st"
            expected = "te" + encoded + "st"
        else:
            input_val = "test" + cp_str
            expected = "test" + encoded

        url = _url_record(scheme)
        setattr(url, property_name, input_val)
        actual = getattr(url, property_name)
        assert actual == expected, (
            f"{property_name} setter should encode {name} at {position} ({scheme})"
        )


class TestPortSetterStripping:
    """Test port setter stripping behavior."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    def test_leading_stripped(self, code_point: int, name: str, scheme: str) -> None:
        """Leading stripped character is removed from port."""
        url = _url_record(scheme)
        url.port = chr(code_point) + "9000"
        assert url.port == "9000", (
            f"Leading {name} in port setter should be stripped ({scheme})"
        )

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    def test_middle_stripped(self, code_point: int, name: str, scheme: str) -> None:
        """Middle stripped character is removed from port."""
        url = _url_record(scheme)
        url.port = "90" + chr(code_point) + "00"
        assert url.port == "9000", (
            f"Middle {name} in port setter should be stripped ({scheme})"
        )

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    def test_trailing_stripped(self, code_point: int, name: str, scheme: str) -> None:
        """Trailing stripped character is removed from port."""
        url = _url_record(scheme)
        url.port = "9000" + chr(code_point)
        assert url.port == "9000", (
            f"Trailing {name} in port setter should be stripped ({scheme})"
        )


class TestPathSearchHashSetterStripping:
    """Test pathname/search/hash setter stripping behavior."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    @pytest.mark.parametrize(
        "property_name,separator",
        [("pathname", "/"), ("search", "?"), ("hash", "#")],
    )
    @pytest.mark.parametrize("position", ["leading", "middle", "trailing"])
    def test_stripped_and_encoded(
        self,
        code_point: int,
        name: str,
        property_name: str,
        separator: str,
        position: str,
        scheme: str,
    ) -> None:
        """Pathname/search/hash setters strip Tab/LF/CR."""
        cp_str = chr(code_point)

        if position == "leading":
            input_val = cp_str + "test"
        elif position == "middle":
            input_val = "te" + cp_str + "st"
        else:
            input_val = "test" + cp_str

        expected = separator + "test"

        url = _url_record(scheme)
        setattr(url, property_name, input_val)
        actual = getattr(url, property_name)
        assert actual == expected, (
            f"{property_name} setter should strip {name} at {position} ({scheme})"
        )


class TestHostSetterStripping:
    """Test host/hostname setter with stripped characters."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", STRIPPED_CHARS)
    @pytest.mark.parametrize("property_name", ["host", "hostname"])
    @pytest.mark.parametrize("position", ["leading", "middle", "trailing"])
    def test_stripped_from_host(
        self, code_point: int, name: str, property_name: str, position: str, scheme: str
    ) -> None:
        """Host/hostname with stripped chars should work correctly."""
        cp_str = chr(code_point)

        if position == "leading":
            input_val = cp_str + "test"
        elif position == "middle":
            input_val = "te" + cp_str + "st"
        else:
            input_val = "test" + cp_str

        url = _url_record(scheme)
        setattr(url, property_name, input_val)
        actual = getattr(url, property_name)

        if property_name == "host":
            assert actual == "test:8000", (
                f"{property_name} setter should strip {name} at {position} ({scheme})"
            )
        else:
            assert actual == "test", (
                f"{property_name} setter should strip {name} at {position} ({scheme})"
            )


class TestHostSetterNonStrippedEdgeCases:
    """Test host/hostname setter with NUL and US (non-stripped edge cases)."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", NON_STRIPPED_EDGE_CASES)
    @pytest.mark.parametrize("property_name", ["host", "hostname"])
    @pytest.mark.parametrize("position", ["leading", "middle", "trailing"])
    def test_non_stripped_host(
        self, code_point: int, name: str, property_name: str, position: str, scheme: str
    ) -> None:
        """NUL/US in host setter behaves as a forbidden host code point.

        Per WPT: NUL always causes no-op. US (0x1F) causes no-op for https,
        but is percent-encoded for non-special schemes.
        """
        cp_str = chr(code_point)
        encoded = f"%{code_point:02X}"

        if position == "leading":
            expected_part = (cp_str if scheme == "https" else encoded) + "test"
        elif position == "middle":
            expected_part = "te" + (cp_str if scheme == "https" else encoded) + "st"
        else:
            expected_part = "test" + (cp_str if scheme == "https" else encoded)

        # NUL always rejects; US rejects for https but not for non-special
        is_rejected = code_point == 0x00 or (scheme == "https" and code_point == 0x1F)

        if position == "leading":
            input_val = cp_str + "test"
        elif position == "middle":
            input_val = "te" + cp_str + "st"
        else:
            input_val = "test" + cp_str

        url = _url_record(scheme)
        setattr(url, property_name, input_val)
        actual = getattr(url, property_name)

        if is_rejected:
            expected = "host:8000" if property_name == "host" else "host"
        else:
            expected = (
                expected_part + ":8000" if property_name == "host" else expected_part
            )

        assert actual == expected, (
            f"{property_name} setter with {name} at {position} ({scheme}): "
            f"expected {expected!r}, got {actual!r}"
        )


class TestPortSetterNonStrippedEdgeCases:
    """Test port setter with NUL and US (non-stripped edge cases)."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", NON_STRIPPED_EDGE_CASES)
    def test_leading_non_stripped(
        self, code_point: int, name: str, scheme: str
    ) -> None:
        """Leading NUL/US in port causes parse to stop immediately."""
        url = _url_record(scheme)
        url.port = chr(code_point) + "9000"
        assert url.port == "8000", (
            f"Leading {name} in port setter should not change port ({scheme})"
        )

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", NON_STRIPPED_EDGE_CASES)
    def test_middle_non_stripped(self, code_point: int, name: str, scheme: str) -> None:
        """Middle NUL/US in port causes parse to stop at that point."""
        url = _url_record(scheme)
        url.port = "90" + chr(code_point) + "00"
        assert url.port == "90", (
            f"Middle {name} in port setter should stop parsing ({scheme})"
        )

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", NON_STRIPPED_EDGE_CASES)
    def test_trailing_non_stripped(
        self, code_point: int, name: str, scheme: str
    ) -> None:
        """Trailing NUL/US in port is ignored (port parsed fine before it)."""
        url = _url_record(scheme)
        url.port = "9000" + chr(code_point)
        assert url.port == "9000", (
            f"Trailing {name} in port setter should not affect result ({scheme})"
        )


class TestPathSearchHashNonStrippedEdgeCases:
    """Test pathname/search/hash setter with NUL and US edge cases."""

    @pytest.mark.parametrize("scheme", ["https", "wpt++"])
    @pytest.mark.parametrize("code_point,name", NON_STRIPPED_EDGE_CASES)
    @pytest.mark.parametrize(
        "property_name,separator",
        [("pathname", "/"), ("search", "?"), ("hash", "#")],
    )
    @pytest.mark.parametrize("position", ["leading", "middle", "trailing"])
    def test_non_stripped_encoded(
        self,
        code_point: int,
        name: str,
        property_name: str,
        separator: str,
        position: str,
        scheme: str,
    ) -> None:
        """NUL/US in pathname/search/hash should be percent-encoded, not stripped."""
        cp_str = chr(code_point)
        encoded = f"%{code_point:02X}"

        if position == "leading":
            input_val = cp_str + "test"
            expected_part = encoded + "test"
        elif position == "middle":
            input_val = "te" + cp_str + "st"
            expected_part = "te" + encoded + "st"
        else:
            input_val = "test" + cp_str
            expected_part = "test" + encoded

        expected = separator + expected_part

        url = _url_record(scheme)
        setattr(url, property_name, input_val)
        actual = getattr(url, property_name)
        assert actual == expected, (
            f"{property_name} setter should encode {name} at {position} ({scheme}): "
            f"expected {expected!r}, got {actual!r}"
        )
