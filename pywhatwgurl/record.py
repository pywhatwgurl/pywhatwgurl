# SPDX-License-Identifier: MIT
"""URLRecord internal data structure per WHATWG URL Standard."""

from __future__ import annotations

from dataclasses import dataclass, field

from .encoding import SPECIAL_SCHEMES


# Host can be:
# - str: domain or opaque host
# - int: IPv4 address (32-bit integer)
# - list[int]: IPv6 address (8 x 16-bit integers)
HostType = str | int | list[int] | None


@dataclass(slots=True)
class URLRecord:
    """Internal URL representation per WHATWG spec."""

    scheme: str = ""
    username: str = ""
    password: str = ""
    host: HostType = None
    port: int | None = None
    path: list[str] | str = field(default_factory=list)
    query: str | None = None
    fragment: str | None = None

    def is_special(self) -> bool:
        """Return True if this URL has a special scheme."""
        return self.scheme in SPECIAL_SCHEMES

    def has_opaque_path(self) -> bool:
        """Return True if URL has an opaque path (string, not list)."""
        return isinstance(self.path, str)

    def includes_credentials(self) -> bool:
        """Return True if URL has non-empty username or password."""
        return bool(self.username or self.password)

    def cannot_have_username_password_port(self) -> bool:
        """Return True if URL cannot have username/password/port."""
        return self.host is None or self.host == "" or self.scheme == "file"

    def default_port(self) -> int | None:
        """Return the default port for this URL's scheme, or None."""
        return SPECIAL_SCHEMES.get(self.scheme)
