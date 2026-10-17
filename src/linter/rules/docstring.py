"""Rules related to docstring summary and overall presence."""

from typing import TYPE_CHECKING

from linter.config import Policy

from ._base import make_error
from ._verbs import VERBS

if TYPE_CHECKING:
    from linter.models import CodeEntity, LintError, ParsedDocstring

# Third-person forms the suffix rules cannot turn back into the base form
_IRREGULAR_VERBS = {"does": "do", "goes": "go", "undoes": "undo"}


def check_docstring_exists(entity: CodeEntity) -> list[LintError]:
    """Check that docstring is present.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if docstring is missing or empty.

    """
    if entity.docstring is None:
        return [make_error(entity, "docstring_exists", "Missing docstring.")]
    if not entity.docstring.strip():
        return [make_error(entity, "docstring_exists", "Docstring is empty.")]
    return []


def check_summary_exists(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that docstring has a summary line.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if summary is missing.

    """
    if parsed_doc is None or not parsed_doc.summary:
        return [make_error(entity, "summary_exists", "Missing summary line in docstring.")]
    return []


def check_description_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the description paragraph.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None:
        return []

    if policy is Policy.REQUIRED and not parsed_doc.description:
        return [make_error(entity, "description_section", "Missing description below the summary.")]
    if policy is Policy.FORBIDDEN and parsed_doc.description:
        return [make_error(entity, "description_section", "Description below the summary is not allowed.")]
    return []


def check_summary_final_period(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the final period policy to the summary line.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None or not parsed_doc.summary:
        return []

    summary = parsed_doc.summary.rstrip()
    if policy is Policy.REQUIRED and not summary.endswith("."):
        return [make_error(entity, "summary_final_period", f"Summary line must end with a period. Got: '{summary[-20:]}'.")]
    if policy is Policy.FORBIDDEN and summary.endswith("."):
        return [make_error(entity, "summary_final_period", f"Summary line must not end with a period. Got: '{summary[-20:]}'.")]
    return []


def check_summary_on_first_line(entity: CodeEntity, policy: Policy) -> list[LintError]:
    """Apply the summary position policy relative to the opening quotes.

    Args:
        entity (CodeEntity): Entity to check.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if not entity.raw_docstring:
        return []

    on_first_line = not entity.raw_docstring.startswith("\n")
    if policy is Policy.REQUIRED and not on_first_line:
        return [make_error(entity, "summary_on_first_line", 'Summary must start on the same line as opening """.')]
    if policy is Policy.FORBIDDEN and on_first_line:
        return [make_error(entity, "summary_on_first_line", 'Summary must start on the line after opening """.')]
    return []


def _to_imperative(word: str) -> str | None:
    """Convert a third-person verb to imperative form.

    The word is reported only when a base form derived from it is a known
    verb, so that plural nouns such as 'Options' or 'Classes' pass.

    Args:
        word (str): First word of the summary.

    Returns:
        str | None: Imperative form, or None if not a third-person verb.

    """
    lower = word.lower()
    if not lower.isalpha():
        return None

    if lower in _IRREGULAR_VERBS:
        candidates = [_IRREGULAR_VERBS[lower]]
    elif lower.endswith("ies"):
        candidates = [lower[:-3] + "y"]
    elif lower.endswith("es"):
        # 'processes' drops 'es', 'creates' drops 's'
        candidates = [lower[:-2], lower[:-1]]
    elif lower.endswith("s") and not lower.endswith("ss"):
        candidates = [lower[:-1]]
    else:
        return None

    base = next((candidate for candidate in candidates if candidate in VERBS), None)
    if base is None:
        return None
    return base.capitalize() if word[0].isupper() else base


def check_summary_too_long(entity: CodeEntity, parsed_doc: ParsedDocstring | None, max_length: int) -> list[LintError]:
    """Check that summary line does not exceed max_length characters.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        max_length (int): Maximum allowed summary length.

    Returns:
        list[LintError]: Errors if summary exceeds max_length.

    """
    if parsed_doc is None or not parsed_doc.summary:
        return []

    length = len(parsed_doc.summary)
    if length > max_length:
        return [make_error(entity, "summary_too_long", f"Summary line too long ({length} > {max_length} characters).")]
    return []


def check_imperative_mood(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that summary starts with an imperative verb.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if summary uses non-imperative mood.

    """
    if parsed_doc is None or not parsed_doc.summary:
        return []

    first_word = parsed_doc.summary.split()[0]
    imperative = _to_imperative(first_word)

    if imperative is not None:
        return [make_error(entity, "imperative_mood", f"Summary should start with imperative mood. '{first_word}' -> '{imperative}'.")]
    return []


def check_unknown_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check for section names not in the recognized list.

    Args:
        entity (CodeEntity): Code entity being validated.
        parsed_doc (ParsedDocstring | None): Parsed docstring, or None.

    Returns:
        list[LintError]: Errors for each unrecognized section name.

    """
    if parsed_doc is None:
        return []
    return [make_error(entity, "unknown_section", f"Unknown section '{name}'.") for name in parsed_doc.unknown_sections]
