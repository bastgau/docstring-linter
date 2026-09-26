"""Shared constants and helpers for docstring lint rules."""

from linter.models import CodeEntity, LintError
from linter.sections import section_header


def make_error(entity: CodeEntity, rule: str, message: str) -> LintError:
    """Create a LintError from entity context.

    Args:
        entity (CodeEntity): Source entity for error context.
        rule (str): Rule identifier.
        message (str): Error message.

    Returns:
        LintError: Constructed error object.

    """
    return LintError(
        filepath=entity.filepath,
        line=entity.line,
        entity_name=entity.name,
        node_type=entity.node_type,
        rule=rule,
        message=message,
    )


def is_placeholder(docstring: str) -> bool:
    """Detect ellipsis placeholder docstring.

    Args:
        docstring (str): Raw docstring content.

    Returns:
        bool: True if docstring is \"\"\"...\"\"\".

    """
    return docstring.strip() == "..."


def extract_section_headers(docstring: str) -> list[str]:
    """Extract ordered list of section header names from raw docstring.

    Args:
        docstring (str): Raw docstring text.

    Returns:
        list[str]: Ordered list of section names found.

    """
    return [name for name in map(section_header, docstring.split("\n")) if name]
