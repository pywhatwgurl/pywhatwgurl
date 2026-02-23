# URL Parsing

This guide covers how pywhatwgurl parses URLs according to the [WHATWG URL Standard](https://url.spec.whatwg.org/).

## The URL Constructor

The `URL` class constructor accepts one or two arguments:

```python
URL(url: str, base: str | URL | None = None)
```

- **url**: The URL string to parse
- **base**: Optional base URL for resolving relative URLs

!!! info "Spec Reference"
    See [URL class constructor](https://url.spec.whatwg.org/#dom-url-url) in the WHATWG URL Standard.

## Absolute URLs

An absolute URL contains all the information needed to locate a resource:

```python
from pywhatwgurl import URL

# Complete absolute URL
url = URL("https://example.com:8080/path?query#hash")

# Minimal absolute URL (just scheme and host)
url = URL("https://example.com")
```

## Relative URLs

Relative URLs are resolved against a base URL using the [URL parsing algorithm](https://url.spec.whatwg.org/#concept-url-parser):

```python
from pywhatwgurl import URL

base = URL("https://example.com/docs/guide/intro.html")

# Path-relative
URL("./images/logo.png", base)  # https://example.com/docs/guide/images/logo.png

# Parent directory
URL("../api/", base)  # https://example.com/docs/api/

# Root-relative
URL("/absolute/path", base)  # https://example.com/absolute/path

# Protocol-relative
URL("//other.com/path", base)  # https://other.com/path

# Query-only
URL("?newquery", base)  # https://example.com/docs/guide/intro.html?newquery

# Fragment-only  
URL("#section", base)  # https://example.com/docs/guide/intro.html#section
```

## URL Normalization

pywhatwgurl normalizes URLs during parsing according to the [URL serialization](https://url.spec.whatwg.org/#concept-url-serializer) rules:

### Scheme Normalization

Schemes are lowercased per the [scheme state](https://url.spec.whatwg.org/#scheme-state):

```python
URL("HTTPS://Example.Com").href  # "https://example.com/"
```

### Host Normalization

Hostnames are lowercased and IDNA-encoded per [host parsing](https://url.spec.whatwg.org/#host-parsing):

```python
URL("https://EXAMPLE.COM").hostname        # "example.com"
URL("https://例え.jp").hostname             # "xn--r8jz45g.jp"
```

!!! info "IDNA Processing"
    Domain names are processed using IDNA 2008 with `CheckHyphens=false` and `VerifyDnsLength=false` as specified in the [domain to ASCII](https://url.spec.whatwg.org/#concept-domain-to-ascii) algorithm.

### Path Normalization

Paths are percent-encoded and dot segments resolved per [path state](https://url.spec.whatwg.org/#path-state):

```python
URL("https://example.com/a/../b/./c").pathname  # "/b/c"
URL("https://example.com/hello world").pathname  # "/hello%20world"
```

### Default Ports

Default ports for known schemes are omitted per [URL serialization](https://url.spec.whatwg.org/#url-serializing):

```python
URL("https://example.com:443").port  # "" (empty, default port)
URL("https://example.com:8080").port  # "8080"
```

## Special Schemes

The WHATWG URL Standard defines [special schemes](https://url.spec.whatwg.org/#special-scheme) with specific parsing rules:

| Scheme | Default Port | Notes |
|--------|-------------|-------|
| `http` | 80 | Standard HTTP |
| `https` | 443 | Secure HTTP |
| `ftp` | 21 | File Transfer Protocol |
| `ws` | 80 | WebSocket |
| `wss` | 443 | Secure WebSocket |
| `file` | — | Local files |

Special schemes have additional behaviors:

```python
from pywhatwgurl import URL

# Special schemes get a default "/" path
URL("https://example.com").pathname  # "/"

# Non-special schemes preserve empty path
URL("custom://example.com").pathname  # ""

# Special schemes allow backslash as path separator
URL("https://example.com\\path").pathname  # "/path"
```

## Parsing Errors

When a URL is invalid, a `ValueError` is raised. The spec defines [validation errors](https://url.spec.whatwg.org/#validation-error) for various failure conditions:

```python
from pywhatwgurl import URL

# Invalid scheme
try:
    URL("://no-scheme")
except ValueError:
    print("Invalid URL")

# Use URL.parse() for graceful error handling
url = URL.parse("invalid url")  # Returns None instead of raising
```

!!! tip "Error Messages"
    Error messages describe why parsing failed, helping debug malformed URLs.

## Comparison with urllib.parse

pywhatwgurl follows the WHATWG standard while `urllib.parse` follows RFC 3986. Key differences:

| Scenario | pywhatwgurl | urllib.parse |
|----------|-------------|--------------|
| `http://example.com\\path` | `/path` | `\\path` |
| `http://example.com:80/path` | Port omitted | Port preserved |
| Hostname case | Always lowercase | Preserved |
| Unicode hosts | IDNA encoded | May raise error |

!!! note "Why WHATWG?"
    The WHATWG URL Standard defines precise parsing rules for web browsers, ensuring consistent behavior across the web. RFC 3986 is a generic URI standard used in broader contexts beyond web browsing.

## Further Reading

- [WHATWG URL Standard](https://url.spec.whatwg.org/) — The complete specification
- [URL parsing algorithm](https://url.spec.whatwg.org/#concept-url-parser) — How URLs are parsed
- [URL serialization](https://url.spec.whatwg.org/#concept-url-serializer) — How URLs are converted to strings

## Next Steps

- Learn about [URL Components](url-components.md)
- Explore [URLSearchParams](search-params.md)
