# SPDX-License-Identifier: MIT
"""WHATWG URL Standard Implementation.

This module provides a complete, spec-compliant implementation of the WHATWG URL
Living Standard (https://url.spec.whatwg.org/).

Public API:
- URL: Parse and manipulate URLs
- URLSearchParams: Parse and manipulate query strings
- domain_to_ascii: Convert domain names to ASCII (IDNA)
- domain_to_unicode: Convert ASCII domain names to Unicode
- percent_encode_after_encoding: Percent-encode a string
"""

from __future__ import annotations

from typing import Optional

from .encoding import (
    _is_userinfo_percent_encode,
    _utf8_percent_encode_string,
    percent_encode_after_encoding,
)
from .host import _serialize_host
from .idna_processor import domain_to_ascii, domain_to_unicode
from .interfaces import URL, URLSearchParams
from .parser import (
    ParserState,
    _basic_url_parse,
    _serialize_url,
    _serialize_url_origin,
)
from .record import URLRecord
from .search_params import (
    URLSearchParamsImpl,
    _parse_urlencoded_string,
)

__all__ = [
    "URL",
    "URLSearchParams",
    "URLImpl",
    "URLSearchParamsImpl",
    "domain_to_ascii",
    "domain_to_unicode",
    "percent_encode_after_encoding",
]


class URLImpl(URL):
    """WHATWG URL Standard implementation.

    A URL object represents a parsed URL and provides properties to read
    and modify its components. This class implements the URL interface
    defined in the WHATWG URL Standard.

    Examples:
        Basic URL parsing and component access:

        ```python
        from pywhatwgurl import URL

        url = URL("https://example.com:8080/path?q=python#section")
        print(url.hostname)  # "example.com"
        print(url.port)      # "8080"
        ```

        Query parameter manipulation using Pythonic syntax:

        ```python
        print(url.search_params["q"])  # "python"
        url.search_params["page"] = "2"
        print(url.search)  # "?q=python&page=2"
        ```

    Note:
        Method documentation is inherited from the URL interface.
    """

    def __init__(self, url: str, base: Optional[str] = None) -> None:
        parsed_base: Optional[URLRecord] = None
        if base is not None:
            parsed_base = _basic_url_parse(base)
            if parsed_base is None:
                raise ValueError(f"Invalid base URL: {base}")

        parsed_url = _basic_url_parse(url, base=parsed_base)
        if parsed_url is None:
            raise ValueError(f"Invalid URL: {url}")

        self._url = parsed_url
        self._query = URLSearchParamsImpl()
        self._query._list = _parse_urlencoded_string(parsed_url.query or "")
        self._query._url = self

    @classmethod
    def parse(cls, url: str, base: Optional[str] = None) -> Optional["URLImpl"]:
        try:
            return cls(url, base)
        except ValueError:
            return None

    @classmethod
    def can_parse(cls, url: str, base: Optional[str] = None) -> bool:
        return cls.parse(url, base) is not None

    @property
    def href(self) -> str:
        return _serialize_url(self._url)

    @href.setter
    def href(self, value: str) -> None:
        parsed = _basic_url_parse(value)
        if parsed is None:
            raise ValueError(f"Invalid URL: {value}")

        self._url = parsed
        # Mutate in-place so iterators see the updated data
        new_params = _parse_urlencoded_string(parsed.query or "")
        self._query._list.clear()
        self._query._list.extend(new_params)

    @property
    def origin(self) -> str:
        return _serialize_url_origin(self._url)

    @property
    def protocol(self) -> str:
        return self._url.scheme + ":"

    @protocol.setter
    def protocol(self, value: str) -> None:
        _basic_url_parse(
            value + ":", url=self._url, state_override=ParserState.SCHEME_START
        )

    @property
    def username(self) -> str:
        return self._url.username

    @username.setter
    def username(self, value: str) -> None:
        if self._url.cannot_have_username_password_port():
            return
        self._url.username = _utf8_percent_encode_string(
            value, _is_userinfo_percent_encode
        )

    @property
    def password(self) -> str:
        return self._url.password

    @password.setter
    def password(self, value: str) -> None:
        if self._url.cannot_have_username_password_port():
            return
        self._url.password = _utf8_percent_encode_string(
            value, _is_userinfo_percent_encode
        )

    @property
    def host(self) -> str:
        if self._url.host is None:
            return ""
        if self._url.port is None:
            return _serialize_host(self._url.host)
        return f"{_serialize_host(self._url.host)}:{self._url.port}"

    @host.setter
    def host(self, value: str) -> None:
        if self._url.has_opaque_path():
            return
        _basic_url_parse(value, url=self._url, state_override=ParserState.HOST)

    @property
    def hostname(self) -> str:
        if self._url.host is None:
            return ""
        return _serialize_host(self._url.host)

    @hostname.setter
    def hostname(self, value: str) -> None:
        if self._url.has_opaque_path():
            return
        _basic_url_parse(value, url=self._url, state_override=ParserState.HOSTNAME)

    @property
    def port(self) -> str:
        if self._url.port is None:
            return ""
        return str(self._url.port)

    @port.setter
    def port(self, value: str) -> None:
        if self._url.cannot_have_username_password_port():
            return
        if value == "":
            self._url.port = None
        else:
            _basic_url_parse(value, url=self._url, state_override=ParserState.PORT)

    @property
    def pathname(self) -> str:
        if self._url.has_opaque_path():
            return self._url.path  # type: ignore[return-value]
        if not self._url.path:
            return ""
        return "/" + "/".join(self._url.path)

    @pathname.setter
    def pathname(self, value: str) -> None:
        if self._url.has_opaque_path():
            return
        self._url.path = []
        _basic_url_parse(value, url=self._url, state_override=ParserState.PATH_START)

    @property
    def search(self) -> str:
        if self._url.query is None or self._url.query == "":
            return ""
        return "?" + self._url.query

    @search.setter
    def search(self, value: str) -> None:
        if value == "":
            self._url.query = None
            self._query._list.clear()
            return

        input_str = value[1:] if value.startswith("?") else value
        self._url.query = ""
        _basic_url_parse(input_str, url=self._url, state_override=ParserState.QUERY)
        # Mutate in-place so iterators see the updated data
        new_params = _parse_urlencoded_string(input_str)
        self._query._list.clear()
        self._query._list.extend(new_params)

    @property
    def search_params(self) -> URLSearchParams:
        return self._query

    @property
    def hash(self) -> str:
        if self._url.fragment is None or self._url.fragment == "":
            return ""
        return "#" + self._url.fragment

    @hash.setter
    def hash(self, value: str) -> None:
        if value == "":
            self._url.fragment = None
            return

        input_str = value[1:] if value.startswith("#") else value
        self._url.fragment = ""
        _basic_url_parse(input_str, url=self._url, state_override=ParserState.FRAGMENT)
