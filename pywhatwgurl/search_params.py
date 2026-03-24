# SPDX-License-Identifier: MIT
"""URLSearchParams implementation per WHATWG URL Standard."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import TYPE_CHECKING

from .encoding import (
    _is_urlencoded_percent_encode,
    _percent_decode_bytes,
    _utf8_percent_encode_string,
)
from .interfaces import URLSearchParams, _URLSearchParamsForEachCallback

if TYPE_CHECKING:
    from .url import URLImpl


def _decode_utf8_lossy(data: bytes) -> str:
    """Decode bytes as UTF-8, replacing invalid sequences."""
    return data.decode("utf-8", errors="replace")


def _parse_urlencoded(data: bytes) -> list[tuple[str, str]]:
    """Parse application/x-www-form-urlencoded bytes into name-value pairs."""
    result: list[tuple[str, str]] = []

    for sequence in data.split(b"&"):
        if not sequence:
            continue

        eq_index = sequence.find(b"=")
        if eq_index >= 0:
            name = sequence[:eq_index]
            value = sequence[eq_index + 1 :]
        else:
            name = sequence
            value = b""

        name_str = _decode_utf8_lossy(_percent_decode_bytes(name.replace(b"+", b" ")))
        value_str = _decode_utf8_lossy(_percent_decode_bytes(value.replace(b"+", b" ")))

        result.append((name_str, value_str))

    return result


def _parse_urlencoded_string(s: str) -> list[tuple[str, str]]:
    """Parse application/x-www-form-urlencoded string into name-value pairs."""
    return _parse_urlencoded(s.encode("utf-8"))


def _serialize_urlencoded(tuples: list[tuple[str, str]]) -> str:
    """Serialize name-value pairs to application/x-www-form-urlencoded format."""
    return "&".join(
        f"{_utf8_percent_encode_string(name, _is_urlencoded_percent_encode, space_as_plus=True)}"
        f"={_utf8_percent_encode_string(value, _is_urlencoded_percent_encode, space_as_plus=True)}"
        for name, value in tuples
    )


class URLSearchParamsImpl(URLSearchParams):
    """WHATWG URLSearchParams implementation.

    Provides methods to work with the query string of a URL. Supports
    Pythonic dictionary-style access as well as all standard URLSearchParams
    methods.

    Examples:
        Basic usage with dictionary-style access:

        ```python
        from pywhatwgurl import URLSearchParams

        params = URLSearchParams("foo=1&bar=2")
        print(params["foo"])      # "1"
        print("bar" in params)    # True
        print(len(params))        # 2
        ```

        Modifying parameters:

        ```python
        params["baz"] = "3"
        del params["bar"]
        print(str(params))  # "foo=1&baz=3"
        ```

    Note:
        Method documentation is inherited from the URLSearchParams interface.
    """

    def __init__(
        self,
        init: str
        | Iterable[Sequence[str]]
        | Mapping[str, str | Sequence[str]]
        | "URLSearchParamsImpl"
        | None = None,
    ) -> None:
        self._list: list[tuple[str, str]] = []
        self._url: URLImpl | None = None

        if init is None:
            return

        if isinstance(init, str):
            if init.startswith("?"):
                init = init[1:]
            self._list = _parse_urlencoded_string(init)
        elif isinstance(init, URLSearchParamsImpl):
            self._list = list(init._list)
        elif isinstance(init, Mapping):
            for key, val in init.items():
                if isinstance(val, str):
                    self._list.append((key, val))
                else:
                    for item in val:
                        self._list.append((key, item))
        else:
            for pair in init:
                seq = list(pair)
                if len(seq) != 2:
                    raise TypeError(
                        "Failed to construct 'URLSearchParams': "
                        "parameter 1 sequence's element does not contain exactly two elements."
                    )
                self._list.append((str(seq[0]), str(seq[1])))

    def _update_steps(self) -> None:
        if self._url is not None:
            serialized = _serialize_urlencoded(self._list)
            self._url._url.query = serialized if serialized else None

    def append(self, name: str, value: str) -> None:
        self._list.append((name, value))
        self._update_steps()

    def delete(self, name: str, value: str | None = None) -> None:
        self._list[:] = [
            (n, v)
            for n, v in self._list
            if not (n == name and (value is None or v == value))
        ]
        self._update_steps()

    def get(self, name: str) -> str | None:  # type: ignore[override]
        for n, v in self._list:
            if n == name:
                return v
        return None

    def get_all(self, name: str) -> tuple[str, ...]:
        return tuple(v for n, v in self._list if n == name)

    def has(self, name: str, value: str | None = None) -> bool:
        return any(n == name and (value is None or v == value) for n, v in self._list)

    def set(self, name: str, value: str) -> None:
        found = False
        i = 0
        while i < len(self._list):
            if self._list[i][0] == name:
                if found:
                    self._list.pop(i)
                else:
                    self._list[i] = (name, value)
                    found = True
                    i += 1
            else:
                i += 1
        if not found:
            self._list.append((name, value))
        self._update_steps()

    def sort(self) -> None:
        # Sort by name using UTF-16 code unit ordering per WHATWG spec
        def utf16_sort_key(item: tuple[str, str]) -> list[int]:
            encoded = item[0].encode("utf-16-be")
            return [
                int.from_bytes(encoded[i : i + 2], "big")
                for i in range(0, len(encoded), 2)
            ]

        self._list.sort(key=utf16_sort_key)
        self._update_steps()

    def to_string(self) -> str:
        return _serialize_urlencoded(self._list)

    @property
    def size(self) -> int:
        return len(self._list)

    def entries(self) -> Iterator[tuple[str, str]]:
        return iter(self._list)

    def for_each(self, callback: _URLSearchParamsForEachCallback) -> None:
        for name, value in self._list:
            callback(value, name, self)
