"""Configuration for the docstring linter.

Support loading from pyproject.toml [tool.docstring-linter] section
with per-rule toggles, style selection, and scope control.
"""

import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import cast


class DocstringStyle(Enum):
    """Enumerate supported docstring styles.

    Attributes:
        GOOGLE (str): Google style docstrings.
        NUMPY (str): NumPy style docstrings.
        SPHINX (str): Sphinx/RST style docstrings.
        PEP257 (str): PEP 257 generic style.

    """

    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    PEP257 = "pep257"


RULES_CATEGORIES: dict[str, list[str]] = {
    "Presence": [
        "docstring_exists",
        "summary_exists",
        "return_type_annotation",
        "attributes_section",
    ],
    "Summary": [
        "summary_first_line",
        "summary_punctuation",
        "summary_too_long",
        "imperative_mood",
    ],
    "Sections": [
        "section_capitalization",
        "section_order",
        "unknown_section",
        "empty_section",
        "blank_line_before_section",
        "blank_line_after_section",
        "no_blank_line_in_section",
        "closing_quotes_blank_line",
        "indentation",
    ],
    "Args / Returns / Raises": [
        "args_match",
        "duplicate_arg",
        "param_order",
        "returns_section",
        "yields_section",
        "raises_match",
        "without_returns_none_init",
        "returns_none_oneliner",
    ],
}

# All available rules with descriptions
RULES_REGISTRY = {
    "docstring_exists": "Docstring must exist",
    "summary_exists": "Summary line must exist",
    "return_type_annotation": "Return type annotation (-> type) must exist",
    "args_match": "Args must match between signature and docstring",
    "duplicate_arg": "Argument must not be documented more than once in Args section",
    "param_order": "Args section must follow the same order as the function signature",
    "returns_section": "Returns section must exist with type",
    "yields_section": "Yields section must exist for generator functions",
    "raises_match": "Raises must match between code and docstring",
    "attributes_section": "Attributes section must exist in class docstring",
    "indentation": "Indentation must be consistent",
    "summary_punctuation": "Summary line must end with a period",
    "summary_too_long": "Summary line must not exceed the configured maximum length",
    "section_capitalization": "Section names must be capitalized (Args, not args)",
    "section_order": "Sections must follow order: Args, Returns, Yields, Raises, Example(s), Note(s)",
    "unknown_section": "Section name is not recognized (e.g. 'Arguments:' instead of 'Args:')",
    "empty_section": "Section must not be empty",
    "blank_line_before_section": "Blank line required before section header",
    "blank_line_after_section": "Blank line required after last section content",
    "imperative_mood": "Summary should start with imperative verb (e.g. 'Process' not 'Processes')",
    "summary_first_line": "Summary must start on the same line as opening triple quotes",
    "closing_quotes_blank_line": "Multi-line docstring must have exactly one blank line before closing triple quotes",
    "no_blank_line_in_section": "No blank lines allowed between entries in Args, Attributes, or Raises sections",
    "without_returns_none_init": "Forbid 'Returns: None' on __init__ methods (when disabled, require it)",
    "returns_none_oneliner": "Require 'Returns: None' on one-liner docstrings returning None",
}

# Rules disabled by default; users opt in via pyproject.toml or --select
OFF_BY_DEFAULT = frozenset({"returns_none_oneliner"})


@dataclass
class LinterConfig:  # pylint: disable=too-many-instance-attributes
    """Hold all linter settings.

    Control which style to enforce, what to check,
    and what to exclude from validation.

    Attributes:
        style (DocstringStyle): Docstring style to enforce.
        check_modules (bool): Whether to check module docstrings.
        check_classes (bool): Whether to check class docstrings.
        check_functions (bool): Whether to check function docstrings.
        check_methods (bool): Whether to check method docstrings.
        exclude_empty_init (bool): Whether to skip empty __init__ methods.
        ignore_placeholder_docstrings (bool): Skip placeholder docstrings like \"\"\"...\"\"\".
        exclude_patterns (list[str]): Glob patterns for files to exclude.
        enabled_rules (list[str]): List of enabled rule identifiers.
        output_format (str): Output format -- text, json, or github-annotations.
        workers (int): Number of parallel workers (1 = sequential).
        summary_max_length (int): Maximum allowed summary line length.

    """

    style: DocstringStyle = DocstringStyle.GOOGLE
    check_modules: bool = True
    check_classes: bool = True
    check_functions: bool = True
    check_methods: bool = True
    exclude_empty_init: bool = True
    ignore_placeholder_docstrings: bool = False
    exclude_patterns: list[str] = field(default_factory=lambda: ["test_*", "*_test.py", ".venv", ".git", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache", ".pytest_cache"])
    enabled_rules: list[str] = field(default_factory=lambda: [r for r in RULES_REGISTRY if r not in OFF_BY_DEFAULT])
    output_format: str = "text"
    workers: int = 1
    summary_max_length: int = 80

    def is_rule_enabled(self, rule: str) -> bool:
        """Check if a specific rule is enabled.

        Args:
            rule (str): Rule identifier to check.

        Returns:
            bool: True if the rule is in the enabled list.

        """
        return rule in self.enabled_rules


STANDALONE_CONFIG_NAME = ".docstring-linter.toml"


def load_config(config_path: str | None = None) -> tuple[LinterConfig, Path | None]:
    """Load config from pyproject.toml, .docstring-linter.toml, or explicit path.

    Lookup order: explicit path, then pyproject.toml, then
    .docstring-linter.toml in current and parent directories, then default.

    Args:
        config_path (str | None): Explicit path to config file.

    Returns:
        tuple[LinterConfig, Path | None]: Parsed config and the config file path, or None.

    """
    toml_path = _find_config(config_path)
    if toml_path is None:
        return LinterConfig(), None

    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    if toml_path.name != "pyproject.toml":
        return _parse_toml_config(data), toml_path

    tool_config = data.get("tool", {}).get("docstring-linter", {})
    if not tool_config:
        return LinterConfig(), None

    return _parse_toml_config(tool_config), toml_path


def _find_config(explicit_path: str | None = None) -> Path | None:
    """Find config file by walking up directories.

    Checks pyproject.toml first, then .docstring-linter.toml at each level.
    An explicit path bypasses discovery entirely.

    Args:
        explicit_path (str | None): Explicit path to check first.

    Returns:
        Path | None: Path to config file, or None if not found.

    """
    if explicit_path:
        path = Path(explicit_path)
        if path.exists():
            return path
        return None

    current = Path.cwd()
    for directory in [current, *current.parents]:
        candidate = directory / "pyproject.toml"
        if candidate.exists():
            with candidate.open("rb") as f:
                data = tomllib.load(f)
            if data.get("tool", {}).get("docstring-linter"):
                return candidate
        candidate = directory / STANDALONE_CONFIG_NAME
        if candidate.exists():
            return candidate

    return None


def _parse_toml_config(data: dict[str, object]) -> LinterConfig:  # noqa: C901, PLR0912  # pylint: disable=too-many-branches
    """Parse TOML config dict into LinterConfig.

    Args:
        data (dict[str, object]): Parsed TOML data from [tool.docstring-linter] section.

    Returns:
        LinterConfig: Populated configuration object.

    """
    config = LinterConfig()

    if "style" in data:
        config.style = DocstringStyle(data["style"])

    scope = cast("dict[str, bool]", data.get("scope", {}))
    if "modules" in scope:
        config.check_modules = scope["modules"]
    if "classes" in scope:
        config.check_classes = scope["classes"]
    if "functions" in scope:
        config.check_functions = scope["functions"]
    if "methods" in scope:
        config.check_methods = scope["methods"]

    if "exclude_empty_init" in data:
        config.exclude_empty_init = cast("bool", data["exclude_empty_init"])
    if "ignore_placeholder_docstrings" in data:
        config.ignore_placeholder_docstrings = cast("bool", data["ignore_placeholder_docstrings"])
    if "exclude" in data:
        config.exclude_patterns = cast("list[str]", data["exclude"])
    if "workers" in data:
        config.workers = max(0, cast("int", data["workers"]))
    if "summary_max_length" in data:
        config.summary_max_length = max(1, cast("int", data["summary_max_length"]))

    select = cast("list[str]", data.get("select", []))
    ignore = cast("list[str]", data.get("ignore", []))

    if select or ignore:
        if select == ["ALL"]:
            enabled: set[str] = set(RULES_REGISTRY)
        elif select:
            enabled = {r for r in select if r in RULES_REGISTRY}
        else:
            enabled = {r for r in RULES_REGISTRY if r not in OFF_BY_DEFAULT}
        enabled -= {r for r in ignore if r in RULES_REGISTRY}
        config.enabled_rules = sorted(enabled)

    return config
