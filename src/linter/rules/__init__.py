"""Validation rules for the docstring linter.

Cross-reference AST entities with parsed docstrings to detect
missing, incomplete, or incorrectly formatted documentation.
"""

from typing import TYPE_CHECKING

from linter.models import CodeEntity, LintError, NodeType, ParsedDocstring
from linter.rules._base import GOOGLE_SECTION_ORDER, GOOGLE_SECTIONS, is_placeholder, make_error
from linter.rules.args import (
    check_allow_oneliner,
    check_args_match,
    check_duplicate_arg,
    check_forbid_init_returns_none,
    check_param_order,
    check_raises_match,
    check_return_type_annotation,
    check_returns_section,
    check_returns_type_match,
    check_yields_section,
)
from linter.rules.attributes import check_attributes_section
from linter.rules.docstring import (
    check_docstring_exists,
    check_imperative_mood,
    check_summary_exists,
    check_summary_first_line,
    check_summary_punctuation,
    check_summary_too_long,
    check_unknown_section,
)
from linter.rules.structure import (
    check_blank_line_after_section,
    check_blank_line_before_section,
    check_closing_quotes_blank_line,
    check_empty_section,
    check_indentation,
    check_no_blank_line_in_section,
    check_section_capitalization,
    check_section_order,
)

if TYPE_CHECKING:
    from linter.config import LinterConfig

__all__ = [
    "GOOGLE_SECTIONS",
    "GOOGLE_SECTION_ORDER",
    "validate_entity",
]


def validate_entity(  # noqa: C901, PLR0912, PLR0915 # pylint: disable=too-many-branches,too-many-statements
    entity: CodeEntity,
    parsed_doc: ParsedDocstring | None,
    config: LinterConfig,
) -> list[LintError]:
    """Run all applicable rules on a code entity.

    Args:
        entity (CodeEntity): Parsed code entity to validate.
        parsed_doc (ParsedDocstring | None): Parsed docstring, or None.
        config (LinterConfig): Linter configuration.

    Returns:
        list[LintError]: List of validation errors found.

    """
    errors: list[LintError] = []

    if entity.is_empty_init and config.exclude_empty_init:
        return errors

    if config.is_rule_enabled("docstring_exists"):
        errors.extend(check_docstring_exists(entity))

    if not entity.docstring or not entity.docstring.strip():
        return errors

    if is_placeholder(entity.docstring):
        if config.ignore_placeholder_docstrings:
            return []
        return [make_error(entity, "docstring_exists", f"Placeholder docstring: '{entity.docstring.strip()}'.")]

    if config.is_rule_enabled("summary_exists"):
        errors.extend(check_summary_exists(entity, parsed_doc))

    if config.is_rule_enabled("summary_punctuation"):
        errors.extend(check_summary_punctuation(entity, parsed_doc))

    if config.is_rule_enabled("summary_too_long"):
        errors.extend(check_summary_too_long(entity, parsed_doc, config.summary_max_length))

    if entity.node_type in (NodeType.FUNCTION, NodeType.METHOD):
        if config.is_rule_enabled("return_type_annotation"):
            errors.extend(check_return_type_annotation(entity))

        if config.is_rule_enabled("args_match"):
            errors.extend(check_args_match(entity, parsed_doc))

        if config.is_rule_enabled("duplicate_arg"):
            errors.extend(check_duplicate_arg(entity, parsed_doc))

        if config.is_rule_enabled("param_order"):
            errors.extend(check_param_order(entity, parsed_doc))

        if config.is_rule_enabled("returns_section"):
            errors.extend(check_returns_section(entity, parsed_doc))

        if config.is_rule_enabled("returns_type_match"):
            errors.extend(check_returns_type_match(entity, parsed_doc))

        errors.extend(check_forbid_init_returns_none(entity, parsed_doc, config))
        errors.extend(check_allow_oneliner(entity, parsed_doc, config))

        if config.is_rule_enabled("raises_match"):
            errors.extend(check_raises_match(entity, parsed_doc))

        if config.is_rule_enabled("yields_section"):
            errors.extend(check_yields_section(entity, parsed_doc))

    if entity.node_type == NodeType.CLASS and config.is_rule_enabled("attributes_section"):
        errors.extend(check_attributes_section(entity, parsed_doc))

    if config.is_rule_enabled("indentation"):
        errors.extend(check_indentation(entity))

    if config.is_rule_enabled("section_capitalization"):
        errors.extend(check_section_capitalization(entity))

    if config.is_rule_enabled("section_order"):
        errors.extend(check_section_order(entity))

    if config.is_rule_enabled("unknown_section"):
        errors.extend(check_unknown_section(entity, parsed_doc))

    if config.is_rule_enabled("empty_section"):
        errors.extend(check_empty_section(entity))

    if config.is_rule_enabled("blank_line_before_section"):
        errors.extend(check_blank_line_before_section(entity))

    if config.is_rule_enabled("blank_line_after_section"):
        errors.extend(check_blank_line_after_section(entity))

    if config.is_rule_enabled("imperative_mood") and entity.node_type != NodeType.MODULE:
        errors.extend(check_imperative_mood(entity, parsed_doc))

    if config.is_rule_enabled("summary_first_line"):
        errors.extend(check_summary_first_line(entity))

    if config.is_rule_enabled("closing_quotes_blank_line"):
        errors.extend(check_closing_quotes_blank_line(entity))

    if config.is_rule_enabled("no_blank_line_in_section"):
        errors.extend(check_no_blank_line_in_section(entity))

    return errors
