# SPDX-License-Identifier: MIT
"""Host parsing and serialization per WHATWG URL Standard."""

from __future__ import annotations
import ipaddress
from .idna_processor import domain_to_ascii

from typing import List, Optional


from .encoding import (
    FORBIDDEN_HOST_CODE_POINTS,
    _is_ascii_digit,
    _is_ascii_hex,
    _is_c0_control_percent_encode,
    _percent_decode_string,
    _utf8_percent_encode_string,
)
from .record import HostType


def _serialize_ipv4(address: int) -> str:
    """Serialize an IPv4 address to dotted-decimal notation."""
    return str(ipaddress.IPv4Address(address))


def _parse_ipv4_number(s: str) -> Optional[int]:
    """Parse an IPv4 number component (decimal, octal, or hex)."""
    if s == "":
        return None

    radix = 10

    if len(s) >= 2 and s[0] == "0" and s[1].lower() == "x":
        s = s[2:]
        radix = 16
    elif len(s) >= 1 and s[0] == "0":
        s = s[1:]
        radix = 8

    if s == "":
        return 0

    if radix == 8:
        if not all(c in "01234567" for c in s):
            return None
    elif radix == 10:
        if not all(c in "0123456789" for c in s):
            return None
    else:
        if not all(c.lower() in "0123456789abcdef" for c in s):
            return None

    return int(s, radix)


def _parse_ipv4(input_str: str) -> Optional[int]:
    """Parse an IPv4 address string into a 32-bit integer."""
    parts = input_str.split(".")

    if parts and parts[-1] == "":
        if len(parts) > 1:
            parts.pop()

    if len(parts) > 4:
        return None

    numbers = []
    for part in parts:
        n = _parse_ipv4_number(part)
        if n is None:
            return None
        numbers.append(n)

    for i in range(len(numbers) - 1):
        if numbers[i] > 255:
            return None

    if numbers[-1] >= 256 ** (5 - len(numbers)):
        return None

    ipv4 = numbers.pop()
    for i, n in enumerate(numbers):
        ipv4 += n * (256 ** (3 - i))

    return ipv4


def _find_ipv6_compress_index(address: List[int]) -> Optional[int]:
    longest_index = None
    longest_size = 1
    current_index = None
    current_size = 0

    for i, piece in enumerate(address):
        if piece != 0:
            if current_size > longest_size:
                longest_index = current_index
                longest_size = current_size
            current_index = None
            current_size = 0
        else:
            if current_index is None:
                current_index = i
            current_size += 1

    if current_size > longest_size:
        return current_index
    return longest_index


def _serialize_ipv6(address: List[int]) -> str:
    """Serialize an IPv6 address to string notation."""
    compress = _find_ipv6_compress_index(address)
    ignore_zero = False
    output = []

    for i in range(8):
        if ignore_zero and address[i] == 0:
            continue
        elif ignore_zero:
            ignore_zero = False

        if compress == i:
            sep = "::" if i == 0 else ":"
            output.append(sep)
            ignore_zero = True
            continue

        output.append(format(address[i], "x"))
        if i != 7:
            output.append(":")

    return "".join(output)


def _parse_ipv6(input_str: str) -> Optional[List[int]]:
    """Parse an IPv6 address string into a list of 8 16-bit integers."""
    address = [0] * 8
    piece_index = 0
    compress: Optional[int] = None
    pointer = 0
    chars = list(input_str)
    length = len(chars)

    def c() -> Optional[str]:
        return chars[pointer] if pointer < length else None

    if c() == ":":
        if pointer + 1 >= length or chars[pointer + 1] != ":":
            return None
        pointer += 2
        piece_index += 1
        compress = piece_index

    while pointer < length:
        if piece_index == 8:
            return None

        if c() == ":":
            if compress is not None:
                return None
            pointer += 1
            piece_index += 1
            compress = piece_index
            continue

        value = 0
        digit_length = 0

        while digit_length < 4:
            current_c = c()
            if current_c is None or not _is_ascii_hex(ord(current_c)):
                break
            value = value * 16 + int(current_c, 16)
            pointer += 1
            digit_length += 1

        if c() == ".":
            if digit_length == 0:
                return None
            pointer -= digit_length

            if piece_index > 6:
                return None

            numbers_seen = 0
            while c() is not None:
                ipv4_piece: Optional[int] = None

                if numbers_seen > 0:
                    if c() == "." and numbers_seen < 4:
                        pointer += 1
                    else:
                        return None

                current_c = c()
                if current_c is None or not _is_ascii_digit(ord(current_c)):
                    return None

                while True:
                    current_c = c()
                    if current_c is None or not _is_ascii_digit(ord(current_c)):
                        break
                    number = int(current_c)
                    if ipv4_piece is None:
                        ipv4_piece = number
                    elif ipv4_piece == 0:
                        return None
                    else:
                        ipv4_piece = ipv4_piece * 10 + number
                    if ipv4_piece > 255:
                        return None
                    pointer += 1

                address[piece_index] = address[piece_index] * 0x100 + (ipv4_piece or 0)
                numbers_seen += 1

                if numbers_seen in (2, 4):
                    piece_index += 1

            if numbers_seen != 4:
                return None
            break

        elif c() == ":":
            pointer += 1
            if c() is None:
                return None
        elif c() is not None:
            return None

        address[piece_index] = value
        piece_index += 1

    if compress is not None:
        swaps = piece_index - compress
        piece_index = 7
        while piece_index != 0 and swaps > 0:
            swap_idx = compress + swaps - 1
            address[piece_index], address[swap_idx] = (
                address[swap_idx],
                address[piece_index],
            )
            piece_index -= 1
            swaps -= 1
    elif compress is None and piece_index != 8:
        return None

    return address


def _serialize_host(host: HostType) -> str:
    """Serialize a host (domain, IPv4, or IPv6) to string."""
    if host is None:
        return ""
    if isinstance(host, int):
        return _serialize_ipv4(host)
    if isinstance(host, list):
        return f"[{_serialize_ipv6(host)}]"
    return host


def _ends_in_number(input_str: str) -> bool:
    parts = input_str.split(".")
    if parts and parts[-1] == "":
        if len(parts) == 1:
            return False
        parts.pop()

    if not parts:
        return False

    last = parts[-1]

    if _parse_ipv4_number(last) is not None:
        return True

    return last.isdigit()


def _parse_opaque_host(input_str: str) -> Optional[str]:
    for char in input_str:
        if char in FORBIDDEN_HOST_CODE_POINTS and char != "%":
            return None

    return _utf8_percent_encode_string(input_str, _is_c0_control_percent_encode)


def _parse_host(input_str: str, is_opaque: bool = False) -> Optional[HostType]:
    """Parse a host string per WHATWG URL Standard.

    Args:
        input_str: The host string to parse.
        is_opaque: True for non-special URL schemes.

    Returns:
        Parsed host (str for domain, int for IPv4, list for IPv6), or None on failure.
    """
    if input_str.startswith("["):
        if not input_str.endswith("]"):
            return None
        return _parse_ipv6(input_str[1:-1])

    if is_opaque:
        return _parse_opaque_host(input_str)

    decoded = _percent_decode_string(input_str)
    try:
        domain = decoded.decode("utf-8")
    except UnicodeDecodeError:
        return None

    ascii_domain = domain_to_ascii(domain)
    if ascii_domain is None:
        return None

    if _ends_in_number(ascii_domain):
        return _parse_ipv4(ascii_domain)

    return ascii_domain
