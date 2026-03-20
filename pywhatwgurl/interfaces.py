# SPDX-License-Identifier: MIT
"""Abstract interfaces for the WHATWG URL Standard."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, Sequence
from typing import Protocol


class _URLSearchParamsForEachCallback(Protocol):
    def __call__(
        self,
        value: str,
        name: str,
        search_params: "URLSearchParams",
    ) -> object: ...


class URLSearchParams(ABC, MutableMapping[str, str]):
    """Represents a URL query string.

    Implement MutableMapping for dictionary-like access (`params['key']`).
    Adhere to the WHATWG URL Standard: https://url.spec.whatwg.org/#interface-urlsearchparams
    """

    @abstractmethod
    def __init__(
        self,
        init: str
        | Iterable[Sequence[str]]
        | Mapping[str, str | Sequence[str]]
        | "URLSearchParams"
        | None = None,
    ) -> None:
        """Initialize the URLSearchParams object.

        Args:
            init: Initializing object. Can be a query string, iterable of pairs,
                mapping (dict), or valid URLSearchParams object.
        """
        raise NotImplementedError

    @abstractmethod
    def append(self, name: str, value: str) -> None:
        """Append a new name-value pair to the query string.

        Args:
            name: The name of the parameter.
            value: The value of the parameter.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, name: str, value: str | None = None) -> None:
        """Remove all name-value pairs where name is `name`.

        If `value` is provided, only remove pairs where both name and value match.

        Note:
            For deleting by name, `del params[name]` is preferred.
            This method is primarily for WHATWG Spec compliance.

        Args:
            name: The name of the parameter(s) to remove.
            value: The specific value to match. If None, removes all pairs with `name`.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> str | None:  # type: ignore[override]
        """Return the first value associated with the given search parameter.

        Note:
            `params[name]` or `params.get(name)` is preferred.
            This method is primarily for WHATWG Spec compliance.

        Args:
            name: The name of the parameter to retrieve.

        Returns:
            The first value associated with `name`, or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self, name: str) -> tuple[str, ...]:
        """Return all values associated with the given search parameter.

        Args:
            name: The name of the parameter to retrieve.

        Returns:
            A tuple containing all values associated with `name`.
        """
        raise NotImplementedError

    @abstractmethod
    def has(self, name: str, value: str | None = None) -> bool:
        """Return True if `name` exists.

        If `value` is provided, return True only if a pair with `name` and `value` exists.

        Note:
            `name in params` is preferred for checking existence of a key.
            This method is primarily for WHATWG Spec compliance.

        Args:
            name: The name of the parameter to check.
            value: The specific value to check for.

        Returns:
            True if the parameter exists (matching value if provided), False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, name: str, value: str) -> None:
        """Set the value associated with a given search parameter to the given value.

        If there were several values, delete the others.

        Note:
            `params[name] = value` is preferred.
            This method is primarily for WHATWG Spec compliance.

        Args:
            name: The name of the parameter to set.
            value: The value to set.
        """
        raise NotImplementedError

    @abstractmethod
    def sort(self) -> None:
        """Sort all name-value pairs by name.

        Note:
            This method is primarily for WHATWG Spec compliance. Valid URLs do not require sorted parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def to_string(self) -> str:
        """Return the query string suitable for use in a URL.

        Note:
            `str(params)` is preferred.
            This method is primarily for WHATWG Spec compliance.

        Returns:
            The serialized query string.
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return self.to_string()

    @property
    @abstractmethod
    def size(self) -> int:
        """Return the total number of name-value pairs.

        Note:
            `len(params)` is preferred.
            This method is primarily for WHATWG Spec compliance.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        return self.size

    @abstractmethod
    def entries(self) -> Iterator[tuple[str, str]]:
        """Return an iterator over all name-value pairs.

        Note:
            `params.items()` is preferred.
            This method is primarily for WHATWG Spec compliance.

        Returns:
            An iterator yielding (name, value) tuples.
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        return self.keys()

    def keys(self) -> Iterator[str]:  # type: ignore[override]
        """Return an iterator over all parameter names."""
        for key, _ in self.entries():
            yield key

    def values(self) -> Iterator[str]:  # type: ignore[override]
        """Return an iterator over all parameter values."""
        for _, value in self.entries():
            yield value

    def items(self) -> Iterator[tuple[str, str]]:  # type: ignore[override]
        """Return an iterator over all (name, value) pairs."""
        return self.entries()

    @abstractmethod
    def for_each(
        self,
        callback: _URLSearchParamsForEachCallback,
    ) -> None:
        """Iterate through all values.

        Note:
            Pythonic iteration (`for k in params`) is preferred.
            This method is primarily for WHATWG Spec compliance.

        Args:
            callback: Function to call for each element.
        """
        raise NotImplementedError

    def __contains__(self, name: object) -> bool:
        if isinstance(name, str):
            return self.has(name)
        return False

    def __getitem__(self, key: str) -> str:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: str) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        if not self.has(key):
            raise KeyError(key)
        self.delete(key)


class URL(ABC):
    """Represents a URL.

    Adhere to the WHATWG URL Standard: https://url.spec.whatwg.org/#interface-url
    """

    @abstractmethod
    def __init__(self, url: str, base: str | None = None) -> None:
        """Parse `url` relative to `base`.

        Args:
            url: The URL string to parse.
            base: An optional base URL string.

        Raises:
            ValueError: If parsing fails.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def parse(cls, url: str, base: str | None = None) -> "URL" | None:
        """Parse `url` relative to `base`.

        Args:
            url: The URL string to parse.
            base: An optional base URL string.

        Returns:
            A new URL object, or None if parsing fails.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def can_parse(cls, url: str, base: str | None = None) -> bool:
        """Return True if `url` (relative to `base`) can be parsed, False otherwise.

        Args:
            url: The URL string to check.
            base: An optional base URL string.

        Returns:
            True if the URL is valid, False otherwise.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def href(self) -> str:
        """Full URL string."""
        raise NotImplementedError

    @href.setter
    @abstractmethod
    def href(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def origin(self) -> str:
        """The URL's origin."""
        raise NotImplementedError

    @property
    @abstractmethod
    def protocol(self) -> str:
        """URL protocol scheme, ending with ':'."""
        raise NotImplementedError

    @protocol.setter
    @abstractmethod
    def protocol(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def username(self) -> str:
        """URL username."""
        raise NotImplementedError

    @username.setter
    @abstractmethod
    def username(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def password(self) -> str:
        """URL password."""
        raise NotImplementedError

    @password.setter
    @abstractmethod
    def password(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def host(self) -> str:
        """URL host (hostname plus port if non-default)."""
        raise NotImplementedError

    @host.setter
    @abstractmethod
    def host(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def hostname(self) -> str:
        """URL hostname."""
        raise NotImplementedError

    @hostname.setter
    @abstractmethod
    def hostname(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def port(self) -> str:
        """URL port."""
        raise NotImplementedError

    @port.setter
    @abstractmethod
    def port(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def pathname(self) -> str:
        """URL pathname."""
        raise NotImplementedError

    @pathname.setter
    @abstractmethod
    def pathname(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def search(self) -> str:
        """URL query string, starting with '?'."""
        raise NotImplementedError

    @search.setter
    @abstractmethod
    def search(self, value: str) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def search_params(self) -> URLSearchParams:
        """URLSearchParams object representing the query string."""
        raise NotImplementedError

    @property
    @abstractmethod
    def hash(self) -> str:
        """URL fragment identifier, starting with '#'."""
        raise NotImplementedError

    @hash.setter
    @abstractmethod
    def hash(self, value: str) -> None:
        raise NotImplementedError

    def to_json(self) -> str:
        """Return the href, for JSON serialization.

        Note:
            This method is primarily for WHATWG Spec compliance.

        Returns:
            The full URL string.
        """
        return self.href

    def to_string(self) -> str:
        """Return the href.

        Returns:
            The full URL string.
        """
        return self.href

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"URL({self.href!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on the serialized URL (href).

        Args:
            other: The object to compare with.

        Returns:
            True if `other` is a URL object with the same href, False otherwise.
        """
        if isinstance(other, URL):
            return self.href == other.href
        return False

    __hash__ = None  # type: ignore[assignment]
