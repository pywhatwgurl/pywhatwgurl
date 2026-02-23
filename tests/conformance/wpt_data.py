from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Tuple

from pywhatwgurl import URL, URLSearchParams


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_list_cases(data: object) -> Iterator[Mapping[str, Any]]:
    if not isinstance(data, list):
        raise TypeError(f"Expected a list, got {type(data).__name__}")
    for entry in data:
        if isinstance(entry, str):
            continue
        if not isinstance(entry, dict):
            raise TypeError(f"Expected dict entry, got {type(entry).__name__}")
        yield entry


def require_public_api() -> Tuple[type, type]:
    return URL, URLSearchParams


def make_case_id(prefix: str, index: int, case: Mapping[str, Any]) -> str:
    input_value = case.get("input")
    if isinstance(input_value, str):
        trimmed = input_value.replace("\n", "\\n").replace("\t", "\\t")
        if len(trimmed) > 40:
            trimmed = trimmed[:40] + "..."
        return f"{prefix}[{index}]:{trimmed}"
    return f"{prefix}[{index}]"


def load_urltestdata_cases(data_dir: Path) -> List[Mapping[str, Any]]:
    data = load_json(data_dir / "urltestdata.json")
    return list(iter_list_cases(data))


def load_toascii_cases(data_dir: Path) -> List[Mapping[str, Any]]:
    data = load_json(data_dir / "toascii.json")
    return list(iter_list_cases(data))


def load_idna_cases(data_dir: Path, filename: str) -> List[Mapping[str, Any]]:
    data = load_json(data_dir / filename)
    return list(iter_list_cases(data))


def load_percent_encoding_cases(data_dir: Path) -> List[Mapping[str, Any]]:
    data = load_json(data_dir / "percent-encoding.json")
    out: List[Mapping[str, Any]] = []
    for entry in iter_list_cases(data):
        input_value = entry.get("input")
        output_value = entry.get("output")
        if not isinstance(input_value, str):
            raise TypeError("percent-encoding case missing string input")
        out.append(
            {
                "input": input_value,
                "output": _extract_percent_encoding_output(output_value),
            }
        )
    return out


def _extract_percent_encoding_output(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        utf8_output = value.get("utf-8")
        if isinstance(utf8_output, str):
            return utf8_output
        raise TypeError("percent-encoding case missing utf-8 output string")
    raise TypeError("percent-encoding case has invalid output type")


def load_setters_cases(data_dir: Path) -> List[Tuple[str, int, Mapping[str, Any]]]:
    data = load_json(data_dir / "setters_tests.json")
    if not isinstance(data, dict):
        raise TypeError(
            f"Expected setters_tests.json to be an object; got {type(data).__name__}"
        )

    out: List[Tuple[str, int, Mapping[str, Any]]] = []
    for attr, cases in data.items():
        if attr == "comment":
            continue
        if not isinstance(cases, list):
            raise TypeError(
                f"Expected list of cases for {attr}; got {type(cases).__name__}"
            )
        for idx, case in enumerate(cases):
            if not isinstance(case, dict):
                raise TypeError(
                    f"Expected dict case for {attr}[{idx}]; got {type(case).__name__}"
                )
            out.append((attr, idx, case))
    return out
