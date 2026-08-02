"""Rules related to class attributes documentation."""

from typing import TYPE_CHECKING

from linter.config import Policy

from ._base import make_error

if TYPE_CHECKING:
    from linter.models import CodeEntity, LintError, ParsedDocstring


def check_attributes_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the Attributes section of a class docstring.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None:
        return []

    if policy is Policy.FORBIDDEN:
        if parsed_doc.attributes:
            return [make_error(entity, "attributes_section", "'Attributes:' section is not allowed.")]
        return []

    if policy is Policy.OPTIONAL or not entity.class_attributes:
        return []

    if not parsed_doc.attributes:
        return [make_error(entity, "attributes_section", "Missing 'Attributes:' section in class docstring.")]

    documented = {attr.name for attr in parsed_doc.attributes}
    return [make_error(entity, "attributes_section", f"Attribute '{name}' not documented in 'Attributes:' section.") for name in entity.class_attributes if name not in documented]


def check_attributes_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None, types: Policy) -> list[LintError]:
    """Check documented attributes against the class attributes.

    Only covers what the docstring declares. Undocumented attributes are
    reported by the attributes_section policy.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        types (Policy): Policy for the type between parentheses.

    Returns:
        list[LintError]: Errors for phantom, untyped, or undescribed attributes.

    """
    if parsed_doc is None or not parsed_doc.attributes:
        return []

    actual = set(entity.class_attributes)
    errors: list[LintError] = []

    for attr in parsed_doc.attributes:
        if attr.name not in actual and not attr.name.startswith("__") and not attr.name.isupper():
            errors.append(make_error(entity, "attributes_match", f"Attribute '{attr.name}' documented but not a class attribute."))
        if types is Policy.REQUIRED and not attr.type_annotation:
            errors.append(make_error(entity, "attributes_match", f"Attribute '{attr.name}' missing type in docstring."))
        if types is Policy.FORBIDDEN and attr.type_annotation:
            errors.append(make_error(entity, "attributes_match", f"Attribute '{attr.name}' must not declare a type in docstring."))
        if not attr.description:
            errors.append(make_error(entity, "attributes_match", f"Attribute '{attr.name}' missing description in docstring."))

    return errors
