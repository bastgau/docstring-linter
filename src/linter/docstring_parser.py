"""Docstring parser for the linter.

Parse raw Google style docstrings into structured data.
"""

import ast
import re

from linter.models import (
    DocstringArg,
    DocstringAttribute,
    DocstringRaise,
    DocstringReturn,
    ParsedDocstring,
)
from linter.sections import canonical_section, section_header


class GoogleStyleParser:
    """Parse Google style docstrings.

    Attributes:
        CANDIDATE_SECTION_PATTERN (re.Pattern): Regex for single-word headers of unknown sections.
        ARG_PATTERN (re.Pattern): Regex for typed arg lines.
        ARG_NO_TYPE_PATTERN (re.Pattern): Regex for untyped arg lines.
        ARG_NO_COLON_PATTERN (re.Pattern): Regex for typed arg lines missing their colon.
        RETURN_PATTERN (re.Pattern): Regex for return type lines.
        RAISE_PATTERN (re.Pattern): Regex for raise lines.

    """

    CANDIDATE_SECTION_PATTERN = re.compile(r"^([A-Z][A-Za-z]*):\s*$")
    ARG_PATTERN = re.compile(r"^\s{4}(\*{0,2}\w+)\s*\(([^)]+)\)\s*:\s*(.*)$")
    ARG_NO_TYPE_PATTERN = re.compile(r"^\s{4}(\*{0,2}\w+)\s*:\s*(.*)$")
    ARG_NO_COLON_PATTERN = re.compile(r"^\s{4}(\*{0,2}\w+)\s*\(([^)]+)\)\s*$")
    RETURN_PATTERN = re.compile(r"^\s{4}([^:]+?)\s*:\s*(.*)$")
    RAISE_PATTERN = re.compile(r"^\s{4}([\w.]+)\s*:\s*(.*)$")

    def parse(self, docstring: str) -> ParsedDocstring:
        """Parse a Google style docstring into structured data.

        Args:
            docstring (str): Raw docstring text.

        Returns:
            ParsedDocstring: Parsed docstring with all sections.

        """
        result = ParsedDocstring()
        if not docstring:
            return result

        sections = self._split_sections(docstring)

        result.summary = sections.get("_summary")
        result.description = sections.get("_description")

        # each parser returns an empty result on an absent section
        result.args = self._parse_args(sections.get("Args", "")) + self._parse_args(sections.get("Other Parameters", ""))
        result.keyword_args = self._parse_args(sections.get("Keyword Args", ""))
        result.returns = self._parse_returns(sections.get("Returns", ""))
        result.yields = self._parse_returns(sections.get("Yields", ""))
        result.raises = self._parse_raises(sections.get("Raises", ""))
        result.attributes = self._parse_attributes(sections.get("Attributes", ""))

        result.unknown_sections = [name for name in sections.get("_unknown_sections", "").split(",") if name]

        return result

    def _split_sections(self, docstring: str) -> dict[str, str]:  # noqa: C901 # pylint: disable=R0912:too-many-branches,too-many-locals
        """Split docstring into named sections.

        Napoleon aliases are stored under their canonical name, and two headers
        resolving to the same section have their contents joined.

        Args:
            docstring (str): Raw docstring text.

        Returns:
            dict[str, str]: Mapping of section names to their content strings.

        """
        sections: dict[str, str] = {}
        unknown: list[str] = []
        lines = docstring.split("\n")

        summary_lines: list[str] = []
        desc_lines: list[str] = []
        current_section: str | None = None
        section_lines: list[str] = []
        in_summary = True

        for line in lines:
            stripped = line.strip()

            header = section_header(line)

            if header:
                if current_section:
                    _store_section(sections, current_section, section_lines)
                current_section = canonical_section(header)
                section_lines = []
                in_summary = False
                continue

            candidate_match = self.CANDIDATE_SECTION_PATTERN.match(line)
            if candidate_match and not in_summary:
                name = candidate_match.group(1)
                if current_section:
                    _store_section(sections, current_section, section_lines)
                current_section = f"_unknown_{name}"
                unknown.append(name)
                section_lines = []
                continue

            if current_section:
                section_lines.append(line)
            elif in_summary:
                if stripped:
                    summary_lines.append(stripped)
                    in_summary = False
            elif stripped:
                desc_lines.append(stripped)

        if current_section:
            _store_section(sections, current_section, section_lines)

        sections["_unknown_sections"] = ",".join(unknown)

        if summary_lines:
            sections["_summary"] = " ".join(summary_lines)
        if desc_lines:
            sections["_description"] = " ".join(desc_lines)

        return sections

    def _parse_args(self, text: str) -> list[DocstringArg]:
        """Parse Args section into list of DocstringArg.

        Args:
            text (str): Raw text content of the Args section.

        Returns:
            list[DocstringArg]: Parsed argument entries.

        """
        args: list[DocstringArg] = []
        current_arg: DocstringArg | None = None

        for line in text.split("\n"):
            match = self.ARG_PATTERN.match(line)
            if match:
                current_arg = DocstringArg(
                    name=match.group(1),
                    type_annotation=match.group(2).strip(),
                    description=match.group(3).strip(),
                )
                args.append(current_arg)
                continue

            match = self.ARG_NO_TYPE_PATTERN.match(line)
            if match and not line.strip().startswith((">>>", "...")):
                current_arg = DocstringArg(
                    name=match.group(1),
                    type_annotation=None,
                    description=match.group(2).strip(),
                )
                args.append(current_arg)
                continue

            match = self.ARG_NO_COLON_PATTERN.match(line)
            if match:
                current_arg = DocstringArg(
                    name=match.group(1),
                    type_annotation=match.group(2).strip(),
                    description="",
                )
                args.append(current_arg)
                continue

            stripped = line.strip()
            if stripped and current_arg:
                current_arg.description = f"{current_arg.description} {stripped}".strip()

        return args

    def _parse_returns(self, text: str) -> DocstringReturn | None:
        """Parse Returns section into DocstringReturn.

        The text before the first colon is the type only when it reads as a
        Python expression, so that 'The mapping: key to value' stays prose.
        Continuation lines extend the description.

        Args:
            text (str): Raw text content of the Returns section.

        Returns:
            DocstringReturn | None: Parsed return entry, or None.

        """
        result: DocstringReturn | None = None

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            if result is not None:
                result.description = f"{result.description or ''} {stripped}".strip()
                continue

            match = self.RETURN_PATTERN.match(line)
            if match and _is_expression(match.group(1).strip()):
                result = DocstringReturn(type_annotation=match.group(1).strip(), description=match.group(2).strip() or None)
            elif stripped.lower() == "none":
                result = DocstringReturn(type_annotation="None", description=None)
            elif " " not in stripped and _is_expression(stripped):
                # degraded form, no colon: a bare type
                result = DocstringReturn(type_annotation=stripped, description=None)
            else:
                result = DocstringReturn(type_annotation=None, description=stripped)

        return result

    def _parse_raises(self, text: str) -> list[DocstringRaise]:
        """Parse Raises section into list of DocstringRaise.

        Args:
            text (str): Raw text content of the Raises section.

        Returns:
            list[DocstringRaise]: Parsed raise entries.

        """
        raises: list[DocstringRaise] = []
        current_raise: DocstringRaise | None = None

        for line in text.split("\n"):
            match = self.RAISE_PATTERN.match(line)
            if match:
                current_raise = DocstringRaise(
                    exception_type=match.group(1).strip(),
                    description=match.group(2).strip(),
                )
                raises.append(current_raise)
                continue

            stripped = line.strip()
            if stripped and current_raise:
                current_raise.description = f"{current_raise.description} {stripped}".strip()

        return raises

    def _parse_attributes(self, text: str) -> list[DocstringAttribute]:
        """Parse Attributes section into list of DocstringAttribute.

        Args:
            text (str): Raw text content of the Attributes section.

        Returns:
            list[DocstringAttribute]: Parsed attribute entries.

        """
        attrs: list[DocstringAttribute] = []
        current_attr: DocstringAttribute | None = None

        for line in text.split("\n"):
            match = self.ARG_PATTERN.match(line)
            if match:
                current_attr = DocstringAttribute(
                    name=match.group(1),
                    type_annotation=match.group(2).strip(),
                    description=match.group(3).strip(),
                )
                attrs.append(current_attr)
                continue

            match = self.ARG_NO_TYPE_PATTERN.match(line)
            if match:
                current_attr = DocstringAttribute(
                    name=match.group(1),
                    type_annotation=None,
                    description=match.group(2).strip(),
                )
                attrs.append(current_attr)
                continue

            match = self.ARG_NO_COLON_PATTERN.match(line)
            if match:
                current_attr = DocstringAttribute(
                    name=match.group(1),
                    type_annotation=match.group(2).strip(),
                    description="",
                )
                attrs.append(current_attr)
                continue

            stripped = line.strip()
            if stripped and current_attr:
                current_attr.description = f"{current_attr.description} {stripped}".strip()

        return attrs


def _store_section(sections: dict[str, str], name: str, lines: list[str]) -> None:
    """Store the content of a section after any content already stored under its name.

    Args:
        sections (dict[str, str]): Section name to content, updated in place.
        name (str): Canonical section name.
        lines (list[str]): Content lines of the section.

    Returns:
        None

    """
    text = "\n".join(lines)
    sections[name] = f"{sections[name]}\n{text}" if name in sections else text


def _is_expression(text: str) -> bool:
    """Check whether a text parses as a Python expression, the form a type takes.

    Args:
        text (str): Candidate type.

    Returns:
        bool: True if the text is a valid expression.

    """
    try:
        ast.parse(text, mode="eval")
    except SyntaxError:
        return False
    return True
