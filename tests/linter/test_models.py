"""Tests for models module."""

from linter.models import LintError, NodeType


def test_lint_error_str() -> None:
    """LintError.__str__ formats as filepath:line: entity_name - [rule] message."""
    error = LintError(
        filepath="src/mymodule.py",
        line=42,
        entity_name="MyClass.my_method",
        node_type=NodeType.METHOD,
        rule="args_match",
        message="Arg 'x' in signature but not documented.",
    )
    assert str(error) == "src/mymodule.py:42: MyClass.my_method - [args_match] Arg 'x' in signature but not documented."
