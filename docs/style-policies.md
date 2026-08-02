# Docstring Linter

## Style Policies

Some constructs are not on/off checks but style choices, where multiple conventions may be valid.  

All policies accept `"required"`, `"forbidden"`, or `"optional"`.

Formatting policies:

| Policy | Default |
|---|---|
| `returns_none` | `"required"` |
| `init_returns_none` | `"forbidden"` |
| `summary_on_first_line` | `"required"` |
| `summary_final_period` | `"required"` |

Section presence policies, one per documentable section:

| Policy | Default | Applies to |
|---|---|---|
| `args_section` | `"required"` | `Args:` |
| `returns_section` | `"required"` | `Returns:` |
| `yields_section` | `"required"` | `Yields:` |
| `raises_section` | `"required"` | `Raises:` |
| `attributes_section` | `"required"` | `Attributes:` |

When present, the content of these sections is also validated by the corresponding content rules. The policy controls whether the section must exist; the corresponding content rule validates what it contains (`args_match`, `returns_match`, `yields_match`, `raises_match`, and `attributes_match`).

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
| `returns_descriptions` | `"required"` | Description on the `Returns:` and `Yields:` lines |

The two halves are independent. The policy answers "must this be documented", the rule answers "is what is documented correct". Under `"optional"`, nothing forces you to document, but everything you do document is still checked. Under `"forbidden"`, the section is rejected and the content rule is not run, to avoid reporting the same block twice.

`"optional"` accepts both forms and therefore allows a codebase to mix them. Set it deliberately.

---

### returns_none

Governs the `Returns: None` section on every function or method whose signature declares `-> None`. Does not apply to `__init__` methods, covered by `init_returns_none`, nor to generators, covered by `yields_section`.

Not applied at all when `returns_section = "forbidden"`: that value drops the `Returns:` section from the whole docstring, `-> None` functions included.

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

Same policy applied to `__init__` methods. Defaults to `"forbidden"`: an `__init__` always returns `None`, documenting it adds nothing. Like `returns_none`, it is not applied when `returns_section = "forbidden"`.

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

A function whose signature declares a return type other than `None` must have a `Returns:` section. Under `"required"` and `"optional"`, the `-> None` case is owned by `returns_none` and `init_returns_none`. Under `"forbidden"`, those two policies are not applied: no `Returns:` section is expected anywhere, whatever their value.

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

# optional: the section becomes free, but when present returns_match
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

# optional: the section becomes free, but when present yields_match
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

Does not apply to `Returns:` and `Yields:`, where the type is the payload of the line: removing it would leave prose with nothing to identify. Their types stay mandatory, checked by `returns_match` and `yields_match`.

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

### returns_descriptions

Governs the description on the `Returns:` and `Yields:` lines. Both are the same slot, a function documents one or the other.

A documented type of `None` is exempt: on `Returns: None` the type is the whole content of the line, there is nothing to describe.

This policy accepts `"forbidden"`: a type-only line is a style some projects adopt, the type alone already names what the function produces. There is no equivalent for `Args:`, `Attributes:` and `Raises:` entries, whose description is always required: an entry stripped of it carries nothing the signature does not already state, and dropping the whole section with `args_section = "forbidden"` says it properly.

```toml
[tool.docstring-linter]
returns_descriptions = "required"
```

```python
# required (default)
def get_name() -> str:
    """Get the user name.

    Returns:
        str: The user name.

    """

# forbidden: the type stands alone
def get_name() -> str:
    """Get the user name.

    Returns:
        str

    """

# optional: both forms accepted
```

---

## Automatic Exemptions

| Case | Behavior |
|------|----------|
| Empty `__init__` method (`pass` only, no parameters) | Docstring not required if `exclude_empty_init_method = true` (default) |
| Empty `__init__.py` file (empty or comments only) | Docstring not required if `exclude_empty_init_module = true` (default) |
| `self`, `cls` | Ignored in parameters |
| `*args`, `**kwargs` | Documented with their stars, `*args (str): ...` |
| Bare / dynamic / indirect `raise` | Ignored by `raises_match` |
| Files excluded by pattern | Not scanned |
| Module docstrings | `imperative_mood` not applied |

### exclude_empty_init_method

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

---

### exclude_empty_init_module

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

## Exclusion Patterns

### Default Exclusion Patterns

The following patterns are excluded by default when scanning directories:

| Pattern | Type | Excludes |
|---------|------|----------|
| `.git` | literal | git metadata directory |
| `.mypy_cache` | literal | mypy cache directory |
| `.pytest_cache` | literal | pytest cache directory |
| `.ruff_cache` | literal | ruff cache directory |
| `.tox` | literal | tox test environments |
| `.venv` | literal | virtual environment directory |
| `__pycache__` | literal | Python bytecode cache |

Literal patterns match any directory component in the path (e.g. `.venv` excludes `src/.venv/foo.py`). Test files are linted like any other file; exclude them explicitly with `exclude = ["test_*", "*_test.py"]` if desired.

Override defaults in `pyproject.toml`:

```toml
[tool.docstring-linter]
exclude = [".venv", "__pycache__", "migrations/"]
```
