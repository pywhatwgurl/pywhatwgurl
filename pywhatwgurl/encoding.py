# SPDX-License-Identifier: MIT
"""Percent-encoding utilities per WHATWG URL Standard."""

from __future__ import annotations

import re
from collections.abc import Callable


C0_CONTROL_AND_SPACE = "".join(chr(c) for c in range(0x20)) + " "
"""C0 control characters (U+0000 to U+001F) plus space, for input trimming."""

SPECIAL_SCHEMES: dict[str, int | None] = {
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


# Pre-computed sets of ASCII codepoints (0x00-0x7E) needing percent-encoding
# for each encoding class. For any codepoint > 0x7E, all predicates return True.
_C0_ENCODE_SET: frozenset[int] = frozenset(range(0x20))
# DEL (0x7F) is intentionally excluded here and handled by the shared
# `c > 0x7E` guard in the percent-encoding predicates below.
_FRAGMENT_ENCODE_SET: frozenset[int] = _C0_ENCODE_SET | frozenset(ord(x) for x in ' "<>`')
_QUERY_ENCODE_SET: frozenset[int] = _C0_ENCODE_SET | frozenset(ord(x) for x in ' "#<>')
_SPECIAL_QUERY_ENCODE_SET: frozenset[int] = _QUERY_ENCODE_SET | {0x27}
_PATH_ENCODE_SET: frozenset[int] = _QUERY_ENCODE_SET | frozenset(ord(x) for x in "?`{}^")
_USERINFO_ENCODE_SET: frozenset[int] = _PATH_ENCODE_SET | frozenset(ord(x) for x in "/:;=@[\\]|")
_COMPONENT_ENCODE_SET: frozenset[int] = _USERINFO_ENCODE_SET | frozenset(ord(x) for x in "$%&+,")
_URLENCODED_ENCODE_SET: frozenset[int] = _COMPONENT_ENCODE_SET | frozenset(ord(x) for x in "!'()~")


def _is_c0_control_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding (C0 control set)."""
    return c > 0x7E or c in _C0_ENCODE_SET


def _is_fragment_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL fragments."""
    return c > 0x7E or c in _FRAGMENT_ENCODE_SET


def _is_query_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL queries."""
    return c > 0x7E or c in _QUERY_ENCODE_SET


def _is_special_query_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in special URL queries."""
    return c > 0x7E or c in _SPECIAL_QUERY_ENCODE_SET


def _is_path_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL paths."""
    return c > 0x7E or c in _PATH_ENCODE_SET


def _is_userinfo_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL userinfo."""
    return c > 0x7E or c in _USERINFO_ENCODE_SET


def _is_component_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in URL components."""
    return c > 0x7E or c in _COMPONENT_ENCODE_SET


def _is_urlencoded_percent_encode(c: int) -> bool:
    """Return True if code point requires percent-encoding in form data."""
    return c > 0x7E or c in _URLENCODED_ENCODE_SET


_PERCENT_ENCODED: tuple[str, ...] = tuple(f"%{byte:02X}" for byte in range(256))
"""Pre-computed percent-encoded representations for all 256 byte values."""

_CHR: tuple[str, ...] = tuple(chr(i) for i in range(128))
"""Pre-computed chr() results for ASCII codepoints, avoiding per-call overhead."""

_CHR_LOWER: tuple[str, ...] = tuple(chr(i).lower() for i in range(128))
"""Pre-computed lowercase chr() results for ASCII codepoints."""


def _percent_encode(byte: int) -> str:
    """Convert a byte to its percent-encoded representation."""
    return _PERCENT_ENCODED[byte]


_PERCENT_RE = re.compile(b"%([0-9A-Fa-f]{2})")


def _percent_decode_bytes(data: bytes) -> bytes:
    """Decode percent-encoded byte sequences."""
    if b"%" not in data:
        return data
    return _PERCENT_RE.sub(lambda m: bytes([int(m.group(1), 16)]), data)


def _percent_decode_string(s: str) -> bytes:
    """Decode a percent-encoded string, returning raw bytes."""
    return _percent_decode_bytes(s.encode("utf-8"))


def _utf8_percent_encode_codepoint(
    codepoint: int, predicate: Callable[[int], bool]
) -> str:
    """Percent-encode a code point using UTF-8 encoding."""
    if codepoint < 0x80:
        return _PERCENT_ENCODED[codepoint] if predicate(codepoint) else _CHR[codepoint]
    encoded = chr(codepoint).encode("utf-8")
    return "".join(
        _PERCENT_ENCODED[byte] if predicate(byte) else chr(byte) for byte in encoded
    )


def _utf8_percent_encode_string(
    s: str, predicate: Callable[[int], bool], space_as_plus: bool = False
) -> str:
    """Percent-encode a string using UTF-8 encoding."""
    parts: list[str] = []
    for char in s:
        if space_as_plus and char == " ":
            parts.append("+")
        else:
            cp = ord(char)
            if cp < 0x80:
                parts.append(_PERCENT_ENCODED[cp] if predicate(cp) else char)
            else:
                parts.append(_utf8_percent_encode_codepoint(cp, predicate))
    return "".join(parts)


def percent_encode_after_encoding(
    s: str,
    encoding: str = "utf-8",
    predicate: Callable[[int], bool] | None = None,
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
