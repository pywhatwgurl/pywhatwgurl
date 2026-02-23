# Exceptions

pywhatwgurl raises standard Python exceptions for error handling.

## ValueError

Raised when URL parsing fails due to an invalid URL:

```python
from pywhatwgurl import URL

try:
    url = URL("not-a-valid-url")
except ValueError as e:
    print(f"Failed to parse URL: {e}")
```

### Common Causes

- Missing or invalid scheme
- Invalid characters in hostname
- Malformed IPv6 address
- Invalid port number

## TypeError

Raised when `URLSearchParams` is initialized with invalid data:

```python
from pywhatwgurl import URLSearchParams

try:
    # List elements must be 2-element sequences
    params = URLSearchParams([("key",)])  # Missing value
except TypeError as e:
    print(f"Invalid initialization: {e}")
```

## KeyError

Raised when accessing a non-existent key in `URLSearchParams`:

```python
from pywhatwgurl import URLSearchParams

params = URLSearchParams("foo=1")

try:
    value = params["nonexistent"]  # Raises KeyError
except KeyError:
    print("Key not found")

# To avoid KeyError, use .get() which returns None
value = params.get("nonexistent")  # Returns None
```

## Examples

### Invalid Scheme

```python
from pywhatwgurl import URL

try:
    URL("://missing-scheme.com")
except ValueError:
    print("URL must have a valid scheme")
```

### Invalid Host

```python
try:
    URL("https://[invalid-ipv6")
except ValueError:
    print("Invalid IPv6 address format")
```

### Invalid Port

```python
try:
    URL("https://example.com:notanumber")
except ValueError:
    print("Port must be a valid number")
```

## Error Handling Best Practices

### Use URL.parse() for Safe Parsing

The `URL.parse()` static method returns `None` instead of raising an exception:

```python
from pywhatwgurl import URL

# Returns None if invalid, never raises
url = URL.parse(user_input)
if url is None:
    print("Please enter a valid URL")
else:
    print(f"Valid URL: {url.href}")
```

### Use URL.can_parse() to Validate

Check if a URL can be parsed without actually parsing it:

```python
from pywhatwgurl import URL

if URL.can_parse(user_input):
    url = URL(user_input)  # Safe to parse
else:
    print("Invalid URL format")
```

### Provide Helpful Error Messages

```python
from pywhatwgurl import URL

def validate_url(url_string: str) -> tuple[bool, str]:
    """Validate a URL and return a user-friendly message."""
    try:
        url = URL(url_string)
        return True, f"Valid URL: {url.href}"
    except ValueError as e:
        return False, f"Invalid URL: {e}"
```
