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
| `--style` | Style to enforce (`google`). Overrides config file. |
| `--exclude` | Glob patterns to exclude. Overrides config file. |
| `--workers` | Number of parallel workers (0 = auto, 1 = sequential). |
| `--format` | Output format: `text` (default), `json`, or `github-annotations`. |
| `--list-rules` | Display all available rules and exit. |
| `--config` | Explicit path to a config file (any `.toml`). |

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
ignore = [
    "returns_none_init",     # opt-in
    "returns_none_oneliner", # opt-in
]
exclude_empty_init = true
ignore_placeholder_docstrings = false
exclude = ["test_*", "*_test.py"]
workers = 1
summary_max_length = 80

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
ignore = [
    "returns_none_init",     # opt-in
    "returns_none_oneliner", # opt-in
]
exclude_empty_init = true
ignore_placeholder_docstrings = false
exclude = ["test_*", "*_test.py"]
workers = 1
summary_max_length = 80

[scope]
modules = true
classes = true
functions = true
methods = true
```

### Keys

| Key | Default | Description |
|-----|---------|-------------|
| `style` | `"google"` | Docstring style to enforce. |
| `select` | all rules minus opt-in | Rules to enable. `["ALL"]` enables everything. |
| `ignore` | `[]` | Rules to disable (applied after `select`). |
| `exclude_empty_init` | `true` | Skip `__init__` methods with no parameters and no body. |
| `ignore_placeholder_docstrings` | `false` | Skip docstrings containing only `...`. |
| `exclude` | see defaults | Glob/literal patterns for files and directories to skip. |
| `workers` | `1` | Parallel workers. `0` = auto-detect CPU count. |
| `summary_max_length` | `80` | Maximum summary line length for `summary_too_long`. |
| `scope.modules` | `true` | Check module-level docstrings. |
| `scope.classes` | `true` | Check class docstrings. |
| `scope.functions` | `true` | Check function docstrings. |
| `scope.methods` | `true` | Check method docstrings. |

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
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
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
| `format` | `github-annotations` | Output format: `text`, `json`, or `github-annotations`. |
| `extra-args` | `""` | Additional arguments passed to `docstring-linter`. |
