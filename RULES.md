# Docstring Linter

Python linter that checks docstring conformance to Google style.

## Rule Reference

26 rules in total, all configurable in `pyproject.toml` file or `.docstring-linter.toml` file.

---

### docstring_exists

Every entity (module, class, function, method) must have a docstring.

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

### summary_exists

The docstring must contain a non-empty summary line.

```python
# Bad
def process() -> None:
    """

    Args:
        ...

    """
    pass

# Good
def process() -> None:
    """Process the input data.
    
    Args:
        ...
    
    """
    pass
```

---

### summary_punctuation

The summary must end with a period.

```python
# Bad
def process() -> None:
    """Process the input data"""

# Good
def process() -> None:
    """Process the input data."""
```

---

### summary_first_line

The summary must start on the same line as the opening triple quotes.

```python
# Bad
def process() -> None:
    """
    Process the input data.
    """

# Good
def process() -> None:
    """Process the input data."""

# Good (multi-line)
def process(data: list) -> list:
    """Process the input data.

    Args:
        data (list): Input data.

    Returns:
        list: Filtered data.

    """
```

---

### imperative_mood

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

Excepted words (not flagged despite trailing `s`): `process`, `access`, `class`, `status`, `focus`, `alias`, `analysis`, `basis`, etc.

Not applied to module docstrings.

---

### summary_too_long

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

### return_type_annotation

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

### args_match

Strict bijection between signature parameters and the `Args:` section of the docstring. Checks name, type `(type)`, and presence of a description.

```python
# Bad: parameter 'age' not documented
def create_user(name: str, age: int) -> dict:
    """Create a new user.

    Args:
        name (str): User name.

    Returns:
        dict: User record.

    """

# Bad: type mismatch (int vs float)
def calculate(value: int) -> float:
    """Calculate result.

    Args:
        value (float): Input value.

    Returns:
        float: Result.

    """

# Bad: phantom parameter 'email' in docstring
def greet(name: str) -> str:
    """Greet a user.

    Args:
        name (str): User name.
        email (str): User email.

    Returns:
        str: Greeting.

    """

# Bad: type missing in docstring
def process(data: list) -> list:
    """Process data.

    Args:
        data: Input data.

    Returns:
        list: Result.

    """

# Good
def create_user(name: str, age: int) -> dict:
    """Create a new user.

    Args:
        name (str): User name.
        age (int): User age in years.

    Returns:
        dict: User record.

    """
```

---

### duplicate_arg

An argument must not appear more than once in the `Args:` section.

```python
# Bad
def process(x: int, y: int) -> int:
    """Process data.

    Args:
        x (int): First input.
        y (int): Second input.
        x (int): Duplicate entry.

    Returns:
        int: Result.

    """

# Good
def process(x: int, y: int) -> int:
    """Process data.

    Args:
        x (int): First input.
        y (int): Second input.

    Returns:
        int: Result.

    """
```

---

### param_order

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

### returns_section

The `Returns:` section must be **present** when the signature declares a return type. This rule only checks presence; type correctness is handled by `returns_type_match`. Disable `returns_section` (keeping `returns_type_match` on) to make the section optional while still validating its type when present.

```python
# Bad: no Returns section
def get_name() -> str:
    """Get the user name."""
    return "Alice"

# Good
def get_name() -> str:
    """Get the user name.

    Returns:
        str: The user name.

    """
    return "Alice"

# Good (one-liner -> None exempt by default)
def reset() -> None:
    """Reset all values."""

# Good (multi-line -> None: Returns required)
def reset(deep: bool) -> None:
    """Reset all values.

    Args:
        deep (bool): Whether to reset nested values.

    Returns:
        None: This method resets in place.

    """
```

---

### returns_type_match

When a `Returns:` section exists, its type must match the signature, and the type must not be missing. This rule never reports a missing section (that is `returns_section`).

```python
# Bad: type mismatch
def get_name() -> str:
    """Get the user name.

    Returns:
        int: The name.

    """
    return "Alice"

# Bad: type missing in Returns
def get_name() -> str:
    """Get the user name.

    Returns:
        The name.

    """
    return "Alice"

# Good
def get_name() -> str:
    """Get the user name.

    Returns:
        str: The user name.

    """
    return "Alice"
```

---

### raises_match

Strict bijection between explicit `raise ExceptionType` statements in the code and the `Raises:` section of the docstring.

```python
# Bad: ValueError raised but not documented
def validate(x: int) -> int:
    """Validate input.

    Args:
        x (int): Input.

    Returns:
        int: Validated input.

    """
    if x < 0:
        raise ValueError("negative")
    return x

# Bad: TypeError documented but never raised
def validate(x: int) -> int:
    """Validate input.

    Args:
        x (int): Input.

    Returns:
        int: Validated input.

    Raises:
        TypeError: Never actually raised.

    """
    return x

# Good
def validate(x: int) -> int:
    """Validate input.

    Args:
        x (int): Input.

    Returns:
        int: Validated input.

    Raises:
        ValueError: If x is negative.

    """
    if x < 0:
        raise ValueError("negative")
    return x
```

Note: bare `raise` (re-raise), dynamic raises, or raises from internal calls are ignored.

---

### attributes_section

Every class must have an `Attributes:` section in its docstring, with type and description for each attribute.

```python
# Bad: no Attributes section
class User:
    """Represent a user."""

# Bad: type missing
class User:
    """Represent a user.

    Attributes:
        name: The user name.

    """

# Good
class User:
    """Represent a user.

    Attributes:
        name (str): The user name.
        age (int): The user age.

    """
```

---

### indentation

Docstring indentation must be consistent. Maximum 2 indentation levels allowed (section headers + content).

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
        None: Nothing.

    """
```

---

### section_capitalization

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

### section_order

Sections must appear in the expected order.

Order: `Attributes` -> `Args` -> `Returns` -> `Yields` -> `Raises` -> `Example`/`Examples` -> `Note`/`Notes` -> `Todo`

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

### unknown_section

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

### empty_section

A declared section must not be empty.

```python
# Bad: empty Args section
def process(x: int) -> int:
    """Process data.

    Args:

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

### blank_line_before_section

A blank line must precede each section header.

```python
# Bad: no blank line before Args
def process(x: int) -> int:
    """Process data.
    Args:
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

### blank_line_after_section

A blank line must separate the content of a section from the next section header.

```python
# Bad: no blank line between Args and Returns
def process(x: int) -> int:
    """Process data.

    Args:
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

### closing_quotes_blank_line

Multi-line docstrings must have exactly one blank line before the closing triple quotes.

```python
# Bad: no blank line before """
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.
    Returns:
        int: Result.
    """

# Bad: two blank lines before """
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.


    """

# Good
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.

    """
```

Not applied to one-liner docstrings or modules.

---

### no_blank_line_in_section

No blank lines are allowed between entries in `Args:`, `Attributes:`, or `Raises:` sections.

```python
# Bad: blank line between two args
def process(x: int, y: int) -> int:
    """Process data.

    Args:
        x (int): First input.

        y (int): Second input.

    Returns:
        int: Result.

    """

# Good
def process(x: int, y: int) -> int:
    """Process data.

    Args:
        x (int): First input.
        y (int): Second input.

    Returns:
        int: Result.

    """
```

`Example`/`Examples` sections are exempt (code examples often contain blank lines).

---

### yields_section

Generator functions (containing `yield` or `yield from`) must have a `Yields:` section instead of `Returns:`.

```python
# Bad: missing Yields section
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file."""
    with open(path) as f:
        yield from f

# Bad: Returns used instead of Yields
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file.

    Returns:
        Iterator[str]: Lines from the file.

    """
    with open(path) as f:
        yield from f

# Good
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): Path to the file.

    Yields:
        str: Each line stripped of whitespace.

    """
    with open(path) as f:
        for line in f:
            yield line.strip()
```

---

### forbid_init_returns_none *(enabled by default)*

Controls `Returns: None` on `__init__` methods. The rule is always active; the toggle inverts its meaning:

- **Enabled (default)**: `Returns: None` is forbidden.
- **Disabled**: `Returns: None` is required, even on multi-line docstrings.

This rule is independent of `returns_section`: it is evaluated for `__init__ -> None` methods regardless of whether `returns_section` is enabled, and its errors are reported under `[forbid_init_returns_none]`.

```toml
[tool.docstring-linter]
# Default: Returns: None forbidden on __init__ (no config needed).
# To require it instead, disable the rule:
ignore = ["forbid_init_returns_none"]
```

```python
# Enabled (default): Returns: None forbidden
# Bad
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    Returns:
        None: This method returns nothing.

    """

# Good
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    """

# Disabled: Returns: None required
# Bad
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    """

# Good
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    Returns:
        None: This method returns nothing.

    """
```

---

### allow_oneliner *(enabled by default)*

Controls whether a `Returns: None` section is required on `-> None` functions whose docstring is a one-liner.

- **Enabled (default)**: a one-liner docstring is accepted as-is. No `Returns:` section is required (a one-liner cannot contain one anyway).
- **Disabled**: one-liner docstrings are not allowed on `-> None` functions; a `Returns: None` section is required, which forces a multi-line docstring.

Does not apply to `__init__` methods (handled by `forbid_init_returns_none`). Independent of `returns_section`: evaluated regardless of whether `returns_section` is enabled, and its errors are reported under `[allow_oneliner]`.

```toml
[tool.docstring-linter]
# Default: one-liner -> None needs no Returns section (no config needed).
# To require Returns: None instead, disable the rule:
ignore = ["allow_oneliner"]
```

```python
# Enabled (default): one-liner accepted
# Good
def reset() -> None:
    """Reset all values."""

# Disabled: Returns: None required
# Bad
def reset() -> None:
    """Reset all values."""

# Good
def reset() -> None:
    """Reset all values.

    Returns:
        None: This method resets in place.

    """
```

---

### Automatic Exemptions

| Case | Behavior |
|------|----------|
| Empty `__init__` (`pass` only, no parameters) | Exempt if `exclude_empty_init = true` |
| `self`, `cls` | Ignored in parameters |
| Bare / dynamic / indirect `raise` | Ignored by `raises_match` |
| Files excluded by pattern | Not scanned |
| Module docstrings | `imperative_mood` not applied |

### Default Exclusion Patterns

The following patterns are excluded by default when scanning directories:

| Pattern | Type | Excludes |
|---------|------|----------|
| `*_test.py` | glob | files ending with `_test.py` |
| `.git` | literal | git metadata directory |
| `.mypy_cache` | literal | mypy cache directory |
| `.pytest_cache` | literal | pytest cache directory |
| `.ruff_cache` | literal | ruff cache directory |
| `.tox` | literal | tox test environments |
| `.venv` | literal | virtual environment directory |
| `__pycache__` | literal | Python bytecode cache |
| `test_*` | glob | files starting with `test_` |

Literal patterns match any directory component in the path (e.g. `.venv` excludes `src/.venv/foo.py`). Glob patterns match only the filename.

Override defaults in `pyproject.toml`:

```toml
[tool.docstring-linter]
exclude = [".venv", "__pycache__", "migrations/"]
```
