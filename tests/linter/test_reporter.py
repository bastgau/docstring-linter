"""Tests for reporter module."""

import json
from typing import TYPE_CHECKING, Any

from linter.models import LintError, NodeType
from linter.reporter import report_cli, report_github_annotations, report_json, report_rules

if TYPE_CHECKING:
    import pytest


def _error(rule: str = "args_match", line: int = 10, filepath: str = "src/foo.py") -> LintError:
    return LintError(
        filepath=filepath,
        line=line,
        entity_name="my_func",
        node_type=NodeType.FUNCTION,
        rule=rule,
        message="Some error.",
    )


# ---------------------------------------------------------------------------
# report_cli
# ---------------------------------------------------------------------------


def test_report_cli_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """No errors: prints summary with 0 errors."""
    report_cli([], files_checked=3)
    out = capsys.readouterr().out
    assert "3 files checked, 0 errors." in out


def test_report_cli_with_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """With errors: prints each error and a summary line."""
    errors = [_error("args_match", line=5), _error("returns_section", line=12)]
    report_cli(errors, files_checked=1)
    out = capsys.readouterr().out
    assert "args_match" in out
    assert "returns_section" in out


def test_report_cli_single_error_grammar(capsys: pytest.CaptureFixture[str]) -> None:
    """Single error: summary says 'error' not 'errors'."""
    report_cli([_error()], files_checked=1)
    out: Any = capsys.readouterr().out
    assert "1 error" in out
    assert "errors" not in out.split("1 error")[1][:1]


def test_report_cli_multiple_files(capsys: pytest.CaptureFixture[str]) -> None:
    """Errors in multiple files: each file is printed separately."""
    errors = [_error(filepath="src/a.py"), _error(filepath="src/b.py")]
    report_cli(errors, files_checked=2)
    out = capsys.readouterr().out
    assert "src/a.py" in out
    assert "src/b.py" in out


# ---------------------------------------------------------------------------
# report_json
# ---------------------------------------------------------------------------


def test_report_json_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """No errors: JSON output has total_errors=0 and empty errors list."""
    report_json([], files_checked=2)
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["files_checked"] == 2
    assert report["summary"]["total_errors"] == 0
    assert report["summary"]["files_with_errors"] == 0
    assert report["errors"] == []


def test_report_json_with_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """With errors: JSON output contains error details with all expected fields."""
    report_json([_error("args_match", line=7)], files_checked=1)
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["total_errors"] == 1
    assert report["summary"]["files_with_errors"] == 1
    error = report["errors"][0]
    assert error["rule"] == "args_match"
    assert error["line"] == 7
    assert error["filepath"] == "src/foo.py"
    assert error["node_type"] == "function"


def test_report_json_sorted_by_file_and_line(capsys: pytest.CaptureFixture[str]) -> None:
    """Errors are sorted by filepath then line in the JSON output."""
    errors = [
        _error(line=20, filepath="src/b.py"),
        _error(line=5, filepath="src/a.py"),
        _error(line=2, filepath="src/a.py"),
    ]
    report_json(errors, files_checked=2)
    report = json.loads(capsys.readouterr().out)
    lines = [(e["filepath"], e["line"]) for e in report["errors"]]
    assert lines == [("src/a.py", 2), ("src/a.py", 5), ("src/b.py", 20)]


# ---------------------------------------------------------------------------
# report_github_annotations
# ---------------------------------------------------------------------------


def test_report_github_annotations_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """No errors: summary line only."""
    report_github_annotations([], files_checked=5)
    assert capsys.readouterr().out.strip() == "5 files checked, 0 errors."


def test_report_github_annotations_format(capsys: pytest.CaptureFixture[str]) -> None:
    """Single error: annotation followed by summary."""
    report_github_annotations([_error("args_match", line=7)], files_checked=1)
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "::error file=src/foo.py,line=7,title=args_match::Some error."
    assert "1 error" in lines[1]


def test_report_github_annotations_sorted(capsys: pytest.CaptureFixture[str]) -> None:
    """Multiple errors: sorted by filepath then line, summary at end."""
    errors = [
        _error(line=20, filepath="src/b.py"),
        _error(line=5, filepath="src/a.py"),
        _error(line=2, filepath="src/a.py"),
    ]
    report_github_annotations(errors, files_checked=2)
    lines = capsys.readouterr().out.splitlines()
    assert "src/a.py" in lines[0]
    assert ",line=2," in lines[0]
    assert "src/a.py" in lines[1]
    assert ",line=5," in lines[1]
    assert "src/b.py" in lines[2]
    assert "3 errors" in lines[3]


# ---------------------------------------------------------------------------
# report_rules
# ---------------------------------------------------------------------------

_CATEGORIES = {
    "Presence": ["rule_a", "rule_b"],
    "Style": ["rule_c"],
}
_REGISTRY = {
    "rule_a": "Description of rule A.",
    "rule_b": "Description of rule B.",
    "rule_c": "Description of rule C.",
}
_OFF_BY_DEFAULT: frozenset[str] = frozenset({"rule_b"})


def test_report_rules_all_categories_present(capsys: pytest.CaptureFixture[str]) -> None:
    """All category names appear in output."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset(_REGISTRY))
    out = capsys.readouterr().out
    assert "Presence" in out
    assert "Style" in out


def test_report_rules_all_rules_present(capsys: pytest.CaptureFixture[str]) -> None:
    """All rule identifiers appear in output."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset(_REGISTRY))
    out = capsys.readouterr().out
    for rule in _REGISTRY:
        assert rule in out


def test_report_rules_enabled_rule_shows_checkmark(capsys: pytest.CaptureFixture[str]) -> None:
    """Enabled rule shows ✔ marker."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset({"rule_a"}))
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_a" in line]
    assert matching
    assert "✔" in matching[0]


def test_report_rules_disabled_rule_shows_cross(capsys: pytest.CaptureFixture[str]) -> None:
    """Disabled rule shows ✘ marker."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset())
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_a" in line]
    assert matching
    assert "✘" in matching[0]


def test_report_rules_off_by_default_label(capsys: pytest.CaptureFixture[str]) -> None:
    """Rule in off_by_default shows '(disabled by default)' label."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset())
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_b" in line]
    assert matching
    assert "(disabled by default)" in matching[0]
