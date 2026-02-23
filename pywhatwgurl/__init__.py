# SPDX-License-Identifier: MIT
"""Pure Python implementation of the WHATWG URL Standard.

This package provides a spec-compliant URL parser and related utilities
per the WHATWG URL Living Standard (https://url.spec.whatwg.org/).

Example:
    >>> from pywhatwgurl import URL, URLSearchParams
    >>> url = URL("https://example.com/path?query=value#hash")
    >>> url.hostname
    'example.com'
    >>> url.search_params.get("query")
    'value'

Classes:
    URL: Parse and manipulate URLs.
    URLSearchParams: Parse and manipulate query strings.

Functions:
    domain_to_ascii: Convert Unicode domain names to ASCII (IDNA).
    domain_to_unicode: Convert ASCII domain names to Unicode.
    percent_encode_after_encoding: Percent-encode a string.
"""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

from .url import (
    URLImpl as URL,
    URLSearchParamsImpl as URLSearchParams,
)
from .idna_processor import domain_to_ascii, domain_to_unicode
from .encoding import percent_encode_after_encoding

__all__ = [
    "URL",
    "URLSearchParams",
    "domain_to_ascii",
    "domain_to_unicode",
    "percent_encode_after_encoding",
]
