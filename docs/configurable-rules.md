# Docstring Linter

## Configurable Rule Reference

These rules can be enabled or disabled through `select` and `ignore`.   For style policies such as `returns_none` or `args_section`, see [Style Policies](/docs/style-policies.md).

### Presence

#### docstring_exists

Every entity (module, class, function, method) must have a docstring.

Subject to the configured scope (`modules`, `classes`, `functions`, `methods`) and the two empty `__init__` exemptions.

```python
# Bad
def process(data: list) -> list:
    return data

# Good
def process(data: list) -> list:
    """Process and return filtered data."""
    return data
```

---

#### return_type_annotation

Every function or method must have a `-> type` return annotation in its signature.

```python
# Bad
def process(data: list):
    return data

# Good
def process(data: list) -> list:
    return data

# Good
def log(message: str) -> None:
    print(message)
```

---

### Summary

#### imperative_mood

The summary must start with an imperative verb, not third-person singular.

```python
# Bad
def process() -> None:
    """Processes the input data."""

# Bad
def get_value() -> int:
    """Returns the current value."""

# Bad
def update() -> None:
    """Modifies the internal state."""

# Good
def process() -> None:
    """Process the input data."""

# Good
def get_value() -> int:
    """Return the current value."""

# Good (known exception, not a conjugated verb)
def access_db() -> None:
    """Access the database."""
```

Words not treated as third-person singular verbs: `process`, `access`, `class`, `status`, `focus`, `alias`, `analysis`, `basis`, etc.

Not applied to module docstrings.

---

#### summary_too_long

The summary line must not exceed the configured maximum length (default: 80 characters).

```python
# Bad (> 80 chars)
def process(data: list) -> list:
    """Process the input data by applying all registered transformations in sequence."""

# Good
def process(data: list) -> list:
    """Process the input data by applying all registered transformations."""
```

Configure the limit in configuration file:

```toml
[tool.docstring-linter]
summary_max_length = 72
```

---

### Args / Returns / Raises

#### args_order

The order of arguments in the `Args:` section must match the order in the function signature.

```python
# Bad
def process(x: int, y: str) -> None:
    """Process data.

    Args:
        y (str): Second.
        x (int): First.

    """

# Good
def process(x: int, y: str) -> None:
    """Process data.

    Args:
        x (int): First.
        y (str): Second.

    """
```

---

### Sections

#### indentation

Docstring indentation must be consistent. Nested indentation beyond a section entry is not allowed.

```python
# Bad: inconsistent indentation (3+ levels)
def process() -> None:
    """Process data.

    Args:
        x (int): Input.
            Extra indent.
                Even more indent.

    """

# Good
def process(x: int) -> None:
    """Process data.

    Args:
        x (int): Input.

    Returns:
        None

    """
```

---

#### section_capitalization

Section names must be correctly capitalized.

```python
# Bad
def process(x: int) -> int:
    """Process data.

    args:
        x (int): Input.

    returns:
        int: Result.

    """

# Good
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.

    Returns:
        int: Result.

    """
```

Recognized sections: `Args`, `Returns`, `Yields`, `Raises`, `Attributes`, `Example`, `Examples`, `Note`, `Notes`, `Todo`.

---

#### section_order

Sections must appear in the expected order.

Expected order: `Attributes` -> `Args` -> `Returns` -> `Yields` -> `Raises` -> `Example`/`Examples` -> `Note`/`Notes` -> `Todo`

```python
# Bad: Returns before Args
def process(x: int) -> int:
    """Process data.

    Returns:
        int: Result.

    Args:
        x (int): Input.

    """

# Good
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.

    Returns:
        int: Result.

    Raises:
        ValueError: If x is negative.

    """
```

---

#### unknown_section

A section name that is not in the recognized list triggers an error. Common mistake: `Arguments:` instead of `Args:`.

Recognized sections: `Args`, `Returns`, `Yields`, `Raises`, `Attributes`, `Example`, `Examples`, `Note`, `Notes`, `Todo`.

```python
# Bad
def process(x: int) -> int:
    """Process data.

    Arguments:
        x (int): Input.

    Returns:
        int: Result.

    """

# Good
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.

    Returns:
        int: Result.

    """
```

---
