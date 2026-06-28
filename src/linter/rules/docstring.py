"""Rules related to docstring summary and overall presence."""

from typing import TYPE_CHECKING

from ._base import make_error

if TYPE_CHECKING:
    from linter.models import CodeEntity, LintError, ParsedDocstring

_IMPERATIVE_EXCEPTIONS = frozenset(
    {
        "this",
        "its",
        "has",
        "was",
        "is",
        "alias",
        "unless",
        "class",
        "less",
        "pass",
        "across",
        "process",
        "access",
        "address",
        "express",
        "progress",
        "success",
        "stress",
        "bonus",
        "bus",
        "plus",
        "focus",
        "status",
        "synopsis",
        "basis",
        "analysis",
        "hypothesis",
        "diagnosis",
        "consensus",
        "opus",
        "corpus",
        "terminus",
        "axis",
    }
)


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


def check_summary_punctuation(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that summary line ends with a period.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if period is missing.

    """
    if parsed_doc is None or not parsed_doc.summary:
        return []

    summary = parsed_doc.summary.rstrip()
    if not summary.endswith("."):
        return [make_error(entity, "summary_punctuation", f"Summary line must end with a period. Got: '{summary[-20:]}'.")]
    return []


def check_summary_first_line(entity: CodeEntity) -> list[LintError]:
    """Check that summary starts on the same line as opening triple quotes.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if summary is not on the first line.

    """
    if not entity.raw_docstring:
        return []

    if entity.raw_docstring.startswith("\n"):
        return [make_error(entity, "summary_first_line", 'Summary must start on the same line as opening """.')]
    return []


def _to_imperative(word: str) -> str | None:
    """Convert a third-person verb to imperative form.

    Args:
        word (str): Verb to convert.

    Returns:
        str | None: Imperative form, or None if not a third-person verb.

    """
    lower = word.lower()

    if lower in _IMPERATIVE_EXCEPTIONS:
        return None

    quantity = 4
    if lower.endswith("ies") and len(lower) > quantity:
        return word[:-3] + "y"

    if lower.endswith(("ches", "shes", "sses", "xes", "zes")):
        return word[:-2]

    quantity = 3
    if lower.endswith("es") and len(lower) > quantity and lower[-3] not in "aeiou":
        return word[:-1]

    if lower.endswith("s") and not lower.endswith(("ss", "us", "is", "os", "ws")) and len(lower) > quantity:
        return word[:-1]

    return None


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
