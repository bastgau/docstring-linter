"""AST parser for the docstring linter.

Extract modules, classes, functions, and their signatures from Python
source files using the standard library ast module.
"""

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING, TypeGuard

from linter.config import POLICIES_REGISTRY, RULES_REGISTRY
from linter.models import ArgInfo, CodeEntity, NodeType, RaiseInfo

if TYPE_CHECKING:
    from collections.abc import Iterator

# Nodes whose body does not run when the enclosing function runs
_NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)

# Statements whose blocks belong to the enclosing module or class body
_COMPOUND_STATEMENTS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try, ast.TryStar, ast.Match)

# '# docstring-linter: ignore' or '# docstring-linter: ignore[rule, ...]' closing a def, class or module docstring line
_IGNORE_COMMENT = re.compile(r"#\s*docstring-linter:\s*ignore(?:\[([^\]]*)\])?\s*$")


class IgnoreCommentError(ValueError):
    """Raised when an ignore comment names a rule that does not exist."""


def parse_file(filepath: str) -> list[CodeEntity]:
    """Parse a Python file and extract all code entities.

    Args:
        filepath (str): Path to the Python source file.

    Returns:
        list[CodeEntity]: List of extracted code entities.

    """
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=filepath)
    entities: list[CodeEntity] = []

    module_doc = ast.get_docstring(tree)
    module_raw = ast.get_docstring(tree, clean=False)
    entities.append(
        CodeEntity(
            name=Path(filepath).stem,
            node_type=NodeType.MODULE,
            line=1,
            filepath=filepath,
            docstring=module_doc,
            raw_docstring=module_raw,
            is_empty_init_module=Path(filepath).name == "__init__.py" and not tree.body,
        )
    )

    _walk_body(tree.body, filepath, entities, parent=None)

    lines = source.splitlines()
    # a module carries its comment on the opening line of its docstring, the others on their def or class line
    module_line = tree.body[0].lineno if module_doc is not None else None
    for entity in entities:
        line = module_line if entity.node_type == NodeType.MODULE else entity.line
        if line is not None:
            _apply_ignore_comment(entity, lines[line - 1], line)
    return entities


def _apply_ignore_comment(entity: CodeEntity, text: str, line: int) -> None:
    """Record on an entity the rules silenced by the ignore comment of its line.

    Args:
        entity (CodeEntity): Entity the line belongs to.
        text (str): Source line of the def, class or module docstring.
        line (int): Line number, for the error message.

    Returns:
        None

    Raises:
        IgnoreCommentError: If the comment names an unknown rule.

    """
    match = _IGNORE_COMMENT.search(text)
    if match is None:
        return
    if match.group(1) is None:
        entity.ignore_all = True
        return

    names = frozenset(name.strip() for name in match.group(1).split(",") if name.strip())
    unknown = sorted(names - set(RULES_REGISTRY) - set(POLICIES_REGISTRY))
    if unknown:
        msg = f"{entity.filepath}:{line}: unknown rule {', '.join(repr(name) for name in unknown)} in ignore comment."
        raise IgnoreCommentError(msg)
    entity.ignored_rules = names


def _walk_body(
    body: list[ast.stmt],
    filepath: str,
    entities: list[CodeEntity],
    parent: CodeEntity | None,
) -> None:
    """Walk AST body recursively to extract classes and functions.

    Args:
        body (list[ast.stmt]): AST body node list.
        filepath (str): Source file path.
        entities (list[CodeEntity]): Accumulator for extracted entities.
        parent (CodeEntity | None): Enclosing class entity, or None for top-level.

    Returns:
        None

    """
    for node in body:
        if isinstance(node, ast.ClassDef):
            entity = _parse_class(node, filepath)
            entities.append(entity)
            _walk_body(node.body, filepath, entities, parent=entity)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if "overload" not in _decorator_names(node):
                entities.append(_parse_function(node, filepath, parent))

        elif isinstance(node, _COMPOUND_STATEMENTS):
            # the body of a main guard only runs as a script, its else branch runs on import
            blocks = [node.orelse] if _is_main_guard(node) else _statement_blocks(node)
            for block in blocks:
                _walk_body(block, filepath, entities, parent)


def _is_main_guard(node: ast.stmt) -> TypeGuard[ast.If]:
    """Check whether a statement is an 'if __name__ == "__main__":' guard.

    Args:
        node (ast.stmt): Statement to inspect.

    Returns:
        TypeGuard[ast.If]: True for the guard, whichever side of == __name__ is on.

    """
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    test = node.test
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    return {ast.unparse(test.left), ast.unparse(test.comparators[0])} == {"__name__", "'__main__'"}


def _statement_blocks(node: ast.stmt) -> list[list[ast.stmt]]:
    """Return the statement blocks nested in a compound statement.

    Args:
        node (ast.stmt): If, loop, with, try or match statement.

    Returns:
        list[list[ast.stmt]]: Every block of the statement, handlers and cases included.

    """
    blocks: list[list[ast.stmt]] = [getattr(node, name, []) for name in ("body", "orelse", "finalbody")]
    blocks.extend(handler.body for handler in getattr(node, "handlers", []))
    blocks.extend(case.body for case in getattr(node, "cases", []))
    return blocks


def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Return the last name segment of each decorator of a function.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): Function node.

    Returns:
        set[str]: Names such as 'overload' for both @overload and @typing.overload.

    """
    names: set[str] = set()
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


def _walk_scope(node: ast.AST) -> Iterator[ast.AST]:
    """Yield the descendants of a node in source order, skipping nested functions.

    Args:
        node (ast.AST): Node whose descendants are visited.

    Yields:
        ast.AST: Each descendant that runs as part of the node itself.

    """
    stack = list(reversed(list(ast.iter_child_nodes(node))))
    while stack:
        child = stack.pop()
        if isinstance(child, _NESTED_SCOPES):
            continue
        yield child
        stack.extend(reversed(list(ast.iter_child_nodes(child))))


def _parse_class(node: ast.ClassDef, filepath: str) -> CodeEntity:
    """Extract class information from AST node.

    Args:
        node (ast.ClassDef): AST class definition node.
        filepath (str): Source file path.

    Returns:
        CodeEntity: Parsed class entity.

    """
    init = next((stmt for stmt in node.body if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == "__init__"), None)
    return CodeEntity(
        name=node.name,
        node_type=NodeType.CLASS,
        line=node.lineno,
        filepath=filepath,
        docstring=ast.get_docstring(node),
        raw_docstring=ast.get_docstring(node, clean=False),
        class_attributes=_extract_class_attributes(node),
        init_args=_extract_args(init.args, skip_first=True) if init else None,
    )


def _extract_class_attributes(node: ast.ClassDef) -> list[str]:  # noqa: C901
    """Extract attribute names from class annotations and __init__ assignments.

    Args:
        node (ast.ClassDef): AST class definition node.

    Returns:
        list[str]: Attribute names in first-seen order, without duplicates.

    """
    names: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        if name.startswith("__") or name.isupper():
            return
        if name not in seen:
            seen.add(name)
            names.append(name)

    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            add(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                for leaf in _unpack_target(target):
                    if isinstance(leaf, ast.Name):
                        add(leaf.id)

    for stmt in node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == "__init__":
            for name in _self_attr_names(stmt):
                add(name)

    return names


def _self_attr_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Collect self.<name> assignment targets inside a function body.

    Args:
        func (ast.FunctionDef | ast.AsyncFunctionDef): Function node to scan.

    Returns:
        list[str]: Attribute names assigned on self.

    """
    names: list[str] = []
    for child in _walk_scope(func):
        if isinstance(child, ast.AnnAssign) and _is_self_attr(child.target):
            names.append(child.target.attr)
        elif isinstance(child, ast.Assign):
            names.extend(leaf.attr for target in child.targets for leaf in _unpack_target(target) if _is_self_attr(leaf))
    return names


def _unpack_target(target: ast.expr) -> list[ast.expr]:
    """Flatten a tuple or list assignment target into its elements.

    'self.a, *self.b = ...' gives self.a and self.b.

    Args:
        target (ast.expr): Assignment target.

    Returns:
        list[ast.expr]: The target itself, or the elements of a tuple or list target.

    """
    if isinstance(target, (ast.Tuple, ast.List)):
        return [leaf for element in target.elts for leaf in _unpack_target(element)]
    if isinstance(target, ast.Starred):
        return _unpack_target(target.value)
    return [target]


def _is_self_attr(target: ast.expr) -> TypeGuard[ast.Attribute]:
    """Check whether an assignment target is self.<name>.

    Args:
        target (ast.expr): Assignment target node.

    Returns:
        TypeGuard[ast.Attribute]: True if the target is an attribute access on self.

    """
    return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self"


def _parse_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filepath: str,
    parent: CodeEntity | None,
) -> CodeEntity:
    """Extract function or method information from AST node.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node.
        filepath (str): Source file path.
        parent (CodeEntity | None): Enclosing class entity, or None for functions.

    Returns:
        CodeEntity: Parsed function or method entity.

    """
    is_method = parent is not None
    node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
    name = f"{parent.name}.{node.name}" if parent else node.name

    args = _extract_args(node.args, skip_first=is_method and "staticmethod" not in _decorator_names(node))
    return_type = ast.unparse(node.returns) if node.returns else None
    raises, is_generator = _scan_body(node)

    is_empty_init = False
    if node.name == "__init__":
        is_empty_init = _is_empty_init(node)

    return CodeEntity(
        name=name,
        node_type=node_type,
        line=node.lineno,
        filepath=filepath,
        docstring=ast.get_docstring(node),
        raw_docstring=ast.get_docstring(node, clean=False),
        args=args,
        return_type=return_type,
        raises=raises,
        is_empty_init=is_empty_init,
        is_generator=is_generator,
        decorators=sorted(_decorator_names(node)),
        class_docstring=parent.docstring if parent and node.name == "__init__" else None,
    )


def _extract_args(arguments: ast.arguments, *, skip_first: bool) -> list[ArgInfo]:
    """Extract argument info from AST arguments node.

    Args:
        arguments (ast.arguments): AST arguments structure.
        skip_first (bool): Whether to drop the first positional parameter, the self or cls of a method.

    Returns:
        list[ArgInfo]: List of parsed argument info objects.

    """
    result: list[ArgInfo] = []

    all_args = arguments.posonlyargs + arguments.args
    defaults = arguments.defaults
    num_no_default = len(all_args) - len(defaults)

    for i, arg in enumerate(all_args):
        if skip_first and i == 0:
            continue

        annotation = ast.unparse(arg.annotation) if arg.annotation else None
        default_idx = i - num_no_default
        default = ast.unparse(defaults[default_idx]) if default_idx >= 0 else None

        result.append(
            ArgInfo(
                name=arg.arg,
                type_annotation=annotation,
                default=default,
                line=arg.lineno,
            )
        )

    if arguments.vararg is not None:
        result.append(_star_arg(arguments.vararg, "*"))

    kw_defaults = arguments.kw_defaults
    for i, arg in enumerate(arguments.kwonlyargs):
        annotation = ast.unparse(arg.annotation) if arg.annotation else None
        kw_default = kw_defaults[i]
        default = ast.unparse(kw_default) if kw_default is not None else None

        result.append(
            ArgInfo(
                name=arg.arg,
                type_annotation=annotation,
                default=default,
                line=arg.lineno,
            )
        )

    if arguments.kwarg is not None:
        result.append(_star_arg(arguments.kwarg, "**"))

    return result


def _star_arg(arg: ast.arg, prefix: str) -> ArgInfo:
    """Build the ArgInfo of a *args or **kwargs parameter.

    The stars are kept in the name so that the docstring entry compares
    as-is, without normalising either side.

    Args:
        arg (ast.arg): AST argument node.
        prefix (str): Star prefix, '*' or '**'.

    Returns:
        ArgInfo: Argument info carrying the starred name.

    """
    return ArgInfo(
        name=f"{prefix}{arg.arg}",
        type_annotation=ast.unparse(arg.annotation) if arg.annotation else None,
        default=None,
        line=arg.lineno,
    )


def _exception_name(node: ast.expr) -> str | None:
    """Return the class name designated by a raise or except expression.

    A dotted name keeps its last segment. Only capitalized names count as
    exception classes, so that errors.ValidationError gives ValidationError
    while a variable such as exc or self.error is ignored.

    Args:
        node (ast.expr): Expression following raise, or an except clause type.

    Returns:
        str | None: Exception name, or None when it cannot be told statically.

    """
    if isinstance(node, ast.Call):
        return _exception_name(node.func)
    if isinstance(node, ast.Name):
        name = node.id
    elif isinstance(node, ast.Attribute):
        name = node.attr
    else:
        return None
    return name if name[:1].isupper() else None


def _scan_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[list[RaiseInfo], bool]:
    """Collect the raise statements and detect yields in one pass over a function body.

    Nested functions and lambdas are skipped: their raises and yields belong to them.
    Raising a name bound by 'except ... as name', or a bare raise inside the handler,
    reports the caught exception types; raising any other variable is ignored.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node.

    Returns:
        tuple[list[RaiseInfo], bool]: Unique raises in source order, and whether the function yields.

    """
    raises: list[RaiseInfo] = []
    seen: set[str] = set()
    is_generator = False
    caught: dict[str, list[str]] = {}
    reraised: dict[ast.Raise, list[str]] = {}

    for child in _walk_scope(node):
        if isinstance(child, (ast.Yield, ast.YieldFrom)):
            is_generator = True
        elif isinstance(child, ast.ExceptHandler) and child.type is not None:
            types = child.type.elts if isinstance(child.type, ast.Tuple) else [child.type]
            names = [name for name in map(_exception_name, types) if name]
            if child.name:
                caught[child.name] = names
            reraised.update(dict.fromkeys(_bare_raises(child), names))
        elif isinstance(child, ast.Raise):
            if child.exc is None:
                names = reraised.get(child, [])
            elif isinstance(child.exc, ast.Name) and child.exc.id in caught:
                names = caught[child.exc.id]
            else:
                exc_name = _exception_name(child.exc)
                names = [exc_name] if exc_name else []
            for name in names:
                if name not in seen:
                    seen.add(name)
                    raises.append(RaiseInfo(exception_type=name, line=child.lineno))

    return raises, is_generator


def _bare_raises(handler: ast.ExceptHandler) -> list[ast.Raise]:
    """Collect the bare raise statements that re-raise the exception of a handler.

    Nested functions and nested handlers are skipped: a bare raise inside a
    nested handler re-raises the exception that handler caught.

    Args:
        handler (ast.ExceptHandler): Except clause.

    Returns:
        list[ast.Raise]: Bare raise statements of the handler body.

    """
    found: list[ast.Raise] = []
    stack: list[ast.AST] = list(handler.body)
    while stack:
        child = stack.pop()
        if isinstance(child, (*_NESTED_SCOPES, ast.ExceptHandler)):
            continue
        if isinstance(child, ast.Raise) and child.exc is None:
            found.append(child)
        stack.extend(ast.iter_child_nodes(child))
    return found


def _is_empty_init(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if __init__ body is empty.

    An __init__ is considered empty if it has no parameters beyond self
    and its body contains only pass statements or a docstring.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node for __init__.

    Returns:
        bool: True if the __init__ is empty.

    """
    real_args = (node.args.posonlyargs + node.args.args)[1:]
    if real_args or node.args.kwonlyargs or node.args.vararg or node.args.kwarg:
        return False

    for stmt in node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue
        if isinstance(stmt, ast.Pass):
            continue
        return False

    return True
