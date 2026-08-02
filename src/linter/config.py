"""Configuration for the docstring linter.

Support loading from pyproject.toml [tool.docstring-linter] section
with per-rule toggles, style selection, and scope control.
"""

import copy
import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePath
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
    "returns_descriptions": "Description on the Returns and Yields lines",
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
        "returns_match",
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
    "returns_match": "Returns section must match the signature type and carry a description",
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
        "returns_match",
        "summary_exists",
        "yields_match",
    }
)


# Keys accepted in the config file besides the policies
SETTING_KEYS: frozenset[str] = frozenset(
    {
        "style",
        "scope",
        "select",
        "ignore",
        "exclude",
        "workers",
        "overrides",
        "exclude_empty_init_method",
        "exclude_empty_init_module",
        "ignore_placeholder_docstrings",
        "summary_max_length",
        "blank_lines_before_section",
        "blank_lines_before_closing_quotes",
    }
)

CONFIG_KEYS: frozenset[str] = SETTING_KEYS | frozenset(POLICIES_REGISTRY)

SCOPE_KEYS: frozenset[str] = frozenset({"modules", "classes", "functions", "methods"})


# Options an override may carry: those that change what gets checked on a file
OVERRIDABLE_OPTIONS: frozenset[str] = frozenset(
    {
        "summary_max_length",
        "blank_lines_before_section",
        "blank_lines_before_closing_quotes",
        "exclude_empty_init_method",
        "exclude_empty_init_module",
        "ignore_placeholder_docstrings",
    }
)


@dataclass
class ConfigOverride:
    """Hold the settings applied to the files matching a set of path patterns.

    Attributes:
        paths (list[str]): Glob patterns the file path is matched against.
        select (list[str] | None): Rules replacing the inherited set, or None.
        ignore (list[str]): Rules removed from the inherited set.
        values (dict[str, object]): Policies and options overriding the inherited ones.

    """

    paths: list[str] = field(default_factory=lambda: [])  # noqa: PIE807
    select: list[str] | None = None
    ignore: list[str] = field(default_factory=lambda: [])  # noqa: PIE807
    values: dict[str, object] = field(default_factory=lambda: {})  # noqa: PIE807

    def matches(self, filepath: str) -> bool:
        """Check whether a file path matches one of the patterns.

        The path is matched as given, then relative to the current directory,
        so that an absolute path on the command line behaves like a relative one.

        Args:
            filepath (str): Path of the file being linted.

        Returns:
            bool: True if the override applies to that file.

        """
        candidates = [PurePath(filepath)]
        absolute = Path(filepath).resolve()
        if absolute.is_relative_to(Path.cwd()):
            candidates.append(PurePath(absolute.relative_to(Path.cwd())))

        return any(candidate.full_match(pattern) for pattern in self.paths for candidate in candidates)


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
        returns_descriptions (Policy): Policy for the description on the Returns and Yields lines.
        overrides (list[ConfigOverride]): Per-path settings applied in declaration order.

    """

    style: DocstringStyle = DocstringStyle.GOOGLE
    check_modules: bool = True
    check_classes: bool = True
    check_functions: bool = True
    check_methods: bool = True
    exclude_empty_init_method: bool = True
    exclude_empty_init_module: bool = True
    ignore_placeholder_docstrings: bool = False
    exclude_patterns: list[str] = field(default_factory=lambda: [".venv", ".git", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache", ".pytest_cache"])
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
    returns_descriptions: Policy = Policy.REQUIRED
    overrides: list[ConfigOverride] = field(default_factory=lambda: [])  # noqa: PIE807

    def for_path(self, filepath: str) -> LinterConfig:
        """Return the config applying to a file, overrides included.

        A single override applies, the last one declared among those matching.
        It is resolved against this config, the other matching ones are ignored.

        Args:
            filepath (str): Path of the file being linted.

        Returns:
            LinterConfig: This config when no override matches, a resolved copy otherwise.

        """
        matching = [override for override in self.overrides if override.matches(filepath)]
        if not matching:
            return self

        override = matching[-1]
        resolved = copy.copy(self)
        enabled = set(self.enabled_rules) if override.select is None else {rule for rule in override.select if rule in RULES_REGISTRY}
        enabled -= {rule for rule in override.ignore if rule in RULES_REGISTRY}

        for name, value in override.values.items():
            setattr(resolved, name, value)

        resolved.enabled_rules = sorted(enabled)
        return resolved

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


def _reject(unknown: list[str], noun: str, location: str = "") -> None:
    """Raise on names the configuration does not define.

    Args:
        unknown (list[str]): Offending names, empty when everything is known.
        noun (str): What the names stand for, in the singular.
        location (str): Config section carrying them, empty for the top level.

    Returns:
        None

    Raises:
        ValueError: If at least one name is unknown.

    """
    if not unknown:
        return

    label = noun if len(unknown) == 1 else f"{noun}s"
    prefix = f"{location}: " if location else ""
    msg = f"{prefix}unknown {label} {', '.join(repr(name) for name in unknown)}."
    raise ValueError(msg)


def _parse_policy(key: str, value: object) -> Policy:
    """Convert a configured value into a Policy.

    Args:
        key (str): Policy identifier, used in the error message.
        value (object): Value read from the config file.

    Returns:
        Policy: Matching policy.

    Raises:
        ValueError: If the value is not a policy name.

    """
    try:
        return Policy(value)
    except ValueError:
        msg = f"'{key}': invalid value {value!r}, expected one of {', '.join(policy.value for policy in Policy)}."
        raise ValueError(msg) from None


def _parse_style(value: object) -> DocstringStyle:
    """Convert a configured value into a DocstringStyle.

    Args:
        value (object): Value read from the config file.

    Returns:
        DocstringStyle: Matching style.

    Raises:
        ValueError: If the value is not a style name.

    """
    try:
        return DocstringStyle(value)
    except ValueError:
        msg = f"'style': invalid value {value!r}, expected one of {', '.join(style.value for style in DocstringStyle)}."
        raise ValueError(msg) from None


def _validate_rules(select: list[str], ignore: list[str], location: str = "") -> None:
    """Check the rule names listed in select and ignore.

    Args:
        select (list[str]): Rule names selected, 'ALL' accepted on its own.
        ignore (list[str]): Rule names ignored.
        location (str): Config section carrying them, empty for the top level.

    Returns:
        None

    Raises:
        ValueError: If an always-on rule is ignored.

    """
    if select != ["ALL"]:
        _reject(sorted(set(select) - set(RULES_REGISTRY)), "rule", f"{location}select" if location else "select")
    _reject(sorted(set(ignore) - set(RULES_REGISTRY)), "rule", f"{location}ignore" if location else "ignore")

    always_on = sorted(set(ignore) & ALWAYS_ON)
    if always_on:
        msg = f"{location}ignore: {', '.join(repr(rule) for rule in always_on)} cannot be ignored, always-on rules report an outright docstring defect."
        raise ValueError(msg)


def _parse_override(data: dict[str, object]) -> ConfigOverride:
    """Parse one [[overrides]] block into a ConfigOverride.

    Args:
        data (dict[str, object]): Parsed TOML table of the override.

    Returns:
        ConfigOverride: Settings applied to the matching files.

    Raises:
        ValueError: If paths is missing or a key is not allowed in an override.

    """
    paths = cast("list[str]", data.get("paths", []))
    if not paths:
        msg = "an override must declare a non-empty 'paths' list."
        raise ValueError(msg)

    override = ConfigOverride(paths=paths, ignore=cast("list[str]", data.get("ignore", [])))

    if "select" in data:
        override.select = cast("list[str]", data["select"])

    _validate_rules(override.select or [], override.ignore, f"override {paths}: ")

    for key, value in data.items():
        if key in {"paths", "select", "ignore"}:
            continue
        if key in POLICIES_REGISTRY:
            override.values[key] = _parse_policy(key, value)
        elif key in OVERRIDABLE_OPTIONS:
            override.values[key] = value
        elif key in CONFIG_KEYS:
            msg = f"override {paths}: '{key}' cannot be set per path, it applies to the whole run."
            raise ValueError(msg)
        else:
            _reject([key], "configuration key", f"override {paths}")

    return override


def _parse_toml_config(data: dict[str, object]) -> LinterConfig:  # noqa: C901, PLR0912  # pylint: disable=too-many-branches
    """Parse TOML config dict into LinterConfig.

    Args:
        data (dict[str, object]): Parsed TOML data from [tool.docstring-linter] section.

    Returns:
        LinterConfig: Populated configuration object.

    """
    config = LinterConfig()

    _reject(sorted(set(data) - CONFIG_KEYS), "configuration key")

    if "style" in data:
        config.style = _parse_style(data["style"])

    scope = cast("dict[str, bool]", data.get("scope", {}))
    _reject(sorted(set(scope) - SCOPE_KEYS), "configuration key", "scope")
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
            setattr(config, policy, _parse_policy(policy, data[policy]))
    if "workers" in data:
        config.workers = max(0, cast("int", data["workers"]))
    if "summary_max_length" in data:
        config.summary_max_length = max(1, cast("int", data["summary_max_length"]))
    if "blank_lines_before_section" in data:
        config.blank_lines_before_section = max(0, cast("int", data["blank_lines_before_section"]))
    if "blank_lines_before_closing_quotes" in data:
        config.blank_lines_before_closing_quotes = max(0, cast("int", data["blank_lines_before_closing_quotes"]))

    config.overrides = [_parse_override(cast("dict[str, object]", block)) for block in cast("list[object]", data.get("overrides", []))]

    select = cast("list[str]", data.get("select", []))
    ignore = cast("list[str]", data.get("ignore", []))
    _validate_rules(select, ignore)

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
