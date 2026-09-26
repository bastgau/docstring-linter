"""Validation rules for the docstring linter.

Cross-reference AST entities with parsed docstrings to detect
missing, incomplete, or incorrectly formatted documentation.
"""

from typing import TYPE_CHECKING

from linter.config import Policy
from linter.models import CodeEntity, LintError, NodeType, ParsedDocstring
from linter.rules._base import is_placeholder, make_error
from linter.rules.args import (
    check_args_match,
    check_args_order,
    check_args_section,
    check_duplicate_arg,
    check_init_returns_none,
    check_raises_extraneous,
    check_raises_match,
    check_raises_section,
    check_return_type_annotation,
    check_returns_match,
    check_returns_none,
    check_returns_section,
    check_yields_match,
    check_yields_section,
)
from linter.rules.attributes import check_attributes_match, check_attributes_section
from linter.rules.docstring import (
    check_description_section,
    check_docstring_exists,
    check_imperative_mood,
    check_summary_exists,
    check_summary_final_period,
    check_summary_on_first_line,
    check_summary_too_long,
    check_unknown_section,
)
from linter.rules.structure import (
    check_blank_lines,
    check_empty_section,
    check_entry_spacing,
    check_indentation,
    check_named_section,
    check_no_blank_line_in_section,
    check_section_alias,
    check_section_capitalization,
    check_section_order,
)

if TYPE_CHECKING:
    from linter.config import LinterConfig

__all__ = [
    "validate_entity",
]


_PROPERTY_GETTERS = frozenset({"property", "cached_property"})
_PROPERTY_ACCESSORS = frozenset({"setter", "deleter"})


def _is_docstring_optional(entity: CodeEntity, config: LinterConfig) -> bool:
    """Check whether the options exempt an entity from having a docstring.

    A docstring that is present is still checked, whatever the exemption.

    Args:
        entity (CodeEntity): Entity to check.
        config (LinterConfig): Linter configuration.

    Returns:
        bool: True if a missing docstring must not be reported.

    """
    if entity.node_type is NodeType.MODULE:
        return entity.is_empty_init_module and config.exclude_empty_init_module

    parts = entity.name.split(".")
    is_dunder = parts[-1].startswith("__") and parts[-1].endswith("__")
    # _name and __name are private, __name__ is a magic method
    is_private = any(part.startswith("_") and not (part.startswith("__") and part.endswith("__")) for part in parts)

    return (
        (entity.is_empty_init and config.exclude_empty_init_method)
        or (is_dunder and parts[-1] != "__init__" and config.exclude_dunder_methods)
        or (is_private and config.exclude_private)
        or ("override" in entity.decorators and config.exclude_overridden)
    )


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

    # Sphinx documents a property from its getter, setters and deleters carry nothing to check
    if config.properties_as_attributes and not _PROPERTY_ACCESSORS.isdisjoint(entity.decorators):
        return errors

    is_getter = config.properties_as_attributes and not _PROPERTY_GETTERS.isdisjoint(entity.decorators)

    if config.is_rule_enabled("docstring_exists") and not _is_docstring_optional(entity, config):
        errors.extend(check_docstring_exists(entity))

    if not entity.docstring or not entity.docstring.strip():
        return errors

    if is_placeholder(entity.docstring):
        if config.ignore_placeholder_docstrings:
            return []
        return [make_error(entity, "docstring_exists", f"Placeholder docstring: '{entity.docstring.strip()}'.")]

    errors.extend(check_summary_exists(entity, parsed_doc))

    errors.extend(check_summary_final_period(entity, parsed_doc, config.summary_final_period))

    errors.extend(check_description_section(entity, parsed_doc, config.description_section))

    errors.extend(check_named_section(entity, ("Examples", "Example"), config.examples_section, "examples_section"))
    errors.extend(check_named_section(entity, ("Note", "Notes"), config.notes_section, "notes_section"))
    errors.extend(check_named_section(entity, ("Todo",), config.todo_section, "todo_section"))

    if config.is_rule_enabled("summary_too_long"):
        errors.extend(check_summary_too_long(entity, parsed_doc, config.summary_max_length))

    if entity.node_type in (NodeType.FUNCTION, NodeType.METHOD):
        if config.is_rule_enabled("return_type_annotation"):
            errors.extend(check_return_type_annotation(entity))

        errors.extend(check_args_section(entity, parsed_doc, config.args_section))

        if config.args_section is not Policy.FORBIDDEN:
            errors.extend(check_args_match(entity, parsed_doc, config.documented_types, config.type_matching))

        errors.extend(check_duplicate_arg(entity, parsed_doc))

        if config.is_rule_enabled("args_order"):
            errors.extend(check_args_order(entity, parsed_doc))

        # a property getter is documented like an attribute, without Returns section
        if not is_getter:
            errors.extend(check_returns_section(entity, parsed_doc, config.returns_section))

        if config.returns_section is not Policy.FORBIDDEN:
            errors.extend(check_returns_match(entity, parsed_doc, config.returns_descriptions, config.documented_types, config.type_matching))
            errors.extend(check_returns_none(entity, parsed_doc, config.returns_none))
            errors.extend(check_init_returns_none(entity, parsed_doc, config.init_returns_none))

        errors.extend(check_raises_section(entity, parsed_doc, config.raises_section))

        if config.raises_section is not Policy.FORBIDDEN:
            errors.extend(check_raises_match(entity, parsed_doc))

            if config.is_rule_enabled("raises_extraneous"):
                errors.extend(check_raises_extraneous(entity, parsed_doc))

        errors.extend(check_yields_section(entity, parsed_doc, config.yields_section))

        if config.yields_section is not Policy.FORBIDDEN:
            errors.extend(check_yields_match(entity, parsed_doc, config.returns_descriptions, config.documented_types))

    if entity.node_type == NodeType.CLASS:
        errors.extend(check_attributes_section(entity, parsed_doc, config.attributes_section))

        if config.attributes_section is not Policy.FORBIDDEN:
            errors.extend(check_attributes_match(entity, parsed_doc, config.documented_types))

    if config.is_rule_enabled("indentation"):
        errors.extend(check_indentation(entity))

    if config.is_rule_enabled("section_capitalization"):
        errors.extend(check_section_capitalization(entity))

    if config.is_rule_enabled("section_alias"):
        errors.extend(check_section_alias(entity))

    if config.is_rule_enabled("section_order"):
        errors.extend(check_section_order(entity))

    if config.is_rule_enabled("unknown_section"):
        errors.extend(check_unknown_section(entity, parsed_doc))

    errors.extend(check_empty_section(entity))

    errors.extend(check_blank_lines(entity, config.blank_lines_before_section, config.blank_lines_before_closing_quotes))

    if config.is_rule_enabled("imperative_mood") and entity.node_type in (NodeType.FUNCTION, NodeType.METHOD) and not is_getter:
        errors.extend(check_imperative_mood(entity, parsed_doc))

    errors.extend(check_summary_on_first_line(entity, config.summary_on_first_line))

    errors.extend(check_no_blank_line_in_section(entity))

    errors.extend(check_entry_spacing(entity))

    return errors
