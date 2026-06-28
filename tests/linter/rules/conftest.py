"""Shared helpers for rules tests."""

import copy

from linter.config import LinterConfig
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
) -> tuple[CodeEntity, ParsedDocstring]:
    entity = CodeEntity(
        name=name,
        node_type=NodeType.CLASS,
        line=1,
        filepath="test.py",
        docstring=docstring,
        raw_docstring=raw_docstring,
    )
    doc = parsed_doc or ParsedDocstring(summary="A class.")
    return entity, doc


def _cfg(**kwargs: object) -> LinterConfig:  # pyright: ignore[reportUnusedFunction]
    c = copy.copy(CONFIG)
    for k, v in kwargs.items():
        object.__setattr__(c, k, v)
    return c


def _rule_only(rule: str) -> LinterConfig:  # pyright: ignore[reportUnusedFunction]
    c = copy.copy(CONFIG)
    object.__setattr__(c, "enabled_rules", [rule])
    return c
