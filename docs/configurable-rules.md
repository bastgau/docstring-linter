# Docstring Linter

## Configurable Rule Reference

These rules can be enabled or disabled through `select` and `ignore`.   For style policies such as `returns_none` or `args_section`, see [Style Policies](/docs/style-policies.md).

### Presence

#### docstring_exists

Every entity (module, class, function, method) must have a docstring.

Subject to the configured scope (`modules`, `classes`, `functions`, `methods`) and to the exemption options: `exclude_empty_init_method`, `exclude_empty_init_module`, `exclude_dunder_methods`, `exclude_private`, `exclude_overridden`. An exempted entity that does have a docstring is still checked.

Functions and classes defined inside `if`, `try`, `with`, `for`, `while` or `match` blocks, at module or class level, are checked like the others. Functions nested inside another function are not checked, code under `if __name__ == "__main__":` is skipped, and `@overload` stubs are skipped: only the implementation needs a docstring.

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

The first word is reported only when the base form derived from it is a known English verb (`Returns` -> `Return`, `Copies` -> `Copy`, `Does` -> `Do`). Plural nouns and other words ending in `s` pass: `Options`, `Classes`, `Status`, `Canvas`.

Applied to functions and methods only, not to module and class docstrings.

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

### Args / Returns / Raises

#### raises_extraneous

Every exception listed in `Raises:` must be raised explicitly in the body. An exception propagated from a called function is invisible to the linter: a project that documents those turns this rule off, which the `google` convention does.

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
```

Only capitalized class names count as raised: `raise ValueError`, `raise errors.ValidationError(...)`, and `raise err` inside `except ValueError as err`. A dotted name in the docstring is compared on its last segment.

---

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

### Sections

#### indentation

The content of a section must sit under its header: every line indented by 4 spaces or more, and the first entry of `Args:`, `Attributes:` and `Raises:` by exactly 4. A description continued on deeper lines is fine. Lines outside sections are not checked, so a description may hold indented code or lists. One error is reported per misindented section.

```python
# Bad: section content indented by 2 spaces
def process(x: int) -> None:
    """Process data.

    Args:
      x (int): Input.

    """

# Good: continuation lines may go deeper
def process(x: int) -> None:
    """Process data.

    Args:
        x (int): Input, described on
            several lines.

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

Every recognized section is covered, Napoleon ones included: see the list under [unknown_section](#unknown_section).

---

#### section_alias

A Napoleon alias is accepted and its content checked as the canonical section, but the header must use the canonical spelling.

```python
# Bad: 'Parameters:' should be written 'Args:'
def process(x: int) -> int:
    """Process data.

    Parameters:
        x (int): Input.

    Returns:
        int: Result.

    """
```

Turn it off with `ignore = ["section_alias"]` to accept `Arguments:`, `Parameters:` and the other aliases as they are.

---

#### section_order

Sections must appear in the expected order.

Expected order: `Attributes` -> `Args` -> `Keyword Args` -> `Other Parameters` -> `Returns` -> `Yields` -> `Raises` -> `Examples` -> `Note`/`Notes` -> `Todo`

An alias takes the place of its canonical section (`Parameters` sits where `Args` does). Free-text sections such as `Warning` or `See Also` may appear anywhere.

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

A single capitalized word followed by a colon, alone on its line, that is not a recognized section triggers an error. Common mistake: `Params:` instead of `Args:`.

Recognized sections, the Napoleon ones included:

| Kind | Sections |
|---|---|
| Checked content | `Args`, `Keyword Args`, `Other Parameters`, `Returns`, `Yields`, `Raises`, `Attributes` |
| Free text | `Examples`, `Note`, `Notes`, `Todo`, `Attention`, `Caution`, `Danger`, `Error`, `Hint`, `Important`, `Methods`, `Receive`, `Receives`, `References`, `See Also`, `Tip`, `Warn`, `Warning`, `Warnings`, `Warns` |
| Aliases, read as their canonical section and reported by `section_alias` | `Example` (`Examples`), `Arguments`, `Parameters` (`Args`), `Keyword Arguments` (`Keyword Args`), `Return` (`Returns`), `Yield` (`Yields`), `Raise` (`Raises`) |

`Note` and `Notes` are two distinct sections: Napoleon renders `Note` as an admonition box and `Notes` as a plain section.

In Napoleon, `Warn` and `Warns` list the warnings a function issues, the way `Raises` lists exceptions. They are accepted here, but their entries are not checked yet.

`Other Parameters` entries are checked like `Args` entries. `Keyword Args` documents the keys of `**kwargs`: its presence counts as documenting the `**kwargs` parameter, and its entries are not compared with the signature, only their description is required.

```python
# Bad
def process(x: int) -> int:
    """Process data.

    Params:
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
