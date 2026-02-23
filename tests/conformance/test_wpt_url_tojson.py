"""URL.toJSON() conformance tests based on WPT url-tojson.any.js."""

from __future__ import annotations

from pywhatwgurl import URL


def test_url_tojson() -> None:
    """Test URL.toJSON() returns href for JSON serialization."""
    url = URL("https://example.com/")

    assert url.to_json() == "https://example.com/"
    assert url.to_json() == url.href
