# WPT URL Test Traceability Matrix

This document provides a complete mapping between WPT URL JavaScript tests and their Python equivalents in pywhatwgurl.

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Applicable tests with Python equivalents | 24 | ✅ Complete |
| Browser-only (intentionally excluded) | 4 | N/A |
| JS-only semantics (intentionally excluded) | See below | N/A |
| **Total WPT JS test files** | **28** | - |

---

## Applicable Tests

### Data-Driven Tests

| WPT JS File | Python Test File | Data File(s) | Tests |
|-------------|------------------|--------------|-------|
| `url-constructor.any.js` | `test_wpt_urltestdata.py` | `urltestdata.json` | 873 |
| `url-origin.any.js` | `test_wpt_urltestdata.py` | `urltestdata.json` | (included) |
| `url-setters.any.js` | `test_wpt_setters.py` | `setters_tests.json` | 274 |
| `url-statics-canparse.any.js` | `test_wpt_url_statics.py` | `urltestdata.json` | 8 + 1 |
| `url-statics-parse.any.js` | `test_wpt_url_statics.py` | `urltestdata.json` | 8 + 1 |
| `url-tojson.any.js` | `test_wpt_url_tojson.py` | - | 2 |
| `toascii.window.js` | `test_wpt_toascii.py` | `toascii.json` | 261 |
| `IdnaTestV2.window.js` | `test_wpt_idna.py` | `IdnaTestV2.json` | 2671×2 |
| `IdnaTestV2-removed.window.js` | `test_wpt_idna.py` | `IdnaTestV2-removed.json` | 20×2 |
| `percent-encoding.window.js` | `test_wpt_percent_encoding.py` | `percent-encoding.json` | 7 |

### Inline Tests (URLSearchParams)

| WPT JS File | Python Test File | Tests |
|-------------|------------------|-------|
| `urlencoded-parser.any.js` | `test_wpt_urlsearchparams.py` | 36 |
| `urlsearchparams-constructor.any.js` | `test_wpt_urlsearchparams.py` | ~15 |
| `urlsearchparams-append.any.js` | `test_wpt_urlsearchparams.py` | 6 |
| `urlsearchparams-delete.any.js` | `test_wpt_urlsearchparams.py` | 15 |
| `urlsearchparams-get.any.js` | `test_wpt_urlsearchparams.py` | 4 |
| `urlsearchparams-getall.any.js` | `test_wpt_urlsearchparams.py` | 4 |
| `urlsearchparams-has.any.js` | `test_wpt_urlsearchparams.py` | 6 |
| `urlsearchparams-set.any.js` | `test_wpt_urlsearchparams.py` | 4 |
| `urlsearchparams-size.any.js` | `test_wpt_urlsearchparams.py` | 8 |
| `urlsearchparams-sort.any.js` | `test_wpt_urlsearchparams.py` | 8 |
| `urlsearchparams-foreach.any.js` | `test_wpt_urlsearchparams.py` | 7 |
| `urlsearchparams-stringifier.any.js` | `test_wpt_urlsearchparams.py` | 26 |

### Other Inline Tests

| WPT JS File | Python Test File | Tests |
|-------------|------------------|-------|
| `url-searchparams.any.js` | `test_wpt_url_searchparams_integration.py` | 7 |
| `url-setters-stripping.any.js` | `test_wpt_setters_stripping.py` | 144 |

---

## Browser-Only Tests (Intentionally Excluded)

| WPT JS File | Reason for Exclusion |
|-------------|---------------------|
| `url-setters-a-area.window.js` | Tests HTML `<a>` and `<area>` element href behavior (DOM) |
| `historical.any.js` | Tests `location`, `createElement`, `structuredClone` (browser APIs) |
| `idlharness.any.js` | Tests Web IDL interface conformance (browser-specific) |
| `javascript-urls.window.js` | Tests `javascript:` URL execution in iframes (browser security) |

---

## Data Files

| WPT File | pywhatwgurl File | Test Cases |
|----------|------------------|------------|
| `resources/urltestdata.json` | `data/urltestdata.json` | 873 |
| `resources/setters_tests.json` | `data/setters_tests.json` | 274 |
| `resources/toascii.json` | `data/toascii.json` | 87 |
| `resources/IdnaTestV2.json` | `data/IdnaTestV2.json` | 2,671 |
| `resources/IdnaTestV2-removed.json` | `data/IdnaTestV2-removed.json` | 20 |
| `resources/percent-encoding.json` | `data/percent-encoding.json` | 7 |
| `resources/urltestdata-javascript-only.json` | *(not included)* | 1 (JS-specific) |

> **Note:** `urltestdata-javascript-only.json` contains 1 test case with lone Unicode surrogates that cannot be represented in Python strings.

---

## Known Differences from WPT JS Tests

### Not Applicable to Python

| Difference | Reason |
|------------|--------|
| `urltestdata-javascript-only.json` not tested | Contains lone Unicode surrogates that cannot exist in Python strings |
| `toascii.window.js` `<a>`/`<area>` element tests | HTML DOM elements not available in Python |

### Methodology Differences

| WPT JS Test | Python Test | Difference |
|-------------|-------------|------------|
| `url-statics-canparse.any.js` | `test_wpt_url_statics.py` | JS passes `undefined` value; Python passes `"undefined"` string |
| `percent-encoding.window.js` | `test_wpt_percent_encoding.py` | JS uses iframe navigation; Python uses URL constructor |

### JS-Only Tests (Intentionally Excluded by Design)

| WPT JS Test | Feature | Reason |
|-------------|---------|--------|
| `urlsearchparams-constructor.any.js` | `DOMException` as arg | Browser-only API |
| `urlsearchparams-constructor.any.js` | `FormData` as arg | Browser-only API |
| `urlsearchparams-constructor.any.js` | `Symbol.iterator` | JS protocol; Python uses `__iter__` |
| `urlsearchparams-constructor.any.js` | Lone surrogate dict keys | Python strings cannot contain lone surrogates |
| `urlsearchparams-delete.any.js` | `null`/`undefined` key coercion | JS auto-coerces; Python callers pass strings |
| `urlsearchparams-has.any.js` | `null`/`undefined` value coercion | JS auto-coerces; Python callers pass strings |
| `urlsearchparams-append.any.js` | `null` name/value coercion | JS auto-coerces; Python callers pass strings |

### Extra Coverage in Python

| Python Test | Benefit |
|-------------|---------|
| `test_wpt_urltestdata.py` | Tests `origin` field inline (WPT has separate `url-origin.any.js`) |
| `test_wpt_idna.py` | Tests both `domain_to_ascii()` directly AND via URL constructor (2× coverage) |
| `test_wpt_toascii.py` | Tests via `domain_to_ascii()`, `host` setter, AND `hostname` setter (3 paths) |

---

## Test Count Summary

```
Total pywhatwgurl conformance tests: 7,162
  - Passed:  7,151
  - Skipped: 1
  - XFailed: 10 (IDNA edge cases where Python idna library differs from WHATWG)
```

