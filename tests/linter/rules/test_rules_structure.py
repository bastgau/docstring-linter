"""Tests for rules/structure.py -- indentation, section layout, closing quotes, blank lines."""

from linter.models import CodeEntity, NodeType, ParsedDocstring

from linter.rules import validate_entity

from .conftest import _func, _rule_only  # pyright: ignore[reportPrivateUsage]

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
    assert not errors


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
    assert not errors


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
    assert not errors


def test_section_order_unknown_section_ignored() -> None:
    """Unknown section between known sections: order check skips it."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n\nCustom:\n    stuff.\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert not errors


def test_section_order_single_section_ok() -> None:
    """Only one recognized section: no section_order error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("section_order"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => empty_section
# ---------------------------------------------------------------------------


def test_empty_section_detected() -> None:
    """Args section with no content: returns empty_section error."""
    raw = "Summary.\n\nArgs:\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("empty_section"))
    assert any(e.rule == "empty_section" and "Args" in e.message for e in errors)


def test_empty_section_with_content() -> None:
    """Args section with content: no empty_section error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("empty_section"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => blank_line_before_section
# ---------------------------------------------------------------------------


def test_blank_line_before_section_missing() -> None:
    """Section header not preceded by blank line: returns blank_line_before_section error."""
    raw = "Summary.\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("blank_line_before_section"))
    assert any(e.rule == "blank_line_before_section" for e in errors)


def test_blank_line_before_section_present() -> None:
    """Section header preceded by blank line: no error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("blank_line_before_section"))
    assert not errors


def test_blank_line_before_section_first_line_skipped() -> None:
    """Section header on first line of docstring: rule skips it."""
    raw = "Args:\n    x (int): Value.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary=None), _rule_only("blank_line_before_section"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => blank_line_after_section
# ---------------------------------------------------------------------------


def test_blank_line_after_section_missing() -> None:
    """Two consecutive sections without blank line between them: returns blank_line_after_section error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("blank_line_after_section"))
    assert any(e.rule == "blank_line_after_section" for e in errors)


def test_blank_line_after_section_present() -> None:
    """Blank line between sections: no error."""
    raw = "Summary.\n\nArgs:\n    x (int): Value.\n\nReturns:\n    int: Result.\n"
    entity = _func(docstring=raw, raw_docstring=raw)
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("blank_line_after_section"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => closing_quotes_blank_line
# ---------------------------------------------------------------------------


def test_closing_quotes_blank_line_correct() -> None:
    """Exactly one blank line before closing quotes: no error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("closing_quotes_blank_line"))
    assert not errors


def test_closing_quotes_blank_line_missing() -> None:
    """No blank line before closing quotes: returns closing_quotes_blank_line error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("closing_quotes_blank_line"))
    assert any(e.rule == "closing_quotes_blank_line" and "Missing" in e.message for e in errors)


def test_closing_quotes_two_blank_lines() -> None:
    """Two blank lines before closing quotes: returns closing_quotes_blank_line error."""
    entity = _func(docstring="Summary.\n\nDetails.", raw_docstring="Summary.\n\nDetails.\n\n\n    ")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("closing_quotes_blank_line"))
    assert any(e.rule == "closing_quotes_blank_line" and "found 2" in e.message for e in errors)


def test_closing_quotes_one_liner_skipped() -> None:
    """One-liner docstring: closing_quotes_blank_line rule not applied."""
    entity = _func(docstring="Summary.", raw_docstring="Summary.")
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("closing_quotes_blank_line"))
    assert not errors


def test_closing_quotes_module_skipped() -> None:
    """Module entity: closing_quotes_blank_line rule not applied."""
    entity = CodeEntity(
        name="mymodule",
        node_type=NodeType.MODULE,
        line=1,
        filepath="test.py",
        docstring="Summary.\n\nDetails.",
        raw_docstring="Summary.\n\nDetails.\n",
    )
    errors = validate_entity(entity, ParsedDocstring(summary="Summary."), _rule_only("closing_quotes_blank_line"))
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
