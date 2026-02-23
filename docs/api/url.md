# URL

The `URL` class represents a parsed URL and provides methods to inspect and manipulate its components according to the [WHATWG URL Standard](https://url.spec.whatwg.org/#url-class).

## Overview

```python
from pywhatwgurl import URL

url = URL("https://example.com:8080/path?q=python#section")
print(url.hostname)  # "example.com"
print(url.search_params["q"])  # "python"
```

## Constructor

::: pywhatwgurl.URL.__init__
    options:
      show_root_heading: false
      heading_level: 3

## Static Methods

These methods provide alternative ways to parse URLs without raising exceptions.

### parse

::: pywhatwgurl.URL.parse
    options:
      show_root_heading: false
      heading_level: 4

### can_parse

::: pywhatwgurl.URL.can_parse
    options:
      show_root_heading: false
      heading_level: 4

## URL Components

All component properties are readable and writable (except `origin` and `search_params` which are read-only).

!!! info "WHATWG Spec Compliance"
    These properties correspond directly to the [URL class](https://url.spec.whatwg.org/#url-class) interface in the WHATWG URL Standard.

### href

::: pywhatwgurl.URL.href
    options:
      show_root_heading: false
      heading_level: 4

### origin

::: pywhatwgurl.URL.origin
    options:
      show_root_heading: false
      heading_level: 4

### protocol

::: pywhatwgurl.URL.protocol
    options:
      show_root_heading: false
      heading_level: 4

### username

::: pywhatwgurl.URL.username
    options:
      show_root_heading: false
      heading_level: 4

### password

::: pywhatwgurl.URL.password
    options:
      show_root_heading: false
      heading_level: 4

### host

::: pywhatwgurl.URL.host
    options:
      show_root_heading: false
      heading_level: 4

### hostname

::: pywhatwgurl.URL.hostname
    options:
      show_root_heading: false
      heading_level: 4

### port

::: pywhatwgurl.URL.port
    options:
      show_root_heading: false
      heading_level: 4

### pathname

::: pywhatwgurl.URL.pathname
    options:
      show_root_heading: false
      heading_level: 4

### search

::: pywhatwgurl.URL.search
    options:
      show_root_heading: false
      heading_level: 4

### search_params

::: pywhatwgurl.URL.search_params
    options:
      show_root_heading: false
      heading_level: 4

### hash

::: pywhatwgurl.URL.hash
    options:
      show_root_heading: false
      heading_level: 4

## Serialization Methods

!!! note "Pythonic Usage"
    Prefer `str(url)` over `url.to_string()`. These methods exist for WHATWG spec compliance.

### to_string

::: pywhatwgurl.URL.to_string
    options:
      show_root_heading: false
      heading_level: 4

### to_json

::: pywhatwgurl.URL.to_json
    options:
      show_root_heading: false
      heading_level: 4

## Special Methods

| Method | Usage | Description |
|--------|-------|-------------|
| `__str__` | `str(url)` | Returns the full URL string |
| `__repr__` | `repr(url)` | Returns `URL('...')` representation |
| `__eq__` | `url1 == url2` | Compares URLs by `href` |
| `__hash__` | — | `None` (URLs are mutable, not hashable) |
