# Docstring Linter

## Always-On Rule Reference

These rules are always enabled, cannot be added to `ignore` and are therefore not listed by `docstring-linter --list-rules`.

### Content

These rules are always on because requiring a section and then tolerating wrong content in it makes no sense.

#### args_match

Checks what the `Args:` section declares: phantom parameters, type `(type)` according to the `documented_types` policy, and presence of a description. A parameter of the signature that is not documented at all is reported by the `args_section` policy, not here.

```python
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

# Good: variadic parameters keep their stars on both sides
def log(level: str, *args: str, **kwargs: object) -> None:
    """Write a formatted message to the log.

    Args:
        level (str): Severity name.
        *args (str): Message fragments joined with a space.
        **kwargs (object): Extra fields attached to the record.

    Returns:
        None

    """
```

---

#### attributes_match

Checks what the `Attributes:` section declares: phantom attributes, type according to the `documented_types` policy, missing description. A class attribute that is not documented at all is reported by the `attributes_section` policy, not here.

Dunder and all-caps names documented without being detected as class attributes are tolerated.

```python
# Bad: type missing
class User:
    """Represent a user.

    Attributes:
        name: The user name.

    """

    def __init__(self) -> None:
        self.name = "x"

# Bad: phantom attribute
class User:
    """Represent a user.

    Attributes:
        name (str): The user name.
        email (str): Never assigned anywhere.

    """

    def __init__(self) -> None:
        self.name = "x"

# Good
class User:
    """Represent a user.

    Attributes:
        name (str): The user name.

    """

    def __init__(self) -> None:
        self.name = "x"
```

---

#### raises_match

Checks what the `Raises:` section declares: an exception documented but never raised in the code, and an exception documented without a description. An exception raised but not documented is reported by the `raises_section` policy, not here.

```python
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

#### returns_match

When a `Returns:` section exists, its type must match the signature, and the type must not be missing. This rule never reports a missing section (that is `returns_section`).

A documented type that contradicts the signature is wrong, not stylistic, so this rule ignores `select` and `ignore` and always reports.

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

#### yields_match

When a `Yields:` section exists, it must declare a type and a description. Its absence on a generator is reported by the `yields_section` policy, not here.

```python
# Bad: no type in Yields
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): Path to the file.

    Yields:
        Each line stripped of whitespace.

    """

# Good
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): Path to the file.

    Yields:
        str: Each line stripped of whitespace.

    """
```

### Summary

`summary_exists` is always on because every supported style opens a docstring with a summary.

#### summary_exists

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

### Layout

These rules are always on because their toggle would only serve to allow a codebase to mix layouts, which is what this linter exists to prevent. The layout itself is chosen through `blank_lines_before_section` and `blank_lines_before_closing_quotes`.

#### blank_lines

The blank line counts of the docstring layout must match the configured values. Two numbers, both cosmetic in the same sense as `summary_max_length`:

| Option | Default | Applies to |
|---|---|---|
| `blank_lines_before_section` | `1` | Gap immediately before any section header |
| `blank_lines_before_closing_quotes` | `1` | Gap before the closing `"""` |

A third gap is checked with a fixed value of one: the blank line separating the summary from the description. It is not configurable because the description carries no header, so any other count either merges it with the summary or leaves an unexplained hole. It is skipped when the summary is the whole docstring, and when a section header follows the summary directly, in which case `blank_lines_before_section` applies.

The count is exact in both directions: too few and too many are both reported. A section header on the first line of the docstring is never counted. The closing quotes count is not applied to one-liners nor to module docstrings.

```toml
[tool.docstring-linter]
blank_lines_before_section = 1
blank_lines_before_closing_quotes = 1
```

```python
# Bad: no blank line before Args, none before the closing quotes
def process(x: int) -> int:
    """Process data.
    Args:
        x (int): Input.
    """

# Bad: two blank lines before the closing quotes
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

# Bad: description glued to the summary
def process(x: int) -> int:
    """Process data.
    Detailed description.

    Args:
        x (int): Input.

    """

# Good
def process(x: int) -> int:
    """Process data.

    Detailed description.

    Args:
        x (int): Input.

    """
```

Setting both to `0` gives the compact layout:

```python
def process(x: int) -> int:
    """Process data.
    Args:
        x (int): Input.
    """
```

---

#### no_blank_line_in_section

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

### Syntax / Structure

These rules are always on because they detect malformed docstrings rather than style choices. A duplicate entry, an empty section, or invalid entry syntax is never considered valid documentation.

#### duplicate_arg

An argument must not appear more than once in the `Args:` section.

There is no reading of a docstring where the same parameter documented twice is correct, so this rule ignores `select` and `ignore` and always reports.

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

#### empty_section

A declared section must not be empty.

An empty section carries no information in any docstring style, so this rule ignores `select` and `ignore` and always reports.

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

#### entry_spacing

Every entry of `Args:`, `Attributes:` and `Raises:` must be written in the canonical form: one space before the parenthesis, none before the colon, one after it.

The presence of `(type)` is governed by the `documented_types` policy. This rule only validates spacing around the parts that are present.

```
name (type): description
name: description
```

```python
# Bad
def process(value: str, other: int, third: str, fourth: str) -> None:
    """Process data.

    Args:
        value(str): No space before the parenthesis.
        other (int) : Space before the colon.
        third (str):No space after the colon.
        fourth (str)

    """

# Good
def process(value: str, other: int, third: str) -> None:
    """Process data.

    Args:
        value (str): A value.
        other (int): Another one.
        third (str): The last one.

    """
```

Continuation lines of a description are not entries and are never flagged. Applies only to the three sections listed above, `Returns:` and `Yields:` hold a single line of a different shape.
