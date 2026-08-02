# Docstring Linter

Python linter that checks docstring conformance to Google style.

## Usage

```bash
# Lint a file
docstring-linter src/module.py

# Lint a project
docstring-linter src/

# List available rules
docstring-linter --list-rules

# Compact one-line-per-error report
docstring-linter src/ --format text

# JSON report (stdout)
docstring-linter src/ --format json

# GitHub Actions annotations (stdout)
docstring-linter src/ --format github-annotations

# Explicit config
docstring-linter src/ --config pyproject.toml

# CI/CD
docstring-linter src/ && echo "OK" || echo "FAIL"
```

### Options

| Option | Description |
|--------|-------------|
| `--exclude` | Glob patterns to exclude. Overrides config file. |
| `--workers` | Number of parallel workers (0 = auto, 1 = sequential). |
| `--format` | Output format: `traceback` (default), `text`, `json`, or `github-annotations`. |
| `--list-rules` | Display all available rules and exit. |
| `--config` | Explicit path to a config file (any `.toml`). |

### Output formats

`traceback` is the default. It prints one location header per entity, in the same shape as a Python traceback, which editors turn into a clickable link:

```
File "/workspaces/project/src/foo.py", line 29, in MyClass.my_method
    [args_match] Arg 'xxx' missing type. Expected '(int)'.
    [raises_match] 'RuntimeError' documented in 'Raises:' but not raised in code.
```

`text` keeps the compact layout, one line per error grouped by file:

```
src/foo.py
  L29   MyClass.my_method [args_match] Arg 'xxx' missing type. Expected '(int)'.
```

## Configuration

Configuration is loaded in this order (first match wins):

1. Explicit `--config path/to/file.toml`
2. `pyproject.toml` with a `[tool.docstring-linter]` section, walking up from the current directory
3. `.docstring-linter.toml`, walking up from the current directory
4. Built-in defaults

### pyproject.toml

```toml
[tool.docstring-linter]
style = "google"
select = ["ALL"]
ignore = []
returns_none = "required"              # "required" | "forbidden" | "optional"
init_returns_none = "forbidden"        # idem
summary_on_first_line = "required"     # idem
summary_final_period = "required"      # idem
args_section = "required"              # idem
returns_section = "required"           # idem
yields_section = "required"            # idem
raises_section = "required"            # idem
attributes_section = "required"        # idem
description_section = "optional"       # idem
examples_section = "optional"          # idem
notes_section = "optional"             # idem
todo_section = "optional"              # idem
documented_types = "required"          # idem
returns_descriptions = "required"      # "required" | "forbidden" | "optional"
exclude_empty_init_method = true
exclude_empty_init_module = true
ignore_placeholder_docstrings = false
exclude = ["test_*", "*_test.py"]
workers = 1
summary_max_length = 80
blank_lines_before_section = 1
blank_lines_before_closing_quotes = 1

[tool.docstring-linter.scope]
modules = true
classes = true
functions = true
methods = true
```

### .docstring-linter.toml

Standalone config file -- same keys, without the `[tool.docstring-linter]` wrapper. `[scope]` replaces `[tool.docstring-linter.scope]`.

```toml
style = "google"
select = ["ALL"]
ignore = []
returns_none = "required"              # "required" | "forbidden" | "optional"
init_returns_none = "forbidden"        # idem
summary_on_first_line = "required"     # idem
summary_final_period = "required"      # idem
args_section = "required"              # idem
returns_section = "required"           # idem
yields_section = "required"            # idem
raises_section = "required"            # idem
attributes_section = "required"        # idem
description_section = "optional"       # idem
examples_section = "optional"          # idem
notes_section = "optional"             # idem
todo_section = "optional"              # idem
documented_types = "required"          # idem
returns_descriptions = "required"      # "required" | "forbidden" | "optional"
exclude_empty_init_method = true
exclude_empty_init_module = true
ignore_placeholder_docstrings = false
exclude = ["test_*", "*_test.py"]
workers = 1
summary_max_length = 80
blank_lines_before_section = 1
blank_lines_before_closing_quotes = 1

[scope]
modules = true
classes = true
functions = true
methods = true
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

- `paths` is required and matched with `PurePath.full_match`, so `tests/**` covers the whole tree. A path given on the command line as an absolute path is matched relative to the current directory as well.
- Blocks are applied in declaration order and **the last match wins**, so declare the general case first and the exceptions after it.
- `ignore` removes rules from the inherited set, `select` replaces that set entirely. Same meaning as at the base level.
- An override may carry any policy, and the options that change what is checked on a file: `summary_max_length`, `blank_lines_before_section`, `blank_lines_before_closing_quotes`, `exclude_empty_init_method`, `exclude_empty_init_module`, `ignore_placeholder_docstrings`.
- `exclude`, `workers`, `style` and `scope.*` apply to the whole run and are rejected inside an override.

`docstring-linter --list-rules` prints the overrides after the base configuration, showing only what each one changes.

### Keys

| Key | Default | Description |
|-----|---------|-------------|
| `style` | `"google"` | Docstring style to enforce. |
| `select` | all rules | Rules to enable. `["ALL"]` enables everything. |
| `ignore` | `[]` | Rules to disable (applied after `select`). Always-on rules cannot be listed here. |
| `returns_none` | `"required"` | Policy for `Returns: None` on `-> None` functions. |
| `init_returns_none` | `"forbidden"` | Policy for `Returns: None` on `__init__` methods. |
| `summary_on_first_line` | `"required"` | Policy for the summary on the opening `"""` line. |
| `summary_final_period` | `"required"` | Policy for the period ending the summary line. |
| `args_section` | `"required"` | Policy for documenting every parameter of the signature. |
| `returns_section` | `"required"` | Policy for the `Returns:` section on a non-`None` return type. |
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
| `exclude` | see defaults | Glob/literal patterns for files and directories to skip. |
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

### Strict configuration

Anything the linter does not recognize is an error, reported on stderr with exit code 2 before any file is read. This covers a key absent from the table above (including inside `[scope]` and inside an override), a rule name absent from `--list-rules` in `select` or `ignore`, an always-on rule listed in `ignore`, and an invalid `style` or policy value.

```console
$ docstring-linter src/
Configuration error: unknown configuration key 'param_order'.
```

## Rule Reference

The list of rules is available on [RULES](/RULES.md) page.

## Integration

### pre-commit / prek

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/bastgau/docstring-linter
    rev: v0.1.0
    hooks:
      - id: docstring-linter
        files: ^src/
```

Then install the hook:

```bash
pre-commit install
# or
prek install
```

### GitHub Actions

#### Composite action

```yaml
- uses: actions/checkout@v7
- uses: actions/setup-python@v7
  with:
    python-version: "3.14"
- uses: bastgau/docstring-linter@v0.1.0
  with:
    paths: src/
    format: github-annotations
```

| Input | Default | Description |
|-------|---------|-------------|
| `paths` | `src/` | Files or directories to lint. |
| `format` | `github-annotations` | Output format: `traceback`, `text`, `json`, or `github-annotations`. |
| `extra-args` | `""` | Additional arguments passed to `docstring-linter`. |
