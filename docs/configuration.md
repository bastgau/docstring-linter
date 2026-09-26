# Docstring Linter

## Configuration options

Configuration is loaded in this order (first match wins):

1. Explicit `--config path/to/file.toml`. A missing file, or a `pyproject.toml` without a `[tool.docstring-linter]` section, is a configuration error.
2. Auto-discovery. Starting from the current directory and walking upward one directory at a time, `pyproject.toml` (with a `[tool.docstring-linter]` section) is checked before `.docstring-linter.toml` in each directory. The first match stops the search.
3. Built-in defaults

The search starts from the current directory, not from the linted files. When linting from elsewhere, pass the file with `--config`.

Path patterns (`exclude`, `--exclude` and the `paths` of an override) are relative to the directory holding the config file, whatever the current directory. With the built-in defaults, they are relative to the current directory.

### pyproject.toml

```toml
[tool.docstring-linter]
select = ["ALL"]
returns_none = "required"
workers = 0

[tool.docstring-linter.scope]
modules = false
classes = true
functions = true
methods = true
```

See the Available keys section below for the complete list of options.

### .docstring-linter.toml

Standalone config file -- same keys, without the `[tool.docstring-linter]` wrapper. `[scope]` replaces `[tool.docstring-linter.scope]`.

```toml
select = ["ALL"]
returns_none = "required"
workers = 0

[scope]
modules = false
classes = true
functions = true
methods = true
```

See the Available keys section below for the complete list of options.

### Available keys

| Key | Default | Description |
|-----|---------|-------------|
| `convention` | `"strict"` | Set of defaults for the policies, options and rules below. See [Conventions](#conventions). |
| `select` | all rules | [Configurable rules](/docs/configurable-rules.md) to enable. `["ALL"]` enables everything. |
| `ignore` | `[]` | [Configurable rules](/docs/configurable-rules.md) to disable (applied after `select`). [Always-on rules](/docs/always-on-rules.md) cannot be listed here. |
| `returns_none` | `"required"` | Policy for `Returns: None` on `-> None` functions. Not applied when `returns_section = "forbidden"`. |
| `init_returns_none` | `"forbidden"` | Policy for `Returns: None` on `__init__` methods. Not applied when `returns_section = "forbidden"`. |
| `summary_on_first_line` | `"required"` | Policy for the summary on the opening `"""` line. |
| `summary_final_period` | `"required"` | Policy for the period ending the summary line. |
| `args_section` | `"required"` | Policy for documenting every parameter of the signature. |
| `returns_section` | `"required"` | Policy for the `Returns:` section on a non-`None` return type. `"forbidden"` also disables `returns_none` and `init_returns_none`. |
| `yields_section` | `"required"` | Policy for the `Yields:` section on generators. |
| `raises_section` | `"required"` | Policy for documenting every exception raised. |
| `attributes_section` | `"required"` | Policy for documenting every class attribute. |
| `description_section` | `"optional"` | Policy for the description paragraph below the summary. |
| `examples_section` | `"optional"` | Policy for the `Examples:` section (`Example:` accepted as an alias). |
| `notes_section` | `"optional"` | Policy for the `Note:` section. |
| `todo_section` | `"optional"` | Policy for the `Todo:` section. |
| `documented_types` | `"required"` | Policy for the type in `Args:` and `Attributes:` entries and on the `Returns:` and `Yields:` lines. |
| `returns_descriptions` | `"required"` | Policy for the description on the `Returns:` and `Yields:` lines. |
| `documented_stars` | `"required"` | Policy for the stars of `*args` and `**kwargs` in their `Args:` entries. |
| `exclude_empty_init_method` | `true` | Do not require a docstring on `__init__` methods with no parameter beyond `self` and a body limited to `pass` or a docstring. |
| `exclude_empty_init_module` | `true` | Do not require a docstring on `__init__.py` files with an empty body (empty file or comments only). |
| `ignore_placeholder_docstrings` | `false` | Skip docstrings containing only `...`. |
| `exclude_dunder_methods` | `false` | Do not require a docstring on magic methods (`__repr__`, `__enter__`...). `__init__` keeps its own option. |
| `exclude_private` | `false` | Do not require a docstring on private functions, methods and classes (`_name`, `__name`) nor on the members of a private class. |
| `exclude_overridden` | `false` | Do not require a docstring on methods decorated with `@override`, which inherit the documentation of the parent method. |
| `sections_optional_on_one_liners` | `false` | Do not require the `Args:`, `Returns:`, `Yields:` and `Raises:` sections (nor `Returns: None`) on a one-line docstring, when the function or method has every parameter and its return annotated. A docstring of more than one line keeps every required section. |
| `properties_as_attributes` | `false` | Document property getters like attributes: no `Returns:` section required, `imperative_mood` not applied. Property setters and deleters are not checked. |
| `exclude` | see [built-in defaults](/docs/style-policies.md#default-exclusion-patterns) | Glob/literal patterns for files and directories to skip. See [matching rules](/docs/style-policies.md#default-exclusion-patterns). |
| `workers` | `0` | Parallel workers. `0` = one per usable CPU, sequential below 50 files where starting the processes costs more than it saves. Any other value is used as is, `1` being sequential. |
| `summary_max_length` | `80` | Maximum summary line length for `summary_too_long`. |
| `blank_lines_before_section` | `1` | Blank lines expected before a section header, checked by `blank_lines`. |
| `blank_lines_before_closing_quotes` | `1` | Blank lines expected before the closing `"""`, checked by `blank_lines`. |
| `type_matching` | `"strict"` | How closely a documented type must match the signature: `"strict"`, `"equivalent"` or `"lenient"`. See [Type matching](#type-matching). |
| `init_args_location` | `"init"` | Docstring documenting the `__init__` parameters: `"init"`, `"class"` or `"either"`. See [`__init__` parameters](#__init__-parameters). |
| `scope.modules` | `true` | Check module-level docstrings. |
| `scope.classes` | `true` | Check class docstrings. |
| `scope.functions` | `true` | Check function docstrings. |
| `scope.methods` | `true` | Check method docstrings. |

Every policy accepts `"required"`, `"forbidden"`, or `"optional"`. For the five section policies, `"optional"` means the section is not required, but what the docstring does declare is still checked by the matching rule (`args_match`, `returns_match`, `yields_match`, `raises_match`, `attributes_match`). The `exclude_*` options only lift `docstring_exists`: a docstring that is present is always checked.

`docstring-linter --list-rules` prints the rules, the policies, and the options that change what gets checked, each with the value it has in the current config.

### Conventions

`convention` picks the defaults every other key starts from. Keys written in the config file always win over the convention, `select` and `ignore` included.

| Setting | `"strict"` (default) | `"google"` |
|---|---|---|
| `returns_none` | `"required"` | `"optional"` |
| `init_returns_none` | `"forbidden"` | `"optional"` |
| `documented_types` | `"required"` | `"optional"` |
| `raises_section` | `"required"` | `"optional"` |
| `attributes_section` | `"required"` | `"optional"` |
| `blank_lines_before_closing_quotes` | `1` | `0` |
| `type_matching` | `"strict"` | `"lenient"` |
| `imperative_mood` rule | enabled | disabled |
| `return_type_annotation` rule | enabled | disabled |
| `raises_extraneous` rule | enabled | disabled |
| `exclude_dunder_methods`, `exclude_private`, `exclude_overridden`, `properties_as_attributes`, `sections_optional_on_one_liners` | `false` | `true` |
| `init_args_location` | `"init"` | `"either"` |

`"strict"` enforces a complete house style: every type repeated in the docstring, `Returns: None` on `-> None` functions, every exception and attribute documented, a blank line before the closing quotes.

`"google"` follows the layout of the Google Python Style Guide: types live in the signature, a function returning `None` has no `Returns:` section, the summary may be descriptive (`Fetches rows.`) or imperative, and the closing quotes follow the last line. What the docstring declares is still checked: a documented type must match the signature, a documented exception must be raised.

```toml
[tool.docstring-linter]
convention = "google"
raises_section = "required"   # stricter than the convention on this point
```

`convention` applies to the whole run and cannot be set in an override.

### Type matching

When a docstring declares a type, `args_match` and `returns_match` compare it with the annotation of the signature. `type_matching` sets how close the two must be. Each level accepts everything the previous one accepts.

| Level | Also considered identical | Example (docstring vs signature) |
|---|---|---|
| `"strict"` | Quotes of forward references, spacing, the `, optional` suffix, the Sphinx `~` prefix | `Node` vs `'Node'`, `bool, optional` vs `bool`, `~Console` vs `Console` |
| `"equivalent"` | The same type spelled differently: `Optional[X]`, `Union[X, None]` and `X \| None`; `List`, `Dict`, `Set`, `Tuple`, `Type` and their builtin form | `str \| None` vs `Optional[str]`, `List[int]` vs `list[int]` |
| `"lenient"` | A docstring leaving `None` implicit when the signature accepts it | `int, optional` vs `Optional[int]` |

Differences that change the type are reported at every level: `int` vs `str`, `List[int]` vs `Iterable[int]`, `IO` vs `IO[str]`. A documented type that is not a Python expression (`list of int`) is compared as text.

`type_matching` may be set in an override.

### `__init__` parameters

The parameters of a constructor are documented either in the `__init__` docstring or in the class docstring. `init_args_location` says where the linter looks for them.

| Value | Where the parameters go | `__init__` docstring |
|---|---|---|
| `"init"` | `Args:` of `__init__` | Required, unless `exclude_empty_init_method` applies |
| `"class"` | `Args:` of the class | Optional; an `Args:` section in it is reported |
| `"either"` | `Args:` of the class when it has one, `Args:` of `__init__` otherwise | Optional when the class has `Args:`; documenting the parameters in both places is reported |

When the class documents them, `args_section`, `args_match`, `duplicate_arg` and `args_order` compare the `Args:` section of the class with the `__init__` signature, and report on the class.

```python
# init_args_location = "either"
class Cache:
    """Store computed values.

    Args:
        size (int): Maximum number of values.
    """

    def __init__(self, size: int) -> None:
        """Create the cache."""
```

### Per-path overrides

A base configuration plus any number of `[[tool.docstring-linter.overrides]]` blocks. Each block declares the path patterns it applies to, then the settings it changes.

```toml
[tool.docstring-linter]
select = ["ALL"]
args_section = "required"

[[tool.docstring-linter.overrides]]
paths = ["tests/**"]
ignore = ["imperative_mood", "args_order"]
args_section = "optional"
summary_max_length = 120

[[tool.docstring-linter.overrides]]
paths = ["example/**", "docs/**"]
select = ["docstring_exists"]
```

Same configuration in `.docstring-linter.toml`, where `[[overrides]]` replaces `[[tool.docstring-linter.overrides]]`. The base keys must be written before the first block, otherwise TOML attaches them to that block.

```toml
select = ["ALL"]
args_section = "required"

[[overrides]]
paths = ["tests/**"]
ignore = ["imperative_mood", "args_order"]
args_section = "optional"
summary_max_length = 120

[[overrides]]
paths = ["example/**", "docs/**"]
select = ["docstring_exists"]
```

- `paths` is required and matched with `PurePath.full_match` against the file path relative to the config file directory, so `tests/**` covers the whole tree. A file outside that directory matches no override.
- **A single block applies to a given file**: the last declared among those matching it. The other matching blocks are ignored, blocks never accumulate. Declare the general case first and the exceptions after it, and make each block self-contained.
- The block that applies is resolved against the base configuration, so a setting it does not declare keeps its base value, not the linter default.
- `ignore` removes rules from the inherited set, `select` replaces that set entirely. Same meaning as at the base level.
- An override may carry any policy, and the options that change what is checked on a file: `summary_max_length`, `blank_lines_before_section`, `blank_lines_before_closing_quotes`, `exclude_empty_init_method`, `exclude_empty_init_module`, `ignore_placeholder_docstrings`, `exclude_dunder_methods`, `exclude_private`, `exclude_overridden`, `properties_as_attributes`, `sections_optional_on_one_liners`, `type_matching`, `init_args_location`.
- `exclude`, `workers` and `scope.*` apply to the whole run rather than individual files, so they are rejected inside an override.

`docstring-linter --list-rules` prints the overrides after the base configuration, showing only what each one changes.

### Strict configuration

Anything the linter does not recognize is an error, reported on stderr with exit code 2 before any file is read. This covers a key absent from the table above (including inside `[scope]` and inside an override), a rule name absent from `--list-rules` in `select` or `ignore`, an always-on rule listed in `ignore`, an invalid policy value, or a value of the wrong type (`workers = "4"`, `exclude = "src"`).

```console
$ docstring-linter src/
Configuration error: unknown configuration key 'param_order'.
```
