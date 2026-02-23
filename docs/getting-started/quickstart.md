# Quick Start

This guide will help you get started with pywhatwgurl in just a few minutes.

## Basic URL Parsing

The `URL` class is the main entry point for parsing URLs:

```python
from pywhatwgurl import URL

# Parse a URL
url = URL("https://user:pass@example.com:8080/path/to/page?query=value#section")
```

## Accessing URL Components

Once parsed, you can access individual URL components:

```python
from pywhatwgurl import URL

url = URL("https://user:pass@example.com:8080/path?query=value#hash")

print(url.protocol)  # "https:"
print(url.username)  # "user"
print(url.password)  # "pass"
print(url.hostname)  # "example.com"
print(url.port)      # "8080"
print(url.pathname)  # "/path"
print(url.search)    # "?query=value"
print(url.hash)      # "#hash"

# Full URL
print(url.href)      # "https://user:pass@example.com:8080/path?query=value#hash"

# Origin (protocol + host)
print(url.origin)    # "https://example.com:8080"
```

## Modifying URLs

URL components are mutable — you can modify them and the URL updates automatically:

```python
from pywhatwgurl import URL

url = URL("https://example.com/old/path")

# Change components
url.pathname = "/new/path"
url.search = "?page=2"
url.hash = "#top"

print(url.href)  # "https://example.com/new/path?page=2#top"
```

## Resolving Relative URLs

Use a base URL to resolve relative URLs:

```python
from pywhatwgurl import URL

base = URL("https://example.com/docs/guide/")

# Resolve relative URLs against the base
url1 = URL("../api/", base)
print(url1.href)  # "https://example.com/docs/api/"

url2 = URL("/absolute/path", base)
print(url2.href)  # "https://example.com/absolute/path"

url3 = URL("page.html", base)
print(url3.href)  # "https://example.com/docs/guide/page.html"
```

## Working with Query Parameters

The `search_params` property provides a `URLSearchParams` object for easy query string manipulation. It supports Pythonic dictionary-style access:

```python
from pywhatwgurl import URL

url = URL("https://example.com/search?q=python&page=1")

# Access parameters using dictionary syntax
print(url.search_params["q"])     # "python"
print(url.search_params["page"])  # "1"

# Check if a parameter exists
if "q" in url.search_params:
    print("Query parameter found!")

# Modify parameters using dictionary syntax
url.search_params["page"] = "2"        # Set a value
url.search_params.append("sort", "date")  # Add another value
del url.search_params["q"]              # Delete a parameter

print(url.search)  # "?page=2&sort=date"

# Iterate over parameters (Pythonic way)
for key, value in url.search_params.items():
    print(f"{key}: {value}")

# Get the number of parameters
print(len(url.search_params))  # 2
```

## Handling Invalid URLs

When a URL cannot be parsed, a `ValueError` is raised:

```python
from pywhatwgurl import URL

try:
    url = URL("not a valid url")
except ValueError as e:
    print(f"Invalid URL: {e}")

# Use URL.parse() for a None-returning alternative
url = URL.parse("not a valid url")
if url is None:
    print("Invalid URL")

# Or check before parsing
if URL.can_parse("https://example.com"):
    url = URL("https://example.com")
```

## Using URLSearchParams Directly

You can also use `URLSearchParams` independently for query string manipulation:

```python
from pywhatwgurl import URLSearchParams

# Create from string
params = URLSearchParams("name=John&age=30")

# Create from dictionary
params = URLSearchParams({"name": "John", "age": "30"})

# Create from list of tuples (useful for duplicate keys)
params = URLSearchParams([("name", "John"), ("tag", "a"), ("tag", "b")])

# Dictionary-style access
print(params["name"])  # "John"
params["city"] = "NYC"
del params["age"]

# Check membership
if "name" in params:
    print("Name is set")

# Get all values for a key (useful when there are duplicates)
print(params.get_all("tag"))  # ("a", "b")

# Convert to string
print(str(params))  # "name=John&tag=a&tag=b&city=NYC"

# Iterate over all key-value pairs
for key, value in params.items():
    print(f"{key}={value}")
```

## Next Steps

- Learn more about [URL Parsing](../guide/url-parsing.md) and edge cases
- Explore [URL Components](../guide/url-components.md) in detail
- See the complete [API Reference](../api/url.md)
