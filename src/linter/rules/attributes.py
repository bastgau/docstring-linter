"""Rules related to class attributes documentation."""

from typing import TYPE_CHECKING

from ._base import make_error

if TYPE_CHECKING:
    from linter.models import CodeEntity, LintError, ParsedDocstring


def check_attributes_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that class docstring has Attributes section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if Attributes section is missing.

    """
    if parsed_doc is None:
        return []

    if not parsed_doc.attributes:
        return [make_error(entity, "attributes_section", "Missing 'Attributes:' section in class docstring.")]

    errors: list[LintError] = []
    for attr in parsed_doc.attributes:
        if not attr.type_annotation:
            errors.append(make_error(entity, "attributes_section", f"Attribute '{attr.name}' missing type in docstring."))
        if not attr.description:
            errors.append(make_error(entity, "attributes_section", f"Attribute '{attr.name}' missing description in docstring."))

    return errors
