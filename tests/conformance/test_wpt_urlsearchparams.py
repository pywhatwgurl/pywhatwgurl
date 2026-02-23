"""URLSearchParams conformance tests based on WPT urlencoded-parser and urlsearchparams tests."""

from __future__ import annotations

from typing import List, Tuple

import pytest

from pywhatwgurl import URL, URLSearchParams


URLENCODED_PARSER_CASES: List[Tuple[str, List[Tuple[str, str]]]] = [
    ("test", [("test", "")]),
    ("\ufefftest=\ufeff", [("\ufefftest", "\ufeff")]),
    ("%EF%BB%BFtest=%EF%BB%BF", [("\ufefftest", "\ufeff")]),
    ("%EF%BF%BF=%EF%BF%BF", [("\uffff", "\uffff")]),
    ("%FE%FF", [("\ufffd\ufffd", "")]),
    ("%FF%FE", [("\ufffd\ufffd", "")]),
    ("†&†=x", [("†", ""), ("†", "x")]),
    ("%C2", [("\ufffd", "")]),
    ("%C2x", [("\ufffdx", "")]),
    (
        "_charset_=windows-1252&test=%C2x",
        [("_charset_", "windows-1252"), ("test", "\ufffdx")],
    ),
    ("", []),
    ("a", [("a", "")]),
    ("a=b", [("a", "b")]),
    ("a=", [("a", "")]),
    ("=b", [("", "b")]),
    ("&", []),
    ("&a", [("a", "")]),
    ("a&", [("a", "")]),
    ("a&a", [("a", ""), ("a", "")]),
    ("a&b&c", [("a", ""), ("b", ""), ("c", "")]),
    ("a=b&c=d", [("a", "b"), ("c", "d")]),
    ("a=b&c=d&", [("a", "b"), ("c", "d")]),
    ("&&&a=b&&&&c=d&", [("a", "b"), ("c", "d")]),
    ("a=a&a=b&a=c", [("a", "a"), ("a", "b"), ("a", "c")]),
    ("a==a", [("a", "=a")]),
    ("a=a+b+c+d", [("a", "a b c d")]),
    ("%=a", [("%", "a")]),
    ("%a=a", [("%a", "a")]),
    ("%a_=a", [("%a_", "a")]),
    ("%61=a", [("a", "a")]),
    ("%61+%4d%4D=", [("a MM", "")]),
    ("id=0&value=%", [("id", "0"), ("value", "%")]),
    ("b=%2sf%2a", [("b", "%2sf*")]),
    ("b=%2%2af%2a", [("b", "%2*f*")]),
    ("b=%%2a", [("b", "%*")]),
]


@pytest.mark.parametrize(
    "input_str,expected",
    URLENCODED_PARSER_CASES,
    ids=[f"parse:{repr(c[0][:30])}" for c in URLENCODED_PARSER_CASES],
)
def test_urlsearchparams_parsing(
    input_str: str, expected: List[Tuple[str, str]]
) -> None:
    """Test URLSearchParams parsing of application/x-www-form-urlencoded data."""
    params = URLSearchParams(input_str)
    result = list(params.items())
    assert result == expected


def test_basic_construction() -> None:
    """Basic URLSearchParams construction."""
    params = URLSearchParams()
    assert str(params) == ""

    params = URLSearchParams("")
    assert str(params) == ""

    params = URLSearchParams("a=b")
    assert str(params) == "a=b"


def test_constructor_removes_leading_question_mark() -> None:
    """URLSearchParams constructor removes leading '?'."""
    params = URLSearchParams("?a=b")
    assert str(params) == "a=b"


def test_constructor_with_empty_dict() -> None:
    """URLSearchParams constructor with {} as argument."""
    params = URLSearchParams({})
    assert str(params) == ""


def test_constructor_string_parsing() -> None:
    """URLSearchParams constructor with string."""
    params = URLSearchParams("a=b")
    assert params.has("a")
    assert not params.has("b")

    params = URLSearchParams("a=b&c")
    assert params.has("a")
    assert params.has("c")

    params = URLSearchParams("&a&&& &&&&a+b=& c&m%c3%b8%c3%b8")
    assert params.has("a")
    assert params.has("a b")
    assert params.has(" ")
    assert not params.has("c")
    assert params.has(" c")
    assert params.has("møø")

    params = URLSearchParams("id=0&value=%")
    assert params.has("id")
    assert params.has("value")
    assert params.get("id") == "0"
    assert params.get("value") == "%"

    params = URLSearchParams("b=%2sf%2a")
    assert params.has("b")
    assert params.get("b") == "%2sf*"

    params = URLSearchParams("b=%2%2af%2a")
    assert params.has("b")
    assert params.get("b") == "%2*f*"

    params = URLSearchParams("b=%%2a")
    assert params.has("b")
    assert params.get("b") == "%*"


def test_constructor_with_urlsearchparams() -> None:
    """URLSearchParams constructor with URLSearchParams object."""
    seed = URLSearchParams("a=b&c=d")
    params = URLSearchParams(seed)

    assert params.get("a") == "b"
    assert params.get("c") == "d"
    assert not params.has("d")

    seed.append("e", "f")
    assert not params.has("e")

    params.append("g", "h")
    assert not seed.has("g")


def test_parse_plus() -> None:
    """Parse + as space."""
    params = URLSearchParams("a=b+c")
    assert params.get("a") == "b c"

    params = URLSearchParams("a+b=c")
    assert params.get("a b") == "c"


def test_parse_encoded_plus() -> None:
    """Parse encoded +."""
    test_value = "+15555555555"
    params = URLSearchParams()
    params.set("query", test_value)
    new_params = URLSearchParams(str(params))

    assert str(params) == "query=%2B15555555555"
    assert params.get("query") == test_value
    assert new_params.get("query") == test_value


def test_parse_space() -> None:
    """Parse space."""
    params = URLSearchParams("a=b c")
    assert params.get("a") == "b c"

    params = URLSearchParams("a b=c")
    assert params.get("a b") == "c"


def test_parse_percent20() -> None:
    """Parse %20."""
    params = URLSearchParams("a=b%20c")
    assert params.get("a") == "b c"

    params = URLSearchParams("a%20b=c")
    assert params.get("a b") == "c"


def test_parse_null() -> None:
    """Parse \\0."""
    params = URLSearchParams("a=b\0c")
    assert params.get("a") == "b\0c"

    params = URLSearchParams("a\0b=c")
    assert params.get("a\0b") == "c"


def test_parse_encoded_null() -> None:
    """Parse %00."""
    params = URLSearchParams("a=b%00c")
    assert params.get("a") == "b\0c"

    params = URLSearchParams("a%00b=c")
    assert params.get("a\0b") == "c"


def test_parse_unicode() -> None:
    """Parse Unicode characters."""
    params = URLSearchParams("a=b\u2384")
    assert params.get("a") == "b\u2384"

    params = URLSearchParams("a\u2384b=c")
    assert params.get("a\u2384b") == "c"

    params = URLSearchParams("a=b%e2%8e%84")
    assert params.get("a") == "b\u2384"

    params = URLSearchParams("a%e2%8e%84b=c")
    assert params.get("a\u2384b") == "c"

    params = URLSearchParams("a=b\U0001f4a9c")
    assert params.get("a") == "b\U0001f4a9c"

    params = URLSearchParams("a\U0001f4a9b=c")
    assert params.get("a\U0001f4a9b") == "c"

    params = URLSearchParams("a=b%f0%9f%92%a9c")
    assert params.get("a") == "b\U0001f4a9c"

    params = URLSearchParams("a%f0%9f%92%a9b=c")
    assert params.get("a\U0001f4a9b") == "c"


def test_constructor_with_sequence() -> None:
    """Constructor with sequence of sequences of strings."""
    params = URLSearchParams([])
    assert len(params) == 0

    params = URLSearchParams([["a", "b"], ["c", "d"]])
    assert params.get("a") == "b"
    assert params.get("c") == "d"

    with pytest.raises(TypeError):
        URLSearchParams([[1]])  # type: ignore

    with pytest.raises(TypeError):
        URLSearchParams([[1, 2, 3]])  # type: ignore


def test_constructor_with_dict() -> None:
    """Constructor with record (dict)."""
    params = URLSearchParams({"+": "%C2"})
    result = list(params.items())
    assert result == [("+", "%C2")]

    params = URLSearchParams({"c": "x", "a": "?"})
    assert params.get("c") == "x"
    assert params.get("a") == "?"


SORT_CASES: List[Tuple[str, List[Tuple[str, str]]]] = [
    ("z=b&a=b&z=a&a=a", [("a", "b"), ("a", "a"), ("z", "b"), ("z", "a")]),
    ("\ufffd=x&\ufffc&\ufffd=a", [("\ufffc", ""), ("\ufffd", "x"), ("\ufffd", "a")]),
    ("ﬃ&🌈", [("🌈", ""), ("ﬃ", "")]),
    ("é&e\ufffd&e\u0301", [("e\u0301", ""), ("e\ufffd", ""), ("é", "")]),
    (
        "z=z&a=a&z=y&a=b&z=x&a=c&z=w&a=d&z=v&a=e&z=u&a=f&z=t&a=g",
        [
            ("a", "a"),
            ("a", "b"),
            ("a", "c"),
            ("a", "d"),
            ("a", "e"),
            ("a", "f"),
            ("a", "g"),
            ("z", "z"),
            ("z", "y"),
            ("z", "x"),
            ("z", "w"),
            ("z", "v"),
            ("z", "u"),
            ("z", "t"),
        ],
    ),
    (
        "bbb&bb&aaa&aa=x&aa=y",
        [("aa", "x"), ("aa", "y"), ("aaa", ""), ("bb", ""), ("bbb", "")],
    ),
    ("z=z&=f&=t&=x", [("", "f"), ("", "t"), ("", "x"), ("z", "z")]),
    ("a🌈&a💩", [("a🌈", ""), ("a💩", "")]),
]


@pytest.mark.parametrize(
    "input_str,expected", SORT_CASES, ids=[f"sort:{i}" for i in range(len(SORT_CASES))]
)
def test_urlsearchparams_sort(input_str: str, expected: List[Tuple[str, str]]) -> None:
    """Test URLSearchParams.sort() - sorts by code units."""
    params = URLSearchParams(input_str)
    params.sort()
    result = list(params.items())
    assert result == expected


def test_size_property() -> None:
    """Test URLSearchParams.size property."""
    params = URLSearchParams("a=1&b=2&a=3")
    assert params.size == 3
    assert len(params) == 3


def test_append() -> None:
    """Test URLSearchParams.append()."""
    params = URLSearchParams()
    params.append("a", "b")
    assert str(params) == "a=b"

    params.append("a", "c")
    assert str(params) == "a=b&a=c"


def test_delete() -> None:
    """Test URLSearchParams.delete()."""
    params = URLSearchParams("a=1&b=2&a=3")
    params.delete("a")
    assert str(params) == "b=2"

    params = URLSearchParams("a=1&b=2&a=3")
    params.delete("a", "1")
    assert params.get_all("a") == ("3",)


def test_get_and_get_all() -> None:
    """Test URLSearchParams.get() and get_all()."""
    params = URLSearchParams("a=1&b=2&a=3")
    assert params.get("a") == "1"
    assert params.get("b") == "2"
    assert params.get("c") is None
    assert params.get_all("a") == ("1", "3")
    assert params.get_all("c") == ()


def test_has() -> None:
    """Test URLSearchParams.has()."""
    params = URLSearchParams("a=1&b=2&a=3")
    assert params.has("a")
    assert params.has("b")
    assert not params.has("c")

    assert params.has("a", "1")
    assert params.has("a", "3")
    assert not params.has("a", "2")


def test_set() -> None:
    """Test URLSearchParams.set()."""
    params = URLSearchParams("a=1&b=2&a=3")
    params.set("a", "4")
    assert str(params) == "a=4&b=2"

    params.set("c", "5")
    assert params.get("c") == "5"


def test_stringifier() -> None:
    """Test URLSearchParams stringification."""
    params = URLSearchParams("a=b&c=d")
    assert str(params) == "a=b&c=d"
    assert params.to_string() == "a=b&c=d"


def test_iteration() -> None:
    """Test URLSearchParams iteration."""
    params = URLSearchParams("a=1&b=2")

    assert list(params.keys()) == ["a", "b"]
    assert list(params.values()) == ["1", "2"]
    assert list(params.items()) == [("a", "1"), ("b", "2")]
    assert list(params) == ["a", "b"]


def test_delete_next_param_during_iteration() -> None:
    """Delete next param during iteration."""
    url = URL("http://localhost/query?param0=0&param1=1&param2=2")
    search_params = url.search_params
    seen: List[Tuple[str, str]] = []

    for key, value in search_params.items():
        if key == "param0":
            search_params.delete("param1")
        seen.append((key, value))

    assert seen == [("param0", "0"), ("param2", "2")]


def test_delete_current_param_during_iteration() -> None:
    """Delete current param during iteration."""
    url = URL("http://localhost/query?param0=0&param1=1&param2=2")
    search_params = url.search_params
    seen: List[Tuple[str, str]] = []

    for key, value in search_params.items():
        if key == "param0":
            search_params.delete("param0")
        else:
            seen.append((key, value))

    assert seen == [("param2", "2")]


def test_delete_every_param_during_iteration() -> None:
    """Delete every param seen during iteration."""
    url = URL("http://localhost/query?param0=0&param1=1&param2=2")
    search_params = url.search_params
    seen: List[str] = []

    for key, _ in search_params.items():
        seen.append(key)
        search_params.delete(key)

    assert seen == ["param0", "param2"], "param1 should not have been seen by the loop"
    assert str(search_params) == "param1=1", "param1 should remain"


def test_modify_search_during_iteration() -> None:
    """Modify url.search during searchParams iteration."""
    url = URL("http://a.b/c?a=1&b=2&c=3&d=4")
    search_params = url.search_params
    seen: List[Tuple[str, str]] = []

    for key, value in search_params.items():
        url.search = "x=1&y=2&z=3"
        seen.append((key, value))

    assert seen[0] == ("a", "1")
    assert seen[1] == ("y", "2")
    assert seen[2] == ("z", "3")


def test_comma_encoding_in_searchparams() -> None:
    """Commas must be percent-encoded in URLSearchParams serialization."""
    url = URL("http://www.example.com/?a=b,c")
    params = url.search_params

    assert str(url) == "http://www.example.com/?a=b,c"
    assert str(params) == "a=b%2Cc"

    params.append("x", "y")

    assert str(url) == "http://www.example.com/?a=b%2Cc&x=y"
    assert str(params) == "a=b%2Cc&x=y"


def test_newline_non_normalization() -> None:
    url = URL("http://www.example.com/")
    params = url.search_params

    params.append("a\nb", "c\rd")
    params.append("e\n\rf", "g\r\nh")

    assert str(params) == "a%0Ab=c%0Dd&e%0A%0Df=g%0D%0Ah"


# -- urlsearchparams-append.any.js --


def test_append_empty_strings() -> None:
    params = URLSearchParams()
    params.append("", "")
    assert str(params) == "="
    params.append("", "")
    assert str(params) == "=&="


def test_append_multiple() -> None:
    params = URLSearchParams()
    params.append("first", "1")
    params.append("second", "2")
    params.append("third", "")
    params.append("first", "10")
    assert params.has("first")
    assert params.get("first") == "1"
    assert params.get("second") == "2"
    assert params.get("third") == ""
    params.append("first", "10")
    assert params.get("first") == "1"


# -- urlsearchparams-delete.any.js --


def test_delete_basics_extended() -> None:
    params = URLSearchParams("a=b&c=d")
    params.delete("a")
    assert str(params) == "c=d"

    params = URLSearchParams("a=a&b=b&a=a&c=c")
    params.delete("a")
    assert str(params) == "b=b&c=c"

    params = URLSearchParams("a=a&=&b=b&c=c")
    params.delete("")
    assert str(params) == "a=a&b=b&c=c"


def test_delete_appended_multiple() -> None:
    params = URLSearchParams()
    params.append("first", "1")
    assert params.has("first")
    assert params.get("first") == "1"
    params.delete("first")
    assert not params.has("first")
    params.append("first", "1")
    params.append("first", "10")
    params.delete("first")
    assert not params.has("first")


def test_delete_all_params_removes_question_mark() -> None:
    url = URL("http://example.com/?param1&param2")
    url.search_params.delete("param1")
    url.search_params.delete("param2")
    assert url.href == "http://example.com/"
    assert url.search == ""


def test_delete_nonexistent_removes_question_mark() -> None:
    url = URL("http://example.com/?")
    url.search_params.delete("param1")
    assert url.href == "http://example.com/"
    assert url.search == ""


def test_delete_opaque_path_trailing_spaces() -> None:
    url = URL("data:space    ?test")
    assert url.search_params.has("test")
    url.search_params.delete("test")
    assert not url.search_params.has("test")
    assert url.search == ""
    assert url.pathname == "space   %20"
    assert url.href == "data:space   %20"


def test_delete_opaque_path_trailing_spaces_fragment() -> None:
    url = URL("data:space    ?test#test")
    url.search_params.delete("test")
    assert url.search == ""
    assert url.pathname == "space   %20"
    assert url.href == "data:space   %20#test"


def test_delete_two_arg() -> None:
    params = URLSearchParams()
    params.append("a", "b")
    params.append("a", "c")
    params.append("a", "d")
    params.delete("a", "c")
    assert str(params) == "a=b&a=d"


# -- urlsearchparams-get.any.js --


def test_get_basics_extended() -> None:
    params = URLSearchParams("a=b&c=d")
    assert params.get("a") == "b"
    assert params.get("c") == "d"
    assert params.get("e") is None

    params = URLSearchParams("a=b&c=d&a=e")
    assert params.get("a") == "b"

    params = URLSearchParams("=b&c=d")
    assert params.get("") == "b"

    params = URLSearchParams("a=&c=d&a=e")
    assert params.get("a") == ""


def test_get_more_basics() -> None:
    params = URLSearchParams("first=second&third&&")
    assert params.has("first")
    assert params.get("first") == "second"
    assert params.get("third") == ""
    assert params.get("fourth") is None


# -- urlsearchparams-getall.any.js --


def test_getall_basics_extended() -> None:
    params = URLSearchParams("a=b&c=d")
    assert params.get_all("a") == ("b",)
    assert params.get_all("c") == ("d",)
    assert params.get_all("e") == ()

    params = URLSearchParams("a=b&c=d&a=e")
    assert params.get_all("a") == ("b", "e")

    params = URLSearchParams("=b&c=d")
    assert params.get_all("") == ("b",)

    params = URLSearchParams("a=&c=d&a=e")
    assert params.get_all("a") == ("", "e")


def test_getall_after_set() -> None:
    params = URLSearchParams("a=1&a=2&a=3&a")
    assert params.has("a")
    matches = params.get_all("a")
    assert len(matches) == 4
    assert matches == ("1", "2", "3", "")
    params.set("a", "one")
    assert params.get("a") == "one"
    matches = params.get_all("a")
    assert len(matches) == 1
    assert matches == ("one",)


# -- urlsearchparams-has.any.js --


def test_has_following_delete() -> None:
    params = URLSearchParams("a=b&c=d&&")
    params.append("first", "1")
    params.append("first", "2")
    assert params.has("a")
    assert params.has("c")
    assert params.has("first")
    assert not params.has("d")
    params.delete("first")
    assert not params.has("first")


def test_has_two_arg_extended() -> None:
    params = URLSearchParams("a=b&a=d&c&e&")
    assert params.has("a", "b")
    assert not params.has("a", "c")
    assert params.has("a", "d")
    assert params.has("e", "")


# -- urlsearchparams-set.any.js --


def test_set_basics_extended() -> None:
    params = URLSearchParams("a=b&c=d")
    params.set("a", "B")
    assert str(params) == "a=B&c=d"

    params = URLSearchParams("a=b&c=d&a=e")
    params.set("a", "B")
    assert str(params) == "a=B&c=d"
    params.set("e", "f")
    assert str(params) == "a=B&c=d&e=f"


def test_set_multiple() -> None:
    params = URLSearchParams("a=1&a=2&a=3")
    assert params.has("a")
    assert params.get("a") == "1"
    params.set("first", "4")
    assert params.has("a")
    assert params.get("a") == "1"
    params.set("a", "4")
    assert params.has("a")
    assert params.get("a") == "4"


# -- urlsearchparams-size.any.js --


def test_size_after_delete() -> None:
    params = URLSearchParams("a=1&b=2&a=3")
    assert len(params) == 3
    params.delete("a")
    assert len(params) == 1


def test_size_after_append() -> None:
    params = URLSearchParams("a=1&b=2&a=3")
    assert len(params) == 3
    params.append("b", "4")
    assert len(params) == 4


def test_size_from_url() -> None:
    url = URL("http://localhost/query?a=1&b=2&a=3")
    assert len(url.search_params) == 3
    url.search_params.delete("a")
    assert len(url.search_params) == 1
    url.search_params.append("b", "4")
    assert len(url.search_params) == 2


def test_size_after_search_setter() -> None:
    url = URL("http://localhost/query?a=1&b=2&a=3")
    assert len(url.search_params) == 3
    url.search = "?"
    assert len(url.search_params) == 0


# -- urlsearchparams-stringifier.any.js --


def test_stringify_space() -> None:
    params = URLSearchParams()
    params.append("a", "b c")
    assert str(params) == "a=b+c"
    params.delete("a")
    params.append("a b", "c")
    assert str(params) == "a+b=c"


def test_stringify_empty_value() -> None:
    params = URLSearchParams()
    params.append("a", "")
    assert str(params) == "a="
    params.append("a", "")
    assert str(params) == "a=&a="
    params.append("", "b")
    assert str(params) == "a=&a=&=b"
    params.append("", "")
    assert str(params) == "a=&a=&=b&="
    params.append("", "")
    assert str(params) == "a=&a=&=b&=&="


def test_stringify_empty_name() -> None:
    params = URLSearchParams()
    params.append("", "b")
    assert str(params) == "=b"
    params.append("", "b")
    assert str(params) == "=b&=b"


def test_stringify_empty_name_and_value() -> None:
    params = URLSearchParams()
    params.append("", "")
    assert str(params) == "="
    params.append("", "")
    assert str(params) == "=&="


def test_stringify_plus() -> None:
    params = URLSearchParams()
    params.append("a", "b+c")
    assert str(params) == "a=b%2Bc"
    params.delete("a")
    params.append("a+b", "c")
    assert str(params) == "a%2Bb=c"


def test_stringify_equals() -> None:
    params = URLSearchParams()
    params.append("=", "a")
    assert str(params) == "%3D=a"
    params.append("b", "=")
    assert str(params) == "%3D=a&b=%3D"


def test_stringify_ampersand() -> None:
    params = URLSearchParams()
    params.append("&", "a")
    assert str(params) == "%26=a"
    params.append("b", "&")
    assert str(params) == "%26=a&b=%26"


def test_stringify_safe_chars() -> None:
    params = URLSearchParams()
    params.append("a", "*-._")
    assert str(params) == "a=*-._"
    params.delete("a")
    params.append("*-._", "c")
    assert str(params) == "*-._=c"


def test_stringify_percent() -> None:
    params = URLSearchParams()
    params.append("a", "b%c")
    assert str(params) == "a=b%25c"
    params.delete("a")
    params.append("a%b", "c")
    assert str(params) == "a%25b=c"

    params = URLSearchParams("id=0&value=%")
    assert str(params) == "id=0&value=%25"


def test_stringify_null_byte() -> None:
    params = URLSearchParams()
    params.append("a", "b\0c")
    assert str(params) == "a=b%00c"
    params.delete("a")
    params.append("a\0b", "c")
    assert str(params) == "a%00b=c"


def test_stringify_unicode() -> None:
    params = URLSearchParams()
    params.append("a", "b\U0001f4a9c")
    assert str(params) == "a=b%F0%9F%92%A9c"
    params.delete("a")
    params.append("a\U0001f4a9b", "c")
    assert str(params) == "a%F0%9F%92%A9b=c"


def test_stringify_roundtrip() -> None:
    params = URLSearchParams("a=b&c=d&&e&&")
    assert str(params) == "a=b&c=d&e="

    params = URLSearchParams("a = b &a=b&c=d%20")
    assert str(params) == "a+=+b+&a=b&c=d+"

    params = URLSearchParams("a=&a=b")
    assert str(params) == "a=&a=b"

    params = URLSearchParams("b=%2sf%2a")
    assert str(params) == "b=%252sf*"

    params = URLSearchParams("b=%2%2af%2a")
    assert str(params) == "b=%252*f*"

    params = URLSearchParams("b=%%2a")
    assert str(params) == "b=%25*"


# -- urlsearchparams-foreach.any.js --


def test_iteration_empty() -> None:
    url = URL("http://a.b/c")
    for _item in url.search_params.items():
        pytest.fail("Should not iterate over empty params")
