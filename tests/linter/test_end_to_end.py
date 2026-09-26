"""End-to-end tests running lint_file on real sources, AST extraction included."""

import textwrap
from pathlib import Path  # noqa: TC003

from linter.cli import lint_file
from linter.config import LinterConfig


def _lint(tmp_path: Path, source: str) -> list[tuple[str, str]]:
    """Lint a source snippet with the default config and return (entity, rule) pairs."""
    f = tmp_path / "sample.py"
    f.write_text(textwrap.dedent(source), encoding="utf-8")
    return [(e.entity_name, e.rule) for e in lint_file(str(f), LinterConfig())]


def test_nested_generator_does_not_make_outer_a_generator(tmp_path: Path) -> None:
    """Function defining a nested generator: documented with Returns, no error."""
    source = '''\
        """Module."""

        from collections.abc import Iterator


        def outer(values: list[int]) -> list[int]:
            """Return the values.

            Args:
                values (list[int]): Values.

            Returns:
                list[int]: The values.

            """

            def gen() -> Iterator[int]:
                yield from values

            return list(gen())
        '''
    assert not _lint(tmp_path, source)


def test_reraise_of_caught_exception(tmp_path: Path) -> None:
    """Raise err inside 'except ValueError as err': ValueError documented, no error."""
    source = '''\
        """Module."""


        def convert(value: str) -> int:
            """Convert the value.

            Args:
                value (str): The value.

            Returns:
                int: The value.

            Raises:
                ValueError: If the value is invalid.

            """
            try:
                return int(value)
            except ValueError as err:
                raise err
        '''
    assert not _lint(tmp_path, source)


def test_dotted_exception(tmp_path: Path) -> None:
    """Raise errors.ValidationError: documented by short or dotted name, no error."""
    source = '''\
        """Module."""

        import errors


        def short(value: int) -> None:
            """Check the value.

            Args:
                value (int): The value.

            Returns:
                None

            Raises:
                ValidationError: If negative.

            """
            if value < 0:
                raise errors.ValidationError


        def dotted(value: int) -> None:
            """Check the value.

            Args:
                value (int): The value.

            Returns:
                None

            Raises:
                errors.ValidationError: If negative.

            """
            if value < 0:
                raise errors.ValidationError
        '''
    assert not _lint(tmp_path, source)


def test_undocumented_dotted_exception_reported(tmp_path: Path) -> None:
    """Raise errors.ValidationError without Raises section: reported by raises_section."""
    source = '''\
        """Module."""

        import errors


        def check(value: int) -> None:
            """Check the value.

            Args:
                value (int): The value.

            Returns:
                None

            """
            if value < 0:
                raise errors.ValidationError
        '''
    assert _lint(tmp_path, source) == [("check", "raises_section")]


def test_function_under_if_is_linted(tmp_path: Path) -> None:
    """Function defined under an if block: linted like a top-level function."""
    source = '''\
        """Module."""

        import sys

        if sys.version_info >= (3, 12):

            def hidden(value: int) -> int:
                return value
        '''
    assert _lint(tmp_path, source) == [("hidden", "docstring_exists")]


def test_metaclass_first_parameter_not_required(tmp_path: Path) -> None:
    """Metaclass __new__(mcs, ...): mcs is not required in Args."""
    source = '''\
        """Module."""


        class Meta(type):
            """Define the metaclass."""

            def __new__(mcs, name: str, bases: tuple[type, ...], ns: dict[str, object]) -> type:
                """Create the class.

                Args:
                    name (str): Name.
                    bases (tuple[type, ...]): Bases.
                    ns (dict[str, object]): Namespace.

                Returns:
                    type: New class.

                """
                return super().__new__(mcs, name, bases, ns)
        '''
    assert not _lint(tmp_path, source)


def test_staticmethod_first_parameter_required(tmp_path: Path) -> None:
    """@staticmethod: the first parameter must be documented like any other."""
    source = '''\
        """Module."""


        class Tools:
            """Group helpers."""

            @staticmethod
            def double(value: int) -> int:
                """Double the value.

                Returns:
                    int: Twice the value.

                """
                return value * 2
        '''
    assert _lint(tmp_path, source) == [("Tools.double", "args_section")]


def test_overload_stubs_not_linted(tmp_path: Path) -> None:
    """@overload stubs without docstring: only the documented implementation is linted."""
    source = '''\
        """Module."""

        from typing import overload


        @overload
        def conv(x: int) -> int: ...
        @overload
        def conv(x: str) -> str: ...
        def conv(x: int | str) -> int | str:
            """Convert the value.

            Args:
                x (int | str): Value.

            Returns:
                int | str: Converted value.

            """
            return x
        '''
    assert not _lint(tmp_path, source)
