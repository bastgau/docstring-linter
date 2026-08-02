# Docstring Linter

Python linter that checks docstring conformance to Google style.

## Rule Reference

20 rules and 14 style policies, configurable in `pyproject.toml` file or `.docstring-linter.toml` file. Eleven rules are always on and cannot be disabled, and are therefore not listed by `docstring-linter --list-rules`: `args_match`, `attributes_match`, `blank_lines`, `duplicate_arg`, `empty_section`, `entry_spacing`, `no_blank_line_in_section`, `raises_match`, `returns_type_match`, `summary_exists`, `yields_match`. The five content rules are always on because requiring a section and then tolerating wrong content in it makes no sense. `summary_exists` is always on because every supported style opens a docstring with a summary. The two layout rules are always on because their toggle would only serve to allow a codebase to mix layouts, which is what this linter exists to prevent; the layout itself is chosen through `blank_lines_before_section` and `blank_lines_before_closing_quotes`.

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

### summary_exists *(always on)*

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

### args_match *(always on)*

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

### duplicate_arg *(always on)*

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

### args_order

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

Moved to the [Style Policies](#style-policies) section: presence of the `Returns:` section is now a policy, not a rule.

---

### returns_type_match *(always on)*

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

### raises_match *(always on)*

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

### attributes_match *(always on)*

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
        None

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

### empty_section *(always on)*

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

### blank_lines *(always on)*

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

### entry_spacing *(always on)*

Every entry of `Args:`, `Attributes:` and `Raises:` must be written in the canonical form: one space before the parenthesis, none before the colon, one after it.

```
name (type): description
name: description
```

```python
# Bad
def process(value: str, other: int, third: str) -> None:
    """Process data.

    Args:
        value(str): No space before the parenthesis.
        other (int) : Space before the colon.
        third (str):No space after the colon.

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

---

### no_blank_line_in_section *(always on)*

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

### yields_match *(always on)*

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

---

## Style Policies

Fourteen constructs are not on/off checks but style choices, where the opposite convention is equally valid. They are configured by value, not through `select` / `ignore`.

All policies accept `"required"`, `"forbidden"`, or `"optional"`.

Formatting policies:

| Policy | Default |
|---|---|
| `returns_none` | `"required"` |
| `init_returns_none` | `"forbidden"` |
| `summary_on_first_line` | `"required"` |
| `summary_final_period` | `"required"` |

Section presence policies, one per documentable section:

| Policy | Default | Rule checking the content when present |
|---|---|---|
| `args_section` | `"required"` | `args_match` (always on) |
| `returns_section` | `"required"` | `returns_type_match` (always on) |
| `yields_section` | `"required"` | `yields_type_match` (always on) |
| `raises_section` | `"required"` | `raises_match` (always on) |
| `attributes_section` | `"required"` | `attributes_match` (always on) |

Four more sections carry no content rule, only a presence policy. They default to `"optional"`, nothing changes unless you set them:

| Policy | Default | Applies to |
|---|---|---|
| `description_section` | `"optional"` | Description paragraph below the summary |
| `examples_section` | `"optional"` | `Example:` or `Examples:` |
| `notes_section` | `"optional"` | `Note:` or `Notes:` |
| `todo_section` | `"optional"` | `Todo:` |

One more policy governs what an entry declares:

| Policy | Default | Applies to |
|---|---|---|
| `documented_types` | `"required"` | Type between parentheses in `Args:` and `Attributes:` entries |

The two halves are independent. The policy answers "must this be documented", the rule answers "is what is documented correct". Under `"optional"`, nothing forces you to document, but everything you do document is still checked. Under `"forbidden"`, the section is rejected and the content rule is not run, to avoid reporting the same block twice.

`"optional"` accepts both forms and therefore allows a codebase to mix them. Set it deliberately.

---

### returns_none

Governs the `Returns: None` section on every function or method whose signature declares `-> None`. Does not apply to `__init__` methods, covered by `init_returns_none`, nor to generators, covered by `yields_section`.

A one-liner docstring cannot contain a `Returns:` section, so under `"required"` a one-liner on a `-> None` function is an error.

```toml
[tool.docstring-linter]
returns_none = "required"
```

```python
# required: section mandatory
# Bad
def reset() -> None:
    """Reset all values."""

# Good
def reset() -> None:
    """Reset all values.

    Returns:
        None

    """

# forbidden: section rejected
# Bad
def reset() -> None:
    """Reset all values.

    Returns:
        None

    """

# Good
def reset() -> None:
    """Reset all values."""

# optional: both forms accepted
```

---

### init_returns_none

Same policy applied to `__init__` methods. Defaults to `"forbidden"`: an `__init__` always returns `None`, documenting it adds nothing.

```toml
[tool.docstring-linter]
init_returns_none = "forbidden"
```

```python
# forbidden (default)
# Bad
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    Returns:
        None

    """

# Good
def __init__(self, name: str) -> None:
    """Initialize the object.

    Args:
        name (str): The name.

    """

# required: the reverse, the section becomes mandatory
# optional: both forms accepted
```

---

### summary_on_first_line

Governs whether the summary starts on the same line as the opening triple quotes.

```toml
[tool.docstring-linter]
summary_on_first_line = "required"
```

```python
# required (default)
# Bad
def process() -> None:
    """
    Process the input data.
    """

# Good
def process() -> None:
    """Process the input data."""

# forbidden: the reverse, the summary must start on the next line
# optional: both forms accepted
```

---

### summary_final_period

Governs the period ending the summary line.

```toml
[tool.docstring-linter]
summary_final_period = "required"
```

```python
# required (default)
# Bad
def process() -> None:
    """Process the input data"""

# Good
def process() -> None:
    """Process the input data."""

# forbidden: the reverse, a trailing period is rejected
# optional: both forms accepted
```

---

### args_section

Every parameter of the signature must be documented in the `Args:` section.

```toml
[tool.docstring-linter]
args_section = "required"
```

```python
# required (default)
# Bad: 'age' not documented
def create_user(name: str, age: int) -> dict:
    """Create a new user.

    Args:
        name (str): User name.

    Returns:
        dict: User record.

    """

# optional: the above is accepted, but a documented parameter is still
# checked by args_match (type, description, phantom)

# forbidden: any Args section is rejected
```

---

### returns_section

A function whose signature declares a return type other than `None` must have a `Returns:` section. The `-> None` case is owned by `returns_none` and `init_returns_none`.

A generator that documents `Returns:` instead of `Yields:` is always reported, whatever the value of this policy.

```toml
[tool.docstring-linter]
returns_section = "required"
```

```python
# required (default)
# Bad
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

# optional: the section becomes free, but when present returns_type_match
# still validates its type
# forbidden: any Returns section is rejected
```

---

### yields_section

A generator function must have a `Yields:` section.

```toml
[tool.docstring-linter]
yields_section = "required"
```

```python
# required (default)
# Bad
def read_lines(path: str) -> Iterator[str]:
    """Read lines from a file one by one.

    Args:
        path (str): Path to the file.

    """
    with open(path) as f:
        yield from f

# optional: the section becomes free, but when present yields_type_match
# still requires a type
# forbidden: any Yields section is rejected
```

---

### raises_section

Every exception explicitly raised in the body must be documented in the `Raises:` section. Bare, dynamic and indirect raises are never collected, see [Automatic Exemptions](#automatic-exemptions).

```toml
[tool.docstring-linter]
raises_section = "required"
```

```python
# required (default)
# Bad
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

# optional: documenting exceptions becomes free, but an exception documented
# and never raised is still reported by raises_match
# forbidden: any Raises section is rejected
```

---

### attributes_section

Every class attribute must be documented in the `Attributes:` section of the class docstring. A class with no detected attribute never requires the section.

```toml
[tool.docstring-linter]
attributes_section = "required"
```

```python
# required (default)
# Bad
class User:
    """Represent a user."""

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

# optional: the section becomes free, but a documented attribute is still
# checked by attributes_match
# forbidden: any Attributes section is rejected
```

---

### description_section

Governs the free-text paragraph between the summary and the first section header.

```toml
[tool.docstring-linter]
description_section = "optional"
```

```python
# required
def process(x: int) -> int:
    """Process data.

    Detailed description of what the function actually does.

    Args:
        x (int): Input.

    Returns:
        int: Result.

    """

# forbidden: the summary must stand alone, sections follow directly
# optional (default): both forms accepted
```

Setting it to `"required"` makes every one-liner docstring invalid, including on trivial helpers. Reach for it only on a codebase that already documents that way.

---

### examples_section, notes_section, todo_section

Same three values, applied to the corresponding section header. Both spellings are accepted where they exist: `Example:` and `Examples:`, `Note:` and `Notes:`.

```toml
[tool.docstring-linter]
examples_section = "required"   # every checked docstring must carry an example
notes_section = "optional"
todo_section = "forbidden"      # no leftover Todo in a released docstring
```

```python
# todo_section = "forbidden"
# Bad
def process(x: int) -> int:
    """Process data.

    Args:
        x (int): Input.

    Returns:
        int: Result.

    Todo:
        Handle the negative case.

    """
```

`"required"` applies to every checked entity, modules and classes included. On `examples_section` that is a heavy demand, restrict the scope with `scope.*` if needed.

---

### documented_types

Governs the type declared between parentheses in `Args:` and `Attributes:` entries. The signature already carries the type, so a project may consider the docstring copy redundant.

Does not apply to `Returns:` and `Yields:`, where the type is the payload of the line: removing it would leave prose with nothing to identify. Their types stay mandatory, checked by `returns_type_match` and `yields_match`.

```toml
[tool.docstring-linter]
documented_types = "required"
```

```python
# required (default)
def create_user(name: str) -> dict:
    """Create a new user.

    Args:
        name (str): User name.

    Returns:
        dict: User record.

    """

# forbidden: the type must not be repeated
def create_user(name: str) -> dict:
    """Create a new user.

    Args:
        name: User name.

    Returns:
        dict: User record.

    """

# optional: both forms accepted, and a type that is present is still
# compared with the signature by args_match
```

The description of an entry is never optional: an `Args:`, `Attributes:`, `Raises:` or `Yields:` entry without a description is always reported. A name alone carries no information the signature does not already give.

---

### Automatic Exemptions

| Case | Behavior |
|------|----------|
| Empty `__init__` method (`pass` only, no parameters) | Docstring not required if `exclude_empty_init_method = true` (default) |
| Empty `__init__.py` file (empty or comments only) | Docstring not required if `exclude_empty_init_module = true` (default) |
| `self`, `cls` | Ignored in parameters |
| `*args`, `**kwargs` | Documented with their stars, `*args (str): ...` |
| Bare / dynamic / indirect `raise` | Ignored by `raises_match` |
| Files excluded by pattern | Not scanned |
| Module docstrings | `imperative_mood` not applied |

#### exclude_empty_init_method

An `__init__` method counts as empty when it declares no parameter beyond `self` and its body contains only `pass` statements or a docstring. When `exclude_empty_init_method = true`, such a method is exempted from `docstring_exists` only: writing a docstring stays optional, but a docstring that is present is checked like any other.

```python
class A:
    def __init__(self) -> None:   # no docstring: accepted
        pass

class B:
    def __init__(self) -> None:
        """initialize the thing"""   # docstring present: checked, missing final period

class C:
    def __init__(self, name: str) -> None:   # not empty, has a parameter
        """Initialize.

        Args:
            name (str): Name.

        """
```

There is no equivalent exemption for regular functions with an empty body: `def noop() -> None: pass` is checked like any other function.

```toml
[tool.docstring-linter]
exclude_empty_init_method = false   # check empty __init__ methods too
```

#### exclude_empty_init_module

An `__init__.py` counts as empty when its AST body is empty: an empty file, or a file containing only comments. A single import or a docstring is enough to make it non-empty, and therefore checked like any other module. As with the method case, the option only lifts `docstring_exists`.

```python
# pkg/__init__.py -- exempt (empty file)

# pkg/__init__.py -- exempt (comments only)
# re-exported below one day

# pkg/__init__.py -- checked, docstring_exists applies
from .core import main
```

```toml
[tool.docstring-linter]
exclude_empty_init_module = false   # check empty __init__.py files too
```

This option only covers the empty case. To skip every `__init__.py` regardless of its content, use `exclude = ["__init__.py"]`.

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
