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

    """

    GOOGLE = "google"


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
    "examples_section": "Examples section",
    "notes_section": "Note section",
    "todo_section": "Todo section",
    "documented_types": "Type in Args and Attributes entries and on the Returns and Yields lines",
    "documented_stars": "Stars of *args and **kwargs in their Args entries",
    "returns_descriptions": "Description on the Returns and Yields lines",
}


# Settings that change what gets checked, reported by --list-rules
OPTIONS_REGISTRY = {
    "convention": "Convention providing the defaults of policies, options and rules",
    "style": "Docstring style enforced",
    "exclude_empty_init_method": "Docstring optional on __init__ methods with no parameter and an empty body",
    "exclude_empty_init_module": "Docstring optional on __init__.py modules with an empty body",
    "ignore_placeholder_docstrings": "Skip docstrings containing only '...'",
    "exclude_dunder_methods": "Docstring optional on magic methods other than __init__",
    "exclude_private": "Docstring optional on private names and on members of private classes",
    "exclude_overridden": "Docstring optional on methods decorated with @override",
    "properties_as_attributes": "Property getters documented like attributes, setters and deleters not checked",
    "summary_max_length": "Maximum summary line length for summary_too_long",
    "blank_lines_before_section": "Blank lines expected before a section header",
    "blank_lines_before_closing_quotes": "Blank lines expected before the closing triple quotes",
    "type_matching": "How closely a documented type must match the signature",
    "init_args_location": "Docstring documenting the __init__ parameters: init, class or either",
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
        "section_alias",
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
        "raises_extraneous",
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
    "raises_match": "Documented exceptions must carry a description",
    "raises_extraneous": "Documented exceptions must be raised explicitly in the body",
    "attributes_match": "Documented attributes must match the class (type, description, no phantom)",
    "indentation": "Section content must be indented by 4 spaces or more, the first entry of Args, Attributes and Raises by exactly 4",
    "summary_too_long": "Summary line must not exceed the configured maximum length",
    "section_capitalization": "Section names must be capitalized (Args, not args)",
    "section_alias": "Section names must use the canonical spelling (Args, not Parameters)",
    "section_order": "Sections must follow order: Attributes, Args, Keyword Args, Other Parameters, Returns, Yields, Raises, Examples, Note(s), Todo",
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


@dataclass(frozen=True)
class Convention:
    """Hold the defaults a convention sets before the config file keys apply.

    Attributes:
        values (dict[str, object]): Policies and options set by the convention.
        disabled_rules (frozenset[str]): Configurable rules the convention turns off.

    """

    values: dict[str, object]
    disabled_rules: frozenset[str]


CONVENTIONS: dict[str, Convention] = {
    # Built-in defaults: every section and type documented, house layout
    "strict": Convention(values={}, disabled_rules=frozenset()),
    # Google Python Style Guide: types live in the signature, no 'Returns: None',
    # no blank line before the closing quotes, descriptive or imperative summary
    "google": Convention(
        values={
            "returns_none": Policy.OPTIONAL,
            "init_returns_none": Policy.OPTIONAL,
            "documented_types": Policy.OPTIONAL,
            "raises_section": Policy.OPTIONAL,
            "attributes_section": Policy.OPTIONAL,
            "blank_lines_before_closing_quotes": 0,
            "type_matching": "lenient",
            "exclude_dunder_methods": True,
            "exclude_private": True,
            "exclude_overridden": True,
            "properties_as_attributes": True,
            "init_args_location": "either",
        },
        disabled_rules=frozenset({"imperative_mood", "return_type_annotation", "raises_extraneous"}),
    ),
}


# Keys accepted in the config file besides the policies
SETTING_KEYS: frozenset[str] = frozenset(
    {
        "convention",
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
        "exclude_dunder_methods",
        "exclude_private",
        "exclude_overridden",
        "properties_as_attributes",
        "summary_max_length",
        "blank_lines_before_section",
        "blank_lines_before_closing_quotes",
        "type_matching",
        "init_args_location",
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
        "exclude_dunder_methods",
        "exclude_private",
        "exclude_overridden",
        "properties_as_attributes",
        "type_matching",
        "init_args_location",
    }
)

# Options taking one value among a fixed list
CHOICE_OPTIONS: dict[str, tuple[str, ...]] = {
    "type_matching": ("strict", "equivalent", "lenient"),
    "init_args_location": ("init", "class", "either"),
}

# Integer options with the minimum value they are clamped to
INT_OPTIONS: dict[str, int] = {
    "workers": 0,
    "summary_max_length": 1,
    "blank_lines_before_section": 0,
    "blank_lines_before_closing_quotes": 0,
}

BOOL_OPTIONS: frozenset[str] = frozenset(
    {
        "exclude_empty_init_method",
        "exclude_empty_init_module",
        "ignore_placeholder_docstrings",
        "exclude_dunder_methods",
        "exclude_private",
        "exclude_overridden",
        "properties_as_attributes",
    }
)


def path_matches(filepath: str, patterns: list[str]) -> bool:
    """Check whether a file path fully matches one of the glob patterns.

    The path is matched as given, then relative to the current directory,
    so that an absolute path on the command line behaves like a relative one.

    Args:
        filepath (str): Path of the file.
        patterns (list[str]): Glob patterns matched with PurePath.full_match.

    Returns:
        bool: True if one of the patterns matches.

    """
    candidates = [PurePath(filepath)]
    absolute = Path(filepath).resolve()
    if absolute.is_relative_to(Path.cwd()):
        candidates.append(PurePath(absolute.relative_to(Path.cwd())))

    return any(candidate.full_match(pattern) for pattern in patterns for candidate in candidates)


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

        Args:
            filepath (str): Path of the file being linted.

        Returns:
            bool: True if the override applies to that file.

        """
        return path_matches(filepath, self.paths)


@dataclass
class LinterConfig:  # pylint: disable=too-many-instance-attributes
    """Hold all linter settings.

    Control which style to enforce, what to check,
    and what to exclude from validation.

    Attributes:
        convention (str): Convention the defaults come from, a key of CONVENTIONS.
        style (DocstringStyle): Docstring style to enforce.
        check_modules (bool): Whether to check module docstrings.
        check_classes (bool): Whether to check class docstrings.
        check_functions (bool): Whether to check function docstrings.
        check_methods (bool): Whether to check method docstrings.
        exclude_empty_init_method (bool): Whether a docstring is optional on empty __init__ methods.
        exclude_empty_init_module (bool): Whether a docstring is optional on empty __init__.py modules.
        ignore_placeholder_docstrings (bool): Skip placeholder docstrings like \"\"\"...\"\"\".
        exclude_dunder_methods (bool): Whether a docstring is optional on magic methods other than __init__.
        exclude_private (bool): Whether a docstring is optional on private names and members of private classes.
        exclude_overridden (bool): Whether a docstring is optional on methods decorated with @override.
        properties_as_attributes (bool): Whether property getters are documented like attributes.
        exclude_patterns (list[str]): Glob patterns for files to exclude.
        enabled_rules (list[str]): List of enabled rule identifiers.
        output_format (str): Output format -- traceback, text, json, or github-annotations.
        workers (int): Number of parallel workers (1 = sequential).
        summary_max_length (int): Maximum allowed summary line length.
        blank_lines_before_section (int): Blank lines expected before a section header.
        blank_lines_before_closing_quotes (int): Blank lines expected before the closing quotes.
        type_matching (str): How closely a documented type must match the signature.
        init_args_location (str): Docstring documenting the __init__ parameters: init, class or either.
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
        examples_section (Policy): Policy for the presence of the Examples section.
        notes_section (Policy): Policy for the presence of the Note section.
        todo_section (Policy): Policy for the presence of the Todo section.
        documented_types (Policy): Policy for the type in Args, Attributes, Returns and Yields.
        documented_stars (Policy): Policy for the stars of *args and **kwargs entries.
        returns_descriptions (Policy): Policy for the description on the Returns and Yields lines.
        overrides (list[ConfigOverride]): Per-path settings applied in declaration order.

    """

    convention: str = "strict"
    style: DocstringStyle = DocstringStyle.GOOGLE
    check_modules: bool = True
    check_classes: bool = True
    check_functions: bool = True
    check_methods: bool = True
    exclude_empty_init_method: bool = True
    exclude_empty_init_module: bool = True
    ignore_placeholder_docstrings: bool = False
    exclude_dunder_methods: bool = False
    exclude_private: bool = False
    exclude_overridden: bool = False
    properties_as_attributes: bool = False
    exclude_patterns: list[str] = field(default_factory=lambda: [".venv", ".git", "__pycache__", ".tox", ".mypy_cache", ".ruff_cache", ".pytest_cache"])
    enabled_rules: list[str] = field(default_factory=lambda: [r for r in RULES_REGISTRY if r not in OFF_BY_DEFAULT])
    output_format: str = "traceback"
    workers: int = 1
    summary_max_length: int = 80
    blank_lines_before_section: int = 1
    blank_lines_before_closing_quotes: int = 1
    type_matching: str = "strict"
    init_args_location: str = "init"
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
    documented_stars: Policy = Policy.REQUIRED
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

        for name, value in override.values.items():
            setattr(resolved, name, value)

        resolved.enabled_rules = _resolve_rules(override.select, override.ignore, self.enabled_rules)
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
            "convention": self.convention,
            "style": self.style.value,
            "exclude_empty_init_method": str(self.exclude_empty_init_method).lower(),
            "exclude_empty_init_module": str(self.exclude_empty_init_module).lower(),
            "ignore_placeholder_docstrings": str(self.ignore_placeholder_docstrings).lower(),
            "exclude_dunder_methods": str(self.exclude_dunder_methods).lower(),
            "exclude_private": str(self.exclude_private).lower(),
            "exclude_overridden": str(self.exclude_overridden).lower(),
            "properties_as_attributes": str(self.properties_as_attributes).lower(),
            "summary_max_length": str(self.summary_max_length),
            "blank_lines_before_section": str(self.blank_lines_before_section),
            "blank_lines_before_closing_quotes": str(self.blank_lines_before_closing_quotes),
            "type_matching": self.type_matching,
            "init_args_location": self.init_args_location,
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

    Raises:
        ValueError: If an explicit pyproject.toml has no [tool.docstring-linter] section.

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
        # discovery only returns a pyproject.toml carrying the section, so this is an explicit path
        msg = f"{toml_path}: no [tool.docstring-linter] section."
        raise ValueError(msg)

    return _parse_toml_config(tool_config), toml_path


def _find_config(explicit_path: str | None = None) -> Path | None:
    """Find config file by walking up directories.

    Checks pyproject.toml first, then .docstring-linter.toml at each level.
    An explicit path bypasses discovery entirely.

    Args:
        explicit_path (str | None): Explicit path to check first.

    Returns:
        Path | None: Path to config file, or None if not found.

    Raises:
        ValueError: If the explicit path is not an existing file.

    """
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_file():
            msg = f"config file not found: {explicit_path}"
            raise ValueError(msg)
        return path

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


def _parse_convention(value: object) -> str:
    """Check that a configured value names a convention.

    Args:
        value (object): Value read from the config file.

    Returns:
        str: The convention name.

    Raises:
        ValueError: If the value is not a convention name.

    """
    if isinstance(value, str) and value in CONVENTIONS:
        return value
    msg = f"'convention': invalid value {value!r}, expected one of {', '.join(CONVENTIONS)}."
    raise ValueError(msg)


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


def _parse_str_list(key: str, value: object, location: str = "") -> list[str]:
    """Check that a configured value is a list of strings.

    Args:
        key (str): Setting identifier, used in the error message.
        value (object): Value read from the config file.
        location (str): Config section carrying it, empty for the top level.

    Returns:
        list[str]: The value, unchanged.

    Raises:
        ValueError: If the value is not a list of strings.

    """
    if isinstance(value, list) and all(isinstance(item, str) for item in cast("list[object]", value)):
        return cast("list[str]", value)
    msg = f"{location}'{key}': expected a list of strings, got {value!r}."
    raise ValueError(msg)


def _parse_bool(key: str, value: object, location: str = "") -> bool:
    """Check that a configured value is a boolean.

    Args:
        key (str): Setting identifier, used in the error message.
        value (object): Value read from the config file.
        location (str): Config section carrying it, empty for the top level.

    Returns:
        bool: The value, unchanged.

    Raises:
        ValueError: If the value is not a boolean.

    """
    if isinstance(value, bool):
        return value
    msg = f"{location}'{key}': expected true or false, got {value!r}."
    raise ValueError(msg)


def _parse_option(key: str, value: object, location: str = "") -> int | bool | str:
    """Check an integer, boolean or choice option, clamping integers to their minimum.

    Args:
        key (str): Option identifier, a key of INT_OPTIONS, BOOL_OPTIONS or CHOICE_OPTIONS.
        value (object): Value read from the config file.
        location (str): Config section carrying it, empty for the top level.

    Returns:
        int | bool | str: The boolean or choice as is, or the integer clamped to its minimum.

    Raises:
        ValueError: If the value does not have the expected type or is not an accepted choice.

    """
    if key in BOOL_OPTIONS:
        return _parse_bool(key, value, location)

    if key in CHOICE_OPTIONS:
        if isinstance(value, str) and value in CHOICE_OPTIONS[key]:
            return value
        msg = f"{location}'{key}': invalid value {value!r}, expected one of {', '.join(CHOICE_OPTIONS[key])}."
        raise ValueError(msg)

    # bool is a subclass of int, reject it explicitly
    if isinstance(value, int) and not isinstance(value, bool):
        return max(INT_OPTIONS[key], value)
    msg = f"{location}'{key}': expected an integer, got {value!r}."
    raise ValueError(msg)


def _resolve_rules(select: list[str] | None, ignore: list[str], inherited: list[str]) -> list[str]:
    """Compute the enabled rules from select, ignore and the inherited set.

    Args:
        select (list[str] | None): Rules replacing the inherited set, ['ALL'] for every rule, None to keep it.
        ignore (list[str]): Rules removed afterwards.
        inherited (list[str]): Rules enabled before select and ignore apply.

    Returns:
        list[str]: Enabled rules, sorted.

    """
    if select is None:
        enabled = set(inherited)
    elif select == ["ALL"]:
        enabled = set(RULES_REGISTRY)
    else:
        enabled = {rule for rule in select if rule in RULES_REGISTRY}
    enabled -= set(ignore)
    return sorted(enabled)


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
    paths = _parse_str_list("paths", data.get("paths", []), "override: ")
    if not paths:
        msg = "an override must declare a non-empty 'paths' list."
        raise ValueError(msg)

    location = f"override {paths}: "
    override = ConfigOverride(paths=paths, ignore=_parse_str_list("ignore", data.get("ignore", []), location))

    if "select" in data:
        override.select = _parse_str_list("select", data["select"], location)

    _validate_rules(override.select or [], override.ignore, location)

    for key, value in data.items():
        if key in {"paths", "select", "ignore"}:
            continue
        if key in POLICIES_REGISTRY:
            override.values[key] = _parse_policy(key, value)
        elif key in OVERRIDABLE_OPTIONS:
            override.values[key] = _parse_option(key, value, location)
        elif key in CONFIG_KEYS:
            msg = f"override {paths}: '{key}' cannot be set per path, it applies to the whole run."
            raise ValueError(msg)
        else:
            _reject([key], "configuration key", f"override {paths}")

    return override


def _parse_scope(value: object) -> dict[str, bool]:
    """Parse the [scope] table.

    Args:
        value (object): Value read from the config file.

    Returns:
        dict[str, bool]: Scope key to whether that kind of entity is checked.

    Raises:
        ValueError: If the value is not a table.

    """
    if isinstance(value, dict):
        scope = cast("dict[str, object]", value)
        _reject(sorted(set(scope) - SCOPE_KEYS), "configuration key", "scope")
        return {key: _parse_bool(f"scope.{key}", item) for key, item in scope.items()}
    msg = f"'scope': expected a table, got {value!r}."
    raise ValueError(msg)


def _parse_overrides(value: object) -> list[ConfigOverride]:
    """Parse the [[overrides]] array of tables.

    Args:
        value (object): Value read from the config file.

    Returns:
        list[ConfigOverride]: Overrides in declaration order.

    Raises:
        ValueError: If the value is not an array of tables.

    """
    if isinstance(value, list) and all(isinstance(block, dict) for block in cast("list[object]", value)):
        return [_parse_override(block) for block in cast("list[dict[str, object]]", value)]
    msg = "'overrides': expected an array of tables."
    raise ValueError(msg)


def _parse_toml_config(data: dict[str, object]) -> LinterConfig:
    """Parse TOML config dict into LinterConfig.

    Args:
        data (dict[str, object]): Parsed TOML data from [tool.docstring-linter] section.

    Returns:
        LinterConfig: Populated configuration object.

    """
    config = LinterConfig()

    _reject(sorted(set(data) - CONFIG_KEYS), "configuration key")

    # The convention only moves the defaults: every key of the file still applies on top
    config.convention = _parse_convention(data.get("convention", config.convention))
    convention = CONVENTIONS[config.convention]
    for key, value in convention.values.items():
        setattr(config, key, value)
    config.enabled_rules = [rule for rule in config.enabled_rules if rule not in convention.disabled_rules]

    if "style" in data:
        config.style = _parse_style(data["style"])

    for key, value in _parse_scope(data.get("scope", {})).items():
        setattr(config, f"check_{key}", value)

    for key, value in data.items():
        if key in POLICIES_REGISTRY:
            setattr(config, key, _parse_policy(key, value))
        elif key in INT_OPTIONS or key in BOOL_OPTIONS or key in CHOICE_OPTIONS:
            setattr(config, key, _parse_option(key, value))

    if "exclude" in data:
        config.exclude_patterns = _parse_str_list("exclude", data["exclude"])

    config.overrides = _parse_overrides(data.get("overrides", []))

    select = _parse_str_list("select", data.get("select", []))
    ignore = _parse_str_list("ignore", data.get("ignore", []))
    _validate_rules(select, ignore)

    if select or ignore:
        config.enabled_rules = _resolve_rules(select or None, ignore, config.enabled_rules)

    return config
