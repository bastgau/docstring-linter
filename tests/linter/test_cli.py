"""Tests for cli module."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from linter.cli import _resolve_workers, collect_python_files, lint_file, main, merge_cli_into_config, run  # pyright: ignore[reportPrivateUsage]
from linter.config import ALWAYS_ON, RULES_CATEGORIES, RULES_REGISTRY, LinterConfig

if TYPE_CHECKING:
    from collections.abc import Iterator

    from linter.models import LintError

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
    assert collect_python_files([str(f)], [], tmp_path) == [str(f)]


def test_collect_non_py_file_ignored(tmp_path: Path) -> None:
    """Non-.py file: not collected."""
    f = tmp_path / "foo.txt"
    f.write_text("", encoding="utf-8")
    assert not collect_python_files([str(f)], [], tmp_path)


def test_collect_explicit_file_kept_despite_exclusion(tmp_path: Path) -> None:
    """File given explicitly and matching an exclusion pattern: still collected."""
    f = tmp_path / "test_foo.py"
    f.write_text("", encoding="utf-8")
    assert collect_python_files([str(f)], ["test_*"], tmp_path) == [str(f)]


def test_collect_explicit_file_skipped_with_force_exclude(tmp_path: Path) -> None:
    """File given explicitly and matching an exclusion pattern, with force_exclude: not collected."""
    f = tmp_path / "test_foo.py"
    f.write_text("", encoding="utf-8")
    assert not collect_python_files([str(f)], ["test_*"], tmp_path, force_exclude=True)


def test_collect_directory_recursive(tmp_path: Path) -> None:
    """Directory with nested .py files: all collected."""
    (tmp_path / "a.py").write_text("", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "b.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], [], tmp_path)
    assert len(files) == 2


def test_collect_venv_excluded_by_literal_pattern(tmp_path: Path) -> None:
    """File inside a .venv directory: excluded by literal pattern matching path parts."""
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "foo.py").write_text("", encoding="utf-8")
    assert not collect_python_files([str(tmp_path)], [".venv"], tmp_path)


def test_collect_literal_excluded_directory_not_walked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Directory named by a literal pattern: skipped during the walk, its content is never listed."""
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    (tmp_path / ".venv" / "lib" / "foo.py").write_text("", encoding="utf-8")
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    walked: list[Path] = []
    real_walk = Path.walk

    def spy_walk(self: Path) -> Iterator[tuple[Path, list[str], list[str]]]:
        for entry in real_walk(self):
            walked.append(entry[0])
            yield entry

    monkeypatch.setattr(Path, "walk", spy_walk)
    assert collect_python_files([str(tmp_path)], [".venv"], tmp_path) == [str(tmp_path / "main.py")]
    assert walked == [tmp_path]


def test_collect_directory_named_like_a_module(tmp_path: Path) -> None:
    """Directory whose name ends with .py: walked into, never collected as a file."""
    (tmp_path / "pkg.py").mkdir()
    (tmp_path / "pkg.py" / "mod.py").write_text("", encoding="utf-8")
    assert collect_python_files([str(tmp_path)], [], tmp_path) == [str(tmp_path / "pkg.py" / "mod.py")]


def test_collect_pycache_excluded_by_literal_pattern(tmp_path: Path) -> None:
    """File inside __pycache__: excluded by literal pattern matching path parts."""
    cache = tmp_path / "src" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "foo.cpython-314.pyc").write_text("", encoding="utf-8")
    (tmp_path / "src" / "foo.py").write_text("", encoding="utf-8")
    files = collect_python_files([str(tmp_path)], ["__pycache__"], tmp_path)
    assert all("__pycache__" not in f for f in files)


def test_collect_recursive_glob_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Pattern tests/**: every file under tests/ is excluded, at any depth."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / "tests" / "unit" / "test_a.py").write_text("", encoding="utf-8")
    (tmp_path / "tests" / "conftest.py").write_text("", encoding="utf-8")
    (tmp_path / "main.py").write_text("", encoding="utf-8")
    assert collect_python_files(["."], ["tests/**"], tmp_path) == ["main.py"]


def test_collect_directory_glob_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Pattern src/gen/*.py: files directly under src/gen/ are excluded, others kept."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "gen").mkdir(parents=True)
    (tmp_path / "src" / "gen" / "model.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "app.py").write_text("", encoding="utf-8")
    assert collect_python_files(["src"], ["src/gen/*.py"], tmp_path) == ["src/app.py"]


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


def test_merge_exclude_override() -> None:
    """--exclude test_*: overrides config.exclude_patterns."""
    args = argparse.Namespace(exclude=["test_*"], format=None, workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.exclude_patterns == ["test_*"]


def test_merge_format_json() -> None:
    """--format json: sets output_format to json."""
    args = argparse.Namespace(exclude=None, format="json", workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.output_format == "json"


def test_merge_format_github_annotations() -> None:
    """--format github-annotations: sets output_format to github-annotations."""
    args = argparse.Namespace(exclude=None, format="github-annotations", workers=None)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.output_format == "github-annotations"


def test_merge_workers_override() -> None:
    """--workers 4: sets config.workers to 4."""
    args = argparse.Namespace(exclude=None, format=None, workers=4)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.workers == 4


def test_merge_workers_negative_clamped_to_zero() -> None:
    """--workers -1: clamped to 0 (auto-detect)."""
    args = argparse.Namespace(exclude=None, format=None, workers=-1)
    config = merge_cli_into_config(LinterConfig(), args)
    assert config.workers == 0


def test_merge_no_overrides_leaves_defaults() -> None:
    """No CLI overrides: config unchanged from defaults."""
    args = argparse.Namespace(exclude=None, format=None, workers=None)
    defaults = LinterConfig()
    config = merge_cli_into_config(LinterConfig(), args)
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


def test_run_syntax_error_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """File with SyntaxError: reported on stderr, run returns 2."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    assert run([str(f)], LinterConfig()) == 2
    captured = capsys.readouterr()
    assert "Syntax error in" in captured.err
    assert "Syntax error in" not in captured.out


def test_run_syntax_error_keeps_json_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """File with SyntaxError under --format json: stdout stays valid JSON, run returns 2."""
    f = tmp_path / "bad.py"
    f.write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    config = LinterConfig()
    config.output_format = "json"
    assert run([str(f)], config) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["files_checked"] == 1


def test_run_undecodable_file_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """File that is not valid UTF-8: reported as unreadable on stderr, run returns 2."""
    f = tmp_path / "latin.py"
    f.write_bytes(b"\xff\xfe bad")
    assert run([str(f)], LinterConfig()) == 2
    assert "Cannot read" in capsys.readouterr().err


def test_run_failure_wins_over_lint_errors(tmp_path: Path) -> None:
    """One unparsable file and one file with lint errors: run returns 2."""
    (tmp_path / "bad.py").write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    (tmp_path / "errors.py").write_text('"""Module."""\n\ndef foo() -> int:\n    pass\n', encoding="utf-8")
    assert run([str(tmp_path)], LinterConfig()) == 2


def test_run_internal_error_returns_three(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Unexpected exception on one file: file named with the traceback, other files still linted, run returns 3."""
    (tmp_path / "bad.py").write_text(_SYNTAX_ERROR_SOURCE, encoding="utf-8")
    (tmp_path / "boom.py").write_text("", encoding="utf-8")
    (tmp_path / "errors.py").write_text('"""Module."""\n\ndef foo() -> int:\n    pass\n', encoding="utf-8")
    real_lint_file = lint_file

    def failing_lint_file(filepath: str, config: LinterConfig) -> list[LintError]:
        if filepath.endswith("boom.py"):
            msg = "unexpected"
            raise RuntimeError(msg)
        return real_lint_file(filepath, config)

    monkeypatch.setattr("linter.cli.lint_file", failing_lint_file)
    config = LinterConfig()
    config.workers = 1
    config.output_format = "text"

    assert run([str(tmp_path)], config) == 3
    captured = capsys.readouterr()
    assert f"Internal error while linting {tmp_path / 'boom.py'}: RuntimeError: unexpected" in captured.err
    assert "Traceback (most recent call last):" in captured.err
    assert "foo" in captured.out


def test_run_missing_path_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Path that does not exist: reported on stderr, run returns 2 without linting."""
    assert run([str(tmp_path / "missing")], LinterConfig()) == 2
    assert "Path not found" in capsys.readouterr().err


def test_resolve_workers_auto_is_the_default() -> None:
    """Default config: workers is 0, the auto mode."""
    assert LinterConfig().workers == 0


def test_resolve_workers_auto_sequential_on_small_runs() -> None:
    """Auto mode below 50 files: sequential, the process pool would cost more than it saves."""
    assert _resolve_workers(0, 49) == 1


def test_resolve_workers_auto_uses_usable_cpus(monkeypatch: pytest.MonkeyPatch) -> None:
    """Auto mode from 50 files: one worker per CPU usable by the process."""
    monkeypatch.setattr("os.process_cpu_count", lambda: 3)
    assert _resolve_workers(0, 50) == 3


def test_resolve_workers_explicit_value_kept() -> None:
    """Explicit worker count: used as is, whatever the number of files."""
    assert _resolve_workers(4, 2) == 4


def test_run_parallel_workers(tmp_path: Path) -> None:
    """Two workers on two files: errors from every file are collected."""
    (tmp_path / "valid.py").write_text(_VALID_SOURCE, encoding="utf-8")
    (tmp_path / "errors.py").write_text('"""Module."""\n\ndef foo() -> int:\n    pass\n', encoding="utf-8")
    config = LinterConfig()
    config.workers = 2
    assert run([str(tmp_path)], config) == 1


def test_run_with_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Run with output_format=json: JSON report is printed to stdout."""
    f = tmp_path / "valid.py"
    f.write_text(_VALID_SOURCE, encoding="utf-8")
    config = LinterConfig()
    config.output_format = "json"
    run([str(f)], config)
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["total_errors"] == 0


def test_main_from_subdirectory_uses_config_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Run from src/ with the config at the root: exclude and override patterns still apply from the root."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.docstring-linter]\nexclude = ["src/gen/*.py"]\n\n[[tool.docstring-linter.overrides]]\npaths = ["src/**"]\nignore = ["docstring_exists"]\n',
        encoding="utf-8",
    )
    (tmp_path / "src" / "gen").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("def f():\n    pass\n", encoding="utf-8")
    (tmp_path / "src" / "gen" / "model.py").write_text("def f():\n    pass\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path / "src")
    monkeypatch.setattr(sys, "argv", ["docstring-linter", ".", "--format", "text"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert "1 file checked, 0 errors." in capsys.readouterr().out


def test_main_force_exclude_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Excluded file passed explicitly: linted by default, skipped with --force-exclude."""
    (tmp_path / "pyproject.toml").write_text('[tool.docstring-linter]\nexclude = ["gen/**"]\n', encoding="utf-8")
    (tmp_path / "gen").mkdir()
    (tmp_path / "gen" / "model.py").write_text("def f():\n    pass\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["docstring-linter", "gen/model.py", "--format", "text"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1

    monkeypatch.setattr(sys, "argv", ["docstring-linter", "gen/model.py", "--format", "text", "--force-exclude"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert "No Python files found." in capsys.readouterr().out


def test_main_closed_output_pipe_exits_quietly(tmp_path: Path) -> None:
    """Output pipe closed before the report is written: exit 1 without a traceback."""
    f = tmp_path / "bad.py"
    f.write_text("def f():\n    pass\n", encoding="utf-8")
    with subprocess.Popen([sys.executable, "-m", "linter.cli", str(f)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:  # noqa: S603
        assert proc.stdout is not None
        proc.stdout.close()
        _, stderr = proc.communicate()
    assert proc.returncode == 1
    assert b"BrokenPipeError" not in stderr


def test_list_rules_output(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """--list-rules: every rule appears, always-on rules in their own section after the categories."""
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--list-rules"])
    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    out = capsys.readouterr().out
    for category in RULES_CATEGORIES:
        assert category in out
    configurable, always_on = out.split("Always on", 1)
    for rule in RULES_REGISTRY:
        if rule in ALWAYS_ON:
            assert f"{rule} " in always_on
            assert f"{rule} " not in configurable
        else:
            assert f"{rule} " in configurable


def test_list_rules_google_convention_disabled_rules(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """--list-rules with the google convention: its disabled rules are counted and labelled as disabled by default."""
    config = tmp_path / "linter.toml"
    config.write_text('convention = "google"\n', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--list-rules", "--config", str(config)])
    with pytest.raises(SystemExit):
        main()

    out = capsys.readouterr().out
    assert "3 disabled by default" in out
    for rule in ("imperative_mood", "return_type_annotation", "raises_extraneous"):
        assert "(disabled by default)" in next(line for line in out.splitlines() if f" {rule} " in line)


def test_main_config_line_on_stderr(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Text format: the Config line goes to stderr, stdout only holds the report."""
    config = tmp_path / "linter.toml"
    config.write_text("", encoding="utf-8")
    (tmp_path / "valid.py").write_text(_VALID_SOURCE, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["docstring-linter", str(tmp_path / "valid.py"), "--config", str(config), "--format", "text"])
    with pytest.raises(SystemExit):
        main()

    captured = capsys.readouterr()
    assert f"Config: {config}" in captured.err
    assert "Config:" not in captured.out
    assert "1 file checked, 0 errors." in captured.out


def test_main_invalid_config_value(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid value in the config file: prints a configuration error and exits with 2."""
    f = tmp_path / "bad.toml"
    f.write_text('returns_descriptions = "maybe"\n', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--config", str(f), str(tmp_path)])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
    assert "Configuration error" in capsys.readouterr().err


def test_main_missing_config_file(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """--config pointing to a missing file: prints a configuration error and exits with 2."""
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--config", str(tmp_path / "missing.toml"), str(tmp_path)])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
    assert "config file not found" in capsys.readouterr().err


def test_run_statistics_counts_errors_per_rule(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Run with statistics: one count per rule instead of each error, same exit code."""
    f = tmp_path / "bad.py"
    f.write_text('"""Module."""\n\ndef foo() -> int:\n    pass\n\n\ndef bar() -> int:\n    pass\n', encoding="utf-8")
    assert run([str(f)], LinterConfig(), statistics=True) == 1
    out = capsys.readouterr().out
    assert "2  docstring_exists" in out
    assert "foo" not in out
    assert "2 errors in 1 file" in out


def test_main_statistics_rejected_with_json(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """--statistics with a machine-readable format: error on stderr and exit 2."""
    config = tmp_path / "linter.toml"
    config.write_text("", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["docstring-linter", "--config", str(config), "--statistics", "--format", "json", str(tmp_path)])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
    assert "--statistics is not available with the json format." in capsys.readouterr().err


def test_run_unknown_rule_in_ignore_comment_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Ignore comment naming an unknown rule: file and line on stderr, run returns 2."""
    f = tmp_path / "typo.py"
    f.write_text('"""Module."""\n\n\ndef foo() -> None:  # docstring-linter: ignore[args_mach]\n    pass\n', encoding="utf-8")
    assert run([str(f)], LinterConfig()) == 2
    assert f"{f}:4: unknown rule 'args_mach' in ignore comment." in capsys.readouterr().err
