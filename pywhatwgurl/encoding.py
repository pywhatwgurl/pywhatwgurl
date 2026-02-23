# SPDX-License-Identifier: MIT
"""Percent-encoding utilities per WHATWG URL Standard."""

from __future__ import annotations

from typing import Callable, Dict, Optional


C0_CONTROL_AND_SPACE = "".join(chr(c) for c in range(0x20)) + " "
"""C0 control characters (U+0000 to U+001F) plus space, for input trimming."""

SPECIAL_SCHEMES: Dict[str, Optional[int]] = {
    "ftp": 21,
    "file": None,
    "http": 80,
    "https": 443,
    "ws": 80,
    "wss": 443,
}
"""Special URL schemes and their default ports per WHATWG spec."""

FORBIDDEN_HOST_CODE_POINTS = frozenset("\x00\t\n\r #/:<>?@[\\]^|")
"""Code points that cannot appear in non-opaque hosts."""

FORBIDDEN_DOMAIN_CODE_POINTS = (
    FORBIDDEN_HOST_CODE_POINTS
    | frozenset(chr(c) for c in range(0x00, 0x20))
    | frozenset("%\x7f")
)
"""Code points that cannot appear in domain names."""


def _is_ascii_alpha(c: int) -> bool:
    """Return True if code point is an ASCII letter."""
    return 0x41 <= c <= 0x5A or 0x61 <= c <= 0x7A


def _is_ascii_digit(c: int) -> bool:
    """Return True if code point is an ASCII digit."""
    return 0x30 <= c <= 0x39


def _is_ascii_alphanumeric(c: int) -> bool:
    """Return True if code point is an ASCII letter or digit."""
    return _is_ascii_alpha(c) or _is_ascii_digit(c)


def _is_ascii_hex(c: int) -> bool:
    """Return True if code point is an ASCII hexadecimal digit."""
    return _is_ascii_digit(c) or 0x41 <= c <= 0x46 or 0x61 <= c <= 0x66


def _is_c0_control_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding (C0 control set)."""
    return c <= 0x1F or c > 0x7E


_EXTRA_FRAGMENT = frozenset(ord(x) for x in ' "<>`')


def _is_fragment_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL fragments."""
    return _is_c0_control_percent_encode(c) or c in _EXTRA_FRAGMENT


_EXTRA_QUERY = frozenset(ord(x) for x in ' "#<>')


def _is_query_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL queries."""
    return _is_c0_control_percent_encode(c) or c in _EXTRA_QUERY


def _is_special_query_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in special URL queries."""
    return _is_query_percent_encode(c) or c == 0x27  # '


_EXTRA_PATH = frozenset(ord(x) for x in "?`{}^")


def _is_path_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL paths."""
    return _is_query_percent_encode(c) or c in _EXTRA_PATH


_EXTRA_USERINFO = frozenset(ord(x) for x in "/:;=@[\\]|")


def _is_userinfo_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL userinfo."""
    return _is_path_percent_encode(c) or c in _EXTRA_USERINFO


_EXTRA_COMPONENT = frozenset(ord(x) for x in "$%&+,")


def _is_component_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL components."""
    return _is_userinfo_percent_encode(c) or c in _EXTRA_COMPONENT


_EXTRA_URLENCODED = frozenset(ord(x) for x in "!'()~")


def _is_urlencoded_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in form data."""
    return _is_component_percent_encode(c) or c in _EXTRA_URLENCODED


def _percent_encode(byte: int) -> str:
    """Convert a byte to its percent-encoded representation."""
    return f"%{byte:02X}"


def _percent_decode_bytes(data: bytes) -> bytes:
    """Decode percent-encoded byte sequences."""
    result = bytearray()
    i = 0
    while i < len(data):
        byte = data[i]
        if byte != 0x25:  # %
            result.append(byte)
            i += 1
        elif i + 2 >= len(data):
            result.append(byte)
            i += 1
        elif not (_is_ascii_hex(data[i + 1]) and _is_ascii_hex(data[i + 2])):
            result.append(byte)
            i += 1
        else:
            hex_str = chr(data[i + 1]) + chr(data[i + 2])
            result.append(int(hex_str, 16))
            i += 3
    return bytes(result)


def _percent_decode_string(s: str) -> bytes:
    """Decode a percent-encoded string, returning raw bytes."""
    return _percent_decode_bytes(s.encode("utf-8"))


def _utf8_percent_encode_codepoint(
    codepoint: int, predicate: Callable[[int], bool]
) -> str:
    """Percent-encode a code point using UTF-8 encoding."""
    char = chr(codepoint)
    encoded = char.encode("utf-8")
    result = []
    for byte in encoded:
        if predicate(byte):
            result.append(_percent_encode(byte))
        else:
            result.append(chr(byte))
    return "".join(result)


def _utf8_percent_encode_string(
    s: str, predicate: Callable[[int], bool], space_as_plus: bool = False
) -> str:
    """Percent-encode a string using UTF-8 encoding."""
    result = []
    for char in s:
        if space_as_plus and char == " ":
            result.append("+")
        else:
            result.append(_utf8_percent_encode_codepoint(ord(char), predicate))
    return "".join(result)


def percent_encode_after_encoding(
    s: str,
    encoding: str = "utf-8",
    predicate: Optional[Callable[[int], bool]] = None,
) -> str:
    """Percent-encode a string using the specified character encoding.

    Args:
        s: The string to encode.
        encoding: Character encoding to use (currently only UTF-8 is supported).
        predicate: Function to determine which bytes require encoding.
            Defaults to the fragment percent-encode set.

    Returns:
        The percent-encoded string.
    """
    if predicate is None:
        predicate = _is_fragment_percent_encode
    return _utf8_percent_encode_string(s, predicate)
