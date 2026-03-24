# SPDX-License-Identifier: MIT
"""URL state machine parser per WHATWG URL Standard."""

from __future__ import annotations

from enum import Enum

from .encoding import (
    C0_CONTROL_AND_SPACE,
    SPECIAL_SCHEMES,
    _CHR,
    _CHR_LOWER,
    _is_ascii_alpha,
    _is_ascii_alphanumeric,
    _is_ascii_digit,
    _is_c0_control_percent_encode,
    _is_fragment_percent_encode,
    _is_path_percent_encode,
    _is_query_percent_encode,
    _is_special_query_percent_encode,
    _is_userinfo_percent_encode,
    _utf8_percent_encode_codepoint,
    _utf8_percent_encode_string,
)
from .host import _parse_host, _serialize_host
from .record import URLRecord


class ParserState(str, Enum):
    """URL parser state machine states per WHATWG spec."""

    SCHEME_START = "scheme start"
    SCHEME = "scheme"
    NO_SCHEME = "no scheme"
    SPECIAL_RELATIVE_OR_AUTHORITY = "special relative or authority"
    PATH_OR_AUTHORITY = "path or authority"
    RELATIVE = "relative"
    RELATIVE_SLASH = "relative slash"
    SPECIAL_AUTHORITY_SLASHES = "special authority slashes"
    SPECIAL_AUTHORITY_IGNORE_SLASHES = "special authority ignore slashes"
    AUTHORITY = "authority"
    HOST = "host"
    HOSTNAME = "hostname"
    PORT = "port"
    FILE = "file"
    FILE_SLASH = "file slash"
    FILE_HOST = "file host"
    PATH_START = "path start"
    PATH = "path"
    OPAQUE_PATH = "opaque path"
    QUERY = "query"
    FRAGMENT = "fragment"


_TAB_NL_CR_TABLE: dict[int, None] = {0x09: None, 0x0A: None, 0x0D: None}

_SINGLE_DOT_SEGMENTS = (".", "%2e")
_DOUBLE_DOT_SEGMENTS = ("..", ".%2e", "%2e.", "%2e%2e")
_WINDOWS_DRIVE_DELIMITERS = (":", "|")
_PATH_TERMINATORS = "/\\?#"


def _is_windows_drive_letter(s: str) -> bool:
    return (
        len(s) == 2 and _is_ascii_alpha(ord(s[0])) and s[1] in _WINDOWS_DRIVE_DELIMITERS
    )


def _is_normalized_windows_drive_letter(s: str) -> bool:
    return len(s) == 2 and _is_ascii_alpha(ord(s[0])) and s[1] == ":"


def _is_single_dot(s: str) -> bool:
    return s.lower() in _SINGLE_DOT_SEGMENTS


def _is_double_dot(s: str) -> bool:
    return s.lower() in _DOUBLE_DOT_SEGMENTS


def _shorten_path(url: URLRecord) -> None:
    path = url.path
    if not isinstance(path, list) or not path:
        return

    if (
        url.scheme == "file"
        and len(path) == 1
        and _is_normalized_windows_drive_letter(path[0])
    ):
        return

    path.pop()


def _starts_with_windows_drive_letter(s: str) -> bool:
    if len(s) < 2:
        return False
    if not _is_ascii_alpha(ord(s[0])):
        return False
    if s[1] not in _WINDOWS_DRIVE_DELIMITERS:
        return False
    if len(s) == 2:
        return True
    return s[2] in _PATH_TERMINATORS


class _URLParser:
    """URL state machine parser per WHATWG spec."""

    def __init__(self) -> None:
        self.url: URLRecord = URLRecord()
        self.base: URLRecord | None = None
        self.input: str = ""
        self.pointer: int = 0
        self.buffer: str = ""
        self.state: ParserState = ParserState.SCHEME_START
        self.state_override: ParserState | None = None
        self.at_sign_seen: bool = False
        self.inside_brackets: bool = False
        self.password_token_seen: bool = False
        self._failure: bool = False
        self._input_codepoints: list[int] = []
        self._cp_len: int = 0

    def _c(self) -> int | None:
        if self.pointer < self._cp_len:
            return self._input_codepoints[self.pointer]
        return None

    def _remaining(self) -> str:
        return self.input[self.pointer + 1 :]

    def _remaining_starts_with(self, s: str) -> bool:
        start = self.pointer + 1
        return self.input[start : start + len(s)] == s

    def parse(
        self,
        input_str: str,
        base: URLRecord | None = None,
        url: URLRecord | None = None,
        state_override: ParserState | None = None,
    ) -> URLRecord | None:
        """Parse a URL string and return a URLRecord, or None on failure."""
        self.base = base
        self.state_override = state_override

        if url is not None:
            self.url = url
        else:
            self.url = URLRecord()
            input_str = input_str.strip(C0_CONTROL_AND_SPACE)

        input_str = input_str.translate(_TAB_NL_CR_TABLE)

        self.input = input_str
        self._input_codepoints = [ord(c) for c in input_str]
        self._cp_len = len(self._input_codepoints)
        self.state = state_override or ParserState.SCHEME_START
        self.pointer = 0
        self.buffer = ""
        self.at_sign_seen = False
        self.inside_brackets = False
        self.password_token_seen = False
        self._failure = False

        dispatch = {
            ParserState.SCHEME_START: self._state_scheme_start,
            ParserState.SCHEME: self._state_scheme,
            ParserState.NO_SCHEME: self._state_no_scheme,
            ParserState.SPECIAL_RELATIVE_OR_AUTHORITY: self._state_special_relative_or_authority,
            ParserState.PATH_OR_AUTHORITY: self._state_path_or_authority,
            ParserState.RELATIVE: self._state_relative,
            ParserState.RELATIVE_SLASH: self._state_relative_slash,
            ParserState.SPECIAL_AUTHORITY_SLASHES: self._state_special_authority_slashes,
            ParserState.SPECIAL_AUTHORITY_IGNORE_SLASHES: self._state_special_authority_ignore_slashes,
            ParserState.AUTHORITY: self._state_authority,
            ParserState.HOST: self._state_hostname,
            ParserState.HOSTNAME: self._state_hostname,
            ParserState.PORT: self._state_port,
            ParserState.FILE: self._state_file,
            ParserState.FILE_SLASH: self._state_file_slash,
            ParserState.FILE_HOST: self._state_file_host,
            ParserState.PATH_START: self._state_path_start,
            ParserState.PATH: self._state_path,
            ParserState.OPAQUE_PATH: self._state_opaque_path,
            ParserState.QUERY: self._state_query,
            ParserState.FRAGMENT: self._state_fragment,
        }
        cp_len = self._cp_len

        while True:
            handler = dispatch.get(self.state)
            if handler is None:
                break
            if not handler():
                break
            if self._failure:
                return None
            self.pointer += 1
            if self.pointer > cp_len:
                break

        return self.url

    def _state_scheme_start(self) -> bool:
        c = self._c()
        if c is not None and _is_ascii_alpha(c):
            self.buffer += _CHR_LOWER[c]
            self.state = ParserState.SCHEME
        elif self.state_override is None:
            self.state = ParserState.NO_SCHEME
            self.pointer -= 1
        else:
            self._failure = True
        return True

    def _state_scheme(self) -> bool:
        c = self._c()
        if c is not None and (
            _is_ascii_alphanumeric(c) or c in (0x2B, 0x2D, 0x2E)  # +, -, .
        ):
            self.buffer += _CHR_LOWER[c]
        elif c == 0x3A:  # :
            if self.state_override is not None:
                if self.url.is_special() and self.buffer not in SPECIAL_SCHEMES:
                    return False
                if not self.url.is_special() and self.buffer in SPECIAL_SCHEMES:
                    return False
                if (
                    self.url.includes_credentials() or self.url.port is not None
                ) and self.buffer == "file":
                    return False
                if self.url.scheme == "file" and self.url.host in (None, ""):
                    return False

            self.url.scheme = self.buffer

            if self.state_override is not None:
                if self.url.port == self.url.default_port():
                    self.url.port = None
                return False

            self.buffer = ""

            if self.url.scheme == "file":
                self.state = ParserState.FILE
            elif self.url.is_special():
                if self.base is not None and self.base.scheme == self.url.scheme:
                    self.state = ParserState.SPECIAL_RELATIVE_OR_AUTHORITY
                else:
                    self.state = ParserState.SPECIAL_AUTHORITY_SLASHES
            elif self._remaining_starts_with("/"):
                self.state = ParserState.PATH_OR_AUTHORITY
                self.pointer += 1
            else:
                self.url.path = ""
                self.state = ParserState.OPAQUE_PATH
        elif self.state_override is None:
            self.buffer = ""
            self.state = ParserState.NO_SCHEME
            self.pointer = -1
        else:
            self._failure = True
        return True

    def _state_no_scheme(self) -> bool:
        c = self._c()
        if self.base is None:
            self._failure = True
        elif self.base.has_opaque_path() and c != 0x23:  # #
            self._failure = True
        elif self.base.has_opaque_path() and c == 0x23:
            self.url.scheme = self.base.scheme
            self.url.path = self.base.path
            self.url.query = self.base.query
            self.url.fragment = ""
            self.state = ParserState.FRAGMENT
        elif self.base.scheme == "file":
            self.state = ParserState.FILE
            self.pointer -= 1
        else:
            self.state = ParserState.RELATIVE
            self.pointer -= 1
        return True

    def _state_special_relative_or_authority(self) -> bool:
        c = self._c()
        if c == 0x2F and self._remaining_starts_with("/"):  # /
            self.state = ParserState.SPECIAL_AUTHORITY_IGNORE_SLASHES
            self.pointer += 1
        else:
            self.state = ParserState.RELATIVE
            self.pointer -= 1
        return True

    def _state_path_or_authority(self) -> bool:
        c = self._c()
        if c == 0x2F:  # /
            self.state = ParserState.AUTHORITY
        else:
            self.state = ParserState.PATH
            self.pointer -= 1
        return True

    def _state_relative(self) -> bool:
        assert self.base is not None
        c = self._c()
        self.url.scheme = self.base.scheme

        if c == 0x2F:  # /
            self.state = ParserState.RELATIVE_SLASH
        elif self.url.is_special() and c == 0x5C:  # \
            self.state = ParserState.RELATIVE_SLASH
        else:
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            if isinstance(self.base.path, list):
                self.url.path = self.base.path.copy()
            else:
                self.url.path = self.base.path
            self.url.query = self.base.query

            if c == 0x3F:  # ?
                self.url.query = ""
                self.state = ParserState.QUERY
            elif c == 0x23:  # #
                self.url.fragment = ""
                self.state = ParserState.FRAGMENT
            elif c is not None:
                self.url.query = None
                if isinstance(self.url.path, list) and self.url.path:
                    self.url.path.pop()
                self.state = ParserState.PATH
                self.pointer -= 1
        return True

    def _state_relative_slash(self) -> bool:
        assert self.base is not None
        c = self._c()
        if self.url.is_special() and c in (0x2F, 0x5C):  # / or \
            self.state = ParserState.SPECIAL_AUTHORITY_IGNORE_SLASHES
        elif c == 0x2F:  # /
            self.state = ParserState.AUTHORITY
        else:
            self.url.username = self.base.username
            self.url.password = self.base.password
            self.url.host = self.base.host
            self.url.port = self.base.port
            self.state = ParserState.PATH
            self.pointer -= 1
        return True

    def _state_special_authority_slashes(self) -> bool:
        c = self._c()
        if c == 0x2F and self._remaining_starts_with("/"):  # /
            self.state = ParserState.SPECIAL_AUTHORITY_IGNORE_SLASHES
            self.pointer += 1
        else:
            self.state = ParserState.SPECIAL_AUTHORITY_IGNORE_SLASHES
            self.pointer -= 1
        return True

    def _state_special_authority_ignore_slashes(self) -> bool:
        c = self._c()
        if c not in (0x2F, 0x5C):  # not / or \
            self.state = ParserState.AUTHORITY
            self.pointer -= 1
        return True

    def _state_authority(self) -> bool:
        c = self._c()

        if c == 0x40:  # @
            if self.at_sign_seen:
                self.buffer = "%40" + self.buffer
            self.at_sign_seen = True

            for char in self.buffer:
                cp = ord(char)
                if cp == 0x3A and not self.password_token_seen:  # :
                    self.password_token_seen = True
                    continue
                encoded = _utf8_percent_encode_codepoint(
                    cp, _is_userinfo_percent_encode
                )
                if self.password_token_seen:
                    self.url.password += encoded
                else:
                    self.url.username += encoded

            self.buffer = ""
        elif (
            c is None
            or c in (0x2F, 0x3F, 0x23)  # /, ?, #
            or (self.url.is_special() and c == 0x5C)  # \
        ):
            if self.at_sign_seen and not self.buffer:
                self._failure = True
                return True
            self.pointer -= len(self.buffer) + 1
            self.buffer = ""
            self.state = ParserState.HOST
        else:
            self.buffer += _CHR[c] if c < 0x80 else chr(c)
        return True

    def _state_hostname(self) -> bool:
        c = self._c()

        if self.state_override is not None and self.url.scheme == "file":
            self.pointer -= 1
            self.state = ParserState.FILE_HOST
        elif c == 0x3A and not self.inside_brackets:  # :
            if not self.buffer:
                self._failure = True
                return True

            if self.state_override == ParserState.HOSTNAME:
                return False

            host = _parse_host(self.buffer, not self.url.is_special())
            if host is None:
                self._failure = True
                return True

            self.url.host = host
            self.buffer = ""
            self.state = ParserState.PORT
        elif (
            c is None
            or c in (0x2F, 0x3F, 0x23)  # /, ?, #
            or (self.url.is_special() and c == 0x5C)  # \
        ):
            self.pointer -= 1

            if self.url.is_special() and not self.buffer:
                self._failure = True
                return True
            elif (
                self.state_override is not None
                and not self.buffer
                and (self.url.includes_credentials() or self.url.port is not None)
            ):
                return False

            host = _parse_host(self.buffer, not self.url.is_special())
            if host is None:
                self._failure = True
                return True

            self.url.host = host
            self.buffer = ""
            self.state = ParserState.PATH_START

            if self.state_override is not None:
                return False
        else:
            if c == 0x5B:  # [
                self.inside_brackets = True
            elif c == 0x5D:  # ]
                self.inside_brackets = False
            self.buffer += _CHR[c] if c < 0x80 else chr(c)
        return True

    def _state_port(self) -> bool:
        c = self._c()

        if c is not None and _is_ascii_digit(c):
            self.buffer += _CHR[c] if c < 0x80 else chr(c)
        elif (
            c is None
            or c in (0x2F, 0x3F, 0x23)  # /, ?, #
            or (self.url.is_special() and c == 0x5C)  # \
            or self.state_override is not None
        ):
            if self.buffer:
                port = int(self.buffer)
                if port > 65535:
                    self._failure = True
                    return True
                self.url.port = None if port == self.url.default_port() else port
                self.buffer = ""

            if self.state_override is not None:
                return False

            self.state = ParserState.PATH_START
            self.pointer -= 1
        else:
            self._failure = True
        return True

    def _state_file(self) -> bool:
        c = self._c()
        self.url.scheme = "file"
        self.url.host = ""

        if c in (0x2F, 0x5C):  # / or \
            self.state = ParserState.FILE_SLASH
        elif self.base is not None and self.base.scheme == "file":
            self.url.host = self.base.host
            if isinstance(self.base.path, list):
                self.url.path = self.base.path.copy()
            else:
                self.url.path = self.base.path
            self.url.query = self.base.query

            if c == 0x3F:  # ?
                self.url.query = ""
                self.state = ParserState.QUERY
            elif c == 0x23:  # #
                self.url.fragment = ""
                self.state = ParserState.FRAGMENT
            elif c is not None:
                self.url.query = None
                if not _starts_with_windows_drive_letter(self.input[self.pointer :]):
                    _shorten_path(self.url)
                else:
                    self.url.path = []
                self.state = ParserState.PATH
                self.pointer -= 1
        else:
            self.state = ParserState.PATH
            self.pointer -= 1
        return True

    def _state_file_slash(self) -> bool:
        c = self._c()
        if c in (0x2F, 0x5C):  # / or \
            self.state = ParserState.FILE_HOST
        else:
            if self.base is not None and self.base.scheme == "file":
                self.url.host = self.base.host
                if (
                    not _starts_with_windows_drive_letter(self.input[self.pointer :])
                    and isinstance(self.base.path, list)
                    and self.base.path
                    and _is_normalized_windows_drive_letter(self.base.path[0])
                ):
                    if isinstance(self.url.path, list):
                        self.url.path.append(self.base.path[0])
            self.state = ParserState.PATH
            self.pointer -= 1
        return True

    def _state_file_host(self) -> bool:
        c = self._c()

        if c is None or c in (0x2F, 0x5C, 0x3F, 0x23):  # /, \, ?, #
            self.pointer -= 1
            if self.state_override is None and _is_windows_drive_letter(self.buffer):
                self.state = ParserState.PATH
            elif not self.buffer:
                self.url.host = ""
                if self.state_override is not None:
                    return False
                self.state = ParserState.PATH_START
            else:
                host = _parse_host(self.buffer, not self.url.is_special())
                if host is None:
                    self._failure = True
                    return True
                if host == "localhost":
                    host = ""
                self.url.host = host

                if self.state_override is not None:
                    return False

                self.buffer = ""
                self.state = ParserState.PATH_START
        else:
            self.buffer += _CHR[c] if c < 0x80 else chr(c)
        return True

    def _state_path_start(self) -> bool:
        c = self._c()
        if self.url.is_special():
            self.state = ParserState.PATH
            if c not in (0x2F, 0x5C):  # / or \
                self.pointer -= 1
        elif self.state_override is None and c == 0x3F:  # ?
            self.url.query = ""
            self.state = ParserState.QUERY
        elif self.state_override is None and c == 0x23:  # #
            self.url.fragment = ""
            self.state = ParserState.FRAGMENT
        elif c is not None:
            self.state = ParserState.PATH
            if c != 0x2F:  # /
                self.pointer -= 1
        elif self.state_override is not None and self.url.host is None:
            if isinstance(self.url.path, list):
                self.url.path.append("")
        return True

    def _state_path(self) -> bool:
        c = self._c()

        if (
            c is None
            or c == 0x2F  # /
            or (self.url.is_special() and c == 0x5C)  # \
            or (self.state_override is None and c in (0x3F, 0x23))  # ?, #
        ):
            if _is_double_dot(self.buffer):
                _shorten_path(self.url)
                if c != 0x2F and not (self.url.is_special() and c == 0x5C):
                    if isinstance(self.url.path, list):
                        self.url.path.append("")
            elif _is_single_dot(self.buffer):
                if c != 0x2F and not (self.url.is_special() and c == 0x5C):
                    if isinstance(self.url.path, list):
                        self.url.path.append("")
            else:
                if (
                    self.url.scheme == "file"
                    and isinstance(self.url.path, list)
                    and not self.url.path
                    and _is_windows_drive_letter(self.buffer)
                ):
                    self.buffer = self.buffer[0] + ":"
                if isinstance(self.url.path, list):
                    self.url.path.append(self.buffer)

            self.buffer = ""

            if c == 0x3F:  # ?
                self.url.query = ""
                self.state = ParserState.QUERY
            elif c == 0x23:  # #
                self.url.fragment = ""
                self.state = ParserState.FRAGMENT
        else:
            self.buffer += _utf8_percent_encode_codepoint(c, _is_path_percent_encode)
        return True

    def _state_opaque_path(self) -> bool:
        c = self._c()

        if c == 0x3F:  # ?
            self.url.query = ""
            self.state = ParserState.QUERY
        elif c == 0x23:  # #
            self.url.fragment = ""
            self.state = ParserState.FRAGMENT
        elif c == 0x20:  # space
            remaining = (
                self._input_codepoints[self.pointer + 1]
                if self.pointer + 1 < len(self._input_codepoints)
                else None
            )
            if remaining in (0x3F, 0x23):  # ? or #
                if isinstance(self.url.path, str):
                    self.url.path += "%20"
            else:
                if isinstance(self.url.path, str):
                    self.url.path += " "
        elif c is not None:
            if isinstance(self.url.path, str):
                self.url.path += _utf8_percent_encode_codepoint(
                    c, _is_c0_control_percent_encode
                )
        return True

    def _state_query(self) -> bool:
        c = self._c()

        if self.state_override is None and c == 0x23:  # #
            predicate = (
                _is_special_query_percent_encode
                if self.url.is_special()
                else _is_query_percent_encode
            )
            self.url.query = (self.url.query or "") + _utf8_percent_encode_string(
                self.buffer, predicate
            )
            self.buffer = ""
            self.url.fragment = ""
            self.state = ParserState.FRAGMENT
        elif c is None:
            predicate = (
                _is_special_query_percent_encode
                if self.url.is_special()
                else _is_query_percent_encode
            )
            self.url.query = (self.url.query or "") + _utf8_percent_encode_string(
                self.buffer, predicate
            )
            self.buffer = ""
        else:
            self.buffer += _CHR[c] if c < 0x80 else chr(c)
        return True

    def _state_fragment(self) -> bool:
        c = self._c()
        if c is not None:
            self.url.fragment = (
                self.url.fragment or ""
            ) + _utf8_percent_encode_codepoint(c, _is_fragment_percent_encode)
        return True


# Singleton parser instance — safe to reuse because parse() fully resets all
# state before each invocation, making __init__ redundant repeated work.
_parser = _URLParser()


def _basic_url_parse(
    input_str: str,
    base: URLRecord | None = None,
    url: URLRecord | None = None,
    state_override: ParserState | None = None,
) -> URLRecord | None:
    """Parse a URL string using the basic URL parser algorithm."""
    return _parser.parse(input_str, base, url, state_override)


def _serialize_url(url: URLRecord, exclude_fragment: bool = False) -> str:
    """Serialize a URLRecord to its string representation."""
    output = url.scheme + ":"

    if url.host is not None:
        output += "//"

        if url.includes_credentials():
            output += url.username
            if url.password:
                output += ":" + url.password
            output += "@"

        output += _serialize_host(url.host)

        if url.port is not None:
            output += ":" + str(url.port)

    if url.has_opaque_path():
        assert isinstance(url.path, str)
        output += url.path
    else:
        assert isinstance(url.path, list)
        if url.host is None and len(url.path) > 1 and url.path[0] == "":
            output += "/."
        for segment in url.path:
            output += "/" + segment

    if url.query is not None:
        output += "?" + url.query

    if not exclude_fragment and url.fragment is not None:
        output += "#" + url.fragment

    return output


def _serialize_url_origin(url: URLRecord) -> str:
    """Serialize a URL's origin per WHATWG spec."""
    match url.scheme:
        case "blob":
            if url.has_opaque_path():
                assert isinstance(url.path, str)
                inner_url = _basic_url_parse(url.path)
                if inner_url is not None and inner_url.scheme in ("http", "https"):
                    return _serialize_url_origin(inner_url)
            return "null"
        case "http" | "https" | "ftp" | "ws" | "wss":
            origin = f"{url.scheme}://{_serialize_host(url.host)}"
            if url.port is not None:
                origin += f":{url.port}"
            return origin
        case _:  # includes "file"
            return "null"
