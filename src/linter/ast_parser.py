"""AST parser for the docstring linter.

Extract modules, classes, functions, and their signatures from Python
source files using the standard library ast module.
"""

import ast
from pathlib import Path

from linter.models import ArgInfo, CodeEntity, NodeType, RaiseInfo


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
        )
    )

    _walk_body(tree.body, filepath, entities, parent_class=None)
    return entities


def _walk_body(
    body: list[ast.stmt],
    filepath: str,
    entities: list[CodeEntity],
    parent_class: str | None,
) -> None:
    """Walk AST body recursively to extract classes and functions.

    Args:
        body (list[ast.stmt]): AST body node list.
        filepath (str): Source file path.
        entities (list[CodeEntity]): Accumulator for extracted entities.
        parent_class (str | None): Parent class name, or None for top-level.

    Returns:
        None: This function mutates entities in place.

    """
    for node in body:
        if isinstance(node, ast.ClassDef):
            entities.append(_parse_class(node, filepath))
            _walk_body(node.body, filepath, entities, parent_class=node.name)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entities.append(_parse_function(node, filepath, parent_class))


def _parse_class(node: ast.ClassDef, filepath: str) -> CodeEntity:
    """Extract class information from AST node.

    Args:
        node (ast.ClassDef): AST class definition node.
        filepath (str): Source file path.

    Returns:
        CodeEntity: Parsed class entity.

    """
    return CodeEntity(
        name=node.name,
        node_type=NodeType.CLASS,
        line=node.lineno,
        filepath=filepath,
        docstring=ast.get_docstring(node),
        raw_docstring=ast.get_docstring(node, clean=False),
    )


def _parse_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filepath: str,
    parent_class: str | None,
) -> CodeEntity:
    """Extract function or method information from AST node.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node.
        filepath (str): Source file path.
        parent_class (str | None): Parent class name, or None for functions.

    Returns:
        CodeEntity: Parsed function or method entity.

    """
    is_method = parent_class is not None
    node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
    name = f"{parent_class}.{node.name}" if parent_class else node.name

    args = _extract_args(node.args)
    return_type = ast.unparse(node.returns) if node.returns else None
    raises = _extract_raises(node)

    is_empty_init = False
    if node.name == "__init__":
        is_empty_init = _is_empty_init(node)

    is_generator = any(isinstance(child, (ast.Yield, ast.YieldFrom)) for child in ast.walk(node))

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
    )


def _extract_args(arguments: ast.arguments) -> list[ArgInfo]:
    """Extract argument info from AST arguments node.

    Args:
        arguments (ast.arguments): AST arguments structure.

    Returns:
        list[ArgInfo]: List of parsed argument info objects.

    """
    skip = {"self", "cls"}
    result: list[ArgInfo] = []

    all_args = arguments.posonlyargs + arguments.args
    defaults = arguments.defaults
    num_no_default = len(all_args) - len(defaults)

    for i, arg in enumerate(all_args):
        if arg.arg in skip:
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

    kw_defaults = arguments.kw_defaults
    for i, arg in enumerate(arguments.kwonlyargs):
        if arg.arg in skip:
            continue

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

    return result


def _extract_raises(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[RaiseInfo]:
    """Extract explicit raise statements from function body.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node.

    Returns:
        list[RaiseInfo]: List of unique raise statements found.

    """
    raises: list[RaiseInfo] = []
    seen: set[str] = set()
    queue: list[ast.AST] = list(ast.iter_child_nodes(node))

    while queue:
        child = queue.pop()
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc_name = None
            if isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                exc_name = child.exc.func.id
            elif isinstance(child.exc, ast.Name):
                exc_name = child.exc.id
            if exc_name and exc_name not in seen:
                seen.add(exc_name)
                raises.append(RaiseInfo(exception_type=exc_name, line=child.lineno))
        else:
            queue.extend(ast.iter_child_nodes(child))

    return raises


def _is_empty_init(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if __init__ body is empty.

    An __init__ is considered empty if it has no parameters beyond self
    and its body contains only pass statements or a docstring.

    Args:
        node (ast.FunctionDef | ast.AsyncFunctionDef): AST function node for __init__.

    Returns:
        bool: True if the __init__ is empty.

    """
    real_args = [a for a in node.args.args if a.arg != "self"]
    if real_args or node.args.kwonlyargs:
        return False

    for stmt in node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue
        if isinstance(stmt, ast.Pass):
            continue
        return False

    return True
