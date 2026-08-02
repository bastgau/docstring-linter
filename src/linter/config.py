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


class Policy(Enum):
    """Enumerate the directions a style policy can take.

    Attributes:
        REQUIRED (str): The construct must be present.
        FORBIDDEN (str): The construct must be absent.
        OPTIONAL (str): The construct is not checked, both forms are accepted.

    """

    REQUIRED = "required"
    FORBIDDEN = "forbidden"
    OPTIONAL = "optional"


# Style policies with descriptions, configured by value instead of on/off
POLICIES_REGISTRY = {
    "returns_none": "'Returns: None' section on -> None functions",
    "init_returns_none": "'Returns: None' section on __init__ methods",
    "summary_on_first_line": "Summary on the same line as the opening triple quotes",
    "summary_final_period": "Period at the end of the summary line",
    "args_section": "Args section documenting every parameter of the signature",
    "returns_section": "Returns section on functions returning something other than None",
    "yields_section": "Yields section on generator functions",
    "raises_section": "Raises section documenting every exception raised",
    "attributes_section": "Attributes section documenting every class attribute",
    "description_section": "Description paragraph below the summary",
    "examples_section": "Example section",
    "notes_section": "Note section",
    "todo_section": "Todo section",
    "documented_types": "Type between parentheses in Args and Attributes entries",
}


# Settings that change what gets checked, reported by --list-rules
OPTIONS_REGISTRY = {
    "style": "Docstring style enforced",
    "exclude_empty_init_method": "Docstring optional on __init__ methods with no parameter and an empty body",
    "exclude_empty_init_module": "Docstring optional on __init__.py modules with an empty body",
    "ignore_placeholder_docstrings": "Skip docstrings containing only '...'",
    "summary_max_length": "Maximum summary line length for summary_too_long",
    "blank_lines_before_section": "Blank lines expected before a section header",
    "blank_lines_before_closing_quotes": "Blank lines expected before the closing triple quotes",
    "scope.modules": "Check module docstrings",
    "scope.classes": "Check class docstrings",
    "scope.functions": "Check function docstrings",
    "scope.methods": "Check method docstrings",
}


RULES_CATEGORIES: dict[str, list[str]] = {
    "Presence": [
        "docstring_exists",
        "summary_exists",
        "return_type_annotation",
    ],
    "Summary": [
        "summary_too_long",
        "imperative_mood",
    ],
    "Sections": [
        "section_capitalization",
        "section_order",
        "unknown_section",
        "empty_section",
        "entry_spacing",
        "no_blank_line_in_section",
        "blank_lines",
        "indentation",
    ],
    "Args / Returns / Raises": [
        "args_match",
        "args_order",
        "duplicate_arg",
        "returns_type_match",
        "yields_match",
        "raises_match",
        "attributes_match",
    ],
}

# All available rules with descriptions
RULES_REGISTRY = {
    "docstring_exists": "Docstring must exist",
    "summary_exists": "Summary line must exist",
    "return_type_annotation": "Return type annotation (-> type) must exist",
    "args_match": "Documented args must match the signature (type, description, no phantom)",
    "duplicate_arg": "Argument must not be documented more than once in Args section",
    "args_order": "Args section must follow the same order as the function signature",
    "returns_type_match": "When a Returns section exists, its type must match the signature",
    "yields_match": "Yields section must declare a type and a description",
    "raises_match": "Documented exceptions must be raised in the code and described",
    "attributes_match": "Documented attributes must match the class (type, description, no phantom)",
    "indentation": "Indentation must be consistent",
    "summary_too_long": "Summary line must not exceed the configured maximum length",
    "section_capitalization": "Section names must be capitalized (Args, not args)",
    "section_order": "Sections must follow order: Args, Returns, Yields, Raises, Example(s), Note(s)",
    "unknown_section": "Section name is not recognized (e.g. 'Arguments:' instead of 'Args:')",
    "empty_section": "Section must not be empty",
    "imperative_mood": "Summary should start with imperative verb (e.g. 'Process' not 'Processes')",
    "no_blank_line_in_section": "No blank lines allowed between entries in Args, Attributes, or Raises sections",
    "entry_spacing": "Entries must be written 'name (type): description'",
    "blank_lines": "Blank line counts must match blank_lines_before_section and blank_lines_before_closing_quotes",
}

# Rules disabled by default; users opt in via pyproject.toml or --select
OFF_BY_DEFAULT: frozenset[str] = frozenset()

# Rules that report an outright docstring defect; select / ignore do not apply to them
ALWAYS_ON: frozenset[str] = frozenset(
    {
        "args_match",
        "attributes_match",
        "blank_lines",
        "duplicate_arg",
        "empty_section",
        "entry_spacing",
        "no_blank_line_in_section",
        "raises_match",
        "returns_type_match",
        "summary_exists",
        "yields_match",
    }
)


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
        exclude_empty_init_method (bool): Whether a docstring is optional on empty __init__ methods.
        exclude_empty_init_module (bool): Whether a docstring is optional on empty __init__.py modules.
        ignore_placeholder_docstrings (bool): Skip placeholder docstrings like \"\"\"...\"\"\".
        exclude_patterns (list[str]): Glob patterns for files to exclude.
        enabled_rules (list[str]): List of enabled rule identifiers.
        output_format (str): Output format -- traceback, text, json, or github-annotations.
        workers (int): Number of parallel workers (1 = sequential).
        summary_max_length (int): Maximum allowed summary line length.
        blank_lines_before_section (int): Blank lines expected before a section header.
        blank_lines_before_closing_quotes (int): Blank lines expected before the closing quotes.
        returns_none (Policy): Policy for 'Returns: None' on -> None functions.
        init_returns_none (Policy): Policy for 'Returns: None' on __init__ methods.
        summary_on_first_line (Policy): Policy for the summary on the opening quotes line.
        summary_final_period (Policy): Policy for the period ending the summary line.
        args_section (Policy): Policy for the presence of the Args section.
        returns_section (Policy): Policy for the presence of the Returns section.
        yields_section (Policy): Policy for the presence of the Yields section.
        raises_section (Policy): Policy for the presence of the Raises section.
        attributes_section (Policy): Policy for the presence of the Attributes section.
        description_section (Policy): Policy for the presence of the description paragraph.
        examples_section (Policy): Policy for the presence of the Example section.
        notes_section (Policy): Policy for the presence of the Note section.
        todo_section (Policy): Policy for the presence of the Todo section.
        documented_types (Policy): Policy for the type in Args and Attributes entries.

    """

    style: DocstringStyle = DocstringStyle.GOOGLE
    check_modules: bool = True
    check_classes: bool = True
    check_functions: bool = True
    check_methods: bool = True
    exclude_empty_init_method: bool = True
    exclude_empty_init_module: bool = True
    ignore_placeholder_docstrings: bool = False
    exclude_patterns: list[str] = field(default_factory=lambda: ["test_*", "*_test.py", ".venv", ".git", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache", ".pytest_cache"])
    enabled_rules: list[str] = field(default_factory=lambda: [r for r in RULES_REGISTRY if r not in OFF_BY_DEFAULT])
    output_format: str = "traceback"
    workers: int = 1
    summary_max_length: int = 80
    blank_lines_before_section: int = 1
    blank_lines_before_closing_quotes: int = 1
    returns_none: Policy = Policy.REQUIRED
    init_returns_none: Policy = Policy.FORBIDDEN
    summary_on_first_line: Policy = Policy.REQUIRED
    summary_final_period: Policy = Policy.REQUIRED
    args_section: Policy = Policy.REQUIRED
    returns_section: Policy = Policy.REQUIRED
    yields_section: Policy = Policy.REQUIRED
    raises_section: Policy = Policy.REQUIRED
    attributes_section: Policy = Policy.REQUIRED
    description_section: Policy = Policy.OPTIONAL
    examples_section: Policy = Policy.OPTIONAL
    notes_section: Policy = Policy.OPTIONAL
    todo_section: Policy = Policy.OPTIONAL
    documented_types: Policy = Policy.REQUIRED

    def policy_values(self) -> dict[str, str]:
        """Return the configured value of every style policy.

        Returns:
            dict[str, str]: Policy identifier to its configured value.

        """
        return {policy: cast("Policy", getattr(self, policy)).value for policy in POLICIES_REGISTRY}

    def option_values(self) -> dict[str, str]:
        """Return the configured value of every option that changes what is checked.

        Returns:
            dict[str, str]: Option identifier to its configured value.

        """
        return {
            "style": self.style.value,
            "exclude_empty_init_method": str(self.exclude_empty_init_method).lower(),
            "exclude_empty_init_module": str(self.exclude_empty_init_module).lower(),
            "ignore_placeholder_docstrings": str(self.ignore_placeholder_docstrings).lower(),
            "summary_max_length": str(self.summary_max_length),
            "blank_lines_before_section": str(self.blank_lines_before_section),
            "blank_lines_before_closing_quotes": str(self.blank_lines_before_closing_quotes),
            "scope.modules": str(self.check_modules).lower(),
            "scope.classes": str(self.check_classes).lower(),
            "scope.functions": str(self.check_functions).lower(),
            "scope.methods": str(self.check_methods).lower(),
        }

    def is_rule_enabled(self, rule: str) -> bool:
        """Check if a specific rule is enabled.

        Args:
            rule (str): Rule identifier to check.

        Returns:
            bool: True if the rule is always on or in the enabled list.

        """
        return rule in ALWAYS_ON or rule in self.enabled_rules


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

    if "exclude_empty_init_method" in data:
        config.exclude_empty_init_method = cast("bool", data["exclude_empty_init_method"])
    if "exclude_empty_init_module" in data:
        config.exclude_empty_init_module = cast("bool", data["exclude_empty_init_module"])
    if "ignore_placeholder_docstrings" in data:
        config.ignore_placeholder_docstrings = cast("bool", data["ignore_placeholder_docstrings"])
    if "exclude" in data:
        config.exclude_patterns = cast("list[str]", data["exclude"])
    for policy in POLICIES_REGISTRY:
        if policy in data:
            setattr(config, policy, Policy(data[policy]))
    if "workers" in data:
        config.workers = max(0, cast("int", data["workers"]))
    if "summary_max_length" in data:
        config.summary_max_length = max(1, cast("int", data["summary_max_length"]))
    if "blank_lines_before_section" in data:
        config.blank_lines_before_section = max(0, cast("int", data["blank_lines_before_section"]))
    if "blank_lines_before_closing_quotes" in data:
        config.blank_lines_before_closing_quotes = max(0, cast("int", data["blank_lines_before_closing_quotes"]))

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
