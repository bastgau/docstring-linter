"""Shared helpers for rules tests."""

import copy

from linter.config import POLICIES_REGISTRY, LinterConfig, Policy
from linter.models import ArgInfo, CodeEntity, NodeType, ParsedDocstring, RaiseInfo

CONFIG = LinterConfig()


def _func(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-positional-arguments # pyright: ignore[reportUnusedFunction]
    name: str = "my_func",
    docstring: str | None = "Do something.",
    raw_docstring: str | None = "Do something.",
    args: list[ArgInfo] | None = None,
    return_type: str | None = None,
    raises: list[RaiseInfo] | None = None,
    node_type: NodeType = NodeType.FUNCTION,
    *,
    is_empty_init: bool = False,
    is_generator: bool = False,
) -> CodeEntity:
    """Build a function or method entity with test defaults.

    Args:
        name (str): Entity name, dotted for a method.
        docstring (str | None): Cleaned docstring.
        raw_docstring (str | None): Raw docstring, indentation included.
        args (list[ArgInfo] | None): Signature arguments.
        return_type (str | None): Return type annotation.
        raises (list[RaiseInfo] | None): Explicit raise statements.
        node_type (NodeType): Function or method.
        is_empty_init (bool): Whether the entity is an empty __init__.
        is_generator (bool): Whether the body contains a yield.

    Returns:
        CodeEntity: Entity ready to feed validate_entity.

    """
    return CodeEntity(
        name=name,
        node_type=node_type,
        line=1,
        filepath="test.py",
        docstring=docstring,
        raw_docstring=raw_docstring,
        args=args or [],
        return_type=return_type,
        raises=raises or [],
        is_empty_init=is_empty_init,
        is_generator=is_generator,
    )


def _class(  # pyright: ignore[reportUnusedFunction]
    name: str = "MyClass",
    docstring: str | None = "A class.",
    raw_docstring: str | None = "A class.",
    parsed_doc: ParsedDocstring | None = None,
    class_attributes: list[str] | None = None,
) -> tuple[CodeEntity, ParsedDocstring]:
    """Build a class entity and its parsed docstring with test defaults.

    Args:
        name (str): Class name.
        docstring (str | None): Cleaned docstring.
        raw_docstring (str | None): Raw docstring, indentation included.
        parsed_doc (ParsedDocstring | None): Parsed docstring to use instead of the default.
        class_attributes (list[str] | None): Attribute names declared on the class.

    Returns:
        tuple[CodeEntity, ParsedDocstring]: Entity and its parsed docstring.

    """
    entity = CodeEntity(
        name=name,
        node_type=NodeType.CLASS,
        line=1,
        filepath="test.py",
        docstring=docstring,
        raw_docstring=raw_docstring,
        class_attributes=class_attributes if class_attributes is not None else ["x"],
    )
    doc = parsed_doc or ParsedDocstring(summary="A class.")
    return entity, doc


def _cfg(**kwargs: object) -> LinterConfig:  # pyright: ignore[reportUnusedFunction]
    """Copy the default config and override the given attributes.

    Args:
        **kwargs (object): Config attributes to override.

    Returns:
        LinterConfig: Config carrying the default values plus the overrides.

    """
    c = copy.copy(CONFIG)
    for k, v in kwargs.items():
        object.__setattr__(c, k, v)
    return c


def _neutral(**kwargs: object) -> LinterConfig:
    """Build a config with every rule off and every policy optional.

    Always-on rules keep reporting, they cannot be disabled.

    Args:
        **kwargs (object): Config attributes to override.

    Returns:
        LinterConfig: Config isolating what the caller enables.

    """
    c = copy.copy(CONFIG)
    object.__setattr__(c, "enabled_rules", [])
    for policy in POLICIES_REGISTRY:
        object.__setattr__(c, policy, Policy.OPTIONAL)
    for k, v in kwargs.items():
        object.__setattr__(c, k, v)
    return c


def _rule_only(rule: str) -> LinterConfig:  # pyright: ignore[reportUnusedFunction]
    """Build a config where a single rule is enabled.

    Args:
        rule (str): Rule identifier to enable.

    Returns:
        LinterConfig: Config with that rule as the only enabled one.

    """
    return _neutral(enabled_rules=[rule])


def _policy_only(policy: str, value: Policy) -> LinterConfig:  # pyright: ignore[reportUnusedFunction]
    """Build a config where a single policy carries a value, every rule off.

    Args:
        policy (str): Policy identifier to set.
        value (Policy): Value to apply.

    Returns:
        LinterConfig: Config isolating that policy.

    """
    return _neutral(**{policy: value})
