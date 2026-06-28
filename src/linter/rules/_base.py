"""Shared constants and helpers for docstring lint rules."""

import re

from linter.models import CodeEntity, LintError

GOOGLE_SECTIONS = [
    "Args",
    "Returns",
    "Yields",
    "Raises",
    "Example",
    "Examples",
    "Note",
    "Notes",
    "Todo",
    "Attributes",
]

GOOGLE_SECTION_ORDER = [
    "Attributes",
    "Args",
    "Returns",
    "Yields",
    "Raises",
    "Example",
    "Examples",
    "Note",
    "Notes",
    "Todo",
]

SECTION_HEADER_RE = re.compile(r"^([A-Za-z]+):\s*$")


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
    headers: list[str] = []
    for line in docstring.split("\n"):
        match = SECTION_HEADER_RE.match(line.strip())
        if match and match.group(1) in GOOGLE_SECTIONS:
            headers.append(match.group(1))
    return headers
