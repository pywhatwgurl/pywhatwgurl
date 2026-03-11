pywhatwgurl
===========

[![CI](https://github.com/pywhatwgurl/pywhatwgurl/actions/workflows/main.yml/badge.svg)](https://github.com/pywhatwgurl/pywhatwgurl/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/pywhatwgurl)](https://pypi.org/project/pywhatwgurl/)
[![Python](https://img.shields.io/pypi/pyversions/pywhatwgurl)](https://pypi.org/project/pywhatwgurl/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/pywhatwgurl/pywhatwgurl/blob/master/LICENSE)
[![Typed](https://img.shields.io/badge/typing-typed-blue)](https://peps.python.org/pep-0561/)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://pywhatwgurl.github.io/pywhatwgurl)

Pure Python implementation of the WHATWG URL Standard. The goal is a small, spec-faithful library for parsing, serializing, and manipulating URLs.

Status
------
- **100% WHATWG URL Standard conformance** for core URL parsing
- Full `URL` and `URLSearchParams` API implementation
- See [Conformance](#conformance) for IDNA limitations

Installation
------------
Requires Python 3.10+.

```bash
pip install pywhatwgurl
```

Quickstart
----------

```python
from pywhatwgurl import URL

url = URL("https://user:pass@example.com:8080/path?q=1#frag")

url.hostname   # 'example.com'
url.port       # '8080'
url.pathname   # '/path'
url.search     # '?q=1'
url.hash       # '#frag'
str(url)       # 'https://user:pass@example.com:8080/path?q=1#frag'
```

`URLSearchParams` works just like the browser API:

```python
from pywhatwgurl import URLSearchParams

params = URLSearchParams("a=1&b=2&a=3")
params.get("a")        # '1'
params.get_all("a")    # ('1', '3')
params.set("b", "42")
str(params)            # 'a=1&b=42&a=3'
```

For full API details, see the [documentation](https://pywhatwgurl.github.io/pywhatwgurl).

Development
-----------
To set up a local development environment, use `uv` (recommended) or `pip`:

```bash
# Clone and install dev dependencies
uv sync --dev

# Run the test suite
uv run pytest
```

If you prefer pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Conformance
-----------
This library targets **100% conformance** with the [WHATWG URL Standard](https://url.spec.whatwg.org/) for core URL parsing, validated against the official [Web Platform Tests](https://github.com/web-platform-tests/wpt/tree/master/url).

| Test Suite | Status |
|------------|--------|
| URL parsing (urltestdata) | ✅ 873/873 (100%) |
| URL setters | ✅ 274/274 (100%) |
| URL setters stripping | ✅ 144/144 (100%) |
| URLSearchParams | ✅ 139/139 (100%) |
| Percent-encoding | ✅ 7/7 (100%) |
| IDNA/ToASCII | ⚠️ xfail (see below) |


### IDNA Limitations

IDNA tests are marked as expected failures (`xfail`) because the Python `idna` library follows stricter RFC 5891/5892 rules than the WHATWG URL Standard's lenient UTS46 processing.

**Why not fix these?**
1. No Python WHATWG-compliant IDNA implementation exists
2. Even [ada-url](https://github.com/nicolubiern/ada-url) (C++ with custom IDNA) only achieves 96.9%
3. Real-world domains work correctly — failures are obscure edge cases

For details, see [tests/conformance/README.md](tests/conformance/README.md).

Supply Chain Security
---------------------
- **SBOM**: A Software Bill of Materials (CycloneDX JSON) is automatically generated for every release and attached to the GitHub Release.
- **Audit**: All runtime dependencies are scanned for known vulnerabilities using `pip-audit` in our CI pipeline.

Roadmap
-------
- ✅ Implement URL parsing/serialization per WHATWG URL Standard
- ✅ Validate against the official URL test suite (99.8% conformance)
- Ship a minimal, typed API suitable for frameworks and tooling

WPT URL test data
-----------------
To pull down the pinned WPT URL resources, use `util/wpt_url_test_data.py`:

```bash
python util/wpt_url_test_data.py download \
  --dest_dir tests/conformance/data \
  --commit <WPT_URL_COMMIT>
```

The script downloads the WPT URL JSON resources (including `urltestdata`, setters, percent-encoding, toascii, and IDNA fixtures), preserves comments, validates schemas, and writes a metadata file with the pinned commit. The scheduled workflow `.github/workflows/fetch_test_data.yml` runs the same script via the composite action and is keyed on the pinned commit; adjust `WPT_URL_COMMIT`/`WPT_TEST_DATA_PATH` in the workflow env if you need a different pin.

Updating the pinned WPT commit
------------------------------
- A helper workflow, `.github/workflows/update_wpt_url.yml`, can be triggered manually (or waits for its weekly schedule) to fetch the latest `url/` commit from WPT, bump all pins, refresh the fixtures, and open a PR.
- To bump manually without the bot:
  1) Get the latest `url/` commit: `NEW_COMMIT=$(curl -s https://api.github.com/repos/web-platform-tests/wpt/commits?path=url&per_page=1 | jq -r '.[0].sha')`
  2) Set `WPT_URL_COMMIT` to that value in `.github/workflows/main.yml` and `.github/workflows/fetch_test_data.yml`, and update the defaults in `.github/workflows/actions/fetch_wpt_url_test_data/action.yml` and `util/wpt_url_test_data.py` to match.
  3) Refresh fixtures: `python util/wpt_url_test_data.py download --dest_dir tests/conformance/data --commit "$NEW_COMMIT"`
  4) Commit the workflow and data changes together.

Building
--------
To build the package distribution (wheel and sdist):

```bash
uv build
```

The artifacts will be generated in the `dist/` directory.

Versioning is dynamic and derived from Git tags (e.g., `0.1.0` or `0.1.dev1+...`).

Documentation
-------------
To build and serve the documentation locally:

```bash
# Install docs dependencies
uv sync --group docs

# Serve locally (with live reload)
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

Documentation is automatically deployed to GitHub Pages when changes are pushed to `master`.
