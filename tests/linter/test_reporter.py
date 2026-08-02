"""Tests for reporter module."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from linter.config import ConfigOverride, Policy
from linter.models import LintError, NodeType
from linter.reporter import report_cli, report_github_annotations, report_json, report_options, report_overrides, report_policies, report_rules, report_traceback

if TYPE_CHECKING:
    import pytest


def _error(rule: str = "args_match", line: int = 10, filepath: str = "src/foo.py") -> LintError:
    """Build a lint error on a dummy function."""
    return LintError(
        filepath=filepath,
        line=line,
        entity_name="my_func",
        node_type=NodeType.FUNCTION,
        rule=rule,
        message="Some error.",
    )


# ---------------------------------------------------------------------------
# report_traceback
# ---------------------------------------------------------------------------


def test_report_traceback_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """No errors: prints summary with 0 errors."""
    report_traceback([], files_checked=3)
    out = capsys.readouterr().out
    assert "3 files checked, 0 errors." in out


def test_report_traceback_location_header(capsys: pytest.CaptureFixture[str]) -> None:
    """With errors: prints one clickable header with the absolute path per entity."""
    report_traceback([_error("args_match", line=5)], files_checked=1)
    out = capsys.readouterr().out
    assert f'File "{Path("src/foo.py").resolve()}", line 5' in out
    assert "my_func" in out
    assert "args_match" in out


def test_report_traceback_groups_errors_by_entity(capsys: pytest.CaptureFixture[str]) -> None:
    """Two errors on the same entity: a single header followed by both messages."""
    errors = [_error("args_match", line=5), _error("raises_match", line=5)]
    report_traceback(errors, files_checked=1)
    out = capsys.readouterr().out
    assert out.count('", line 5') == 1
    assert "args_match" in out
    assert "raises_match" in out


def test_report_traceback_separate_entities(capsys: pytest.CaptureFixture[str]) -> None:
    """Errors on different lines: one header each."""
    errors = [_error("args_match", line=5), _error("args_match", line=12)]
    report_traceback(errors, files_checked=1)
    out = capsys.readouterr().out
    assert out.count("my_func") == 2


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
_ALWAYS_ON: frozenset[str] = frozenset({"rule_c"})


def test_report_rules_all_categories_present(capsys: pytest.CaptureFixture[str]) -> None:
    """Category names with at least one configurable rule appear in output."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset(), frozenset(_REGISTRY))
    out = capsys.readouterr().out
    assert "Presence" in out
    assert "Style" in out


def test_report_rules_category_hidden_when_all_rules_always_on(capsys: pytest.CaptureFixture[str]) -> None:
    """Category whose rules are all always on: the category is not printed."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, _ALWAYS_ON, frozenset(_REGISTRY))
    out = capsys.readouterr().out
    assert "Presence" in out
    assert "Style" not in out


def test_report_rules_all_rules_present(capsys: pytest.CaptureFixture[str]) -> None:
    """All configurable rule identifiers appear in output."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, frozenset(), frozenset(_REGISTRY))
    out = capsys.readouterr().out
    for rule in _REGISTRY:
        assert rule in out


def test_report_rules_enabled_rule_shows_checkmark(capsys: pytest.CaptureFixture[str]) -> None:
    """Enabled rule shows ✔ marker."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, _ALWAYS_ON, frozenset({"rule_a"}))
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_a" in line]
    assert matching
    assert "✔" in matching[0]


def test_report_rules_disabled_rule_shows_cross(capsys: pytest.CaptureFixture[str]) -> None:
    """Disabled rule shows ✘ marker."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, _ALWAYS_ON, frozenset())
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_a" in line]
    assert matching
    assert "✘" in matching[0]


def test_report_rules_always_on_hidden(capsys: pytest.CaptureFixture[str]) -> None:
    """Rule in always_on is not listed and is not counted in the header."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, _ALWAYS_ON, frozenset())
    out = capsys.readouterr().out
    assert "rule_c" not in out
    assert "2 configurable rules" in out


def test_report_rules_off_by_default_label(capsys: pytest.CaptureFixture[str]) -> None:
    """Rule in off_by_default shows '(disabled by default)' label."""
    report_rules(_CATEGORIES, _REGISTRY, _OFF_BY_DEFAULT, _ALWAYS_ON, frozenset())
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "rule_b" in line]
    assert matching
    assert "(disabled by default)" in matching[0]


# ---------------------------------------------------------------------------
# report_policies
# ---------------------------------------------------------------------------

_POLICIES = {
    "policy_a": "Description of policy A.",
    "policy_b": "Description of policy B.",
}


def test_report_policies_all_policies_present(capsys: pytest.CaptureFixture[str]) -> None:
    """All policy identifiers and their values appear in output."""
    report_policies(_POLICIES, {"policy_a": "required", "policy_b": "forbidden"})
    out = capsys.readouterr().out
    assert "policy_a" in out
    assert "required" in out
    assert "policy_b" in out
    assert "forbidden" in out


def test_report_policies_optional_value(capsys: pytest.CaptureFixture[str]) -> None:
    """Policy set to optional shows its value on the matching line."""
    report_policies(_POLICIES, {"policy_a": "optional", "policy_b": "required"})
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "policy_a" in line]
    assert matching
    assert "optional" in matching[0]


# ---------------------------------------------------------------------------
# report_options
# ---------------------------------------------------------------------------

_OPTIONS = {
    "option_a": "Description of option A.",
    "option_b": "Description of option B.",
}


def test_report_options_all_options_present(capsys: pytest.CaptureFixture[str]) -> None:
    """All option identifiers and their values appear in output."""
    report_options(_OPTIONS, {"option_a": "true", "option_b": "80"})
    out = capsys.readouterr().out
    assert "option_a" in out
    assert "option_b" in out


def test_report_options_value_on_matching_line(capsys: pytest.CaptureFixture[str]) -> None:
    """Each option value is printed on the line of its option."""
    report_options(_OPTIONS, {"option_a": "false", "option_b": "80"})
    out = capsys.readouterr().out
    matching = [line for line in out.splitlines() if "option_a" in line]
    assert matching
    assert "false" in matching[0]


# ---------------------------------------------------------------------------
# report_overrides
# ---------------------------------------------------------------------------


def test_report_overrides_nothing_printed_when_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """No override declared: nothing is printed."""
    report_overrides([], {})
    assert capsys.readouterr().out == ""


def test_report_overrides_shows_paths_and_delta(capsys: pytest.CaptureFixture[str]) -> None:
    """Override declared: paths, changed values and the base value appear."""
    override = ConfigOverride(paths=["tests/**"], ignore=["imperative_mood"], values={"args_section": Policy.OPTIONAL})
    report_overrides([override], {"args_section": "required"})
    out = capsys.readouterr().out
    assert "tests/**" in out
    assert "imperative_mood" in out
    assert "optional" in out
    assert "(base: required)" in out
