"""Rules related to docstring structure, formatting, and section layout."""

from linter.models import CodeEntity, LintError, NodeType
from linter.rules._base import GOOGLE_SECTION_ORDER, GOOGLE_SECTIONS, SECTION_HEADER_RE, extract_section_headers, make_error

_SECTION_WITH_ENTRIES = frozenset({"Args", "Attributes", "Raises"})


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


def check_blank_line_before_section(entity: CodeEntity) -> list[LintError]:
    """Check that a blank line precedes each section header.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if blank line is missing before a section.

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

        if i == 0:
            continue

        prev_line = lines[i - 1].strip()
        if prev_line != "":
            errors.append(make_error(entity, "blank_line_before_section", f"Missing blank line before '{section_name}:' section."))

    return errors


def check_blank_line_after_section(entity: CodeEntity) -> list[LintError]:
    """Check that sections are separated by blank lines.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if blank line is missing between sections.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    lines = entity.docstring.split("\n")
    section_indices: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        match = SECTION_HEADER_RE.match(line.strip())
        if match and match.group(1) in GOOGLE_SECTIONS:
            section_indices.append((i, match.group(1)))

    for idx in range(len(section_indices) - 1):
        _, current_name = section_indices[idx]
        next_pos, _ = section_indices[idx + 1]

        if next_pos > 0 and lines[next_pos - 1].strip() != "":
            errors.append(make_error(entity, "blank_line_after_section", f"Missing blank line after '{current_name}:' section content."))

    return errors


def check_closing_quotes_blank_line(entity: CodeEntity) -> list[LintError]:
    """Check that multi-line docstrings have one blank line before closing quotes.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if blank line count before closing quotes is not exactly one.

    """
    if not entity.raw_docstring:
        return []

    if entity.node_type == NodeType.MODULE:
        return []

    if "\n" not in entity.raw_docstring:
        return []

    stripped = entity.raw_docstring.rstrip(" \t")
    trailing_newlines = len(stripped) - len(stripped.rstrip("\n"))

    quantity = 2
    if trailing_newlines == quantity:
        return []

    quantity = 1
    msg = 'Missing blank line before closing """.' if trailing_newlines <= quantity else f'Expected exactly one blank line before closing """, found {trailing_newlines - 1}.'

    return [make_error(entity, "closing_quotes_blank_line", msg)]


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
