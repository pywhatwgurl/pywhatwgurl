# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-03

### Added
- Initial public release of `pywhatwgurl`.
- Full `URL` and `URLSearchParams` API implementation per the WHATWG URL Standard.
- 100% WHATWG URL Standard conformance for core URL parsing (validated against [Web Platform Tests](https://github.com/web-platform-tests/wpt/tree/master/url)).
- Pure Python, fully type-annotated (`py.typed`), zero compiled dependencies.
- Comprehensive documentation with API reference, user guide, and migration notes.
- CI pipeline with linting (ruff), type checking (mypy), and security scanning (pip-audit).
- Automated weekly WPT test data updates via GitHub Actions.
- SBOM generation (CycloneDX) attached to every GitHub release.

### Known Limitations
- **IDNA Conformance**: IDNA tests are marked as expected failures (`xfail`). The Python `idna` library follows stricter RFC 5891/5892 rules than the WHATWG URL Standard's lenient UTS46 processing.
    - Real-world domains generally work correctly; failures are primarily with obscure edge cases not covered by the stricter RFCs.
    - No Python WHATWG-compliant IDNA implementation currently exists.
