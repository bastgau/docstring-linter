"""Integration tests for the docstring linter CLI and lint_file pipeline."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from linter.cli import collect_python_files, lint_file
from linter.config import LinterConfig

_SRC = str(Path(__file__).parent.parent.parent / "src")
_ENV = {**os.environ, "PYTHONPATH": _SRC}

_VALID_SOURCE = '''\
"""Module docstring."""


def add(x: int, y: int) -> int:
    """Add two integers.

    Args:
        x (int): First operand.
        y (int): Second operand.

    Returns:
        int: The sum.

    """
    return x + y
'''

_INVALID_SOURCE = '''\
"""Module docstring."""


def broken(x: int) -> int:
    """Missing Args and Returns sections."""
    return x
'''

_SYNTAX_ERROR_SOURCE = "def bad(:\n    pass\n"


# ---------------------------------------------------------------------------
# lint_file -- valid file
# ---------------------------------------------------------------------------


def test_lint_file_valid_returns_no_errors(tmp_path: Path) -> None:
    """Valid well-documented file: lint_file returns no errors."""
    f = tmp_path / "valid.py"
    f.write_text(_VALID_SOURCE, encoding="utf-8")
    config = LinterConfig()
    errors = lint_file(str(f), config)
    assert not errors


# ---------------------------------------------------------------------------
# lint_file -- file with errors
# ---------------------------------------------------------------------------


def test_lint_file_invalid_returns_errors(tmp_path: Path) -> None:
    """File with missing Args and Returns sections: lint_file returns errors."""
    f = tmp_path / "invalid.py"
    f.write_text(_INVALID_SOURCE, encoding="utf-8")
    config = LinterConfig()
    errors = lint_file(str(f), config)
    rules = {e.rule for e in errors}
    assert "args_match" in rules
    assert "returns_section" in rules


# ---------------------------------------------------------------------------
# lint_file -- syntax error
# ---------------------------------------------------------------------------


def test_lint_file_syntax_error_propagates(tmp_path: Path) -> None:
    """File with SyntaxError: lint_file raises SyntaxError."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    with pytest.raises(SyntaxError):
        lint_file(str(f), LinterConfig())


# ---------------------------------------------------------------------------
# collect_python_files -- directory scan
# ---------------------------------------------------------------------------


def test_collect_python_files_finds_all_py(tmp_path: Path) -> None:
    """Directory with multiple .py files: collect_python_files returns all of them."""
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "b.py").write_text("", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], [])
    names = {Path(f).name for f in files}
    assert names == {"a.py", "b.py", "c.py"}


def test_collect_python_files_exclude_pattern(tmp_path: Path) -> None:
    """Directory with exclusion pattern: matching files are not collected."""
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    (tmp_path / "test_main.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], ["test_*"])
    names = {Path(f).name for f in files}
    assert "main.py" in names
    assert "test_main.py" not in names


# ---------------------------------------------------------------------------
# CLI -- --list-rules
# ---------------------------------------------------------------------------


def test_cli_list_rules_exit_zero() -> None:
    """--list-rules: exits with code 0 and prints rule names."""
    result = subprocess.run(
        [sys.executable, "-m", "linter.cli", "--list-rules"],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 0
    assert "docstring_exists" in result.stdout
    assert "args_match" in result.stdout


# ---------------------------------------------------------------------------
# CLI -- valid file exit code 0
# ---------------------------------------------------------------------------


def test_cli_valid_file_exit_zero(tmp_path: Path) -> None:
    """CLI on valid file: exits with code 0."""
    f = tmp_path / "valid.py"
    f.write_text(_VALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(f)],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# CLI -- file with errors exit code 1
# ---------------------------------------------------------------------------


def test_cli_invalid_file_exit_one(tmp_path: Path) -> None:
    """CLI on file with errors: exits with code 1."""
    f = tmp_path / "invalid.py"
    f.write_text(_INVALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(f)],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 1
    assert "args_match" in result.stdout or "args_match" in result.stderr


# ---------------------------------------------------------------------------
# CLI -- syntax error does not crash
# ---------------------------------------------------------------------------


def test_cli_syntax_error_no_crash(tmp_path: Path) -> None:
    """CLI on file with SyntaxError: does not crash, prints error message, exits 0."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(f)],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 0
    assert "Syntax error" in result.stdout or "Syntax error" in result.stderr


# ---------------------------------------------------------------------------
# CLI -- --format json output
# ---------------------------------------------------------------------------


def test_cli_json_output_valid_file(tmp_path: Path) -> None:
    """--format json on valid file: JSON report printed to stdout with 0 errors."""
    src = tmp_path / "valid.py"
    src.write_text(_VALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(src), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["summary"]["total_errors"] == 0
    assert report["summary"]["files_checked"] == 1


def test_cli_json_output_invalid_file(tmp_path: Path) -> None:
    """--format json on file with errors: JSON report on stdout with errors."""
    src = tmp_path / "invalid.py"
    src.write_text(_INVALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(src), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["summary"]["total_errors"] > 0
    assert report["summary"]["files_checked"] == 1
    assert report["summary"]["files_with_errors"] == 1
    rules = {e["rule"] for e in report["errors"]}
    assert "args_match" in rules


# ---------------------------------------------------------------------------
# CLI -- --format github-annotations output
# ---------------------------------------------------------------------------


def test_cli_github_annotations_valid_file(tmp_path: Path) -> None:
    """--format github-annotations on valid file: no output, exit 0."""
    src = tmp_path / "valid.py"
    src.write_text(_VALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(src), "--format", "github-annotations"],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 0
    assert "1 files checked, 0 errors." in result.stdout


def test_cli_github_annotations_invalid_file(tmp_path: Path) -> None:
    """--format github-annotations on file with errors: annotations on stdout, exit 1."""
    src = tmp_path / "invalid.py"
    src.write_text(_INVALID_SOURCE, encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "linter.cli", str(src), "--format", "github-annotations"],
        capture_output=True,
        text=True,
        check=False,
        env=_ENV,
    )
    assert result.returncode == 1
    assert "::error file=" in result.stdout
    assert ",title=" in result.stdout
