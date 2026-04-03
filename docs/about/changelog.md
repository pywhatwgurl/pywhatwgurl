# Changelog

All notable changes to pywhatwgurl are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-03

### Changed
- Improved parser dispatch and percent-encoding hot paths for better runtime performance.
- Modernized internal type annotations and cleaned up Python implementation details.
- Refreshed the pinned WPT URL test data used by the conformance suite.

### Fixed
- Repaired CI and release workflow issues so the Python test matrix, dependency audit, and SBOM generation run correctly.
- Corrected test mock signatures and removed unreachable utility code.
- Cleaned up documentation issues in the README, CONTRIBUTING guide, and IDNA notes.

## [0.1.0] - 2026-03-03

### Added
- Initial public release of `pywhatwgurl`.
- Full `URL` and `URLSearchParams` API implementation per the WHATWG URL Standard.
- 100% WHATWG URL Standard conformance for core URL parsing, validated against the official Web Platform Tests.
- Pure Python, fully type-annotated (`py.typed`), with no compiled dependencies.
- Comprehensive documentation with API reference, user guide, and migration notes.
- CI pipeline with linting (`ruff`), type checking (`mypy`), and security scanning (`pip-audit`).
- Automated weekly WPT test data updates via GitHub Actions.
- SBOM generation (CycloneDX) attached to each GitHub release.

### Known Limitations
- IDNA tests are marked as expected failures (`xfail`) because Python's `idna` library follows stricter RFC 5891/5892 rules than the WHATWG URL Standard's lenient UTS46 processing.

[Unreleased]: https://github.com/pywhatwgurl/pywhatwgurl/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pywhatwgurl/pywhatwgurl/releases/tag/v0.1.1
[0.1.0]: https://github.com/pywhatwgurl/pywhatwgurl/releases/tag/v0.1.0
