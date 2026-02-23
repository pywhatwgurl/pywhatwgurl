"""WPT conformance tests for IDNA test vectors.

Tests the domain_to_ascii() function against IdnaTestV2.json and
IdnaTestV2-removed.json, which validate IDNA2008/UTS46 domain processing.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Tuple

import pytest

from pywhatwgurl import URL, domain_to_ascii
from tests.conformance.conftest import DATA_DIR
from tests.conformance.wpt_data import load_idna_cases, make_case_id


def _load_all_idna_cases() -> List[Tuple[str, Mapping[str, Any]]]:
    """Load IDNA test cases from both IdnaTestV2.json and IdnaTestV2-removed.json."""
    cases: List[Tuple[str, Mapping[str, Any]]] = []
    for case in load_idna_cases(DATA_DIR, "IdnaTestV2.json"):
        cases.append(("idna", case))
    for case in load_idna_cases(DATA_DIR, "IdnaTestV2-removed.json"):
        cases.append(("idna-removed", case))
    return cases


# Known failing test indices where Python's idna library is stricter than WHATWG
_XFAIL_INDICES = {1823, 1824, 1911, 1912, 1913}

_ALL_CASES = _load_all_idna_cases()

_PARAMS = [
    pytest.param(
        (source, case),
        marks=pytest.mark.xfail(
            reason="IDNA edge case: Python idna library stricter than WHATWG",
            strict=False,
        ),
    )
    if source == "idna" and i in _XFAIL_INDICES
    else (source, case)
    for i, (source, case) in enumerate(_ALL_CASES)
]

_IDS = [make_case_id(source, i, case) for i, (source, case) in enumerate(_ALL_CASES)]


@pytest.mark.parametrize("idna_case", _PARAMS, ids=_IDS)
def test_idna_case(idna_case: Tuple[str, Mapping[str, Any]]) -> None:
    """Test domain_to_ascii against IDNA test vectors."""
    source, case = idna_case
    input_value = case.get("input")
    expected_output = case.get("output")
    comment = case.get("comment", "")

    assert isinstance(input_value, str), f"{source} case missing string input"

    actual = domain_to_ascii(input_value)

    if expected_output is None:
        assert actual is None, f"Expected failure but got {actual!r} ({comment})"
    else:
        assert actual == expected_output, (
            f"Expected {expected_output!r} but got {actual!r} ({comment})"
        )


@pytest.mark.parametrize("idna_case", _PARAMS, ids=_IDS)
def test_idna_via_url_constructor(idna_case: Tuple[str, Mapping[str, Any]]) -> None:
    """Test IDNA domain processing via URL constructor.

    Per WPT IdnaTestV2.window.js: constructing URL with IDNA domain should
    process the domain and set host/hostname/pathname/href correctly.
    """
    source, case = idna_case
    input_value = case.get("input")
    expected_output = case.get("output")
    comment = case.get("comment", "")

    assert isinstance(input_value, str), f"{source} case missing string input"

    if input_value == "":
        pytest.skip("Cannot test empty string input via URL constructor")

    if expected_output is None:
        with pytest.raises(ValueError):
            URL(f"https://{input_value}/x")
    else:
        url = URL(f"https://{input_value}/x")
        assert url.host == expected_output, (
            f"host: expected {expected_output!r} but got {url.host!r} ({comment})"
        )
        assert url.hostname == expected_output, (
            f"hostname: expected {expected_output!r} but got {url.hostname!r} ({comment})"
        )
        assert url.pathname == "/x", (
            f"pathname: expected '/x' but got {url.pathname!r} ({comment})"
        )
        assert url.href == f"https://{expected_output}/x", (
            f"href: expected 'https://{expected_output}/x' but got {url.href!r} ({comment})"
        )
