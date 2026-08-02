"""Tests for validate_entity special cases -- entity-level guards and disabled rules."""

from linter.models import CodeEntity, NodeType, ParsedDocstring

from linter.rules import validate_entity

from .conftest import _cfg, _func, _rule_only  # pyright: ignore[reportPrivateUsage]


def test_empty_init_method_excluded_when_configured() -> None:
    """Empty __init__ with exclude_empty_init_method=True: no errors even with missing docstring."""
    entity = _func(name="MyClass.__init__", docstring=None, raw_docstring=None, is_empty_init=True)
    cfg = _cfg(exclude_empty_init_method=True)
    errors = validate_entity(entity, None, cfg)
    assert not errors


def test_empty_init_method_not_excluded_when_flag_false() -> None:
    """Empty __init__ with exclude_empty_init_method=False: docstring_exists is still checked."""
    entity = _func(name="MyClass.__init__", docstring=None, raw_docstring=None, is_empty_init=True)
    cfg = _cfg(exclude_empty_init_method=False, enabled_rules=["docstring_exists"])
    errors = validate_entity(entity, None, cfg)
    assert any(e.rule == "docstring_exists" for e in errors)


def test_empty_init_method_docstring_still_checked() -> None:
    """Empty __init__ with exclude_empty_init_method=True: an existing docstring is still checked."""
    entity = _func(name="MyClass.__init__", docstring="initialize", raw_docstring="initialize", is_empty_init=True)
    cfg = _cfg(exclude_empty_init_method=True)
    errors = validate_entity(entity, ParsedDocstring(summary="initialize"), cfg)
    assert any(e.rule == "summary_final_period" for e in errors)


def test_empty_init_module_excluded_when_configured() -> None:
    """Empty __init__.py with exclude_empty_init_module=True: no errors even with missing docstring."""
    entity = CodeEntity(name="__init__", node_type=NodeType.MODULE, line=1, filepath="pkg/__init__.py", is_empty_init_module=True)
    cfg = _cfg(exclude_empty_init_module=True)
    errors = validate_entity(entity, None, cfg)
    assert not errors


def test_empty_init_module_not_excluded_when_flag_false() -> None:
    """Empty __init__.py with exclude_empty_init_module=False: docstring_exists is still checked."""
    entity = CodeEntity(name="__init__", node_type=NodeType.MODULE, line=1, filepath="pkg/__init__.py", is_empty_init_module=True)
    cfg = _cfg(exclude_empty_init_module=False, enabled_rules=["docstring_exists"])
    errors = validate_entity(entity, None, cfg)
    assert any(e.rule == "docstring_exists" for e in errors)


def test_disabled_rule_not_checked() -> None:
    """When all rules are disabled: no error for missing docstring."""
    entity = _func(docstring=None, raw_docstring=None)
    cfg = _cfg(enabled_rules=[])
    errors = validate_entity(entity, None, cfg)
    assert not errors


def test_method_node_type_triggers_function_rules() -> None:
    """METHOD node type: function-level rules like return_type_annotation are applied."""
    entity = _func(return_type=None, node_type=NodeType.METHOD)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("return_type_annotation"))
    assert any(e.rule == "return_type_annotation" for e in errors)


def test_imperative_mood_skipped_for_module() -> None:
    """Module node type: imperative_mood rule is not applied (plural nouns like 'Rules' are valid)."""
    entity = CodeEntity(
        name="mymodule",
        node_type=NodeType.MODULE,
        line=1,
        filepath="test.py",
        docstring="Rules related to something.",
        raw_docstring="Rules related to something.",
    )
    errors = validate_entity(entity, ParsedDocstring(summary="Rules related to something."), _rule_only("imperative_mood"))
    assert not errors
