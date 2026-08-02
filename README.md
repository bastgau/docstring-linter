# Docstring Linter

## Overview

Python linter that validates Google-style docstrings against the actual implementation of functions, methods, classes, and modules.

It can detect mismatches between documented arguments, return values, raised exceptions, and type annotations.

## What is checked?

Examples include:

- Parameter documentation mismatches
- Return documentation mismatches
- Raised exception mismatches
- Yielded value mismatches
- Class attribute mismatches
- Missing or empty docstrings
- Duplicate argument entries
- Missing or invalid summary lines
- Missing required sections
- Section ordering and formatting issues
- Google-style formatting issues

See the rule reference for the complete list.

## Usage

```bash
# Lint a file
docstring-linter src/module.py

# Lint a directory
docstring-linter src/

# List available rules
docstring-linter --list-rules

# Compact one-line-per-error report
docstring-linter src/ --format text

# JSON report (stdout)
docstring-linter src/ --format json

# GitHub Actions annotations (stdout)
docstring-linter src/ --format github-annotations

# Use an explicit config file
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

Command-line options always override configuration file values.

## Output formats

`traceback` is the default. It prints one location header per entity, in the same shape as a Python traceback, which editors turn into a clickable link:

```
File "/workspaces/docstring-linter/example/docstring_format_reference.py", line 84, in divide
    [args_match] Arg 'numerator' missing type. Expected '(int)'.
    [returns_section] Missing 'Returns:' section. Signature declares -> float.

✗ 2 errors in 1 file (2 files checked).
```

<details>

<summary>Other output formats</summary>

`text` keeps the compact layout, one line per error grouped by file:

```
example/docstring_format_reference.py
  L84   divide [args_match] Arg 'numerator' missing type. Expected '(int)'.
  L84   divide [returns_section] Missing 'Returns:' section. Signature declares -> float.

✗ 2 errors in 1 file (2 files checked).
```

`json` produces a machine-readable report suitable for automation and tooling.

```
{
  "summary": {
    "files_checked": 2,
    "total_errors": 2,
    "files_with_errors": 1
  },
  "errors": [
    {
      "filepath": "example/docstring_format_reference.py",
      "line": 84,
      "entity_name": "divide",
      "node_type": "function",
      "rule": "args_match",
      "message": "Arg 'numerator' missing type. Expected '(int)'."
    },
    {
      "filepath": "example/docstring_format_reference.py",
      "line": 84,
      "entity_name": "divide",
      "node_type": "function",
      "rule": "returns_section",
      "message": "Missing 'Returns:' section. Signature declares -> float."
    }
  ]
}
```

`github-annotations` produces GitHub workflow annotations displayed directly in pull requests and CI logs.

```
::error file=example/docstring_format_reference.py,line=84,title=args_match::Arg 'numerator' missing type. Expected '(int)'.
::error file=example/docstring_format_reference.py,line=84,title=returns_section::Missing 'Returns:' section. Signature declares -> float.
2 errors in 1 file (2 files checked).
```

</details>

## Configuration

Every key has a built-in default, so no config file is required at all.

The full list of options is available on the [configuration](/docs/configuration.md) page.

### Rule Reference

The rule documentation is available on:
- [Configurable Rules](/docs/configurable-rules.md)
- [Always-On Rules](/docs/always-on-rules.md)
- [Style Policies](/docs/style-policies.md)

## pre-commit / prek

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/bastgau/docstring-linter
    rev: v0.9.0
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

## GitHub Actions

### Composite action

```yaml
- uses: actions/checkout@v7
- uses: actions/setup-python@v7
  with:
    python-version: "3.14"
- uses: bastgau/docstring-linter@v0.9.0
  with:
    paths: src/
    format: github-annotations
```

| Input | Default | Description |
|-------|---------|-------------|
| `paths` | `src/` | Files or directories to lint. |
| `format` | `github-annotations` | Output format: `traceback`, `text`, `json`, or `github-annotations`. |
| `extra-args` | `""` | Additional arguments passed to `docstring-linter`. |
