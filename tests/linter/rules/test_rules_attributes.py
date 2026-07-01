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


def test_attributes_section_no_attributes_no_error() -> None:
    """Class with no attributes and no Attributes section: no error."""
    entity, doc = _class(class_attributes=[])
    doc.attributes = []
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert not errors


def test_attributes_section_attribute_not_documented() -> None:
    """Class attribute missing from the Attributes section: returns attributes_section error."""
    entity, doc = _class(class_attributes=["x", "y"])
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert any(e.rule == "attributes_section" and "y" in e.message and "not documented" in e.message for e in errors)


def test_attributes_section_phantom_documented() -> None:
    """Attribute documented but not a class attribute: returns attributes_section error."""
    entity, doc = _class(class_attributes=["x"])
    doc.attributes = [
        DocstringAttribute(name="x", type_annotation="int", description="A value."),
        DocstringAttribute(name="ghost", type_annotation="str", description="Not real."),
    ]
    errors = validate_entity(entity, doc, _rule_only("attributes_section"))
    assert any(e.rule == "attributes_section" and "ghost" in e.message and "not a class attribute" in e.message for e in errors)
