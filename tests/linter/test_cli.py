"""Tests for cli module."""

import argparse
import json
import sys
from pathlib import Path  # noqa: TC003

import pytest
from linter.cli import collect_python_files, lint_file, main, merge_cli_into_config, run
from linter.config import RULES_CATEGORIES, RULES_REGISTRY, DocstringStyle, LinterConfig

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

_SYNTAX_ERROR_SOURCE = "def bad(:\n    pass\n"


# ---------------------------------------------------------------------------
# collect_python_files
# ---------------------------------------------------------------------------


def test_collect_single_file(tmp_path: Path) -> None:
    """Single .py file path: returns that file."""
    f = tmp_path / "foo.py"
    f.write_text("", encoding="utf-8")
    assert collect_python_files([str(f)], []) == [str(f)]


def test_collect_non_py_file_ignored(tmp_path: Path) -> None:
    """Non-.py file: not collected."""
    f = tmp_path / "foo.txt"
    f.write_text("", encoding="utf-8")
    assert not collect_python_files([str(f)], [])


def test_collect_excluded_file_skipped(tmp_path: Path) -> None:
    """Single file matching exclusion pattern: not collected."""
    f = tmp_path / "test_foo.py"
    f.write_text("", encoding="utf-8")
    assert not collect_python_files([str(f)], ["test_*"])


def test_collect_directory_recursive(tmp_path: Path) -> None:
    """Directory with nested .py files: all collected."""
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "b.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], [])
    assert len(files) == 2


def test_collect_venv_excluded_by_literal_pattern(tmp_path: Path) -> None:
    """File inside a .venv directory: excluded by literal pattern matching path parts."""
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "foo.py").write_text("", encoding="utf-8")
    assert not collect_python_files([str(tmp_path)], [".venv"])


def test_collect_pycache_excluded_by_literal_pattern(tmp_path: Path) -> None:
    """File inside __pycache__: excluded by literal pattern matching path parts."""
    cache = tmp_path / "src" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "foo.cpython-314.pyc").write_text("", encoding="utf-8")
    (tmp_path / "src" / "foo.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], ["__pycache__"])
    assert all("__pycache__" not in f for f in files)


# ---------------------------------------------------------------------------
# lint_file
# ---------------------------------------------------------------------------


def test_lint_file_scope_modules_false(tmp_path: Path) -> None:
    """check_modules=False: module entity is skipped, no module-level errors."""
    f = tmp_path / "nomod.py"
    f.write_text("", encoding="utf-8")
    config = LinterConfig()
    config.check_modules = False
    errors = lint_file(str(f), config)
    assert not errors


def test_lint_file_scope_functions_false(tmp_path: Path) -> None:
    """check_functions=False: function entities are skipped."""
    f = tmp_path / "fn.py"
    f.write_text('"""Module."""\n\ndef foo() -> None:\n    pass\n', encoding="utf-8")
    config = LinterConfig()
    config.check_functions = False
    errors = lint_file(str(f), config)
    rules = {e.rule for e in errors}
    assert "docstring_exists" not in rules


def test_lint_file_syntax_error_raises(tmp_path: Path) -> None:
    """SyntaxError in file: lint_file raises SyntaxError."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    with pytest.raises(SyntaxError):
        lint_file(str(f), LinterConfig())


# ---------------------------------------------------------------------------
# merge_cli_into_config
# ---------------------------------------------------------------------------


def test_merge_style_override() -> None:
    """--style google: overrides config.style."""
    args = argparse.Namespace(style="google", exclude=None, format=None, workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.style == DocstringStyle.GOOGLE


def test_merge_exclude_override() -> None:
    """--exclude test_*: overrides config.exclude_patterns."""
    args = argparse.Namespace(style=None, exclude=["test_*"], format=None, workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.exclude_patterns == ["test_*"]


def test_merge_format_json() -> None:
    """--format json: sets output_format to json."""
    args = argparse.Namespace(style=None, exclude=None, format="json", workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.output_format == "json"


def test_merge_format_github_annotations() -> None:
    """--format github-annotations: sets output_format to github-annotations."""
    args = argparse.Namespace(style=None, exclude=None, format="github-annotations", workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.output_format == "github-annotations"


def test_merge_workers_override() -> None:
    """--workers 4: sets config.workers to 4."""
    args = argparse.Namespace(style=None, exclude=None, format=None, workers=4)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.workers == 4


def test_merge_workers_negative_clamped_to_zero() -> None:
    """--workers -1: clamped to 0 (auto-detect)."""
    args = argparse.Namespace(style=None, exclude=None, format=None, workers=-1)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.workers == 0


def test_merge_no_overrides_leaves_defaults() -> None:
    """No CLI overrides: config unchanged from defaults."""
    args = argparse.Namespace(style=None, exclude=None, format=None, workers=None)
    defaults = LinterConfig()
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.style == defaults.style
    assert config.exclude_patterns == defaults.exclude_patterns


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


def test_run_no_files_returns_zero(tmp_path: Path) -> None:
    """No .py files found: run returns 0."""
    result = run([str(tmp_path)], LinterConfig())
    assert result == 0


def test_run_valid_file_returns_zero(tmp_path: Path) -> None:
    """Valid file with no errors: run returns 0."""
    f = tmp_path / "valid.py"
    f.write_text(_VALID_SOURCE, encoding="utf-8")
    assert run([str(f)], LinterConfig()) == 0


def test_run_invalid_file_returns_one(tmp_path: Path) -> None:
    """File with lint errors: run returns 1."""
    f = tmp_path / "bad.py"
    f.write_text('"""Module."""\n\ndef foo() -> int:\n    pass\n', encoding="utf-8")
    assert run([str(f)], LinterConfig()) == 1


def test_run_syntax_error_returns_zero(tmp_path: Path) -> None:
    """File with SyntaxError: error is caught, run returns 0 (no lint errors)."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    assert run([str(f)], LinterConfig()) == 0


def test_run_with_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Run with output_format=json: JSON report is printed to stdout."""
    f = tmp_path / "valid.py"
    f.write_text(_VALID_SOURCE, encoding="utf-8")
    config = LinterConfig()
    config.output_format = "json"
    run([str(f)], config)
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["total_errors"] == 0


def test_list_rules_output(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """--list-rules: all rules appear in output grouped by category."""
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--list-rules"])
    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    out = capsys.readouterr().out
    for category in RULES_CATEGORIES:
        assert category in out
    for rule in RULES_REGISTRY:
        assert rule in out
