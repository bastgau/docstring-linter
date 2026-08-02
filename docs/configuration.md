# Docstring Linter

## Configuration options

Configuration is loaded in this order (first match wins):

1. Explicit `--config path/to/file.toml`
2. Auto-discovery. Starting from the current directory and walking upward one directory at a time, `pyproject.toml` (with a `[tool.docstring-linter]` section) is checked before `.docstring-linter.toml` in each directory. The first match stops the search.
3. Built-in defaults

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
| `examples_section` | `"optional"` | Policy for the `Example:` section. |
| `notes_section` | `"optional"` | Policy for the `Note:` section. |
| `todo_section` | `"optional"` | Policy for the `Todo:` section. |
| `documented_types` | `"required"` | Policy for the type between parentheses in `Args:` and `Attributes:` entries. |
| `returns_descriptions` | `"required"` | Policy for the description on the `Returns:` and `Yields:` lines. |
| `exclude_empty_init_method` | `true` | Do not require a docstring on `__init__` methods with no parameter beyond `self` and a body limited to `pass` or a docstring. |
| `exclude_empty_init_module` | `true` | Do not require a docstring on `__init__.py` files with an empty body (empty file or comments only). |
| `ignore_placeholder_docstrings` | `false` | Skip docstrings containing only `...`. |
| `exclude` | see [built-in defaults](/docs/style-policies.md#default-exclusion-patterns) | Glob/literal patterns for files and directories to skip. |
| `workers` | `1` | Parallel workers. `0` = auto-detect CPU count. |
| `summary_max_length` | `80` | Maximum summary line length for `summary_too_long`. |
| `blank_lines_before_section` | `1` | Blank lines expected before a section header, checked by `blank_lines`. |
| `blank_lines_before_closing_quotes` | `1` | Blank lines expected before the closing `"""`, checked by `blank_lines`. |
| `scope.modules` | `true` | Check module-level docstrings. |
| `scope.classes` | `true` | Check class docstrings. |
| `scope.functions` | `true` | Check function docstrings. |
| `scope.methods` | `true` | Check method docstrings. |

Every policy accepts `"required"`, `"forbidden"`, or `"optional"`. For the five section policies, `"optional"` means the section is not required, but what the docstring does declare is still checked by the matching rule (`args_match`, `returns_match`, `yields_match`, `raises_match`, `attributes_match`). The two `exclude_empty_init_*` options only lift `docstring_exists`: a docstring that is present is always checked.

`docstring-linter --list-rules` prints the rules, the policies, and the options that change what gets checked, each with the value it has in the current config.

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

- `paths` is required and matched with `PurePath.full_match`, so `tests/**` covers the whole tree. A path given on the command line as an absolute path is matched relative to the current directory as well.
- **A single block applies to a given file**: the last declared among those matching it. The other matching blocks are ignored, blocks never accumulate. Declare the general case first and the exceptions after it, and make each block self-contained.
- The block that applies is resolved against the base configuration, so a setting it does not declare keeps its base value, not the linter default.
- `ignore` removes rules from the inherited set, `select` replaces that set entirely. Same meaning as at the base level.
- An override may carry any policy, and the options that change what is checked on a file: `summary_max_length`, `blank_lines_before_section`, `blank_lines_before_closing_quotes`, `exclude_empty_init_method`, `exclude_empty_init_module`, `ignore_placeholder_docstrings`.
- `exclude`, `workers` and `scope.*` apply to the whole run rather than individual files, so they are rejected inside an override.

`docstring-linter --list-rules` prints the overrides after the base configuration, showing only what each one changes.

### Strict configuration

Anything the linter does not recognize is an error, reported on stderr with exit code 2 before any file is read. This covers a key absent from the table above (including inside `[scope]` and inside an override), a rule name absent from `--list-rules` in `select` or `ignore`, an always-on rule listed in `ignore`, or an invalid policy value.

```console
$ docstring-linter src/
Configuration error: unknown configuration key 'param_order'.
```
