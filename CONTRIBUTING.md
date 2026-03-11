# Contributing

Thank you for your interest in contributing to pywhatwgurl! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Setting Up the Development Environment

1. **Fork and clone the repository**

    ```bash
    git clone https://github.com/YOUR_USERNAME/pywhatwgurl.git
    cd pywhatwgurl
    ```

2. **Install dependencies**

    ```bash
    uv sync
    ```

3. **Install pre-commit hooks**

    ```bash
    uv run pre-commit install
    ```

4. **Run tests to verify setup**

    ```bash
    uv run pytest
    ```

## Development Workflow

### Creating a Branch

Create a branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Write your code following our style guidelines
2. Add or update tests as needed
3. Update documentation if applicable
4. Run the test suite

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pywhatwgurl

# Run specific test file
uv run pytest tests/unit/test_python_api.py

# Run conformance tests only
uv run pytest tests/conformance/
```

### Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

Pre-commit hooks will run these checks automatically before each commit.

### Security Checks

CI and pre-commit run two security-related checks:

- **Ruff `S` rules** ([flake8-bandit](https://github.com/tylerwince/flake8-bandit)) — static analysis for common security pitfalls in Python code. These run as part of `uv run ruff check`.
- **pip-audit** — scans runtime dependencies for known vulnerabilities. Only runtime dependencies (not dev tools) are audited.
- **cyclonedx-bom** — generates a Software Bill of Materials (SBOM) for releases.

## Submitting Changes

### Commit Messages

Write clear, concise commit messages:

```
feat: add support for blob URLs
fix: handle empty port correctly
docs: update installation guide
test: add edge case tests for IPv6
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Tests only
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Pull Requests

1. Push your branch to your fork
2. Open a Pull Request against `master`
3. Fill out the PR template
4. Wait for review

## Types of Contributions

### Bug Reports

Found a bug? Please open an issue with:

- Python version
- pywhatwgurl version
- Minimal reproduction code
- Expected vs actual behavior

### Feature Requests

Have an idea? Open an issue describing:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve API documentation

### Code Contributions

Before starting significant work, please open an issue to discuss your approach.

## Testing Guidelines

### Test Structure

- Unit tests go in `tests/`
- Conformance tests go in `tests/conformance/`
- Use descriptive test names

### Writing Tests

```python
def test_url_parsing_with_port():
    """URL should correctly parse port from URL string."""
    url = URL("https://example.com:8080/path")
    assert url.port == "8080"
    assert url.hostname == "example.com"
```

### Conformance Tests

This project aims for 100% compliance with the [WHATWG URL Standard](https://url.spec.whatwg.org/).

We use the [Web Platform Tests (WPT)](https://github.com/web-platform-tests/wpt) suite to verify conformance. These tests are located in `tests/conformance/`. When adding or modifying features, you must ensure that your changes pass these conformance tests.

If you find a discrepancy between our implementation and the spec, please check the WPT tests first.

## Documentation Guidelines

### Building Docs Locally

```bash
# Install docs dependencies
uv sync --group docs

# Serve docs locally
uv run mkdocs serve

# Build docs
uv run mkdocs build
```

### Writing Documentation

- Use clear, simple language
- Include code examples
- Link to related sections
- Keep the user's perspective in mind

## Questions?

- Open a [GitHub Discussion](https://github.com/pywhatwgurl/pywhatwgurl/discussions)
- Check existing issues and PRs

Thank you for contributing!
