"""Tests for ast_parser module."""

import ast
import textwrap
from pathlib import Path  # noqa: TC003

import pytest
from linter.ast_parser import _extract_args, _extract_class_attributes, _extract_raises, _is_empty_init, parse_file  # pyright: ignore[reportPrivateUsage]


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


# ---------------------------------------------------------------------------
# _extract_args
# ---------------------------------------------------------------------------


def test_extract_args_no_args() -> None:
    """Only self in signature: returns empty list because self is always skipped."""
    node = _parse_func("def f(self): pass")
    assert not _extract_args(node.args)


def test_extract_args_positional_with_type_and_default() -> None:
    """Positional arg with type annotation and default value: all three fields are populated.

    def f(self, x: int = 0) -> x.name="x", x.type_annotation="int", x.default="0"
    """
    node = _parse_func("def f(self, x: int = 0): pass")
    args = _extract_args(node.args)
    assert len(args) == 1
    assert args[0].name == "x"
    assert args[0].type_annotation == "int"
    assert args[0].default == "0"


def test_extract_args_positional_without_type() -> None:
    """Positional arg with no type annotation: type_annotation is None.

    def f(self, x) -> x.type_annotation=None
    """
    node = _parse_func("def f(self, x): pass")
    args = _extract_args(node.args)
    assert args[0].type_annotation is None


def test_extract_args_positional_without_default() -> None:
    """Positional arg with no default value: default is None.

    def f(self, x: int) -> x.default=None
    """
    node = _parse_func("def f(self, x: int): pass")
    args = _extract_args(node.args)
    assert args[0].default is None


def test_extract_args_keyword_only() -> None:
    """Keyword-only arg (after bare *): extracted with correct name and type.

    def f(self, *, name: str) -> name is keyword-only, still returned
    """
    node = _parse_func("def f(self, *, name: str): pass")
    args = _extract_args(node.args)
    assert len(args) == 1
    assert args[0].name == "name"
    assert args[0].type_annotation == "str"


def test_extract_args_keyword_only_with_default() -> None:
    """Keyword-only arg with a default value: default is correctly extracted.

    def f(self, *, strict: bool = False) -> strict.default="False"
    """
    node = _parse_func("def f(self, *, strict: bool = False): pass")
    args = _extract_args(node.args)
    assert args[0].default == "False"


def test_extract_args_skips_self_and_cls() -> None:
    """Both self and cls are always excluded from the result, regardless of position."""
    node = _parse_func("def f(self, cls, x: int): pass")
    args = _extract_args(node.args)
    assert len(args) == 1
    assert args[0].name == "x"


def test_extract_args_skips_cls_in_kwonly() -> None:
    """Keyword-only arg named cls is excluded, just like in positional position.

    def f(*, cls, x: int) -> only x is returned
    """
    node = _parse_func("def f(*, cls, x: int): pass")
    args = _extract_args(node.args)
    assert len(args) == 1
    assert args[0].name == "x"


def test_extract_args_mixed_positional_and_keyword_only() -> None:
    """Mix of positional and keyword-only args: both are returned in declaration order.

    def f(self, a: int, *, b: str = "x") -> [a, b]
    """
    node = _parse_func('def f(self, a: int, *, b: str = "x"): pass')
    args = _extract_args(node.args)

    assert len(args) == 2
    assert args[0].name == "a"
    assert args[1].name == "b"


def test_extract_args_positional_only() -> None:
    """Positional-only args (before /) are extracted with name and type.

    def f(a: int, b: str, /) -> [a, b]
    """
    node = _parse_func("def f(a: int, b: str, /): pass")
    args = _extract_args(node.args)

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
    args = _extract_args(node.args)

    assert len(args) == 1
    assert args[0].name == "x"


def test_extract_args_positional_only_default_alignment() -> None:
    """Defaults align by the end of posonlyargs + args combined.

    def f(a, b, /, c, d=5, *, e=10) -> only d and e have defaults
    """
    node = _parse_func("def f(a, b, /, c, d=5, *, e=10): pass")
    args = _extract_args(node.args)

    by_name = {a.name: a.default for a in args}
    assert by_name == {"a": None, "b": None, "c": None, "d": "5", "e": "10"}


def test_extract_args_positional_only_with_default() -> None:
    """Positional-only arg with a default has its default extracted.

    def f(a, b=2, /) -> b.default="2"
    """
    node = _parse_func("def f(a, b=2, /): pass")
    args = _extract_args(node.args)

    assert args[0].name == "a"
    assert args[0].default is None
    assert args[1].name == "b"
    assert args[1].default == "2"


# ---------------------------------------------------------------------------
# _extract_raises
# ---------------------------------------------------------------------------


def test_extract_raises_none() -> None:
    """Function with no raise statements: returns empty list."""
    node = _parse_func("def f(): pass")
    assert not _extract_raises(node)


def test_extract_raises_simple_call() -> None:
    """Raise ValueError("msg"): detected by the exception class name.

    The exception_type is "ValueError", not the message.
    """
    node = _parse_func('def f():\n    raise ValueError("msg")')
    raises = _extract_raises(node)
    assert len(raises) == 1
    assert raises[0].exception_type == "ValueError"


def test_extract_raises_bare_name() -> None:
    """Raise err where err is a plain name (not a call): the name itself is recorded."""
    node = _parse_func("def f():\n    err = RuntimeError()\n    raise err")
    raises = _extract_raises(node)
    assert len(raises) == 1
    assert raises[0].exception_type == "err"


def test_extract_raises_bare_raise_ignored() -> None:
    """Bare re-raise (raise with no argument): ignored because there is no exception type."""
    node = _parse_func("def f():\n    raise")
    assert not _extract_raises(node)


def test_extract_raises_deduplicates() -> None:
    """Same exception raised twice: appears only once in the result list."""
    source = "def f():\n    raise ValueError('a')\n    raise ValueError('b')"
    node = _parse_func(source)
    raises = _extract_raises(node)
    assert len(raises) == 1


def test_extract_raises_multiple_distinct() -> None:
    """Two different exceptions raised: both are present in the result."""
    source = "def f():\n    raise ValueError('a')\n    raise TypeError('b')"
    node = _parse_func(source)
    names = {r.exception_type for r in _extract_raises(node)}
    assert names == {"ValueError", "TypeError"}


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
