from typing import Iterator, Optional, Tuple, Union
from pywhatwgurl.interfaces import URL, URLSearchParams, _URLSearchParamsForEachCallback


class MockURLSearchParams(URLSearchParams):
    def __init__(
        self,
        init: Optional[Union[str, list, tuple, dict, "MockURLSearchParams"]] = None,
    ):
        self._store = {}
        if init:
            if isinstance(init, dict):
                for k, v in init.items():
                    # Simplified: if sequence (list/tuple) but not str, take first item for simple dict-like mocking
                    if not isinstance(v, str) and isinstance(v, (list, tuple)):
                        self._store[k] = v[0] if v else ""
                    else:
                        self._store[k] = str(v)
            elif isinstance(init, str):
                pass  # Parse string not implemented in mock
            else:
                # Assume iterable of pairs
                for item in init:
                    if len(item) == 2:
                        self._store[item[0]] = item[1]

    def append(self, name: str, value: str) -> None:
        self._store[name] = value

    def delete(self, name: str, value: Optional[str] = None) -> None:
        if name in self._store:
            del self._store[name]

    def get(self, name: str) -> Optional[str]:
        return self._store.get(name)

    def get_all(self, name: str) -> Tuple[str, ...]:
        return (self._store[name],) if name in self._store else ()

    def has(self, name: str, value: Optional[str] = None) -> bool:
        return name in self._store

    def set(self, name: str, value: str) -> None:
        self._store[name] = value

    def sort(self) -> None:
        pass

    def to_string(self) -> str:
        return ""

    @property
    def size(self) -> int:
        return len(self._store)

    def entries(self) -> Iterator[Tuple[str, str]]:
        return iter(self._store.items())

    def for_each(
        self, callback: _URLSearchParamsForEachCallback, this_arg: object = None
    ) -> None:
        pass


class MockURL(URL):
    def __init__(self, url: str, base: Optional[str] = None):
        self._href = url

    @property
    def href(self) -> str:
        return self._href

    @href.setter
    def href(self, value: str) -> None:
        self._href = value

    # Minimal implementation of other abstract methods
    def can_parse(cls, url: str, base: Optional[str] = None) -> bool:
        return True

    def parse(cls, url: str, base: Optional[str] = None) -> Optional["URL"]:
        return None

    @property
    def origin(self) -> str:
        return ""

    @property
    def protocol(self) -> str:
        return ""

    @protocol.setter
    def protocol(self, value: str) -> None:
        pass

    @property
    def username(self) -> str:
        return ""

    @username.setter
    def username(self, value: str) -> None:
        pass

    @property
    def password(self) -> str:
        return ""

    @password.setter
    def password(self, value: str) -> None:
        pass

    @property
    def host(self) -> str:
        return ""

    @host.setter
    def host(self, value: str) -> None:
        pass

    @property
    def hostname(self) -> str:
        return ""

    @hostname.setter
    def hostname(self, value: str) -> None:
        pass

    @property
    def port(self) -> str:
        return ""

    @port.setter
    def port(self, value: str) -> None:
        pass

    @property
    def pathname(self) -> str:
        return ""

    @pathname.setter
    def pathname(self, value: str) -> None:
        pass

    @property
    def search(self) -> str:
        return ""

    @search.setter
    def search(self, value: str) -> None:
        pass

    @property
    def search_params(self) -> URLSearchParams:
        return MockURLSearchParams()

    @property
    def hash(self) -> str:
        return ""

    @hash.setter
    def hash(self, value: str) -> None:
        pass
