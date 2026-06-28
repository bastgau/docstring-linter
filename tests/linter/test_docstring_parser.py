"""Tests for docstring_parser module."""

import pytest
from linter.config import DocstringStyle
from linter.docstring_parser import GoogleStyleParser, get_parser

PARSER = GoogleStyleParser()


# ---------------------------------------------------------------------------
# parse -- empty / one-liner
# ---------------------------------------------------------------------------


def test_parse_empty_docstring() -> None:
    """Empty docstring: returns empty ParsedDocstring with no fields set."""
    result = PARSER.parse("")
    assert result.summary is None
    assert not result.args
    assert result.returns is None


def test_parse_oneliner() -> None:
    """One-liner docstring: summary is set, no other fields."""
    result = PARSER.parse("Do something.")
    assert result.summary == "Do something."
    assert not result.args
    assert result.returns is None


def test_parse_summary_and_description() -> None:
    """Summary + blank line + description: both summary and description are set."""
    result = PARSER.parse("Do something.\n\nDetailed description here.")
    assert result.summary == "Do something."
    assert result.description == "Detailed description here."


# ---------------------------------------------------------------------------
# parse -- Args section
# ---------------------------------------------------------------------------


def test_parse_arg_with_type_and_description() -> None:
    """Arg with type and description: all fields populated."""
    result = PARSER.parse("Do something.\n\nArgs:\n    x (int): The input value.\n")
    assert len(result.args) == 1
    assert result.args[0].name == "x"
    assert result.args[0].type_annotation == "int"
    assert result.args[0].description == "The input value."


def test_parse_arg_without_type() -> None:
    """Arg without type annotation: type_annotation is None."""
    result = PARSER.parse("Do something.\n\nArgs:\n    x: The input value.\n")
    assert result.args[0].type_annotation is None
    assert result.args[0].description == "The input value."


def test_parse_arg_multiline_description() -> None:
    """Arg with continuation line: description is concatenated."""
    docstring = "Do something.\n\nArgs:\n    x (int): First line.\n        Second line.\n"
    result = PARSER.parse(docstring)
    assert result.args[0].description == "First line. Second line."


def test_parse_multiple_args() -> None:
    """Multiple args: all are returned in order."""
    docstring = "Do something.\n\nArgs:\n    x (int): First.\n    y (str): Second.\n"
    result = PARSER.parse(docstring)
    assert len(result.args) == 2
    assert result.args[0].name == "x"
    assert result.args[1].name == "y"


# ---------------------------------------------------------------------------
# parse -- Returns section
# ---------------------------------------------------------------------------


def test_parse_returns_with_type_and_description() -> None:
    """Standard Returns line: type and description are extracted."""
    result = PARSER.parse("Do something.\n\nReturns:\n    int: The result value.\n")
    assert result.returns is not None
    assert result.returns.type_annotation == "int"
    assert result.returns.description == "The result value."


def test_parse_returns_none_keyword() -> None:
    """Returns section containing only 'None': type_annotation is 'None', description is None."""
    result = PARSER.parse("Do something.\n\nReturns:\n    None\n")
    assert result.returns is not None
    assert result.returns.type_annotation == "None"
    assert result.returns.description is None


def test_parse_no_returns_section() -> None:
    """Docstring without Returns section: returns field is None."""
    result = PARSER.parse("Do something.")
    assert result.returns is None


# ---------------------------------------------------------------------------
# parse -- Raises section
# ---------------------------------------------------------------------------


def test_parse_raises_single() -> None:
    """Single Raises entry: exception_type and description populated."""
    result = PARSER.parse("Do something.\n\nRaises:\n    ValueError: If input is negative.\n")
    assert len(result.raises) == 1
    assert result.raises[0].exception_type == "ValueError"
    assert result.raises[0].description == "If input is negative."


def test_parse_raises_multiline_description() -> None:
    """Raises entry with continuation line: description is concatenated."""
    docstring = "Do something.\n\nRaises:\n    ValueError: First line.\n        Second line.\n"
    result = PARSER.parse(docstring)
    assert result.raises[0].description == "First line. Second line."


def test_parse_raises_multiple() -> None:
    """Multiple Raises entries: all are returned."""
    docstring = "Do something.\n\nRaises:\n    ValueError: Bad value.\n    TypeError: Wrong type.\n"
    result = PARSER.parse(docstring)
    assert len(result.raises) == 2


# ---------------------------------------------------------------------------
# parse -- Attributes section
# ---------------------------------------------------------------------------


def test_parse_attributes_with_type() -> None:
    """Attribute with type and description: all fields populated."""
    result = PARSER.parse("A class.\n\nAttributes:\n    name (str): The name.\n")
    assert len(result.attributes) == 1
    assert result.attributes[0].name == "name"
    assert result.attributes[0].type_annotation == "str"
    assert result.attributes[0].description == "The name."


def test_parse_attributes_without_type() -> None:
    """Attribute without type annotation: type_annotation is None."""
    result = PARSER.parse("A class.\n\nAttributes:\n    name: The name.\n")
    assert result.attributes[0].type_annotation is None


def test_parse_attributes_multiline_description() -> None:
    """Attribute with continuation line: description is concatenated."""
    docstring = "A class.\n\nAttributes:\n    name (str): First line.\n        Second line.\n"
    result = PARSER.parse(docstring)
    assert result.attributes[0].description == "First line. Second line."


def test_parse_attributes_multiple() -> None:
    """Multiple attributes: all are returned in order."""
    docstring = "A class.\n\nAttributes:\n    name (str): The name.\n    count (int): The count.\n"
    result = PARSER.parse(docstring)
    assert len(result.attributes) == 2


# ---------------------------------------------------------------------------
# parse -- Example / unknown sections
# ---------------------------------------------------------------------------


def test_parse_example_section() -> None:
    """Docstring with Example section: examples list is populated."""
    result = PARSER.parse("Do something.\n\nExample:\n    >>> f(1)\n    1\n")
    assert len(result.examples) == 1


def test_parse_examples_section() -> None:
    """Docstring with Examples section (plural): examples list is populated."""
    result = PARSER.parse("Do something.\n\nExamples:\n    >>> f(1)\n    1\n")
    assert len(result.examples) == 1


def test_parse_unknown_section_ignored() -> None:
    """Unknown section name: not parsed, does not affect other fields."""
    result = PARSER.parse("Do something.\n\nCustom:\n    some content.\n")
    assert result.summary == "Do something."
    assert not result.args


def test_parse_lowercase_section_not_recognized() -> None:
    """Lowercase section name (args: instead of Args:): not recognized, no args parsed."""
    result = PARSER.parse("Do something.\n\nargs:\n    x (int): Input.\n")
    assert not result.args


# ---------------------------------------------------------------------------
# style property
# ---------------------------------------------------------------------------


def test_parser_style_property() -> None:
    """Style property: returns DocstringStyle.GOOGLE."""
    assert PARSER.style == DocstringStyle.GOOGLE


# ---------------------------------------------------------------------------
# get_parser
# ---------------------------------------------------------------------------


def test_get_parser_google() -> None:
    """get_parser(GOOGLE): returns a GoogleStyleParser instance."""
    parser = get_parser(DocstringStyle.GOOGLE)
    assert isinstance(parser, GoogleStyleParser)


def test_get_parser_unsupported() -> None:
    """get_parser with unsupported style: raises ValueError with style name."""
    with pytest.raises(ValueError, match="numpy"):
        get_parser(DocstringStyle.NUMPY)


# ---------------------------------------------------------------------------
# unknown sections
# ---------------------------------------------------------------------------


def test_unknown_section_detected() -> None:
    """Section name not in known list: captured in unknown_sections."""
    doc = "Do something.\n\nArguments:\n    x (int): Input.\n"
    result = PARSER.parse(doc)
    assert result.unknown_sections == ["Arguments"]
    assert result.args == []


def test_unknown_section_known_not_flagged() -> None:
    """Known section: not captured in unknown_sections."""
    doc = "Do something.\n\nArgs:\n    x (int): Input.\n\nReturns:\n    int: Result.\n\n"
    result = PARSER.parse(doc)
    assert result.unknown_sections == []


def test_unknown_section_multiple() -> None:
    """Multiple unknown sections: all captured."""
    doc = "Do something.\n\nArguments:\n    x (int): Input.\n\nParams:\n    y (int): Other.\n\n"
    result = PARSER.parse(doc)
    assert set(result.unknown_sections) == {"Arguments", "Params"}
