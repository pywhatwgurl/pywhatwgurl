# URLSearchParams

The `URLSearchParams` class provides utilities for working with URL query strings according to the [WHATWG URL Standard](https://url.spec.whatwg.org/#interface-urlsearchparams).

## Overview

`URLSearchParams` implements Python's `MutableMapping` interface, enabling dictionary-style access alongside WHATWG-compliant methods.

```python
from pywhatwgurl import URLSearchParams

params = URLSearchParams("foo=1&bar=2")
print(params["foo"])      # "1" (Pythonic)
print("bar" in params)    # True (Pythonic)
params["baz"] = "3"       # Pythonic assignment
del params["bar"]         # Pythonic deletion
```

## Pythonic vs WHATWG Methods

| Operation | Pythonic (Preferred) | WHATWG Method |
|-----------|---------------------|---------------|
| Get value | `params["key"]` | `params.get("key")` |
| Set value | `params["key"] = "value"` | `params.set("key", "value")` |
| Delete | `del params["key"]` | `params.delete("key")` |
| Check exists | `"key" in params` | `params.has("key")` |
| Get length | `len(params)` | `params.size` |
| Iterate | `params.items()` | `params.entries()` |
| To string | `str(params)` | `params.to_string()` |

## Constructor

::: pywhatwgurl.URLSearchParams.__init__
    options:
      show_root_heading: false
      heading_level: 3

## Reading Parameters

### get

::: pywhatwgurl.URLSearchParams.get
    options:
      show_root_heading: false
      heading_level: 4

### get_all

Use this method when a parameter may have multiple values.

::: pywhatwgurl.URLSearchParams.get_all
    options:
      show_root_heading: false
      heading_level: 4

### has

::: pywhatwgurl.URLSearchParams.has
    options:
      show_root_heading: false
      heading_level: 4

## Modifying Parameters

### set

::: pywhatwgurl.URLSearchParams.set
    options:
      show_root_heading: false
      heading_level: 4

### append

Use this method to add multiple values for the same key.

::: pywhatwgurl.URLSearchParams.append
    options:
      show_root_heading: false
      heading_level: 4

### delete

::: pywhatwgurl.URLSearchParams.delete
    options:
      show_root_heading: false
      heading_level: 4

### sort

::: pywhatwgurl.URLSearchParams.sort
    options:
      show_root_heading: false
      heading_level: 4

## Iteration

### entries

::: pywhatwgurl.URLSearchParams.entries
    options:
      show_root_heading: false
      heading_level: 4

### keys

::: pywhatwgurl.URLSearchParams.keys
    options:
      show_root_heading: false
      heading_level: 4

### values

::: pywhatwgurl.URLSearchParams.values
    options:
      show_root_heading: false
      heading_level: 4

### items

Pythonic method equivalent to `entries()`.

::: pywhatwgurl.URLSearchParams.items
    options:
      show_root_heading: false
      heading_level: 4

### for_each

::: pywhatwgurl.URLSearchParams.for_each
    options:
      show_root_heading: false
      heading_level: 4

## Size and Serialization

### size

::: pywhatwgurl.URLSearchParams.size
    options:
      show_root_heading: false
      heading_level: 4

### to_string

::: pywhatwgurl.URLSearchParams.to_string
    options:
      show_root_heading: false
      heading_level: 4

## Special Methods

| Method | Usage | Description |
|--------|-------|-------------|
| `__getitem__` | `params["key"]` | Get value (raises `KeyError` if not found) |
| `__setitem__` | `params["key"] = "value"` | Set value (replaces existing) |
| `__delitem__` | `del params["key"]` | Delete key (raises `KeyError` if not found) |
| `__contains__` | `"key" in params` | Check if key exists |
| `__len__` | `len(params)` | Get number of parameters |
| `__iter__` | `for key in params` | Iterate over keys |
| `__str__` | `str(params)` | Convert to query string |

