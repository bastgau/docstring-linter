"""End-to-end tests running lint_file on real sources, AST extraction included."""

import textwrap
from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING

import pytest
from linter.cli import lint_file
from linter.config import LinterConfig, _parse_toml_config  # pyright: ignore[reportPrivateUsage]

if TYPE_CHECKING:
    from linter.models import LintError


def _lint(tmp_path: Path, source: str, config: LinterConfig | None = None) -> list[tuple[str, str]]:
    """Lint a source snippet, with the default config unless one is given, and return (entity, rule) pairs."""
    f = tmp_path / "sample.py"
    f.write_text(textwrap.dedent(source), encoding="utf-8")
    return [(e.entity_name, e.rule) for e in lint_file(str(f), config or LinterConfig())]


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


def test_main_guard_not_linted(tmp_path: Path) -> None:
    """Demo code under 'if __name__ == "__main__":' without docstrings: no error."""
    source = '''\
        """Module."""

        if __name__ == "__main__":

            def demo(value):
                return value

            class Demo:
                pass
        '''
    assert not _lint(tmp_path, source)


def test_variable_raise_not_required_in_raises(tmp_path: Path) -> None:
    """Raise of a variable holding an exception: nothing to document, no error."""
    source = '''\
        """Module."""


        def fail(message: str) -> None:
            """Fail with a message.

            Args:
                message (str): The message.

            Returns:
                None

            """
            error = RuntimeError(message)
            raise error
        '''
    assert not _lint(tmp_path, source)


_GOOGLE_GUIDE_SOURCE = '''\
    """Module."""


    class Cache:
        """Store computed values.

        Attributes:
            size: Number of cached values.
        """

        def __init__(self) -> None:
            """Initialize an empty cache."""
            self.size = 0
            self._store: dict[str, int] = {}

        def fetch(self, key: str, default: int | None = None) -> int | None:
            """Fetches a cached value.

            Args:
                key: Cache key.
                default: Value returned when the key is missing.

            Returns:
                int | None: The cached value, or the default.
            """
            return self._store.get(key, default)

        def clear(self) -> None:
            """Removes every cached value."""
            self._store.clear()
    '''


def test_google_convention_accepts_google_guide_style(tmp_path: Path) -> None:
    """Google guide layout (untyped Args, no Returns: None, descriptive mood): no error under convention google."""
    assert not _lint(tmp_path, _GOOGLE_GUIDE_SOURCE, _parse_toml_config({"convention": "google"}))


def test_strict_convention_rejects_google_guide_style(tmp_path: Path) -> None:
    """Same source under the strict default: the house rules the google convention relaxes are reported."""
    rules = {rule for _, rule in _lint(tmp_path, _GOOGLE_GUIDE_SOURCE)}
    assert {"args_match", "attributes_section", "blank_lines", "imperative_mood", "returns_none"} <= rules


def test_google_convention_accepts_napoleon_types(tmp_path: Path) -> None:
    """Optional parameter documented '(int, optional)', forward reference, untyped Returns: no error under google."""
    source = '''\
        """Module."""

        from typing import Optional


        class Node:
            """Store a node."""

            def resize(self, width: Optional[int] = None, other: "Node | None" = None) -> "Node":
                """Return a resized copy.

                Args:
                    width (int, optional): New width. Defaults to None.
                    other (~Node, optional): Node to copy the height from.

                Returns:
                    The new node: a copy with the requested size.
                """
                return self
        '''
    assert not _lint(tmp_path, source, _parse_toml_config({"convention": "google"}))


def test_strict_convention_reports_implicit_none(tmp_path: Path) -> None:
    """Same kind of source under strict: '(int, optional)' for Optional[int] and the untyped Returns are reported."""
    source = '''\
        """Module."""

        from typing import Optional


        def scale(width: Optional[int] = None) -> int:
            """Scale the width.

            Args:
                width (int, optional): New width.

            Returns:
                The scaled width: twice the input.

            """
            return (width or 0) * 2
        '''
    assert _lint(tmp_path, source) == [("scale", "args_match"), ("scale", "returns_match")]


_PROPAGATED_SOURCE = '''\
    """Module."""


    def parse(value: str) -> int:
        """Parse the value.

        Args:
            value (str): Text to parse.

        Returns:
            int: Parsed value.

        Raises:
            ValueError: Propagated from int() when the text is not a number.

        """
        return int(value)
    '''


def test_propagated_exception_reported_under_strict(tmp_path: Path) -> None:
    """Exception documented but raised by a callee: raises_extraneous under the strict default."""
    assert _lint(tmp_path, _PROPAGATED_SOURCE) == [("parse", "raises_extraneous")]


def test_propagated_exception_accepted_under_google(tmp_path: Path) -> None:
    """Same source under convention google, blank line kept before the quotes: raises_extraneous is off, no error."""
    assert not _lint(tmp_path, _PROPAGATED_SOURCE, _parse_toml_config({"convention": "google", "blank_lines_before_closing_quotes": 1}))


def test_napoleon_sections(tmp_path: Path) -> None:
    """Keyword Args, Warning and See Also: **kwargs documented, no unknown section, no error."""
    source = '''\
        """Module."""


        def configure(**options: int) -> None:
            """Configure the widget.

            Keyword Args:
                width (int): Width in pixels.

            Warning:
                Experimental.

            See Also:
                reset().

            Returns:
                None

            """
        '''
    assert not _lint(tmp_path, source)


def test_parameters_alias(tmp_path: Path) -> None:
    """Parameters instead of Args: arguments count as documented, section_alias is the only error."""
    source = '''\
        """Module."""


        def double(value: int) -> int:
            """Double the value.

            Parameters:
                value (int): The value.

            Returns:
                int: Twice the value.

            """
            return value * 2
        '''
    assert _lint(tmp_path, source) == [("double", "section_alias")]


_EXEMPTIONS_SOURCE = '''\
    """Module."""

    from typing import override


    class Base:
        """Define the base."""

        def run(self) -> int:
            """Run the job.

            Returns:
                int: Result.

            """
            return 0


    class Child(Base):
        """Define the child."""

        def __repr__(self) -> str:
            return "Child"

        def _cache_key(self) -> str:
            return "key"

        @override
        def run(self) -> int:
            return 1

        @property
        def size(self) -> int:
            """The number of items."""
            return 1

        @size.setter
        def size(self, value: int) -> None:
            pass


    def _helper(value):
        return value


    class _Private:
        def method(self):
            pass
    '''


def test_exemptions_off_by_default(tmp_path: Path) -> None:
    """Strict default: dunder, private, overridden and property methods are all checked."""
    errors = _lint(tmp_path, _EXEMPTIONS_SOURCE)
    assert {
        ("Child.__repr__", "docstring_exists"),
        ("Child._cache_key", "docstring_exists"),
        ("Child.run", "docstring_exists"),
        ("Child.size", "returns_section"),
        ("_helper", "docstring_exists"),
        ("_Private.method", "docstring_exists"),
    } <= set(errors)


def test_exemptions_enabled(tmp_path: Path) -> None:
    """All four options on: none of those entities is reported."""
    config = _parse_toml_config({"exclude_dunder_methods": True, "exclude_private": True, "exclude_overridden": True, "properties_as_attributes": True, "ignore": ["return_type_annotation"]})
    assert not _lint(tmp_path, _EXEMPTIONS_SOURCE, config)


def test_exempted_docstring_still_checked(tmp_path: Path) -> None:
    """Dunder with a docstring under exclude_dunder_methods: the docstring content is still checked."""
    source = '''\
        """Module."""


        class Box:
            """Store a value."""

            def __len__(self) -> int:
                """Count the values."""
                return 1
        '''
    assert _lint(tmp_path, source, _parse_toml_config({"exclude_dunder_methods": True})) == [("Box.__len__", "returns_section")]


_CLASS_ARGS = '''\
    """Module."""


    class Cache:
        """Store computed values.

        Args:
            size (int): Maximum number of values.

        """

        def __init__(self, size: int) -> None:
            print(size)
    '''


def test_init_args_in_class_rejected_by_default(tmp_path: Path) -> None:
    """Parameters documented in the class, init_args_location = 'init' (default): __init__ lacks a docstring."""
    assert _lint(tmp_path, _CLASS_ARGS) == [("Cache.__init__", "docstring_exists")]


@pytest.mark.parametrize("location", ["class", "either"])
def test_init_args_in_class_accepted(tmp_path: Path, location: str) -> None:
    """Parameters documented in the class, location class or either: no error."""
    assert not _lint(tmp_path, _CLASS_ARGS, _parse_toml_config({"init_args_location": location}))


def test_init_args_in_class_checked(tmp_path: Path) -> None:
    """Class Args missing a parameter, location either: the parameter is reported on the class."""
    source = _CLASS_ARGS.replace("self, size: int", "self, size: int, ttl: int")
    assert _lint(tmp_path, source, _parse_toml_config({"init_args_location": "either"})) == [("Cache", "args_section")]


def test_init_args_either_falls_back_to_init(tmp_path: Path) -> None:
    """Class without Args, location either: __init__ is checked as usual and needs its docstring."""
    source = _CLASS_ARGS.replace("        Args:\n            size (int): Maximum number of values.\n\n", "")
    assert _lint(tmp_path, source, _parse_toml_config({"init_args_location": "either"})) == [("Cache.__init__", "docstring_exists")]


def test_init_args_short_init_docstring(tmp_path: Path) -> None:
    """__init__ with a docstring but no Args, class with Args, location either: no error."""
    source = _CLASS_ARGS.replace("            print(size)", '            """Create the cache."""\n            print(size)')
    assert not _lint(tmp_path, source, _parse_toml_config({"init_args_location": "either"}))


def test_init_args_mixed(tmp_path: Path) -> None:
    """Args in the class and in __init__, location either: reported as mixed on __init__."""
    init_doc = '            """Create the cache.\n\n            Args:\n                size (int): Maximum.\n\n            """\n            print(size)'
    source = _CLASS_ARGS.replace("            print(size)", init_doc)
    errors = _lint_errors(tmp_path, source, _parse_toml_config({"init_args_location": "either"}))
    assert [(e.entity_name, e.message) for e in errors] == [("Cache.__init__", "Parameters of __init__ are documented both in the class docstring and in '__init__'.")]


def test_init_args_class_location_rejects_init_args(tmp_path: Path) -> None:
    """Args only in __init__, location class: reported on __init__, and missing on the class."""
    init_doc = '            """Create the cache.\n\n            Args:\n                size (int): Maximum.\n\n            """\n            print(size)'
    source = _CLASS_ARGS.replace("        Args:\n            size (int): Maximum number of values.\n\n", "").replace("            print(size)", init_doc)
    errors = _lint_errors(tmp_path, source, _parse_toml_config({"init_args_location": "class"}))
    assert [(e.entity_name, e.rule, e.message) for e in errors] == [
        ("Cache", "args_section", "Arg 'size' in signature but not documented."),
        ("Cache.__init__", "args_section", "Parameters of __init__ must be documented in the class docstring, not in '__init__'."),
    ]


def _lint_errors(tmp_path: Path, source: str, config: LinterConfig) -> list[LintError]:
    """Lint a source snippet and return the full errors, messages included."""
    f = tmp_path / "sample.py"
    f.write_text(textwrap.dedent(source), encoding="utf-8")
    return lint_file(str(f), config)


_ONE_LINERS = '''\
    """Module."""

    from collections.abc import Iterator


    def scale(width: int, factor: int = 2) -> int:
        """Scale a width by a factor."""
        if width < 0:
            raise ValueError(width)
        return width * factor


    def count(limit: int) -> Iterator[int]:
        """Count up to the limit."""
        yield from range(limit)


    def reset(width: int) -> None:
        """Reset the width."""
    '''


def test_one_liners_need_sections_by_default(tmp_path: Path) -> None:
    """One-line docstrings on annotated functions, option off (strict default): every missing section is reported."""
    rules = {rule for _, rule in _lint(tmp_path, _ONE_LINERS)}
    assert {"args_section", "returns_section", "raises_section", "yields_section", "returns_none"} <= rules


def test_one_liners_sections_optional(tmp_path: Path) -> None:
    """Same functions, sections_optional_on_one_liners on: no error."""
    assert not _lint(tmp_path, _ONE_LINERS, _parse_toml_config({"sections_optional_on_one_liners": True}))


def test_one_liner_without_annotations_still_checked(tmp_path: Path) -> None:
    """One-line docstring on a function missing an annotation: sections still required."""
    source = _ONE_LINERS.replace("def scale(width: int, factor: int = 2)", "def scale(width, factor: int = 2)")
    errors = _lint(tmp_path, source, _parse_toml_config({"sections_optional_on_one_liners": True, "ignore": ["return_type_annotation"]}))
    assert ("scale", "args_section") in errors


def test_multi_line_docstring_still_checked(tmp_path: Path) -> None:
    """Docstring with a description but no section: not a one-liner, sections still required."""
    source = _ONE_LINERS.replace('"""Scale a width by a factor."""', '"""Scale a width by a factor.\n\n        Negative widths are rejected.\n\n        """')
    errors = _lint(tmp_path, source, _parse_toml_config({"sections_optional_on_one_liners": True}))
    assert ("scale", "args_section") in errors
