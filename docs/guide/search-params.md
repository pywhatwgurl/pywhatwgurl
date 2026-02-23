# URLSearchParams

The `URLSearchParams` class provides utilities for working with URL query strings according to the [WHATWG URL Standard](https://url.spec.whatwg.org/#interface-urlsearchparams). It implements Python's `MutableMapping` interface, allowing Pythonic dictionary-style access.

## Creating URLSearchParams

The [URLSearchParams constructor](https://url.spec.whatwg.org/#dom-urlsearchparams-urlsearchparams) accepts several initialization formats:

### From a Query String

```python
from pywhatwgurl import URLSearchParams

# With or without leading "?"
params = URLSearchParams("name=John&age=30")
params = URLSearchParams("?name=John&age=30")
```

!!! info "Query String Parsing"
    Query strings are parsed using the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser).

### From a Dictionary

```python
params = URLSearchParams({"name": "John", "age": "30"})
```

### From a List of Tuples

Useful when you have duplicate keys:

```python
params = URLSearchParams([
    ("tag", "python"),
    ("tag", "url"),
    ("tag", "parsing")
])
```

### Empty

```python
params = URLSearchParams()
```

## Reading Parameters

### Dictionary-Style Access (Recommended)

```python
params = URLSearchParams("name=John&age=30")

# Get a value (raises KeyError if not found)
print(params["name"])  # "John"

# Check if a parameter exists
if "name" in params:
    print("Name is set!")

# Safe get with default
value = params.get("missing")  # None
```

### `get_all(name)` for Multiple Values

Returns all values for a parameter as a tuple. Corresponds to [getAll()](https://url.spec.whatwg.org/#dom-urlsearchparams-getall) in the spec:

```python
params = URLSearchParams("tag=a&tag=b&tag=c")
print(params.get_all("tag"))      # ("a", "b", "c")
print(params.get_all("missing"))  # ()
```

## Modifying Parameters

### Dictionary-Style Assignment (Recommended)

```python
params = URLSearchParams("tag=a&tag=b")

# Set a value (replaces all existing values for this key)
params["tag"] = "new"
print(str(params))  # "tag=new"

# Delete a key
del params["tag"]
```

### `append(name, value)` for Multiple Values

The [append()](https://url.spec.whatwg.org/#dom-urlsearchparams-append) method adds a parameter without removing existing ones:

```python
params = URLSearchParams("tag=a")
params.append("tag", "b")
print(str(params))  # "tag=a&tag=b"
```

### `delete(name, value)` for Specific Values

The [delete()](https://url.spec.whatwg.org/#dom-urlsearchparams-delete) method can remove only matching values:

```python
params = URLSearchParams("a=1&a=2&a=3")
params.delete("a", "2")  # Only remove a=2
print(str(params))  # "a=1&a=3"
```

## Iterating

### Pythonic Iteration (Recommended)

```python
params = URLSearchParams("a=1&b=2&c=3")

# Iterate over key-value pairs
for key, value in params.items():
    print(f"{key}: {value}")

# Get all keys
for key in params.keys():
    print(key)

# Get all values
for value in params.values():
    print(value)
```

### Alternative Iterations

```python
params = URLSearchParams("a=1&b=2")

print(list(params.keys()))    # ["a", "b"]
print(list(params.values()))  # ["1", "2"]
print(list(params.items()))   # [("a", "1"), ("b", "2")]
```

## Size and Length

Use `len()` to get the number of parameters. Corresponds to the [size](https://url.spec.whatwg.org/#dom-urlsearchparams-size) property:

```python
params = URLSearchParams("a=1&b=2&c=3")
print(len(params))  # 3
```

## Sorting

### `sort()`

The [sort()](https://url.spec.whatwg.org/#dom-urlsearchparams-sort) method sorts parameters by key using a stable sort:

```python
params = URLSearchParams("c=3&a=1&b=2")
params.sort()
print(str(params))  # "a=1&b=2&c=3"
```

## String Conversion

Use `str()` to get the encoded query string (without `?`). This uses the [application/x-www-form-urlencoded serializer](https://url.spec.whatwg.org/#concept-urlencoded-serializer):

```python
params = URLSearchParams({"name": "John Doe", "city": "New York"})
print(str(params))  # "name=John+Doe&city=New+York"
```

!!! note "Space Encoding"
    `URLSearchParams` encodes spaces as `+` (not `%20`) per the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#application/x-www-form-urlencoded) format, which is standard for query strings and HTML form data.

## Using with URL

`URLSearchParams` integrates seamlessly with the `URL` class via the [searchParams](https://url.spec.whatwg.org/#dom-url-searchparams) property:

```python
from pywhatwgurl import URL

url = URL("https://example.com/search?q=python")

# Access search_params with dictionary-style syntax
print(url.search_params["q"])  # "python"

# Modify search_params (automatically updates the URL)
url.search_params["q"] = "javascript"
url.search_params["page"] = "2"

print(url.href)  # "https://example.com/search?q=javascript&page=2"

# Delete parameters
del url.search_params["page"]
print(url.search)  # "?q=javascript"
```

!!! info "URL Update Steps"
    When `search_params` is modified, the URL's query is automatically updated per the [update steps](https://url.spec.whatwg.org/#concept-urlsearchparams-update) defined in the spec.

## Practical Examples

### Building a Query String

```python
from pywhatwgurl import URLSearchParams

params = URLSearchParams()
params["search"] = "python url parsing"
params["category"] = "libraries"
params["sort"] = "stars"
params["order"] = "desc"

query = str(params)
# "search=python+url+parsing&category=libraries&sort=stars&order=desc"
```

### Parsing Form Data

The [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded-parser) format is used for HTML form submissions:

```python
form_data = "username=john_doe&email=john%40example.com&newsletter=on"
params = URLSearchParams(form_data)

print(params["username"])      # "john_doe"
print(params["email"])         # "john@example.com"
print("newsletter" in params)  # True
```

### Handling Multiple Values

```python
params = URLSearchParams()

# Add multiple tags (use append for duplicates)
for tag in ["python", "url", "whatwg", "parsing"]:
    params.append("tag", tag)

print(params.get_all("tag"))  # ("python", "url", "whatwg", "parsing")
print(str(params))            # "tag=python&tag=url&tag=whatwg&tag=parsing"
```

## Further Reading

- [URLSearchParams interface](https://url.spec.whatwg.org/#interface-urlsearchparams) — Complete API specification
- [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#urlencoded-parsing) — Parsing and serialization rules

## Next Steps

- See the complete [URLSearchParams API Reference](../api/urlsearchparams.md)
- Learn about [URL Components](url-components.md)
