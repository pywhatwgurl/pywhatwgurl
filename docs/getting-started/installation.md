# Installation

## Requirements

- Python 3.10 or higher

## Install from PyPI

The recommended way to install pywhatwgurl is from PyPI:

=== "pip"

    ```bash
    pip install pywhatwgurl
    ```

=== "uv"

    ```bash
    uv add pywhatwgurl
    ```

=== "poetry"

    ```bash
    poetry add pywhatwgurl
    ```

=== "pipx (CLI tools)"

    ```bash
    pipx install pywhatwgurl
    ```

## Install from Source

For development or to get the latest unreleased changes:

```bash
git clone https://github.com/pywhatwgurl/pywhatwgurl.git
cd pywhatwgurl
pip install -e .
```

Or with uv:

```bash
git clone https://github.com/pywhatwgurl/pywhatwgurl.git
cd pywhatwgurl
uv sync
```

## Verify Installation

After installation, verify it works:

```python
>>> from pywhatwgurl import URL
>>> url = URL("https://example.com/path")
>>> url.hostname
'example.com'
```

## Dependencies

pywhatwgurl has minimal dependencies:

| Package | Purpose |
|---------|---------|
| `idna` | IDNA 2008 encoding for internationalized domain names |

All other functionality is implemented in pure Python with no compiled extensions.

## Next Steps

Now that you have pywhatwgurl installed, head to the [Quick Start](quickstart.md) guide to learn the basics.
