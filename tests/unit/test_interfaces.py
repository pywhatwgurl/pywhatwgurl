import pytest
from typing import Any
from tests.mocks import MockURLSearchParams, MockURL


@pytest.mark.parametrize(
    "init_data, expected_key, expected_val",
    [
        ({"foo": "bar"}, "foo", "bar"),
        ([("foo", "bar")], "foo", "bar"),
        (((k, v) for k, v in [("foo", "bar")]), "foo", "bar"),
        (
            {"foo": ["val1", "val2"]},
            "foo",
            "val1",
        ),  # Mock simplifies list to first element
        ([["foo", "bar"]], "foo", "bar"),
    ],
)
def test_url_search_params_init_types(
    init_data: Any, expected_key: str, expected_val: str
) -> None:
    params = MockURLSearchParams(init_data)
    assert params[expected_key] == expected_val


def test_url_search_params_mutable_mapping() -> None:
    params = MockURLSearchParams({"foo": "bar", "baz": "qux"})

    # Test __getitem__
    assert params["foo"] == "bar"
    with pytest.raises(KeyError):
        _ = params["missing"]

    # Test __setitem__
    params["new"] = "value"
    assert params.get("new") == "value"
    assert params.has("new")

    # Test __delitem__
    del params["foo"]
    assert not params.has("foo")
    with pytest.raises(KeyError):
        del params["missing"]

    # Test __len__
    assert len(params) == 2  # baz, new

    # Test __iter__ / keys
    keys = list(params)
    assert "baz" in keys
    assert "new" in keys
    assert len(keys) == 2

    # Test values
    values = list(params.values())
    assert "qux" in values
    assert "value" in values

    # Test items
    items = list(params.items())
    assert ("baz", "qux") in items
    assert ("new", "value") in items

    # Test __contains__
    assert "baz" in params
    assert "missing" not in params


@pytest.mark.parametrize(
    "url1, url2, expected_eq",
    [
        ("https://example.com", "https://example.com", True),
        (
            "https://example.com",
            "https://example.com/",
            False,
        ),  # String exact match in mock
        ("https://example.com", "https://other.com", False),
    ],
)
def test_url_equality(url1: str, url2: str, expected_eq: bool) -> None:
    u1 = MockURL(url1)
    u2 = MockURL(url2)
    if expected_eq:
        assert u1 == u2
    else:
        assert u1 != u2


def test_url_equality_type_check() -> None:
    u1 = MockURL("https://example.com")
    assert u1 != "https://example.com"  # Should not equal a string
