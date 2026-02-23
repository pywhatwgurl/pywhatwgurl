# Migrating from urllib.parse

This guide helps you migrate from Python's `urllib.parse` module to pywhatwgurl. It covers equivalent APIs, behavioral differences, and common patterns.

!!! note "Different Standards"
    `urllib.parse` follows [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986) while pywhatwgurl implements the [WHATWG URL Standard](https://url.spec.whatwg.org/). These standards intentionally differ in how they parse URLs. This guide highlights where behavior diverges so you can migrate with confidence.

## Quick Reference

| `urllib.parse` | pywhatwgurl | Notes |
|----------------|-------------|-------|
| `urlparse(url)` | `URL(url)` | Returns an object with named properties instead of a tuple |
| `urlsplit(url)` | `URL(url)` | Same as above (`params` is not a WHATWG concept) |
| `urljoin(base, url)` | `URL(url, base).href` | Argument order is reversed |
| `parse_qs(qs)` | `URLSearchParams(qs)` | Returns a mapping-like object, not `dict[str, list]` |
| `parse_qsl(qs)` | `list(URLSearchParams(qs).items())` | Returns `list[tuple[str, str]]` |
| `quote(s)` | Automatic per-component encoding | See [Percent-Encoding](#percent-encoding) |
| `unquote(s)` | Automatic on parsed URL properties | Decoded values accessible via properties |
| `quote_plus(s)` | `str(URLSearchParams({"k": s}))` | Spaces → `+` in query strings |
| `urlunparse(parts)` | Build with `URL` + property setters | See [Building URLs](#building-urls-from-parts) |
| `urlencode(query)` | `str(URLSearchParams(query))` | Accepts dict or list of tuples |

## Parsing URLs

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import urlparse

    result = urlparse("https://user:pass@example.com:8080/path?q=1#frag")
    print(result.scheme)    # "https"
    print(result.netloc)    # "user:pass@example.com:8080"
    print(result.hostname)  # "example.com"
    print(result.port)      # 8080 (int)
    print(result.path)      # "/path"
    print(result.query)     # "q=1"
    print(result.fragment)  # "frag"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URL

    url = URL("https://user:pass@example.com:8080/path?q=1#frag")
    print(url.protocol)  # "https:"  (includes colon)
    print(url.host)      # "example.com:8080"
    print(url.hostname)  # "example.com"
    print(url.port)      # "8080"  (string, not int)
    print(url.pathname)  # "/path"
    print(url.search)    # "?q=1"  (includes ?)
    print(url.hash)      # "#frag" (includes #)
    print(url.username)  # "user"
    print(url.password)  # "pass"
    ```

Key differences:

- `protocol` includes the trailing colon (`"https:"` vs `"https"`)
- `search` includes the leading `?` (`"?q=1"` vs `"q=1"`)
- `hash` includes the leading `#` (`"#frag"` vs `"frag"`)
- `port` is a string, not an integer
- There is no `netloc` — use `host`, `hostname`, `username`, `password` separately
- There is no `params` — semicolons in paths are not treated specially

## Joining URLs

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import urljoin

    result = urljoin("https://example.com/docs/", "../api/v2")
    print(result)  # "https://example.com/api/v2"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URL

    url = URL("../api/v2", "https://example.com/docs/")
    print(url.href)  # "https://example.com/api/v2"
    ```

!!! warning "Argument Order"
    `urljoin(base, url)` takes base first, but `URL(url, base)` takes the URL first and base second. This matches the [WHATWG URL constructor](https://url.spec.whatwg.org/#dom-url-url).

## Query String Parsing

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import parse_qs, parse_qsl

    # parse_qs returns dict with list values
    result = parse_qs("tag=a&tag=b&lang=py")
    print(result)  # {"tag": ["a", "b"], "lang": ["py"]}

    # parse_qsl returns list of tuples
    result = parse_qsl("tag=a&tag=b&lang=py")
    print(result)  # [("tag", "a"), ("tag", "b"), ("lang", "py")]
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URLSearchParams

    params = URLSearchParams("tag=a&tag=b&lang=py")

    # Dictionary-style access (first value)
    print(params["lang"])  # "py"

    # All values for a key
    print(params.get_all("tag"))  # ("a", "b")

    # As list of tuples (like parse_qsl)
    print(list(params.items()))  # [("tag", "a"), ("tag", "b"), ("lang", "py")]
    ```

!!! note "Separator Differences"
    `parse_qs` treats both `&` and `;` as separators by default. `URLSearchParams` only uses `&` per the [WHATWG spec](https://url.spec.whatwg.org/#concept-urlencoded-parser). If your data uses `;` as a separator, you'll need to replace it before parsing.

## Query String Building

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import urlencode

    query = urlencode({"search": "hello world", "page": "2"})
    print(query)  # "search=hello+world&page=2"

    # With sequences
    query = urlencode([("tag", "a"), ("tag", "b")], doseq=True)
    print(query)  # "tag=a&tag=b"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URLSearchParams

    params = URLSearchParams({"search": "hello world", "page": "2"})
    print(str(params))  # "search=hello+world&page=2"

    # With multiple values
    params = URLSearchParams([("tag", "a"), ("tag", "b")])
    print(str(params))  # "tag=a&tag=b"
    ```

## Percent-Encoding

`urllib.parse` provides explicit `quote()` / `unquote()` functions. pywhatwgurl encodes automatically when you set URL properties, using the correct [percent-encode set](https://url.spec.whatwg.org/#percent-encode-sets) for each component.

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import quote, unquote

    encoded = quote("/path/hello world", safe="/")
    print(encoded)  # "/path/hello%20world"

    decoded = unquote("/path/hello%20world")
    print(decoded)  # "/path/hello world"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URL

    url = URL("https://example.com")
    url.pathname = "/path/hello world"
    print(url.pathname)  # "/path/hello%20world" (auto-encoded)
    ```

For standalone encoding, use `percent_encode_after_encoding`:

```python
from pywhatwgurl import percent_encode_after_encoding

result = percent_encode_after_encoding("hello world")
print(result)  # "hello%20world"
```

!!! info "Encoding Differences"
    `urllib.parse.quote` uses a `safe` parameter to specify characters that should *not* be encoded. WHATWG uses component-specific encode sets — the path, query, fragment, and userinfo components each have different rules for which characters require encoding. This means the same character may be encoded differently depending on where it appears.

## Building URLs from Parts

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import urlunparse

    url = urlunparse((
        "https",           # scheme
        "example.com:443", # netloc
        "/api/v2",         # path
        "",                # params
        "key=value",       # query
        "section",         # fragment
    ))
    print(url)  # "https://example.com:443/api/v2?key=value#section"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URL

    # Start with a base and set components
    url = URL("https://example.com")
    url.pathname = "/api/v2"
    url.search = "key=value"
    url.hash = "section"
    print(url.href)  # "https://example.com/api/v2?key=value#section"
    ```

!!! tip "Default Port Normalization"
    Notice that pywhatwgurl omits the default port (443 for HTTPS) during serialization, while `urlunparse` preserves whatever you pass in. This normalization is required by the [WHATWG URL serializer](https://url.spec.whatwg.org/#url-serializing).

## Error Handling

=== "Before (urllib.parse)"

    ```python
    from urllib.parse import urlparse

    # urllib.parse never raises — it returns a result for any input
    result = urlparse("not a url")
    print(result.scheme)  # ""
    print(result.path)    # "not a url"
    ```

=== "After (pywhatwgurl)"

    ```python
    from pywhatwgurl import URL

    # URL() raises ValueError for invalid input
    try:
        url = URL("not a url")
    except ValueError:
        print("Invalid URL")

    # Use URL.parse() for non-throwing behavior
    url = URL.parse("not a url")  # Returns None

    # Use URL.can_parse() to check validity
    if URL.can_parse("https://example.com"):
        url = URL("https://example.com")
    ```

## Behavioral Differences

The following table summarizes how the same input is parsed differently:

| Input | `urllib.parse` | pywhatwgurl | Why |
|-------|---------------|-------------|-----|
| `http://example.com\path` | path = `\path` | pathname = `/path` | WHATWG normalizes `\` to `/` in special schemes |
| `HTTP://EXAMPLE.COM` | scheme = `http`, netloc = `EXAMPLE.COM` | protocol = `http:`, hostname = `example.com` | WHATWG lowercases hosts |
| `http://example.com:80/` | port = `80` | port = `""` | WHATWG omits default ports |
| `http://例え.jp` | raises or preserves Unicode | hostname = `xn--r8jz45g.jp` | WHATWG applies IDNA encoding |
| `http:///path` | netloc = `""`, path = `/path` | hostname = `""`, pathname = `/path` | Both preserve empty authority |

## What Doesn't Map

Some `urllib.parse` concepts have no WHATWG equivalent:

- **`params` (semicolons in paths)**: `urlparse` supports a `params` component separated by `;` in the path. WHATWG does not recognize this — semicolons are treated as regular path characters.
- **`netloc` as a single string**: WHATWG tracks `username`, `password`, `hostname`, and `port` as separate fields. Use `url.host` for `hostname:port`.
- **`safe` parameter for encoding**: WHATWG uses fixed, component-specific encode sets. There is no way to customize which characters are encoded in the URL parser.
- **Scheme-generic parsing**: `urllib.parse` parses any `scheme://...` generically. WHATWG has [special schemes](https://url.spec.whatwg.org/#special-scheme) (`http`, `https`, `ftp`, `ws`, `wss`, `file`) with specific rules, and treats non-special schemes differently (opaque paths, no authority).

## Common Patterns

### Extracting the Domain

```python
from pywhatwgurl import URL

url = URL("https://subdomain.example.com:8080/path")
print(url.hostname)  # "subdomain.example.com"
```

### Checking if a URL is Valid

```python
from pywhatwgurl import URL

if URL.can_parse("https://example.com"):
    print("Valid URL")
```

### Normalizing a URL

```python
from pywhatwgurl import URL

# WHATWG parsing + serialization normalizes the URL
normalized = URL("HTTP://Example.COM:80/a/../b").href
print(normalized)  # "http://example.com/b"
```

### Modifying Query Parameters

```python
from pywhatwgurl import URL

url = URL("https://example.com/search?q=python&page=1")
url.search_params["page"] = "2"
url.search_params["sort"] = "date"
del url.search_params["q"]
print(url.href)  # "https://example.com/search?page=2&sort=date"
```

## Further Reading

- [URL Parsing](url-parsing.md) — How pywhatwgurl parses URLs
- [URL Components](url-components.md) — All URL properties explained
- [URLSearchParams](search-params.md) — Query string manipulation
- [WHATWG URL Standard](https://url.spec.whatwg.org/) — The complete specification
