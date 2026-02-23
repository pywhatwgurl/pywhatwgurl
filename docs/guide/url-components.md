# URL Components

A URL is composed of several components. This guide explains each component and how to access and modify them according to the [WHATWG URL Standard](https://url.spec.whatwg.org/#api).

## URL Structure

A complete URL has the following structure per the [URL representation](https://url.spec.whatwg.org/#url-representation):

```
  https://user:pass@example.com:8080/path/page?query=value#section
  └─┬──┘ └──┬───┘ └────┬─────┘└─┬─┘└────┬────┘└─────┬────┘└───┬──┘
 protocol username   hostname  port  pathname    search     hash
           password            └────────┬───────┘
                                       host
          └────────────────┬───────────────────┘
                          origin
```

## Component Properties

The following properties correspond to the [URL interface](https://url.spec.whatwg.org/#url-class) in the WHATWG specification.

### `href`

The [serialized URL](https://url.spec.whatwg.org/#dom-url-href) as a complete string:

```python
url = URL("https://example.com/path")
print(url.href)  # "https://example.com/path"

# Setting href re-parses the entire URL
url.href = "https://other.com/new"
print(url.hostname)  # "other.com"
```

### `protocol`

The [scheme](https://url.spec.whatwg.org/#dom-url-protocol) followed by `:`:

```python
url = URL("https://example.com")
print(url.protocol)  # "https:"

url.protocol = "http:"
print(url.href)  # "http://example.com/"
```

!!! warning "Protocol Restrictions"
    Changing between [special](https://url.spec.whatwg.org/#special-scheme) and non-special schemes may fail silently or produce unexpected results per the spec.

### `hostname`

The [host](https://url.spec.whatwg.org/#dom-url-hostname) domain name or IP address:

```python
url = URL("https://example.com:8080/path")
print(url.hostname)  # "example.com"

url.hostname = "other.com"
print(url.href)  # "https://other.com:8080/path"
```

### `port`

The [port](https://url.spec.whatwg.org/#dom-url-port) number as a string (empty if default):

```python
url = URL("https://example.com:8080/path")
print(url.port)  # "8080"

url = URL("https://example.com/path")
print(url.port)  # "" (empty, using default 443)

url.port = "9000"
print(url.href)  # "https://example.com:9000/path"
```

### `host`

The [host](https://url.spec.whatwg.org/#dom-url-host) combining hostname and port:

```python
url = URL("https://example.com:8080/path")
print(url.host)  # "example.com:8080"

url = URL("https://example.com/path")
print(url.host)  # "example.com" (no port for default)

url.host = "other.com:3000"
print(url.hostname)  # "other.com"
print(url.port)      # "3000"
```

### `origin`

The [origin](https://url.spec.whatwg.org/#dom-url-origin) (scheme, hostname, and port) — read-only:

```python
url = URL("https://example.com:8080/path?query#hash")
print(url.origin)  # "https://example.com:8080"

# Origin is read-only per the spec
# url.origin = "..."  # This would raise an error
```

!!! info "Origin Serialization"
    Origin is serialized according to the [origin serialization](https://html.spec.whatwg.org/multipage/browsers.html#origin) algorithm in the HTML Standard.

### `username` and `password`

[Credentials](https://url.spec.whatwg.org/#dom-url-username) in the URL:

```python
url = URL("https://user:pass@example.com/path")
print(url.username)  # "user"
print(url.password)  # "pass"

url.username = "newuser"
url.password = "newpass"
print(url.href)  # "https://newuser:newpass@example.com/path"
```

!!! warning "Security Note"
    Embedding credentials in URLs is generally discouraged for security reasons. Consider using HTTP authentication headers instead.

### `pathname`

The [path](https://url.spec.whatwg.org/#dom-url-pathname) portion of the URL:

```python
url = URL("https://example.com/path/to/page")
print(url.pathname)  # "/path/to/page"

url.pathname = "/new/path"
print(url.href)  # "https://example.com/new/path"
```

### `search`

The [query](https://url.spec.whatwg.org/#dom-url-search) string including `?`:

```python
url = URL("https://example.com/path?query=value")
print(url.search)  # "?query=value"

url.search = "?new=query"
print(url.href)  # "https://example.com/path?new=query"

# Remove query string
url.search = ""
print(url.href)  # "https://example.com/path"
```

### `search_params`

A [URLSearchParams](https://url.spec.whatwg.org/#dom-url-searchparams) object for query manipulation (read-only property, but the object is mutable). Supports Pythonic dictionary-style access:

```python
url = URL("https://example.com/path?a=1&b=2")

# Read parameters using dictionary syntax
print(url.search_params["a"])  # "1"

# Modify parameters (updates the URL automatically)
url.search_params["a"] = "100"
url.search_params.append("c", "3")
print(url.search)  # "?a=100&b=2&c=3"

# Delete parameters
del url.search_params["b"]
print(url.search)  # "?a=100&c=3"
```

### `hash`

The [fragment](https://url.spec.whatwg.org/#dom-url-hash) identifier including `#`:

```python
url = URL("https://example.com/path#section")
print(url.hash)  # "#section"

url.hash = "#new-section"
print(url.href)  # "https://example.com/path#new-section"

# Remove hash
url.hash = ""
print(url.href)  # "https://example.com/path"
```

## IPv6 Addresses

IPv6 addresses are enclosed in brackets per [host serialization](https://url.spec.whatwg.org/#concept-host-serializer):

```python
url = URL("https://[::1]:8080/path")
print(url.hostname)  # "[::1]"
print(url.host)      # "[::1]:8080"
```

## Component Encoding

Components are automatically [percent-encoded](https://url.spec.whatwg.org/#percent-encoded-bytes) as needed:

```python
url = URL("https://example.com/path")

# Spaces are encoded in paths
url.pathname = "/hello world"
print(url.pathname)  # "/hello%20world"

# Special characters in query
url.search = "?name=John Doe&city=New York"
print(url.search)  # "?name=John%20Doe&city=New%20York"
```

!!! info "Encode Sets"
    Different URL components use different [percent-encode sets](https://url.spec.whatwg.org/#percent-encode-sets). For example, the query component uses a different set than the path component.

## Further Reading

- [URL interface](https://url.spec.whatwg.org/#url-class) — Complete API specification
- [URL record](https://url.spec.whatwg.org/#concept-url) — Internal URL representation

## Next Steps

- Learn about [URLSearchParams](search-params.md) for query string manipulation
- See the complete [API Reference](../api/url.md)
