"""Rules related to docstring structure, formatting, and section layout."""

import re

from linter.config import Policy
from linter.models import CodeEntity, LintError, NodeType
from linter.rules._base import extract_section_headers, make_error
from linter.sections import ENTRY_SECTIONS, KNOWN_SECTIONS, SECTION_ALIASES, SECTION_HEADER_RE, SECTION_ORDER, canonical_section, section_header

_SECTION_INDENT = 4

_ENTRY_LAX = re.compile(r"^\s{4}(\*{0,2}\w+)\s*(\([^)]*\))?\s*:\s*(.*)$")
_ENTRY_LAX_NO_COLON = re.compile(r"^\s{4}(\*{0,2}\w+)\s*(\([^)]+\))\s*$")
_ENTRY_STRICT = re.compile(r"^ {4}\*{0,2}\w+(?: \([^)]*\))?:(?: \S.*)?$")


def check_indentation(entity: CodeEntity) -> list[LintError]:
    """Check that the content of each section is indented under its header.

    Inside a section, every line is indented by 4 spaces or more, and the first
    entry of Args, Attributes and Raises by exactly 4. Lines outside sections are
    not checked: a description may hold indented code or lists.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: One error per section whose content is misindented.

    """
    if not entity.docstring:
        return []

    errors: list[LintError] = []
    section: str | None = None
    first_line = False
    reported = False

    for line in entity.docstring.split("\n")[1:]:
        stripped = line.strip()
        if not stripped:
            continue

        indent = len(line) - len(line.lstrip())
        header = section_header(line)
        if indent == 0 and header:
            section, first_line, reported = header, True, False
            continue

        if section and not reported:
            if 0 < indent < _SECTION_INDENT:
                errors.append(make_error(entity, "indentation", f"Line '{stripped[:30]}' in '{section}:' is indented by {indent} spaces, expected at least {_SECTION_INDENT}."))
                reported = True
            elif first_line and _is_entry_section(section) and indent != _SECTION_INDENT:
                errors.append(make_error(entity, "indentation", f"First entry of '{section}:' is indented by {indent} spaces, expected {_SECTION_INDENT}."))
                reported = True
        first_line = False

    return errors


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
    lowercase_sections = {s.lower(): s for s in KNOWN_SECTIONS}

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


def check_section_alias(entity: CodeEntity) -> list[LintError]:
    """Check that sections use their canonical name rather than a Napoleon alias.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors for every section written with an alias.

    """
    if not entity.docstring:
        return []
    return [make_error(entity, "section_alias", f"Section '{name}:' should be written '{SECTION_ALIASES[name]}:'.") for name in extract_section_headers(entity.docstring) if name in SECTION_ALIASES]


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

    order_map = {name: idx for idx, name in enumerate(SECTION_ORDER)}
    canonical_found = {canonical_section(name) for name in found_sections}

    prev_idx = -1
    prev_name = ""
    for section in found_sections:
        # free-text sections have no position
        idx = order_map.get(canonical_section(section), -1)
        if idx == -1:
            continue
        if idx < prev_idx:
            return [
                make_error(
                    entity,
                    "section_order",
                    f"Section '{section}:' must come before '{prev_name}:'. Expected order: {', '.join(s for s in SECTION_ORDER if s in canonical_found)}.",
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
        section_name = section_header(line)
        if section_name is None:
            continue

        has_content = False
        for next_line in lines[i + 1 :]:
            if not next_line.strip():
                continue
            has_content = section_header(next_line) is None
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
    return section_header(line) is not None


def _is_entry_section(name: str | None) -> bool:
    """Check whether a section is made of 'name (type): description' entries.

    Args:
        name (str | None): Section name as written, None outside any section.

    Returns:
        bool: True for Args, Attributes, Raises and their aliases.

    """
    return name is not None and canonical_section(name) in ENTRY_SECTIONS


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
        header = section_header(line)
        if header is None or i == 0:
            continue

        found = 0
        while found < i and lines[i - 1 - found].strip() == "":
            found += 1

        if found != expected:
            errors.append(make_error(entity, "blank_lines", f"Expected {expected} {_plural(expected)} before '{header}:' section, found {found}."))

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

    if found < 0:
        return [make_error(entity, "blank_lines", 'Closing """ must be on its own line.')]
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
        header = section_header(line)
        if header:
            current_section = header
            continue

        if not _is_entry_section(current_section):
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

        header = section_header(line)
        if header:
            current_section = header
            in_section_content = False
            pending_blank = False
            continue

        if not _is_entry_section(current_section):
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
