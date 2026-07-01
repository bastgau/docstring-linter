"""Docstring parser for the linter.

Parse raw docstrings into structured data. Extensible via abstract
base class for multiple styles (Google, NumPy, Sphinx, PEP 257).
"""

import re
from abc import ABC, abstractmethod

from linter.config import DocstringStyle
from linter.models import (
    DocstringArg,
    DocstringAttribute,
    DocstringRaise,
    DocstringReturn,
    ParsedDocstring,
)


class BaseDocstringParser(ABC):
    """Define abstract interface for docstring parsers."""

    @abstractmethod
    def parse(self, docstring: str) -> ParsedDocstring:
        """Parse a raw docstring into structured data.

        Args:
            docstring (str): Raw docstring text.

        Returns:
            ParsedDocstring: Parsed docstring structure.

        """

    @property
    @abstractmethod
    def style(self) -> DocstringStyle:
        """Return the style this parser handles.

        Returns:
            DocstringStyle: Parser style identifier.

        """


class GoogleStyleParser(BaseDocstringParser):
    """Parse Google style docstrings.

    Attributes:
        SECTION_PATTERN (re.Pattern): Regex for section headers.
        ARG_PATTERN (re.Pattern): Regex for typed arg lines.
        ARG_NO_TYPE_PATTERN (re.Pattern): Regex for untyped arg lines.
        RETURN_PATTERN (re.Pattern): Regex for return type lines.
        RAISE_PATTERN (re.Pattern): Regex for raise lines.

    """

    SECTION_PATTERN = re.compile(
        r"^(Args|Returns|Raises|Attributes|Example|Examples|Note|Notes|Todo|Yields):\s*$",
        re.MULTILINE,
    )
    CANDIDATE_SECTION_PATTERN = re.compile(r"^([A-Z][A-Za-z]*):\s*$")
    ARG_PATTERN = re.compile(r"^\s{4}(\w+)\s*\(([^)]+)\)\s*:\s*(.+)$")
    ARG_NO_TYPE_PATTERN = re.compile(r"^\s{4}(\w+)\s*:\s*(.+)$")
    RETURN_PATTERN = re.compile(r"^\s{4}(.+?)\s*:\s+(.+)$")
    RAISE_PATTERN = re.compile(r"^\s{4}(\w+)\s*:\s*(.+)$")

    @property
    def style(self) -> DocstringStyle:
        """Return Google style identifier.

        Returns:
            DocstringStyle: GOOGLE enum value.

        """
        return DocstringStyle.GOOGLE

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

        if "Args" in sections:
            result.args = self._parse_args(sections["Args"])
        if "Returns" in sections:
            result.returns = self._parse_returns(sections["Returns"])
        if "Yields" in sections:
            result.yields = self._parse_returns(sections["Yields"])
        if "Raises" in sections:
            result.raises = self._parse_raises(sections["Raises"])
        if "Attributes" in sections:
            result.attributes = self._parse_attributes(sections["Attributes"])
        if "Example" in sections:
            result.examples = [sections["Example"]]
        if "Examples" in sections:
            result.examples = [sections["Examples"]]

        raw = sections.get("_unknown_sections", "")
        if raw:
            result.unknown_sections = raw.split(",")

        return result

    def _split_sections(self, docstring: str) -> dict[str, str]:  # noqa: C901, PLR0912 # pylint: disable=R0912:too-many-branches,too-many-locals
        """Split docstring into named sections.

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
        found_blank_after_summary = False

        for line in lines:
            stripped = line.strip()

            section_match = self.SECTION_PATTERN.match(stripped)

            if section_match:
                if current_section:
                    sections[current_section] = "\n".join(section_lines)
                current_section = section_match.group(1)
                section_lines = []
                in_summary = False
                continue

            candidate_match = self.CANDIDATE_SECTION_PATTERN.match(stripped)
            if candidate_match and not in_summary:
                name = candidate_match.group(1)
                if current_section:
                    sections[current_section] = "\n".join(section_lines)
                current_section = f"_unknown_{name}"
                unknown.append(name)
                section_lines = []
                continue

            if current_section:
                section_lines.append(line)
            elif in_summary:
                if stripped == "" and summary_lines:
                    in_summary = False
                    found_blank_after_summary = True
                elif stripped:
                    summary_lines.append(stripped)
            elif found_blank_after_summary and stripped:
                desc_lines.append(stripped)

        if current_section:
            sections[current_section] = "\n".join(section_lines)

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

            stripped = line.strip()
            if stripped and current_arg:
                current_arg.description = f"{current_arg.description} {stripped}"

        return args

    def _parse_returns(self, text: str) -> DocstringReturn | None:
        """Parse Returns section into DocstringReturn.

        Args:
            text (str): Raw text content of the Returns section.

        Returns:
            DocstringReturn | None: Parsed return entry, or None.

        """
        for line in text.split("\n"):
            match = self.RETURN_PATTERN.match(line)
            if match:
                return DocstringReturn(
                    type_annotation=match.group(1).strip(),
                    description=match.group(2).strip(),
                )
            stripped = line.strip()
            if stripped.lower() == "none":
                return DocstringReturn(type_annotation="None", description=None)

        return None

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
                current_raise.description = f"{current_raise.description} {stripped}"

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

            stripped = line.strip()
            if stripped and current_attr:
                current_attr.description = f"{current_attr.description} {stripped}"

        return attrs


PARSERS = {
    DocstringStyle.GOOGLE: GoogleStyleParser,
}


def get_parser(style: DocstringStyle) -> BaseDocstringParser:
    """Get the appropriate parser for the given style.

    Args:
        style (DocstringStyle): Docstring style to use.

    Returns:
        BaseDocstringParser: Parser instance for the requested style.

    Raises:
        ValueError: If the style is not supported.

    """
    parser_cls = PARSERS.get(style)
    if parser_cls is None:
        msg = f"Unsupported docstring style: {style.value}"
        raise ValueError(msg)
    return parser_cls()
