"""Validation rules for the docstring linter.

Cross-reference AST entities with parsed docstrings to detect
missing, incomplete, or incorrectly formatted documentation.
"""

from dataclasses import replace
from typing import TYPE_CHECKING

from linter.config import Policy
from linter.models import CodeEntity, LintError, NodeType, ParsedDocstring
from linter.rules._base import has_args_section, is_placeholder, make_error
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

# Policies requiring a section, lifted on one-line docstrings by sections_optional_on_one_liners
_SECTION_POLICIES = ("args_section", "returns_section", "yields_section", "raises_section", "returns_none", "init_returns_none")


def _sections_optional(entity: CodeEntity, config: LinterConfig) -> bool:
    """Check whether a one-line docstring is enough for a function or method.

    The Google guide omits the sections when the name and the signature say it
    all, so the signature must be fully annotated.

    Args:
        entity (CodeEntity): Entity to check.
        config (LinterConfig): Linter configuration.

    Returns:
        bool: True if the required section policies do not apply to this docstring.

    """
    return (
        config.sections_optional_on_one_liners
        and entity.node_type in (NodeType.FUNCTION, NodeType.METHOD)
        and entity.docstring is not None
        and "\n" not in entity.docstring.strip()
        and entity.return_type is not None
        and all(arg.type_annotation for arg in entity.args)
    )


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


def _init_args_expected_in_class(class_docstring: str | None, config: LinterConfig) -> bool:
    """Check whether the __init__ parameters belong to the class docstring.

    Args:
        class_docstring (str | None): Docstring of the class.
        config (LinterConfig): Linter configuration.

    Returns:
        bool: True under init_args_location 'class', or 'either' when the class has an Args section.

    """
    if config.args_section is Policy.FORBIDDEN or config.init_args_location == "init":
        return False
    return config.init_args_location == "class" or has_args_section(class_docstring)


def _init_args_in_class(entity: CodeEntity, config: LinterConfig) -> bool:
    """Check whether an entity is an __init__ documented by its class docstring.

    Args:
        entity (CodeEntity): Entity to check.
        config (LinterConfig): Linter configuration.

    Returns:
        bool: True if the __init__ docstring is optional and its parameters are checked on the class.

    """
    if entity.node_type is not NodeType.METHOD or not entity.name.endswith(".__init__"):
        return False
    return _init_args_expected_in_class(entity.class_docstring, config)


def _check_args(entity: CodeEntity, parsed_doc: ParsedDocstring | None, config: LinterConfig) -> list[LintError]:
    """Run the rules comparing the Args section with the signature.

    Args:
        entity (CodeEntity): Entity carrying the signature parameters.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        config (LinterConfig): Linter configuration.

    Returns:
        list[LintError]: Errors of args_section, args_match, duplicate_arg and args_order.

    """
    errors = check_args_section(entity, parsed_doc, config.args_section)
    if config.args_section is not Policy.FORBIDDEN:
        errors.extend(check_args_match(entity, parsed_doc, config.documented_types, config.type_matching, config.documented_stars))
    errors.extend(check_duplicate_arg(entity, parsed_doc))
    if config.is_rule_enabled("args_order"):
        errors.extend(check_args_order(entity, parsed_doc))
    return errors


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

    if _sections_optional(entity, config):
        config = replace(config, **{policy: Policy.OPTIONAL for policy in _SECTION_POLICIES if getattr(config, policy) is Policy.REQUIRED})

    init_in_class = _init_args_in_class(entity, config)

    if config.is_rule_enabled("docstring_exists") and not (_is_docstring_optional(entity, config) or init_in_class):
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

        if not init_in_class:
            errors.extend(_check_args(entity, parsed_doc, config))
        elif has_args_section(entity.docstring):
            where = "must be documented in the class docstring, not in '__init__'" if config.init_args_location == "class" else "are documented both in the class docstring and in '__init__'"
            errors.append(make_error(entity, "args_section", f"Parameters of __init__ {where}."))

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
        # the parameters of __init__, when the class docstring documents them
        if entity.init_args is not None and _init_args_expected_in_class(entity.docstring, config):
            errors.extend(_check_args(replace(entity, args=entity.init_args), parsed_doc, config))

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
