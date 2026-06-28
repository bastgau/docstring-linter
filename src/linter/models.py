"""Data models for the docstring linter.

Define dataclasses representing parsed code entities, docstring structures,
and linting errors used throughout the linter pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Enumerate AST node types the linter inspects.

    Attributes:
        MODULE (str): Module-level node.
        CLASS (str): Class definition node.
        FUNCTION (str): Top-level function node.
        METHOD (str): Class method node.

    """

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


@dataclass
class ArgInfo:
    """Store a function or method argument extracted from AST.

    Attributes:
        name (str): Argument name.
        type_annotation (str | None): Type annotation string.
        default (str | None): Default value string.
        line (int): Source line number.

    """

    name: str
    type_annotation: str | None = None
    default: str | None = None
    line: int = 0


@dataclass
class RaiseInfo:
    """Store a raise statement extracted from AST.

    Attributes:
        exception_type (str): Exception class name.
        line (int): Source line number.

    """

    exception_type: str
    line: int = 0


@dataclass
class CodeEntity:  # pylint: disable=too-many-instance-attributes
    """Store a module, class, function, or method extracted from AST.

    Attributes:
        name (str): Entity name.
        node_type (NodeType): Type of AST node.
        line (int): Source line number.
        filepath (str): Source file path.
        docstring (str | None): Raw docstring content.
        raw_docstring (str | None): Uncleaned docstring preserving whitespace.
        args (list[ArgInfo]): Function arguments.
        return_type (str | None): Return type annotation.
        raises (list[RaiseInfo]): Explicit raise statements.
        is_empty_init (bool): Whether this is an empty __init__.
        is_generator (bool): Whether the function contains a yield statement.

    """

    name: str
    node_type: NodeType
    line: int
    filepath: str
    docstring: str | None = None
    raw_docstring: str | None = None
    args: list[ArgInfo] = field(default_factory=lambda: [])
    return_type: str | None = None
    raises: list[RaiseInfo] = field(default_factory=lambda: [])
    is_empty_init: bool = False
    is_generator: bool = False


@dataclass
class DocstringArg:
    """Store a parameter parsed from a docstring.

    Attributes:
        name (str): Parameter name.
        type_annotation (str | None): Declared type.
        description (str | None): Parameter description.

    """

    name: str
    type_annotation: str | None = None
    description: str | None = None


@dataclass
class DocstringRaise:
    """Store a raise entry parsed from a docstring.

    Attributes:
        exception_type (str): Exception class name.
        description (str | None): When the exception is raised.

    """

    exception_type: str
    description: str | None = None


@dataclass
class DocstringReturn:
    """Store a return entry parsed from a docstring.

    Attributes:
        type_annotation (str | None): Return type.
        description (str | None): Return value description.

    """

    type_annotation: str | None = None
    description: str | None = None


@dataclass
class DocstringAttribute:
    """Store a class attribute parsed from a docstring.

    Attributes:
        name (str): Attribute name.
        type_annotation (str | None): Declared type.
        description (str | None): Attribute description.

    """

    name: str
    type_annotation: str | None = None
    description: str | None = None


@dataclass
class ParsedDocstring:  # pylint: disable=too-many-instance-attributes
    """Store a fully parsed docstring with all sections.

    Attributes:
        summary (str | None): First line summary.
        description (str | None): Extended description.
        args (list[DocstringArg]): Parsed Args section.
        returns (DocstringReturn | None): Parsed Returns section.
        yields (DocstringReturn | None): Parsed Yields section.
        raises (list[DocstringRaise]): Parsed Raises section.
        attributes (list[DocstringAttribute]): Parsed Attributes section.
        examples (list[str]): Parsed Example section content.
        unknown_sections (list[str]): Section names not recognized by the parser.

    """

    summary: str | None = None
    description: str | None = None
    args: list[DocstringArg] = field(default_factory=lambda: [])
    returns: DocstringReturn | None = None
    yields: DocstringReturn | None = None
    raises: list[DocstringRaise] = field(default_factory=lambda: [])
    attributes: list[DocstringAttribute] = field(default_factory=lambda: [])
    examples: list[str] = field(default_factory=lambda: [])
    unknown_sections: list[str] = field(default_factory=lambda: [])


@dataclass
class LintError:
    """Store a single linting error.

    Attributes:
        filepath (str): Source file path.
        line (int): Line number of the error.
        entity_name (str): Name of the entity with the error.
        node_type (NodeType): Type of AST node.
        rule (str): Rule identifier that triggered the error.
        message (str): Human-readable error message.

    """

    filepath: str
    line: int
    entity_name: str
    node_type: NodeType
    rule: str
    message: str

    def __str__(self) -> str:
        """Format error as file:line: entity - [rule] message string.

        Returns:
            str: Formatted error string.

        """
        return f"{self.filepath}:{self.line}: {self.entity_name} - [{self.rule}] {self.message}"
