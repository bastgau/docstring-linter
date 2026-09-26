# Docstring Linter

## Overview

Python linter that checks Google-style docstrings against the code they document: the signature, the body and the class they belong to.

- **Consistency with the code**: every parameter documented, no phantom parameter, documented types matching the annotations, `Returns:` and `Yields:` matching what the function does, every exception raised documented, class attributes documented.
- **House style, as strict as you want**: every construct is a policy (`required`, `forbidden` or `optional`), from the `Args:` section to the period ending the summary. Two conventions give the starting point: `strict` (default) and `google`, which follows the Google Python Style Guide.
- **Layout**: section order and names, blank lines, indentation, entry spacing.
- **Per-path settings**, a configuration that rejects anything it does not recognize, and no runtime dependency.

## Requirements and installation

Python 3.14 is required. The package is not published on PyPI yet: install it from GitHub.

```bash
pip install "git+https://github.com/bastgau/docstring-linter.git"
# or, as a standalone tool
uv tool install "git+https://github.com/bastgau/docstring-linter.git"
```

## Quick start

```python
# src/shop.py
"""Shopping cart helpers."""


def total(prices: list[float], discount: float = 0.0) -> float:
    """Compute the total price.

    Args:
        prices (list[int]): Item prices.

    """
    if discount < 0:
        raise ValueError(discount)
    return sum(prices) * (1 - discount)
```

```console
$ docstring-linter src/
Config: defaults (no config file found)

File "/path/to/project/src/shop.py", line 4, in total
    [args_section] Arg 'discount' in signature but not documented.
    [args_match] Arg 'prices' type mismatch: signature='list[float]', docstring='list[int]'.
    [returns_section] Missing 'Returns:' section. Signature declares -> float.
    [raises_section] 'ValueError' raised in code but not documented in 'Raises:'.

✗ 4 errors in 1 file (1 file checked).
```

## Usage

```bash
# Lint a file
docstring-linter src/module.py

# Lint a directory
docstring-linter src/

# List the rules, policies and options, with their value in the current config
docstring-linter --list-rules

# Compact one-line-per-error report
docstring-linter src/ --format text

# Number of errors per rule
docstring-linter src/ --statistics

# JSON report (stdout)
docstring-linter src/ --format json

# GitHub Actions annotations (stdout)
docstring-linter src/ --format github-annotations

# Use an explicit config file
docstring-linter src/ --config pyproject.toml
```

### Options

| Option | Description |
|--------|-------------|
| `--exclude` | Glob patterns to exclude. Overrides config file. |
| `--workers` | Number of parallel workers (0 = auto, 1 = sequential). |
| `--format` | Output format: `traceback` (default), `text`, `json`, or `github-annotations`. |
| `--statistics` | Report the number of errors per rule instead of each error. Only with the `traceback` and `text` formats. |
| `--list-rules` | Display all available rules and exit. |
| `--config` | Explicit path to a config file (any `.toml`). |

Command-line options always override configuration file values.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | No error found. |
| `1` | Lint errors found. |
| `2` | Invalid configuration, missing path, or a file that could not be read or parsed. Details are printed on stderr. |

## Output formats

Colors are only used when the output is a terminal, and never when the `NO_COLOR` environment variable is set to a non-empty value.

`traceback` is the default, shown in the quick start. It prints one location header per entity, in the same shape as a Python traceback, which editors turn into a clickable link. Errors point to the line of the `def` or `class`.

<details>

<summary>Other output formats</summary><br />

`text` keeps the compact layout, one line per error grouped by file:

```
src/shop.py
  L4    total [args_section] Arg 'discount' in signature but not documented.
  L4    total [args_match] Arg 'prices' type mismatch: signature='list[float]', docstring='list[int]'.
  L4    total [returns_section] Missing 'Returns:' section. Signature declares -> float.
  L4    total [raises_section] 'ValueError' raised in code but not documented in 'Raises:'.

✗ 4 errors in 1 file (1 file checked).
```

`json` produces a machine-readable report suitable for automation and tooling:

```json
{
  "summary": {
    "files_checked": 1,
    "total_errors": 4,
    "files_with_errors": 1
  },
  "errors": [
    {
      "filepath": "src/shop.py",
      "line": 4,
      "entity_name": "total",
      "node_type": "function",
      "rule": "args_section",
      "message": "Arg 'discount' in signature but not documented."
    }
  ]
}
```

The `errors` list above is shortened to its first entry.

`github-annotations` produces GitHub workflow annotations displayed directly in pull requests and CI logs:

```
::error file=src/shop.py,line=4,title=args_section::Arg 'discount' in signature but not documented.
::error file=src/shop.py,line=4,title=args_match::Arg 'prices' type mismatch: signature='list[float]', docstring='list[int]'.
::error file=src/shop.py,line=4,title=returns_section::Missing 'Returns:' section. Signature declares -> float.
::error file=src/shop.py,line=4,title=raises_section::'ValueError' raised in code but not documented in 'Raises:'.
4 errors in 1 file (1 file checked).
```

</details>

## Configuration

Every key has a built-in default, so no config file is required at all. The configuration is read from `[tool.docstring-linter]` in `pyproject.toml`, or from a standalone `.docstring-linter.toml`.

The defaults enforce a strict house style: every type repeated in the docstring, `Returns: None` on `-> None` functions, every exception and attribute documented. To follow the Google Python Style Guide instead, start from the `google` convention:

```toml
[tool.docstring-linter]
convention = "google"
```

Among other things, it leaves types to the signature, accepts one-line docstrings without sections on fully annotated functions, documents properties like attributes, and lets `__init__` parameters live in the class docstring. Any key written in the file overrides the convention.

The full list of options, the conventions and the per-path overrides are described on the [configuration](/docs/configuration.md) page.

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
        language_version: python3.14  # when python3.14 is not the default interpreter
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

## Known limitations

- Functions and classes defined inside a function are not checked.
- Code under `if __name__ == "__main__":` and `@overload` signatures are skipped.
- `Raises:` only sees the explicit `raise` statements of the function body: exceptions raised by called functions and the `raise` of a plain variable are not detected.
- Class attributes are read from class-level assignments and from `self.x = ...` in `__init__` only: attributes created in other methods are not detected.
- Type aliases are not resolved, and Sphinx roles such as ``:class:`Path` `` are not recognized in documented types.
- `exclude_overridden` only recognizes `@override`, not a method overridden through inheritance.
- Every error points to the `def` or `class` line, not to the docstring line at fault.
- Google style only. The content of `Warn:` and `Warns:` sections is not checked.
- No inline suppression (`# noqa`) or baseline yet.

## How it compares

State of the tools checked in September 2026.

| Tool | Focus |
|------|-------|
| [ruff](https://docs.astral.sh/ruff/) `D` rules | Docstring format (PEP 257, Google, NumPy conventions). Its `DOC` rules, which compare the docstring with the code, are still in preview (7 rules in ruff 0.16.8). |
| [pydoclint](https://github.com/jsh9/pydoclint) | Consistency between docstring and code (arguments, returns, yields, raises, class attributes), with a baseline and `noqa` support. |
| [docsig](https://github.com/jshwi/docsig) | Consistency between the documented parameters and the signature. |
| docstring-linter | Consistency with the code, plus a configurable house style: tri-state policies for every section and construct, layout rules, and the `strict` and `google` conventions. Google style only. |

docstring-linter does not replace ruff: it can run next to its `D` rules, with the rules both tools check turned off on one side.
