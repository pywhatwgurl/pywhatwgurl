"""URL and URLSearchParams integration tests based on WPT url-searchparams.any.js."""

from __future__ import annotations

import pytest

from pywhatwgurl import URL, URLSearchParams


def test_url_searchparams_getter() -> None:
    """URL.searchParams getter returns URLSearchParams object."""
    url = URL("http://example.org/?a=b")
    assert hasattr(url, "search_params")

    search_params = url.search_params
    assert url.search_params is search_params


def test_url_searchparams_updating_clearing() -> None:
    """URL.searchParams updating and clearing."""
    url = URL("http://example.org/?a=b")
    search_params = url.search_params
    assert str(search_params) == "a=b"

    search_params.set("a", "b")
    assert str(url.search_params) == "a=b"
    assert url.search == "?a=b"

    url.search = ""
    assert str(url.search_params) == ""
    assert url.search == ""
    assert str(search_params) == ""


def test_url_searchparams_readonly() -> None:
    """URL.searchParams is readonly (cannot be reassigned)."""
    url = URL("http://example.org")

    with pytest.raises(AttributeError):
        url.search_params = URLSearchParams("x=y")  # type: ignore


def test_url_search_and_searchparams_sync() -> None:
    """URL.search and URL.searchParams stay synchronized."""
    url = URL("http://example.org/file?a=b&c=d")
    search_params = url.search_params

    assert url.search == "?a=b&c=d"
    assert str(search_params) == "a=b&c=d"

    url.search = "e=f&g=h"
    assert url.search == "?e=f&g=h"
    assert str(search_params) == "e=f&g=h"

    url.search = "?e=f&g=h"
    assert url.search == "?e=f&g=h"
    assert str(search_params) == "e=f&g=h"

    search_params.append("i", " j ")
    assert url.search == "?e=f&g=h&i=+j+"
    assert str(url.search_params) == "e=f&g=h&i=+j+"
    assert search_params.get("i") == " j "

    search_params.set("e", "updated")
    assert url.search == "?e=updated&g=h&i=+j+"
    assert search_params.get("e") == "updated"


def test_url_double_question_mark() -> None:
    """URL with double question mark in query."""
    url = URL("http://example.org/file??a=b&c=d")
    assert url.search == "??a=b&c=d"
    assert str(url.search_params) == "%3Fa=b&c=d"

    url.href = "http://example.org/file??a=b"
    assert url.search == "??a=b"
    assert str(url.search_params) == "%3Fa=b"


def test_url_searchparams_sort_updates_url() -> None:
    """Sorting searchParams updates URL."""
    url = URL("https://example/?z=1&a=2")
    url.search_params.sort()

    assert url.search == "?a=2&z=1"


def test_url_searchparams_empty_after_sort() -> None:
    """Sorting non-existent params removes ? from URL."""
    url = URL("http://example.com/?")
    url.search_params.sort()

    assert url.href == "http://example.com/"
    assert url.search == ""
