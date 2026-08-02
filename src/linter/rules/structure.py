"""Rules related to docstring structure, formatting, and section layout."""

import re

from linter.config import Policy
from linter.models import CodeEntity, LintError, NodeType
from linter.rules._base import GOOGLE_SECTION_ORDER, GOOGLE_SECTIONS, SECTION_HEADER_RE, extract_section_headers, make_error

_SECTION_WITH_ENTRIES = frozenset({"Args", "Attributes", "Raises"})

_ENTRY_LAX = re.compile(r"^\s{4}(\*{0,2}\w+)\s*(\([^)]*\))?\s*:\s*(.*)$")
_ENTRY_LAX_NO_COLON = re.compile(r"^\s{4}(\*{0,2}\w+)\s*(\([^)]+\))\s*$")
_ENTRY_STRICT = re.compile(r"^ {4}\*{0,2}\w+(?: \([^)]*\))?:(?: \S.*)?$")


def check_indentation(entity: CodeEntity) -> list[LintError]:
    """Check docstring indentation consistency.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if indentation is inconsistent.

    """
    if not entity.docstring:
        return []

    lines = entity.docstring.split("\n")
    if len(lines) <= 1:
        return []

    indents: set[int] = set()
    for line in lines[1:]:
        if not line.strip():
            continue
        leading = len(line) - len(line.lstrip())
        indents.add(leading)

    quantity = 2
    if len(indents) > quantity:
        return [make_error(entity, "indentation", "Inconsistent indentation in docstring.")]
    return []


def check_section_capitalization(entity: CodeEntity) -> list[LintError]:
    """Check that section names are properly capitalized.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors for incorrectly capitalized sections.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    lowercase_sections = {s.lower(): s for s in GOOGLE_SECTIONS}

    for line in entity.docstring.split("\n"):
        match = SECTION_HEADER_RE.match(line.strip())
        if not match:
            continue

        section_name = match.group(1)
        lower = section_name.lower()

        if lower in lowercase_sections and section_name != lowercase_sections[lower]:
            expected = lowercase_sections[lower]
            errors.append(make_error(entity, "section_capitalization", f"Section '{section_name}:' should be '{expected}:'."))

    return errors


def check_section_order(entity: CodeEntity) -> list[LintError]:
    """Check that sections appear in the correct order.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if sections are out of order.

    """
    if not entity.docstring:
        return []

    found_sections = extract_section_headers(entity.docstring)
    if len(found_sections) <= 1:
        return []

    order_map = {name: idx for idx, name in enumerate(GOOGLE_SECTION_ORDER)}

    prev_idx = -1
    prev_name = ""
    for section in found_sections:
        idx = order_map.get(section, -1)
        if idx == -1:
            continue
        if idx < prev_idx:
            return [
                make_error(
                    entity,
                    "section_order",
                    f"Section '{section}:' must come before '{prev_name}:'. Expected order: {', '.join(s for s in GOOGLE_SECTION_ORDER if s in found_sections)}.",
                )
            ]
        prev_idx = idx
        prev_name = section

    return []


def check_empty_section(entity: CodeEntity) -> list[LintError]:
    """Check that no section is declared empty.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors for empty sections.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    lines = entity.docstring.split("\n")

    for i, line in enumerate(lines):
        match = SECTION_HEADER_RE.match(line.strip())
        if not match or match.group(1) not in GOOGLE_SECTIONS:
            continue

        section_name = match.group(1)
        has_content = False
        for next_line in lines[i + 1 :]:
            stripped = next_line.strip()
            if not stripped:
                continue
            next_match = SECTION_HEADER_RE.match(stripped)
            if next_match and next_match.group(1) in GOOGLE_SECTIONS:
                break
            has_content = True
            break

        if not has_content:
            errors.append(make_error(entity, "empty_section", f"Section '{section_name}:' is empty."))

    return errors


def _plural(count: int) -> str:
    """Return the singular or plural form of 'blank line'.

    Args:
        count (int): Number of blank lines.

    Returns:
        str: Wording matching the count.

    """
    return "blank line" if count == 1 else "blank lines"


def check_blank_lines(entity: CodeEntity, before_section: int, before_closing_quotes: int) -> list[LintError]:
    """Check the configured number of blank lines in the docstring layout.

    Args:
        entity (CodeEntity): Entity to check.
        before_section (int): Blank lines expected before a section header.
        before_closing_quotes (int): Blank lines expected before the closing quotes.

    Returns:
        list[LintError]: Errors for every gap that does not match.

    """
    return _check_after_summary(entity) + _check_before_sections(entity, before_section) + _check_before_closing_quotes(entity, before_closing_quotes)


def _is_section_header(line: str) -> bool:
    """Check whether a docstring line declares a known section.

    Args:
        line (str): Line to inspect.

    Returns:
        bool: True if the line is a Google section header.

    """
    match = SECTION_HEADER_RE.match(line.strip())
    return match is not None and match.group(1) in GOOGLE_SECTIONS


def _check_after_summary(entity: CodeEntity) -> list[LintError]:
    """Check the single blank line separating the summary from the description.

    The count is fixed at one: the description carries no header, so a
    smaller gap makes the boundary disappear. Docstrings whose summary is
    followed by nothing, or directly by a section header, are not concerned.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Error if the description does not follow one blank line.

    """
    if not entity.docstring:
        return []

    lines = entity.docstring.split("\n")
    summary = next((i for i, line in enumerate(lines) if line.strip()), None)
    if summary is None or _is_section_header(lines[summary]):
        return []

    found = 0
    for line in lines[summary + 1 :]:
        if line.strip():
            break
        found += 1
    else:
        return []

    if _is_section_header(lines[summary + 1 + found]):
        return []

    if found != 1:
        return [make_error(entity, "blank_lines", f"Expected 1 blank line between the summary and the description, found {found}.")]
    return []


def _check_before_sections(entity: CodeEntity, expected: int) -> list[LintError]:
    """Check the number of blank lines preceding each section header.

    Args:
        entity (CodeEntity): Entity to check.
        expected (int): Blank lines expected before a section header.

    Returns:
        list[LintError]: Errors for every section header with a wrong gap.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    lines = entity.docstring.split("\n")

    for i, line in enumerate(lines):
        match = SECTION_HEADER_RE.match(line.strip())
        if not match or match.group(1) not in GOOGLE_SECTIONS or i == 0:
            continue

        found = 0
        while found < i and lines[i - 1 - found].strip() == "":
            found += 1

        if found != expected:
            errors.append(make_error(entity, "blank_lines", f"Expected {expected} {_plural(expected)} before '{match.group(1)}:' section, found {found}."))

    return errors


def _check_before_closing_quotes(entity: CodeEntity, expected: int) -> list[LintError]:
    """Check the number of blank lines preceding the closing triple quotes.

    Args:
        entity (CodeEntity): Entity to check.
        expected (int): Blank lines expected before the closing quotes.

    Returns:
        list[LintError]: Error if the gap does not match.

    """
    if not entity.raw_docstring or entity.node_type == NodeType.MODULE or "\n" not in entity.raw_docstring:
        return []

    stripped = entity.raw_docstring.rstrip(" \t")
    found = len(stripped) - len(stripped.rstrip("\n")) - 1

    if found != expected:
        return [make_error(entity, "blank_lines", f'Expected {expected} {_plural(expected)} before closing """, found {found}.')]
    return []


def check_named_section(entity: CodeEntity, names: tuple[str, ...], policy: Policy, rule: str) -> list[LintError]:
    """Apply a presence policy to a section identified by its header.

    Args:
        entity (CodeEntity): Entity to check.
        names (tuple[str, ...]): Accepted spellings of the header.
        policy (Policy): Policy to apply.
        rule (str): Rule identifier carrying the error.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if not entity.docstring or policy is Policy.OPTIONAL:
        return []

    found = [name for name in extract_section_headers(entity.docstring) if name in names]

    if policy is Policy.REQUIRED and not found:
        return [make_error(entity, rule, f"Missing '{names[0]}:' section.")]
    if policy is Policy.FORBIDDEN and found:
        return [make_error(entity, rule, f"'{found[0]}:' section is not allowed.")]
    return []


def check_entry_spacing(entity: CodeEntity) -> list[LintError]:
    """Check the spacing of every entry in Args, Attributes, and Raises.

    The canonical form is 'name (type): description', with one space before
    the parenthesis, none before the colon, and one after it.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors for every entry written differently.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    current_section: str | None = None

    for line in entity.docstring.split("\n"):
        match = SECTION_HEADER_RE.match(line.strip())
        if match and match.group(1) in GOOGLE_SECTIONS:
            current_section = match.group(1)
            continue

        if current_section not in _SECTION_WITH_ENTRIES:
            continue

        entry = _ENTRY_LAX.match(line) or _ENTRY_LAX_NO_COLON.match(line)
        if entry is None or _ENTRY_STRICT.match(line.rstrip()):
            continue

        canonical = f"{entry.group(1)} {entry.group(2)}:" if entry.group(2) else f"{entry.group(1)}:"
        errors.append(make_error(entity, "entry_spacing", f"Entry '{entry.group(1)}' in '{current_section}:' must be written '{canonical} description'."))

    return errors


def check_no_blank_line_in_section(entity: CodeEntity) -> list[LintError]:
    """Check that no blank lines appear between entries in Args, Attributes, or Raises.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if blank lines are found inside a section.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    lines = entity.docstring.split("\n")
    current_section: str | None = None
    in_section_content = False
    pending_blank = False

    for line in lines:
        stripped = line.strip()

        match = SECTION_HEADER_RE.match(stripped)
        if match and match.group(1) in GOOGLE_SECTIONS:
            current_section = match.group(1)
            in_section_content = False
            pending_blank = False
            continue

        if current_section not in _SECTION_WITH_ENTRIES:
            pending_blank = False
            continue

        if not stripped:
            if in_section_content:
                pending_blank = True
            continue

        if pending_blank and in_section_content:
            errors.append(make_error(entity, "no_blank_line_in_section", f"Blank line found between entries in '{current_section}:' section."))
            pending_blank = False

        in_section_content = True

    return errors
