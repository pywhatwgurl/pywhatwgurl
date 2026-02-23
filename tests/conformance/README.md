# Conformance Test Coverage

This directory contains tests that validate `pywhatwgurl` against the [Web Platform Tests (WPT)](https://github.com/web-platform-tests/wpt) URL test suite.

## Test Data Coverage

| JSON File | Test Cases | Test File | Status |
|-----------|------------|-----------|--------|
| `urltestdata.json` | 869 | `test_wpt_urltestdata.py` | ✅ 100% |
| `setters_tests.json` | 274 | `test_wpt_setters.py` | ✅ 100% |
| `percent-encoding.json` | 6 | `test_wpt_percent_encoding.py` | ✅ 100% |
| `toascii.json` | 87 | `test_wpt_toascii.py` | ⚠️ xfail |
| `IdnaTestV2.json` | 2,671 | `test_wpt_idna.py` | ⚠️ xfail |
| `IdnaTestV2-removed.json` | 20 | `test_wpt_idna.py` | ⚠️ xfail |

**In-scope tests: 1,149 (100% passing)**

## IDNA Tests (xfail)

IDNA tests are marked as expected failures (`xfail`) because the Python `idna` library follows stricter RFC 5891/5892 rules than the WHATWG URL Standard's lenient UTS46 processing.

### Why Not Fix These?

1. **No Python WHATWG-compliant IDNA exists** — The `idna` library is the best available option
2. **Custom UTS46 would be error-prone** — WHATWG leniency exists for browser compatibility, not correctness
3. **Real-world domains work correctly** — Failures are obscure edge cases

> [!NOTE]
> Even ada-url (C++ with custom IDNA) only achieves 96.9% on these tests.

## Running Tests

```bash
# Run all conformance tests
uv run pytest tests/conformance/ -v

# Run only in-scope tests (URL parsing, setters, percent-encoding)
uv run pytest tests/conformance/ -v --ignore=tests/conformance/test_wpt_idna.py --ignore=tests/conformance/test_wpt_toascii.py
```
