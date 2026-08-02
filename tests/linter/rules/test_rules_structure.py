"""Tests for rules/structure.py -- indentation, section layout, closing quotes, blank lines."""

from linter.config import Policy
from linter.models import CodeEntity, NodeType, ParsedDocstring

from linter.rules import validate_entity

from .conftest import _cfg, _func, _neutral, _policy_only, _rule_only  # pyright: ignore[reportPrivateUsage]

# ---------------------------------------------------------------------------
# Rule => indentation
# ---------------------------------------------------------------------------


def test_indentation_inconsistent() -> None:
    """More than 2 indent levels in docstring: returns indentation error."""
    raw = "Summary.\n\nArgs:\n    x: Value.\n        continuation.\n            deep.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("indentation"))
    assert any(e.rule == "indentation" for e in errors)


def test_indentation_consistent() -> None:
    """Normal Google-style docstring with 2 levels: no indentation error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("indentation"))
    assert not any(e.rule == "indentation" for e in errors)


def test_indentation_one_liner_skipped() -> None:
    """One-liner docstring: indentation rule skips it, no error."""
    entity = _func(docstring="Do something.", raw_docstring="Do something.")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("indentation"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => section_capitalization
# ---------------------------------------------------------------------------


def test_section_capitalization_wrong() -> None:
    """Lowercase section header 'args:': returns section_capitalization error."""
    raw = "Summary.\n\nargs:\n    x: Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_capitalization"))
    assert any(e.rule == "section_capitalization" for e in errors)


def test_section_capitalization_correct() -> None:
    """Correctly capitalized section 'Args:': no error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_capitalization"))
    assert not any(e.rule == "section_capitalization" for e in errors)


# ---------------------------------------------------------------------------
# Rule => section_order
# ---------------------------------------------------------------------------


def test_section_order_wrong() -> None:
    """Returns before Args: returns section_order error."""
    raw = "Summary.\n\nReturns:\n    int: Result.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert any(e.rule == "section_order" for e in errors)


def test_section_order_correct() -> None:
    """Args before Returns: no section_order error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert not any(e.rule == "section_order" for e in errors)


def test_section_order_unknown_section_ignored() -> None:
    """Unknown section between known sections: order check skips it."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n\nCustom:\n    stuff.\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert not any(e.rule == "section_order" for e in errors)


def test_section_order_single_section_ok() -> None:
    """Only one recognized section: no section_order error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert not any(e.rule == "section_order" for e in errors)


# ---------------------------------------------------------------------------
# Rule => empty_section
# ---------------------------------------------------------------------------


def test_empty_section_detected() -> None:
    """Args section with no content: returns empty_section error."""
    raw = "Summary.\n\nArgs:\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("empty_section"))
    assert any(e.rule == "empty_section" and "Args" in e.message for e in errors)


def test_empty_section_cannot_be_disabled() -> None:
    """Rule listed in ignore: the empty section is still reported, the rule is always on."""
    raw = "Summary.\n\nArgs:\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "empty_section" for e in errors)


def test_empty_section_with_content() -> None:
    """Args section with content: no empty_section error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("empty_section"))
    assert not any(e.rule == "empty_section" for e in errors)


# ---------------------------------------------------------------------------
# Rule => blank_lines
# ---------------------------------------------------------------------------

_TWO_SECTIONS = "Summary.\n\nArgs:\n    x (int): Value.\n\nReturns:\n    int: Result.\n"
_NO_GAP = "Summary.\nArgs:\n    x (int): Value.\nReturns:\n    int: Result.\n"


def test_blank_lines_after_summary_missing() -> None:
    """Description glued to the summary: returns blank_lines error."""
    raw = "Summary.\nDescription here.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "blank_lines" and "between the summary and the description, found 0" in e.message for e in errors)


def test_blank_lines_after_summary_present() -> None:
    """One blank line between summary and description: no blank_lines error."""
    raw = "Summary.\n\nDescription here.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "blank_lines" for e in errors)


def test_blank_lines_after_summary_too_many() -> None:
    """Two blank lines between summary and description: returns blank_lines error."""
    raw = "Summary.\n\n\nDescription here.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "blank_lines" and "found 2" in e.message for e in errors)


def test_blank_lines_after_summary_only_summary() -> None:
    """Docstring limited to a summary: the gap is not checked."""
    raw = "Summary.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "blank_lines" for e in errors)


def test_blank_lines_after_summary_section_follows() -> None:
    """Summary followed by a section header: governed by blank_lines_before_section only."""
    raw = "Summary.\nArgs:\n    x (int): Value.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    cfg = _neutral(blank_lines_before_section=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert not any(e.rule == "blank_lines" for e in errors)


def test_blank_lines_before_section_default_missing() -> None:
    """Default of 1, no blank line before a section header: returns blank_lines error."""
    entity = _func(docstring=_NO_GAP, raw_docstring=_NO_GAP)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert any(e.rule == "blank_lines" and "Expected 1 blank line before 'Args:' section, found 0" in e.message for e in errors)


def test_blank_lines_before_section_default_present() -> None:
    """Default of 1, one blank line before each section header: no error."""
    entity = _func(docstring=_TWO_SECTIONS, raw_docstring=_TWO_SECTIONS)
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert not errors


def test_blank_lines_before_section_zero() -> None:
    """Configured to 0, no blank line before a section header: no error."""
    entity = _func(docstring=_NO_GAP, raw_docstring=_NO_GAP)
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_section=0, blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert not errors


def test_blank_lines_before_section_zero_but_gap_present() -> None:
    """Configured to 0, a blank line before a section header: returns blank_lines error."""
    entity = _func(docstring=_TWO_SECTIONS, raw_docstring=_TWO_SECTIONS)
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_section=0, blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert any(e.rule == "blank_lines" and "found 1" in e.message for e in errors)


def test_blank_lines_before_section_two() -> None:
    """Configured to 2, only one blank line before a section header: returns blank_lines error."""
    entity = _func(docstring=_TWO_SECTIONS, raw_docstring=_TWO_SECTIONS)
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_section=2, blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert any(e.rule == "blank_lines" and "Expected 2 blank lines" in e.message for e in errors)


def test_blank_lines_section_on_first_line_skipped() -> None:
    """Section header on the first line of the docstring: not counted."""
    raw = "Args:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary=None), cfg)
    assert not any(e.rule == "blank_lines" for e in errors)


def test_blank_lines_before_closing_quotes_default_missing() -> None:
    """Default of 1, no blank line before the closing quotes: returns blank_lines error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert any(e.rule == "blank_lines" and 'before closing """, found 0' in e.message for e in errors)


def test_blank_lines_before_closing_quotes_default_present() -> None:
    """Default of 1, one blank line before the closing quotes: no error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert not errors


def test_blank_lines_before_closing_quotes_too_many() -> None:
    """Default of 1, two blank lines before the closing quotes: returns blank_lines error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n\n\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert any(e.rule == "blank_lines" and "found 2" in e.message for e in errors)


def test_blank_lines_before_closing_quotes_zero() -> None:
    """Configured to 0, no blank line before the closing quotes: no error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n    ")
    cfg = _neutral(enabled_rules=["blank_lines"], blank_lines_before_closing_quotes=0)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), cfg)
    assert not errors


def test_no_blank_line_in_section_cannot_be_disabled() -> None:
    """Rule listed in ignore: the blank line between entries is still reported, the rule is always on."""
    raw = "Summary.\n\nArgs:\n    x (int): First.\n\n    y (str): Second.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "no_blank_line_in_section" for e in errors)


def test_blank_lines_cannot_be_disabled() -> None:
    """Rule listed in ignore: a wrong blank line count is still reported, the rule is always on."""
    entity = _func(docstring=_NO_GAP, raw_docstring=_NO_GAP)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "blank_lines" for e in errors)


def test_blank_lines_one_liner_skipped() -> None:
    """One-liner docstring: the closing quotes count is not checked."""
    entity = _func(docstring="Summary.", raw_docstring="Summary.")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert not errors


def test_blank_lines_module_skipped() -> None:
    """Module entity: the closing quotes count is not checked."""
    entity = CodeEntity(
        name="mymodule",
        node_type=NodeType.MODULE,
        line=1,
        filepath="test.py",
        docstring="Summary.\n\nDetails.",
        raw_docstring="Summary.\n\nDetails.\n",
    )
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral(enabled_rules=["blank_lines"]))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => no_blank_line_in_section
# ---------------------------------------------------------------------------


def test_no_blank_line_in_args_section() -> None:
    """Blank line between two Args entries: returns no_blank_line_in_section error."""
    doc = "Summary.\n\nArgs:\n    x (int): First.\n\n    y (int): Second.\n\n    "
    entity = _func(docstring=doc, raw_docstring=doc)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("no_blank_line_in_section"))
    assert any(e.rule == "no_blank_line_in_section" and "Args" in e.message for e in errors)


def test_no_blank_line_in_raises_section() -> None:
    """Blank line between two Raises entries: returns no_blank_line_in_section error."""
    doc = "Summary.\n\nRaises:\n    ValueError: Bad.\n\n    TypeError: Wrong.\n\n    "
    entity = _func(docstring=doc, raw_docstring=doc)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("no_blank_line_in_section"))
    assert any(e.rule == "no_blank_line_in_section" and "Raises" in e.message for e in errors)


def test_no_blank_line_in_attributes_section() -> None:
    """Blank line between two Attributes entries: returns no_blank_line_in_section error."""
    doc = "A class.\n\nAttributes:\n    x (int): First.\n\n    y (str): Second.\n\n    "
    entity = _func(docstring=doc, raw_docstring=doc, node_type=NodeType.CLASS)
    errors = validate_entity(entity, ParsedDocstring(summary="A class."), _rule_only("no_blank_line_in_section"))
    assert any(e.rule == "no_blank_line_in_section" and "Attributes" in e.message for e in errors)


def test_no_blank_line_in_section_correct() -> None:
    """No blank lines between Args entries: no error."""
    doc = "Summary.\n\nArgs:\n    x (int): First.\n    y (int): Second.\n\n    "
    entity = _func(docstring=doc, raw_docstring=doc)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("no_blank_line_in_section"))
    assert not errors


def test_no_blank_line_in_example_ignored() -> None:
    """Blank line inside Example section: not flagged (rule only applies to Args/Attributes/Raises)."""
    doc = "Summary.\n\nExample:\n    >>> f(1)\n\n    >>> f(2)\n\n    "
    entity = _func(docstring=doc, raw_docstring=doc)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("no_blank_line_in_section"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => entry_spacing
# ---------------------------------------------------------------------------


def _entry(line: str) -> str:
    """Build a docstring whose Args section holds a single entry."""
    return f"Summary.\n\nArgs:\n    {line}\n\n"


def test_entry_spacing_canonical() -> None:
    """Entry written 'name (type): description': no error."""
    raw = _entry("value (str): A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_missing_space_before_parenthesis() -> None:
    """Entry written 'name(type): description': returns entry_spacing error."""
    raw = _entry("value(str): A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "entry_spacing" and "value (str): description" in e.message for e in errors)


def test_entry_spacing_space_before_colon() -> None:
    """Entry written 'name (type) : description': returns entry_spacing error."""
    raw = _entry("value (str) : A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_no_space_after_colon() -> None:
    """Entry written 'name (type):description': returns entry_spacing error."""
    raw = _entry("value (str):A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_missing_colon() -> None:
    """Entry written 'name (type)' without its colon: returns entry_spacing error."""
    raw = _entry("value (str)")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "entry_spacing" and "value (str): description" in e.message for e in errors)


def test_entry_spacing_untyped_entry() -> None:
    """Entry without a type: the canonical form drops the parenthesis."""
    raw = _entry("value : A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert any(e.rule == "entry_spacing" and "value: description" in e.message for e in errors)


def test_entry_spacing_starred_entry() -> None:
    """Starred entry written canonically: no error."""
    raw = _entry("**opts (object): Options.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_ignores_continuation_lines() -> None:
    """Continuation line of a description: not read as an entry."""
    raw = "Summary.\n\nArgs:\n    value (str): A value that\n        wraps here.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_ignores_other_sections() -> None:
    """Returns section content: not read as an entry."""
    raw = "Summary.\n\nReturns:\n    int:A result.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
    assert not any(e.rule == "entry_spacing" for e in errors)


def test_entry_spacing_cannot_be_disabled() -> None:
    """Rule listed in ignore: the bad spacing is still reported, the rule is always on."""
    raw = _entry("value(str): A value.")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _cfg(enabled_rules=[]))
    assert any(e.rule == "entry_spacing" for e in errors)


# ---------------------------------------------------------------------------
# Policies => examples_section, notes_section, todo_section
# ---------------------------------------------------------------------------


def _with_section(header: str) -> str:
    """Build a docstring holding a single named section."""
    return f"Summary.\n\n{header}:\n    Content.\n\n"


def test_examples_section_required_missing() -> None:
    """Policy required, no Example section: returns examples_section error."""
    raw = "Summary.\n\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _policy_only("examples_section", Policy.REQUIRED))
    assert any(e.rule == "examples_section" and "Missing 'Example:'" in e.message for e in errors)


def test_examples_section_required_present_plural() -> None:
    """Policy required, an Examples section: the plural spelling is accepted."""
    raw = _with_section("Examples")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _policy_only("examples_section", Policy.REQUIRED))
    assert not any(e.rule == "examples_section" for e in errors)


def test_examples_section_forbidden_present() -> None:
    """Policy forbidden, an Example section: returns examples_section error."""
    raw = _with_section("Example")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _policy_only("examples_section", Policy.FORBIDDEN))
    assert any(e.rule == "examples_section" and "not allowed" in e.message for e in errors)


def test_notes_section_forbidden_present() -> None:
    """Policy forbidden, a Note section: returns notes_section error."""
    raw = _with_section("Note")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _policy_only("notes_section", Policy.FORBIDDEN))
    assert any(e.rule == "notes_section" and "not allowed" in e.message for e in errors)


def test_todo_section_forbidden_present() -> None:
    """Policy forbidden, a Todo section: returns todo_section error."""
    raw = _with_section("Todo")
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _policy_only("todo_section", Policy.FORBIDDEN))
    assert any(e.rule == "todo_section" and "not allowed" in e.message for e in errors)


def test_named_sections_optional_by_default() -> None:
    """Default config: Example, Note and Todo sections are neither required nor rejected."""
    for header in ("Example", "Note", "Todo"):
        raw = _with_section(header)
        entity = _func(docstring=raw, raw_docstring=raw)
        assert not validate_entity(entity, ParsedDocstring(summary="Summary."), _neutral())
