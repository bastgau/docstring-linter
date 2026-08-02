"""Tests for rules/attributes.py -- class Attributes section."""

from linter.config import Policy
from linter.models import DocstringAttribute

from linter.rules import validate_entity

from .conftest import _class, _neutral, _policy_only  # pyright: ignore[reportPrivateUsage]


def test_attributes_section_required_missing() -> None:
    """Policy required, class with attributes but no Attributes section: returns an error."""
    entity, doc = _class()
    doc.attributes = []
    errors = validate_entity(entity, doc, _policy_only("attributes_section", Policy.REQUIRED))
    assert any(e.rule == "attributes_section" and "Missing" in e.message for e in errors)


def test_attributes_section_optional_missing() -> None:
    """Policy optional, class with attributes but no Attributes section: no error."""
    entity, doc = _class()
    doc.attributes = []
    errors = validate_entity(entity, doc, _policy_only("attributes_section", Policy.OPTIONAL))
    assert not errors


def test_attributes_section_forbidden_present() -> None:
    """Policy forbidden, Attributes section present: returns an error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _policy_only("attributes_section", Policy.FORBIDDEN))
    assert any(e.rule == "attributes_section" and "not allowed" in e.message for e in errors)


def test_attributes_section_attribute_not_documented() -> None:
    """Policy required, class attribute missing from the section: returns an error."""
    entity, doc = _class(class_attributes=["x", "y"])
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _policy_only("attributes_section", Policy.REQUIRED))
    assert any(e.rule == "attributes_section" and "y" in e.message and "not documented" in e.message for e in errors)


def test_attributes_section_no_attributes_no_error() -> None:
    """Class with no attributes and no Attributes section: no error."""
    entity, doc = _class(class_attributes=[])
    doc.attributes = []
    errors = validate_entity(entity, doc, _policy_only("attributes_section", Policy.REQUIRED))
    assert not errors


def test_attributes_match_missing_type() -> None:
    """Attribute without type in docstring: returns attributes_match error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation=None, description="A value.")]
    errors = validate_entity(entity, doc, _neutral(documented_types=Policy.REQUIRED))
    assert any(e.rule == "attributes_match" and "missing type" in e.message for e in errors)


def test_attributes_match_missing_description() -> None:
    """Attribute without description in docstring: returns attributes_match error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description=None)]
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "attributes_match" and "missing description" in e.message for e in errors)


def test_attributes_match_phantom_documented() -> None:
    """Attribute documented but not a class attribute: returns attributes_match error."""
    entity, doc = _class(class_attributes=["x"])
    doc.attributes = [
        DocstringAttribute(name="x", type_annotation="int", description="A value."),
        DocstringAttribute(name="ghost", type_annotation="str", description="Not real."),
    ]
    errors = validate_entity(entity, doc, _neutral(enabled_rules=["attributes_match"]))
    assert any(e.rule == "attributes_match" and "ghost" in e.message and "not a class attribute" in e.message for e in errors)


def test_attributes_match_checked_when_section_optional() -> None:
    """Policy optional: a documented attribute is still checked."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation=None, description="A value.")]
    cfg = _neutral(attributes_section=Policy.OPTIONAL, documented_types=Policy.REQUIRED)
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "attributes_match" and "missing type" in e.message for e in errors)


def test_attributes_section_correct() -> None:
    """Attribute with type and description: no error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _neutral(enabled_rules=["attributes_match"], attributes_section=Policy.REQUIRED))
    assert not errors


def test_attributes_match_type_forbidden() -> None:
    """Policy forbidden, attribute documented with a type: returns attributes_match error."""
    entity, doc = _class()
    doc.attributes = [DocstringAttribute(name="x", type_annotation="int", description="A value.")]
    errors = validate_entity(entity, doc, _neutral(documented_types=Policy.FORBIDDEN))
    assert any(e.rule == "attributes_match" and "must not declare a type" in e.message for e in errors)
