# pywhatwgurl

**Pure Python implementation of the WHATWG URL Standard.**

[![PyPI version](https://img.shields.io/pypi/v/pywhatwgurl.svg)](https://pypi.org/project/pywhatwgurl/)
[![Python versions](https://img.shields.io/pypi/pyversions/pywhatwgurl.svg)](https://pypi.org/project/pywhatwgurl/)
[![License](https://img.shields.io/github/license/pywhatwgurl/pywhatwgurl.svg)](https://github.com/pywhatwgurl/pywhatwgurl/blob/master/LICENSE)
[![Typed](https://img.shields.io/badge/typing-typed-blue)](https://peps.python.org/pep-0561/)

---

## What is pywhatwgurl?

**pywhatwgurl** is a Python library that implements the [WHATWG URL Standard](https://url.spec.whatwg.org/) — the same URL parsing specification used by modern web browsers.

Unlike Python's built-in `urllib.parse`, which follows RFC 3986/3987, pywhatwgurl prioritizes web compatibility:

- ✅ **Browser-compatible URL parsing** — Parse URLs exactly like Chrome, Firefox, and Safari
- ✅ **Modern API** — Familiar `URL` and `URLSearchParams` classes matching the Web API
- ✅ **Pure Python** — No compiled dependencies, works everywhere Python runs
- ✅ **Type-annotated** — Full type hints for excellent IDE support

## Quick Example

```python
from pywhatwgurl import URL

# Parse a URL
url = URL("https://example.com:8080/path?query=value#hash")

print(url.hostname)  # "example.com"
print(url.port)      # "8080"
print(url.pathname)  # "/path"
print(url.search)    # "?query=value"
print(url.hash)      # "#hash"

# Modify URL components
url.pathname = "/new/path"
print(url.href)  # "https://example.com:8080/new/path?query=value#hash"

# Work with query parameters (Pythonic dictionary-style access)
url.search_params["page"] = "2"
print(url.search)  # "?query=value&page=2"
```

## Why WHATWG URL?

The WHATWG URL Standard defines how browsers act, refining the generic URI syntax from RFC 3986 to ensure interoperability on the web.

| Feature | WHATWG URL | RFC 3986 |
|---------|------------|----------|
| Browser compatibility | ✅ Matches browsers exactly | ⚠️ Defines generic syntax |
| Error handling | ✅ Strictly defined | ℹ️ Implementation-dependent |
| Unicode support | ✅ Full IDNA (UTS #46) | ℹ️ Varies by implementation |
| Edge cases | ✅ Specified behavior | ℹ️ Flexible |

## Staying Current

The WHATWG URL Standard is a [living standard](https://whatwg.org/faq#living-standard) — it evolves continuously. pywhatwgurl tracks spec changes automatically:

- A **weekly CI workflow** checks the WPT repository for updates to the `url/` test data and opens a PR when changes are detected
- All conformance tests must pass before any merge — regressions are caught immediately
- Test data is **pinned to a specific WPT commit** for reproducibility, so every build is validated against a known snapshot
- The workflow can also be **triggered manually** for urgent spec updates

This means spec changes are typically picked up within a week of landing in WPT, with a review cycle to verify correctness before merging.

## Installation

```bash
pip install pywhatwgurl
```

Or with uv:

```bash
uv add pywhatwgurl
```

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Install pywhatwgurl and learn the basics

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-book-open-variant:{ .lg .middle } **User Guide**

    ---

    Learn how to parse URLs and work with components

    [:octicons-arrow-right-24: URL Parsing](guide/url-parsing.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation with examples

    [:octicons-arrow-right-24: API Docs](api/url.md)

-   :material-check-circle:{ .lg .middle } **Compliance**

    ---

    Learn about WHATWG URL standard conformance

    [:octicons-arrow-right-24: Compliance](about/compliance.md)

</div>
