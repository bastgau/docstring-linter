"""Tests for the type comparison between docstrings and signatures."""

import pytest
from linter.rules._types import types_match  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    ("documented", "signature", "strict", "equivalent", "lenient"),
    [
        # cosmetic differences, accepted at every level
        ("int", "int", True, True, True),
        ("Node", "'Node'", True, True, True),
        ("list[Node]", "list['Node']", True, True, True),
        ("dict[str,int]", "dict[str, int]", True, True, True),
        ("bool, optional", "bool", True, True, True),
        ("~ConsoleOptions", "'ConsoleOptions'", True, True, True),
        # same type, other spelling
        ("str | None", "Optional[str]", False, True, True),
        ("Union[int, str]", "int | str", False, True, True),
        ("typing.Optional[int]", "int | None", False, True, True),
        ("List[int]", "list[int]", False, True, True),
        ("Optional[List[str]]", "list[str] | None", False, True, True),
        # None left implicit in the docstring
        ("int, optional", "Optional[int]", False, False, True),
        ("int | str", "Union[None, int, str]", False, False, True),
        # real differences, reported at every level
        ("int", "str", False, False, False),
        ("int | None", "int", False, False, False),
        ("List[int]", "Iterable[int]", False, False, False),
        ("IO", "IO[str]", False, False, False),
        ("int", "wintypes.WORD", False, False, False),
        # prose is compared as text
        ("list of int", "list[int]", False, False, False),
        ("list of int", "list of int", True, True, True),
    ],
)
def test_types_match(documented: str, signature: str, strict: bool, equivalent: bool, lenient: bool) -> None:  # noqa: FBT001
    """Each level accepts what the previous one accepts, and real differences are always reported."""
    assert types_match(documented, signature, "strict") is strict
    assert types_match(documented, signature, "equivalent") is equivalent
    assert types_match(documented, signature, "lenient") is lenient
