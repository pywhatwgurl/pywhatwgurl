# Changelog

All notable changes to pywhatwgurl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release
- `URL` class implementing the WHATWG URL Standard
- `URLSearchParams` class for query string manipulation
- Full IDNA 2008 support via the `idna` library
- Comprehensive test suite including WPT conformance tests
- Documentation with MkDocs Material

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## Version History

### [0.1.0] - TBD

Initial public release.

#### Features
- Complete `URL` class implementation
- Complete `URLSearchParams` class implementation  
- Browser-compatible URL parsing
- Full support for special schemes (http, https, ftp, ws, wss, file)
- IPv4 and IPv6 address parsing
- Internationalized domain name (IDN) support
- Relative URL resolution
- URL normalization

#### Compatibility
- Python 3.10+
- Tested on Linux, macOS, and Windows

[Unreleased]: https://github.com/pywhatwgurl/pywhatwgurl/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pywhatwgurl/pywhatwgurl/releases/tag/v0.1.0
