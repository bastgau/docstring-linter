"""Section headers recognized in Google style docstrings.

Shared by the docstring parser and the structure rules, so that both agree on
what a section header is.
"""

import re

# Canonical sections, in the order the section_order rule expects
SECTION_ORDER = [
    "Attributes",
    "Args",
    "Keyword Args",
    "Other Parameters",
    "Returns",
    "Yields",
    "Raises",
    "Examples",
    "Note",
    "Notes",
    "Todo",
]

# Napoleon spellings read as a canonical section and reported by section_alias.
# Note and Notes stay distinct: Napoleon renders the first as an admonition.
SECTION_ALIASES = {
    "Example": "Examples",
    "Arguments": "Args",
    "Parameters": "Args",
    "Keyword Arguments": "Keyword Args",
    "Return": "Returns",
    "Yield": "Yields",
    "Raise": "Raises",
}

# Free-text sections: accepted, content not checked, outside section_order.
# Napoleon reads Warn and Warns like Raises, for warnings: their entries are not checked yet.
FREE_TEXT_SECTIONS = frozenset(
    {
        "Attention",
        "Caution",
        "Danger",
        "Error",
        "Hint",
        "Important",
        "Methods",
        "Receive",
        "Receives",
        "References",
        "See Also",
        "Tip",
        "Warn",
        "Warning",
        "Warnings",
        "Warns",
    }
)

KNOWN_SECTIONS = frozenset(SECTION_ORDER) | frozenset(SECTION_ALIASES) | FREE_TEXT_SECTIONS

# Sections made of 'name (type): description' entries
ENTRY_SECTIONS = frozenset({"Args", "Keyword Args", "Other Parameters", "Attributes", "Raises"})

SECTION_HEADER_RE = re.compile(r"^([A-Za-z]+(?: [A-Za-z]+)*):\s*$")


def canonical_section(name: str) -> str:
    """Return the canonical name of a section, resolving Napoleon aliases.

    Args:
        name (str): Section name as written.

    Returns:
        str: Canonical name, or the name unchanged when it is not an alias.

    """
    return SECTION_ALIASES.get(name, name)


def section_header(line: str) -> str | None:
    """Return the section a docstring line opens, if any.

    Args:
        line (str): Docstring line, indentation included.

    Returns:
        str | None: Section name as written, or None if the line is not a known header.

    """
    match = SECTION_HEADER_RE.match(line.strip())
    if match and match.group(1) in KNOWN_SECTIONS:
        return match.group(1)
    return None
