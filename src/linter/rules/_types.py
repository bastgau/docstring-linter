"""Type comparison between docstrings and signatures.

Three levels, each including the previous one:

- strict: cosmetic differences only (quotes, spacing, ', optional', Sphinx '~').
- equivalent: same type spelled differently (Optional[X], X | None, List, list).
- lenient: the docstring may omit None from a union declared in the signature.
"""

import ast
import re

_TYPING_ALIASES = {"List": "list", "Dict": "dict", "Set": "set", "FrozenSet": "frozenset", "Tuple": "tuple", "Type": "type"}

_SPHINX_SHORT_REF = re.compile(r"~(?=[A-Za-z_])")


def _parse(text: str) -> ast.expr | None:
    """Parse a type written as a Python expression.

    Args:
        text (str): Type text.

    Returns:
        ast.expr | None: Expression node, or None if the text is not valid Python.

    """
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError:
        return None


class _Unquote(ast.NodeTransformer):
    """Replace string forward references by the expression they contain."""

    def visit_Constant(self, node: ast.Constant) -> ast.expr:  # pylint: disable=invalid-name
        """Parse a string constant as a type expression when possible.

        Args:
            node (ast.Constant): Constant node.

        Returns:
            ast.expr: Parsed expression, or the constant when it is not a type.

        """
        if isinstance(node.value, str):
            parsed = _parse(node.value)
            if parsed is not None:
                return self.visit(parsed)
        return node


class _Unalias(ast.NodeTransformer):
    """Rename the typing aliases of builtin generics: List becomes list."""

    def visit_Name(self, node: ast.Name) -> ast.Name:  # pylint: disable=invalid-name
        """Rename a typing alias to its builtin.

        Args:
            node (ast.Name): Name node.

        Returns:
            ast.Name: Node carrying the builtin name, or the node unchanged.

        """
        return ast.Name(id=_TYPING_ALIASES.get(node.id, node.id))


def _cosmetic(text: str) -> ast.expr | str:
    """Drop the cosmetic parts of a type: ', optional', Sphinx '~', quotes and spacing.

    Args:
        text (str): Type as written.

    Returns:
        ast.expr | str: Parsed expression, or the cleaned text when it is not valid Python.

    """
    cleaned = _SPHINX_SHORT_REF.sub("", text.strip().removesuffix(", optional").strip())
    parsed = _parse(cleaned)
    if parsed is None:
        return cleaned
    return _Unquote().visit(parsed)


def _is_named(node: ast.expr, name: str) -> bool:
    """Check whether a node is a name or an attribute ending with the given name.

    Args:
        node (ast.expr): Node to inspect.
        name (str): Expected name, such as 'Optional'.

    Returns:
        bool: True for Optional as well as typing.Optional.

    """
    return (isinstance(node, ast.Name) and node.id == name) or (isinstance(node, ast.Attribute) and node.attr == name)


def _union_members(node: ast.expr) -> frozenset[str]:
    """Flatten a union into the set of its members, whatever its spelling.

    Args:
        node (ast.expr): Type expression.

    Returns:
        frozenset[str]: Members as source text, 'None' included when the union allows it.

    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _union_members(node.left) | _union_members(node.right)
    if isinstance(node, ast.Subscript) and _is_named(node.value, "Optional"):
        return _union_members(node.slice) | {"None"}
    if isinstance(node, ast.Subscript) and _is_named(node.value, "Union"):
        elements = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
        members: frozenset[str] = frozenset()
        return members.union(*(_union_members(element) for element in elements))
    return frozenset({ast.unparse(_Unalias().visit(node))})


def types_match(documented: str, signature: str, level: str) -> bool:
    """Check whether a documented type matches the signature annotation.

    Args:
        documented (str): Type written in the docstring.
        signature (str): Annotation from the signature, as unparsed by ast.
        level (str): Matching level, strict, equivalent or lenient.

    Returns:
        bool: True if the types are considered identical at that level.

    """
    doc = _cosmetic(documented)
    sig = _cosmetic(signature)
    if isinstance(doc, str) or isinstance(sig, str):
        return doc == sig

    if ast.unparse(doc) == ast.unparse(sig):
        return True
    if level == "strict":
        return False

    doc_members = _union_members(doc)
    sig_members = _union_members(sig)
    return doc_members == sig_members or (level == "lenient" and doc_members == sig_members - {"None"})
