# WHATWG Compliance

pywhatwgurl aims to be a compliant implementation of the [WHATWG URL Standard](https://url.spec.whatwg.org/).

## What is the WHATWG URL Standard?

The WHATWG (Web Hypertext Application Technology Working Group) URL Standard defines how URLs should be parsed, serialized, and manipulated. It was created to:

- **Unify browser behavior**: All major browsers follow this standard
- **Refine generic RFCs**: Adapts the generic URI syntax from RFC 3986 for web browser requirements
- **Define error handling**: Specifies exactly how invalid URLs should be handled

## Conformance Testing

pywhatwgurl is tested against the official [Web Platform Tests (WPT)](https://github.com/web-platform-tests/wpt) for URL parsing. These are the same tests used by browser vendors to verify their implementations.

### Test Results

| Category | Tests | Status |
|----------|-------|--------|
| URL parsing | 873 | ✅ 100% |
| URL setters | 274 | ✅ 100% |
| URL setters stripping | 144 | ✅ 100% |
| URLSearchParams | 139 | ✅ 100% |
| Percent encoding | 7 | ✅ 100% |
| IDNA/ToASCII | 5,342 | ⚠️ See below |

**Total conformance tests: 7,162 (7,151 passed, 1 skipped, 10 xfailed)**

### Running Conformance Tests

```bash
# Clone the repository
git clone https://github.com/pywhatwgurl/pywhatwgurl.git
cd pywhatwgurl

# Install dependencies
uv sync

# Run conformance tests
uv run pytest tests/conformance/
```

## IDNA Processing

IDNA (Internationalized Domain Names in Applications) tests are marked as expected failures because the Python `idna` library follows stricter RFC 5891/5892 rules than the WHATWG URL Standard's lenient UTS46 processing.

The WHATWG URL Standard specifies IDNA with:

- `CheckHyphens` = false
- `VerifyDnsLength` = false

Our implementation configures these options, but some edge cases still differ due to underlying library behavior. Real-world domain names work correctly.


## Comparison with urllib.parse

| Feature | pywhatwgurl | urllib.parse |
|---------|-------------|--------------|
| Standard | WHATWG URL | RFC 3986 |
| Browser compatible | ✅ Yes | ⚠️ Generic URI parser |
| Backslash handling | Converts to `/` | Preserved |
| Default port handling | Omitted | Preserved |
| Host normalization | Lowercase | Preserved |
| Unicode hosts | IDNA encoded | Preserved |

## Contributing to Compliance

Found a compliance issue? Please:

1. Check if it's already reported in [GitHub Issues](https://github.com/pywhatwgurl/pywhatwgurl/issues)
2. If not, open a new issue with:
   - The input URL
   - Expected behavior (per WHATWG spec)
   - Actual behavior
   - Link to the relevant spec section

### Missing Test Cases

If a URL behavior is not covered by the WPT test suite, consider [contributing to WPT](https://github.com/web-platform-tests/wpt/blob/master/CONTRIBUTING.md) directly. This benefits all implementations.

### Conformance Test Discrepancies

Our conformance tests should mirror the WPT test suite exactly. If you find a discrepancy between our tests and WPT, please open an issue or PR to align them.

## Resources

- [WHATWG URL Standard](https://url.spec.whatwg.org/)
- [Web Platform Tests - URL](https://github.com/web-platform-tests/wpt/tree/master/url)
- [MDN: URL API](https://developer.mozilla.org/en-US/docs/Web/API/URL)
