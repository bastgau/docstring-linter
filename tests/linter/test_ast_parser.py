"""Tests for ast_parser module."""

import ast
import textwrap
from pathlib import Path  # noqa: TC003

import pytest
from linter.ast_parser import _extract_args, _extract_class_attributes, _is_empty_init, _scan_body, parse_file  # pyright: ignore[reportPrivateUsage]


def _parse_func(source: str) -> ast.FunctionDef:
    """Parse a source snippet and return the first function node."""
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node
    msg = "No function found in source"
    raise ValueError(msg)


def _parse_class(source: str) -> ast.ClassDef:
    """Parse a source snippet and return the first class node."""
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            return node
    msg = "No class found in source"
    raise ValueError(msg)


def test_extract_class_attributes_annotations() -> None:
    """Class-level annotations are extracted as attributes."""
    node = _parse_class("class C:\n    x: int\n    y: str = 'a'\n")
    assert _extract_class_attributes(node) == ["x", "y"]


def test_extract_class_attributes_self_assignments() -> None:
    """self.x assignments in __init__ are extracted as attributes."""
    node = _parse_class("class C:\n    def __init__(self):\n        self.a = 1\n        self.b: int = 2\n")
    assert _extract_class_attributes(node) == ["a", "b"]


def test_extract_class_attributes_dedup_and_order() -> None:
    """Class annotations and __init__ assignments merge without duplicates, in first-seen order."""
    node = _parse_class("class C:\n    x: int\n    def __init__(self):\n        self.x = 1\n        self.y = 2\n")
    assert _extract_class_attributes(node) == ["x", "y"]


def test_extract_class_attributes_skips_dunder() -> None:
    """Dunder assignments like __slots__ are not treated as attributes."""
    node = _parse_class("class C:\n    __slots__ = ('x',)\n    value: int\n")
    assert _extract_class_attributes(node) == ["value"]


def test_extract_class_attributes_skips_constants() -> None:
    """All-uppercase names (constants) are not treated as attributes."""
    node = _parse_class("class C:\n    MAX_SIZE = 10\n    PATTERN: str = 'x'\n    value: int\n")
    assert _extract_class_attributes(node) == ["value"]


def test_extract_class_attributes_none() -> None:
    """Class with no attributes: returns empty list."""
    node = _parse_class("class C:\n    def method(self):\n        return 1\n")
    assert not _extract_class_attributes(node)


def test_extract_class_attributes_ignores_nested_function() -> None:
    """self.x assigned inside a function nested in __init__: not a class attribute."""
    node = _parse_class("class A:\n    def __init__(self):\n        self.a = 1\n        def later():\n            self.b = 2")
    assert _extract_class_attributes(node) == ["a"]


# ---------------------------------------------------------------------------
# _extract_args
# ---------------------------------------------------------------------------


def test_extract_args_no_args() -> None:
    """Only self in signature: returns empty list because self is always skipped."""
    node = _parse_func("def f(self): pass")
    assert not _extract_args(node.args, skip_first=True)


def test_extract_args_positional_with_type_and_default() -> None:
    """Positional arg with type annotation and default value: all three fields are populated.

    def f(self, x: int = 0) -> x.name="x", x.type_annotation="int", x.default="0"
    """
    node = _parse_func("def f(self, x: int = 0): pass")
    args = _extract_args(node.args, skip_first=True)
    assert len(args) == 1
    assert args[0].name == "x"
    assert args[0].type_annotation == "int"
    assert args[0].default == "0"


def test_extract_args_positional_without_type() -> None:
    """Positional arg with no type annotation: type_annotation is None.

    def f(self, x) -> x.type_annotation=None
    """
    node = _parse_func("def f(self, x): pass")
    args = _extract_args(node.args, skip_first=True)
    assert args[0].type_annotation is None


def test_extract_args_positional_without_default() -> None:
    """Positional arg with no default value: default is None.

    def f(self, x: int) -> x.default=None
    """
    node = _parse_func("def f(self, x: int): pass")
    args = _extract_args(node.args, skip_first=True)
    assert args[0].default is None


def test_extract_args_keyword_only() -> None:
    """Keyword-only arg (after bare *): extracted with correct name and type.

    def f(self, *, name: str) -> name is keyword-only, still returned
    """
    node = _parse_func("def f(self, *, name: str): pass")
    args = _extract_args(node.args, skip_first=True)
    assert len(args) == 1
    assert args[0].name == "name"
    assert args[0].type_annotation == "str"


def test_extract_args_keyword_only_with_default() -> None:
    """Keyword-only arg with a default value: default is correctly extracted.

    def f(self, *, strict: bool = False) -> strict.default="False"
    """
    node = _parse_func("def f(self, *, strict: bool = False): pass")
    args = _extract_args(node.args, skip_first=True)
    assert args[0].default == "False"


def test_extract_args_skips_first_param_whatever_its_name() -> None:
    """Method: the first positional parameter is dropped by position, not by name.

    def __new__(mcs, name: str) -> only name is returned
    """
    node = _parse_func("def __new__(mcs, name: str): pass")
    args = _extract_args(node.args, skip_first=True)
    assert [a.name for a in args] == ["name"]


def test_extract_args_keeps_self_and_cls_names_on_functions() -> None:
    """Plain function: parameters named self or cls are regular parameters."""
    node = _parse_func("def f(self, cls, *, x: int): pass")
    args = _extract_args(node.args, skip_first=False)
    assert [a.name for a in args] == ["self", "cls", "x"]


def test_extract_args_skips_only_the_first_param() -> None:
    """Method with a second parameter named cls: only the first parameter is dropped."""
    node = _parse_func("def f(self, cls, x: int): pass")
    args = _extract_args(node.args, skip_first=True)
    assert [a.name for a in args] == ["cls", "x"]


def test_extract_args_mixed_positional_and_keyword_only() -> None:
    """Mix of positional and keyword-only args: both are returned in declaration order.

    def f(self, a: int, *, b: str = "x") -> [a, b]
    """
    node = _parse_func('def f(self, a: int, *, b: str = "x"): pass')
    args = _extract_args(node.args, skip_first=True)

    assert len(args) == 2
    assert args[0].name == "a"
    assert args[1].name == "b"


def test_extract_args_vararg_and_kwarg() -> None:
    """*args and **kwargs are extracted with their stars in the name."""
    node = _parse_func("def f(a: int, *rest: str, **opts: object): pass")
    args = _extract_args(node.args, skip_first=False)

    names = [arg.name for arg in args]
    assert names == ["a", "*rest", "**opts"]
    assert args[1].type_annotation == "str"
    assert args[2].type_annotation == "object"


def test_extract_args_vararg_without_annotation() -> None:
    """*args without annotation: type_annotation is None."""
    node = _parse_func("def f(*rest): pass")
    args = _extract_args(node.args, skip_first=False)

    assert len(args) == 1
    assert args[0].name == "*rest"
    assert args[0].type_annotation is None


def test_extract_args_positional_only() -> None:
    """Positional-only args (before /) are extracted with name and type.

    def f(a: int, b: str, /) -> [a, b]
    """
    node = _parse_func("def f(a: int, b: str, /): pass")
    args = _extract_args(node.args, skip_first=False)

    assert len(args) == 2
    assert args[0].name == "a"
    assert args[0].type_annotation == "int"
    assert args[1].name == "b"
    assert args[1].type_annotation == "str"


def test_extract_args_positional_only_skips_self() -> None:
    """Exclude self when it appears in positional-only position.

    def f(self, x: int, /) -> [x]
    """
    node = _parse_func("def f(self, x: int, /): pass")
    args = _extract_args(node.args, skip_first=True)

    assert len(args) == 1
    assert args[0].name == "x"


def test_extract_args_positional_only_default_alignment() -> None:
    """Defaults align by the end of posonlyargs + args combined.

    def f(a, b, /, c, d=5, *, e=10) -> only d and e have defaults
    """
    node = _parse_func("def f(a, b, /, c, d=5, *, e=10): pass")
    args = _extract_args(node.args, skip_first=False)

    by_name = {a.name: a.default for a in args}
    assert by_name == {"a": None, "b": None, "c": None, "d": "5", "e": "10"}


def test_extract_args_positional_only_with_default() -> None:
    """Positional-only arg with a default has its default extracted.

    def f(a, b=2, /) -> b.default="2"
    """
    node = _parse_func("def f(a, b=2, /): pass")
    args = _extract_args(node.args, skip_first=False)

    assert args[0].name == "a"
    assert args[0].default is None
    assert args[1].name == "b"
    assert args[1].default == "2"


# ---------------------------------------------------------------------------
# _scan_body -- raises
# ---------------------------------------------------------------------------


def test_extract_raises_none() -> None:
    """Function with no raise statements: returns empty list."""
    node = _parse_func("def f(): pass")
    assert not _scan_body(node)[0]


def test_extract_raises_simple_call() -> None:
    """Raise ValueError("msg"): detected by the exception class name.

    The exception_type is "ValueError", not the message.
    """
    node = _parse_func('def f():\n    raise ValueError("msg")')
    raises = _scan_body(node)[0]
    assert len(raises) == 1
    assert raises[0].exception_type == "ValueError"


def test_extract_raises_variable_ignored() -> None:
    """Raise err where err is a variable, not bound by an except clause: ignored."""
    node = _parse_func("def f():\n    err = RuntimeError()\n    raise err")
    assert not _scan_body(node)[0]


def test_extract_raises_bare_class_name() -> None:
    """Raise ValueError without call: the class name is recorded."""
    node = _parse_func("def f():\n    raise ValueError")
    assert [r.exception_type for r in _scan_body(node)[0]] == ["ValueError"]


def test_extract_raises_lowercase_factory_ignored() -> None:
    """Raise make_error('x'): a lowercase callable is not an exception class, ignored."""
    node = _parse_func("def f():\n    raise make_error('x')")
    assert not _scan_body(node)[0]


def test_extract_raises_bare_raise_ignored() -> None:
    """Bare re-raise (raise with no argument): ignored because there is no exception type."""
    node = _parse_func("def f():\n    raise")
    assert not _scan_body(node)[0]


def test_extract_raises_deduplicates() -> None:
    """Same exception raised twice: appears only once in the result list."""
    source = "def f():\n    raise ValueError('a')\n    raise ValueError('b')"
    node = _parse_func(source)
    raises = _scan_body(node)[0]
    assert len(raises) == 1


def test_extract_raises_multiple_distinct() -> None:
    """Two different exceptions raised: both are present in the result."""
    source = "def f():\n    raise ValueError('a')\n    raise TypeError('b')"
    node = _parse_func(source)
    names = {r.exception_type for r in _scan_body(node)[0]}
    assert names == {"ValueError", "TypeError"}


def test_scan_body_reraise_of_caught_name() -> None:
    """Raise err inside 'except ValueError as err': reported as ValueError, not as err."""
    node = _parse_func("def f():\n    try:\n        pass\n    except ValueError as err:\n        raise err")
    assert [r.exception_type for r in _scan_body(node)[0]] == ["ValueError"]


def test_scan_body_reraise_of_caught_tuple() -> None:
    """Raise err inside 'except (KeyError, mod.Error) as err': every caught type is reported."""
    node = _parse_func("def f():\n    try:\n        pass\n    except (KeyError, mod.Error) as err:\n        raise err")
    assert [r.exception_type for r in _scan_body(node)[0]] == ["KeyError", "Error"]


def test_scan_body_dotted_exception() -> None:
    """Raise errors.ValidationError(...): reported by its last name segment."""
    node = _parse_func("def f():\n    raise errors.ValidationError('bad')")
    assert [r.exception_type for r in _scan_body(node)[0]] == ["ValidationError"]


def test_scan_body_lowercase_attribute_ignored() -> None:
    """Raise self.error: not an exception class name, ignored."""
    node = _parse_func("def f(self):\n    raise self.error")
    assert not _scan_body(node)[0]


def test_scan_body_nested_function_ignored() -> None:
    """Raise and yield inside a nested function or lambda: not attributed to the outer function."""
    source = "def f():\n    def g():\n        yield 1\n        raise ValueError\n    h = lambda: (yield)\n    return g"
    raises, is_generator = _scan_body(_parse_func(source))
    assert not raises
    assert is_generator is False


def test_scan_body_source_order() -> None:
    """Several raises: reported in source order, with the line of the first occurrence."""
    node = _parse_func("def f(x):\n    if x:\n        raise KeyError\n    raise ValueError")
    assert [(r.exception_type, r.line) for r in _scan_body(node)[0]] == [("KeyError", 3), ("ValueError", 4)]


# ---------------------------------------------------------------------------
# _is_empty_init
# ---------------------------------------------------------------------------


def test_is_empty_init_pass_only() -> None:
    """__init__(self) with only a pass statement: classified as empty."""
    node = _parse_func("def __init__(self): pass")
    assert _is_empty_init(node) is True


def test_is_empty_init_docstring_only() -> None:
    """__init__(self) with only a docstring: classified as empty (docstring is not logic)."""
    node = _parse_func('def __init__(self):\n    """docstring"""')
    assert _is_empty_init(node) is True


def test_is_empty_init_with_positional_arg() -> None:
    """__init__(self, name: str): has a real positional arg, not empty."""
    node = _parse_func("def __init__(self, name: str): pass")
    assert _is_empty_init(node) is False


def test_is_empty_init_with_kwonly_arg() -> None:
    """__init__(self, *, name: str): has a keyword-only arg, not empty.

    This was a bug: kwonlyargs were not checked before the fix.
    """
    node = _parse_func("def __init__(self, *, name: str): pass")
    assert _is_empty_init(node) is False


def test_is_empty_init_with_body() -> None:
    """__init__(self) with self.x = 1 in the body: has real statements, not empty."""
    node = _parse_func("def __init__(self):\n    self.x = 1")
    assert _is_empty_init(node) is False


@pytest.mark.parametrize("signature", ["def __init__(self, *args): pass", "def __init__(self, **kwargs): pass"])
def test_is_empty_init_with_star_args(signature: str) -> None:
    """__init__ taking *args or **kwargs: has parameters, not empty."""
    assert _is_empty_init(_parse_func(signature)) is False


# ---------------------------------------------------------------------------
# parse_file
# ---------------------------------------------------------------------------


def test_parse_file_returns_module_entity(tmp_path: Path) -> None:
    """Any Python file produces a MODULE entity as the first result, with its docstring."""
    f = tmp_path / "sample.py"
    f.write_text('"""Module docstring."""\n', encoding="utf-8")
    entities = parse_file(str(f))
    assert entities[0].node_type.value == "module"
    assert entities[0].docstring == "Module docstring."


def test_parse_file_extracts_function(tmp_path: Path) -> None:
    """Top-level function: extracted as a FUNCTION entity with the function name."""
    f = tmp_path / "sample.py"
    f.write_text("def my_func() -> None:\n    pass\n", encoding="utf-8")
    entities = parse_file(str(f))
    names = [e.name for e in entities]
    assert "my_func" in names


def test_parse_file_extracts_method(tmp_path: Path) -> None:
    """Method inside a class: extracted as a METHOD entity named ClassName.method_name."""
    f = tmp_path / "sample.py"
    f.write_text("class MyClass:\n    def my_method(self) -> None:\n        pass\n", encoding="utf-8")
    entities = parse_file(str(f))
    names = [e.name for e in entities]
    assert "MyClass.my_method" in names


def test_parse_file_sets_is_empty_init(tmp_path: Path) -> None:
    """__init__ with no args and pass body: is_empty_init is True on the extracted entity."""
    f = tmp_path / "sample.py"
    f.write_text("class MyClass:\n    def __init__(self): pass\n", encoding="utf-8")
    entities = parse_file(str(f))
    init = next(e for e in entities if e.name == "MyClass.__init__")
    assert init.is_empty_init is True


def test_parse_file_syntax_error(tmp_path: Path) -> None:
    """File with invalid Python syntax: SyntaxError is raised and not swallowed."""
    f = tmp_path / "bad.py"
    f.write_text("def broken(:\n    pass\n", encoding="utf-8")
    with pytest.raises(SyntaxError):
        parse_file(str(f))


# ---------------------------------------------------------------------------
# is_generator
# ---------------------------------------------------------------------------


def test_is_generator_with_yield(tmp_path: Path) -> None:
    """Function with yield: is_generator is True."""
    f = tmp_path / "sample.py"
    f.write_text("def gen():\n    yield 1\n", encoding="utf-8")
    entities = parse_file(str(f))
    gen = next(e for e in entities if e.name == "gen")
    assert gen.is_generator is True


def test_is_generator_with_yield_from(tmp_path: Path) -> None:
    """Function with yield from: is_generator is True."""
    f = tmp_path / "sample.py"
    f.write_text("def gen():\n    yield from [1, 2]\n", encoding="utf-8")
    entities = parse_file(str(f))
    gen = next(e for e in entities if e.name == "gen")
    assert gen.is_generator is True


def test_is_generator_without_yield(tmp_path: Path) -> None:
    """Function without yield: is_generator is False."""
    f = tmp_path / "sample.py"
    f.write_text("def f():\n    return 1\n", encoding="utf-8")
    entities = parse_file(str(f))
    func = next(e for e in entities if e.name == "f")
    assert func.is_generator is False


def test_is_generator_nested_generator_not_propagated(tmp_path: Path) -> None:
    """Function defining a nested generator: the outer function is not a generator."""
    f = tmp_path / "sample.py"
    f.write_text("def outer():\n    def gen():\n        yield 1\n    return list(gen())\n", encoding="utf-8")
    entities = parse_file(str(f))
    outer = next(e for e in entities if e.name == "outer")
    assert outer.is_generator is False


# ---------------------------------------------------------------------------
# parse_file -- entities under compound statements and decorators
# ---------------------------------------------------------------------------


def test_parse_file_functions_under_compound_statements(tmp_path: Path) -> None:
    """Functions defined under if, else, try, except, with and match: all extracted."""
    source = textwrap.dedent(
        """\
        import sys

        if sys.version_info >= (3, 12):
            def in_if(): pass
        else:
            def in_else(): pass
        try:
            def in_try(): pass
        except ImportError:
            def in_except(): pass
        with open(__file__) as f:
            def in_with(): pass
        match sys.platform:
            case "linux":
                def in_case(): pass
        """
    )
    f = tmp_path / "sample.py"
    f.write_text(source, encoding="utf-8")
    names = {e.name for e in parse_file(str(f))}
    assert {"in_if", "in_else", "in_try", "in_except", "in_with", "in_case"} <= names


def test_parse_file_method_under_if_in_class(tmp_path: Path) -> None:
    """Method defined under an if inside a class body: extracted as a method of that class."""
    f = tmp_path / "sample.py"
    f.write_text("class A:\n    if True:\n        def m(self): pass\n", encoding="utf-8")
    assert "A.m" in {e.name for e in parse_file(str(f))}


def test_parse_file_skips_overload_stubs(tmp_path: Path) -> None:
    """@overload and @typing.overload stubs: not extracted, the implementation is."""
    source = textwrap.dedent(
        """\
        import typing
        from typing import overload

        @overload
        def conv(x: int) -> int: ...
        @typing.overload
        def conv(x: str) -> str: ...
        def conv(x): return x
        """
    )
    f = tmp_path / "sample.py"
    f.write_text(source, encoding="utf-8")
    convs = [e for e in parse_file(str(f)) if e.name == "conv"]
    assert len(convs) == 1
    assert convs[0].line == 8


def test_parse_file_staticmethod_keeps_first_param(tmp_path: Path) -> None:
    """@staticmethod: the first parameter is a regular parameter, even when named self."""
    f = tmp_path / "sample.py"
    f.write_text("class A:\n    @staticmethod\n    def m(self, x): pass\n    def n(this, y): pass\n", encoding="utf-8")
    entities = {e.name: e for e in parse_file(str(f))}
    assert [a.name for a in entities["A.m"].args] == ["self", "x"]
    assert [a.name for a in entities["A.n"].args] == ["y"]


def test_parse_file_skips_main_guard_body(tmp_path: Path) -> None:
    """Functions and classes under 'if __name__ == "__main__":': skipped, the else branch is kept."""
    source = textwrap.dedent(
        """\
        def api(): pass

        if __name__ == "__main__":
            def demo(): pass
            class Demo: pass
        else:
            def on_import(): pass

        if "__main__" == __name__:
            def reversed_demo(): pass
        """
    )
    f = tmp_path / "sample.py"
    f.write_text(source, encoding="utf-8")
    names = {e.name for e in parse_file(str(f))}
    assert {"api", "on_import"} <= names
    assert not {"demo", "Demo", "reversed_demo"} & names


def test_parse_file_records_decorators(tmp_path: Path) -> None:
    """Decorators: recorded by their last name segment, sorted, attribute and call forms included."""
    source = "import functools\n\nclass A:\n    @property\n    def size(self): pass\n    @size.setter\n    def size(self, value): pass\n    @functools.cache\n    @staticmethod\n    def m(): pass\n"
    f = tmp_path / "sample.py"
    f.write_text(source, encoding="utf-8")
    decorators = [(e.name, e.decorators) for e in parse_file(str(f)) if e.name.startswith("A.")]
    assert decorators == [("A.size", ["property"]), ("A.size", ["setter"]), ("A.m", ["cache", "staticmethod"])]
