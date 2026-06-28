"""Tests for rules/attributes.py -- class Attributes section."""

from linter.models import DocstringAttribute

from linter.rules import validate_entity

from .conftest import _class, _rule_only  # pyright: ignore[reportPrivateUsage]


def test_attributes_section_missing() -> None:
    """Class with no Attributes section: returns attributes_section error."""
    entity, doc = _class()
    doc.attributes = []
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert any(e.rule == "attributes_section" and "Missing" in e.message for e in errors)


def test_attributes_section_missing_type() -> None:
    """Attribute without type in docstring: returns attributes_section error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation=None, description="A value.")]
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert any("missing type" in e.message for e in errors)


def test_attributes_section_missing_description() -> None:
    """Attribute without description in docstring: returns attributes_section error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description=None)]
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert any("missing description" in e.message for e in errors)


def test_attributes_section_correct() -> None:
    """Attribute with type and description: no error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert not errors
