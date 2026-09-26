"""Shared constants and helpers for docstring lint rules."""

from linter.models import CodeEntity, LintError
from linter.sections import canonical_section, section_header


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


def has_args_section(docstring: str | None) -> bool:
    """Check whether a docstring carries an Args section, under any alias.

    Args:
        docstring (str | None): Docstring text, or None.

    Returns:
        bool: True if an Args section header is present.

    """
    return docstring is not None and "Args" in {canonical_section(name) for name in extract_section_headers(docstring)}
