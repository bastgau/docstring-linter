"""Tests for config module."""

import os
import re
from pathlib import Path

import pytest
from linter.config import (
    ALWAYS_ON,
    OFF_BY_DEFAULT,
    OPTIONS_REGISTRY,
    RULES_REGISTRY,
    DocstringStyle,
    LinterConfig,
    Policy,
    _parse_toml_config,  # pyright: ignore[reportPrivateUsage]
    load_config,
)

# ---------------------------------------------------------------------------
# LinterConfig defaults
# ---------------------------------------------------------------------------


def test_default_config_style() -> None:
    """Default config: style is GOOGLE."""
    assert LinterConfig().style == DocstringStyle.GOOGLE


def test_default_config_rules_exclude_off_by_default() -> None:
    """Default config: OFF_BY_DEFAULT rules are not in enabled_rules."""
    config = LinterConfig()
    for rule in OFF_BY_DEFAULT:
        assert rule not in config.enabled_rules


def test_default_config_all_other_rules_enabled() -> None:
    """Default config: all rules except OFF_BY_DEFAULT are enabled."""
    config = LinterConfig()
    for rule in RULES_REGISTRY:
        if rule not in OFF_BY_DEFAULT:
            assert rule in config.enabled_rules


def test_default_config_exclude_patterns_include_common_dirs() -> None:
    """Default config: exclude_patterns includes .venv, .git, __pycache__, .tox."""
    patterns = LinterConfig().exclude_patterns
    for expected in (".venv", ".git", "__pycache__", ".tox"):
        assert expected in patterns


def test_is_rule_enabled_true() -> None:
    """is_rule_enabled returns True for a rule in enabled_rules."""
    config = LinterConfig()
    assert config.is_rule_enabled("args_match") is True


def test_is_rule_enabled_false() -> None:
    """is_rule_enabled returns False for a rule not in enabled_rules."""
    config = LinterConfig(enabled_rules=["args_match"])
    assert config.is_rule_enabled("returns_section") is False


# ---------------------------------------------------------------------------
# _parse_toml_config -- select / ignore
# ---------------------------------------------------------------------------


def test_parse_select_all() -> None:
    """Select = ['ALL']: all rules in RULES_REGISTRY are enabled."""
    config = _parse_toml_config({"select": ["ALL"]})
    for rule in RULES_REGISTRY:
        assert rule in config.enabled_rules


def test_parse_select_all_with_ignore() -> None:
    """Select = ['ALL'] + ignore = ['imperative_mood']: all rules except imperative_mood."""
    config = _parse_toml_config({"select": ["ALL"], "ignore": ["imperative_mood"]})
    assert "imperative_mood" not in config.enabled_rules
    assert "docstring_exists" in config.enabled_rules


def test_parse_select_explicit_list() -> None:
    """Select = ['docstring_exists', 'args_match']: only those two rules enabled."""
    config = _parse_toml_config({"select": ["docstring_exists", "args_match"]})
    assert config.enabled_rules == ["args_match", "docstring_exists"]


def test_parse_ignore_only() -> None:
    """Ignore only (no select): starts from default set minus ignored rules."""
    config = _parse_toml_config({"ignore": ["imperative_mood"]})
    assert "imperative_mood" not in config.enabled_rules
    assert "docstring_exists" in config.enabled_rules


def test_parse_no_select_no_ignore() -> None:
    """Empty data: enabled_rules matches default config."""
    config = _parse_toml_config({})
    assert config.enabled_rules == LinterConfig().enabled_rules


# ---------------------------------------------------------------------------
# _parse_toml_config -- style
# ---------------------------------------------------------------------------


def test_parse_style_google() -> None:
    """Style = 'google': config.style is DocstringStyle.GOOGLE."""
    config = _parse_toml_config({"style": "google"})
    assert config.style == DocstringStyle.GOOGLE


def test_parse_style_unknown() -> None:
    """Style = 'unknown': raises ValueError listing the accepted styles."""
    with pytest.raises(ValueError, match=r"'style': invalid value 'unknown', expected one of google\."):
        _parse_toml_config({"style": "unknown"})


def test_parse_style_without_parser() -> None:
    """Style = 'numpy': rejected at load time, no parser implements it."""
    with pytest.raises(ValueError, match="'style': invalid value 'numpy'"):
        _parse_toml_config({"style": "numpy"})


# ---------------------------------------------------------------------------
# _parse_toml_config -- other fields
# ---------------------------------------------------------------------------


def test_parse_exclude_empty_init_method_false() -> None:
    """exclude_empty_init_method = false: config.exclude_empty_init_method is False."""
    config = _parse_toml_config({"exclude_empty_init_method": False})
    assert config.exclude_empty_init_method is False


def test_parse_exclude_empty_init_module_false() -> None:
    """exclude_empty_init_module = false: config.exclude_empty_init_module is False."""
    config = _parse_toml_config({"exclude_empty_init_module": False})
    assert config.exclude_empty_init_module is False


def test_parse_workers() -> None:
    """Workers = 4: config.workers is 4."""
    config = _parse_toml_config({"workers": 4})
    assert config.workers == 4


def test_parse_workers_zero_allowed() -> None:
    """Workers = 0: config.workers is 0 (auto-detect at runtime)."""
    config = _parse_toml_config({"workers": 0})
    assert config.workers == 0


def test_parse_scope_modules_false() -> None:
    """scope.modules = false: config.check_modules is False."""
    config = _parse_toml_config({"scope": {"modules": False}})
    assert config.check_modules is False


def test_parse_scope_all_false() -> None:
    """All scope flags set to false: all check_* fields are False."""
    config = _parse_toml_config({"scope": {"modules": False, "classes": False, "functions": False, "methods": False}})
    assert config.check_modules is False
    assert config.check_classes is False
    assert config.check_functions is False
    assert config.check_methods is False


def test_parse_exclude_patterns() -> None:
    """Exclude = ['test_*']: config.exclude_patterns is set."""
    config = _parse_toml_config({"exclude": ["test_*"]})
    assert config.exclude_patterns == ["test_*"]


def test_parse_ignore_placeholder_docstrings() -> None:
    """ignore_placeholder_docstrings = true: config flag is True."""
    config = _parse_toml_config({"ignore_placeholder_docstrings": True})
    assert config.ignore_placeholder_docstrings is True


def test_parse_summary_max_length() -> None:
    """summary_max_length = 72: config.summary_max_length is 72."""
    config = _parse_toml_config({"summary_max_length": 72})
    assert config.summary_max_length == 72


def test_parse_summary_max_length_minimum_one() -> None:
    """summary_max_length = 0: clamped to 1."""
    config = _parse_toml_config({"summary_max_length": 0})
    assert config.summary_max_length == 1


def test_parse_blank_lines_options() -> None:
    """blank_lines_before_section and blank_lines_before_closing_quotes: parsed as integers."""
    config = _parse_toml_config({"blank_lines_before_section": 2, "blank_lines_before_closing_quotes": 0})
    assert config.blank_lines_before_section == 2
    assert config.blank_lines_before_closing_quotes == 0


def test_parse_blank_lines_options_minimum_zero() -> None:
    """Negative blank line counts: clamped to 0."""
    config = _parse_toml_config({"blank_lines_before_section": -3, "blank_lines_before_closing_quotes": -1})
    assert config.blank_lines_before_section == 0
    assert config.blank_lines_before_closing_quotes == 0


def test_default_policies() -> None:
    """Default config: returns_none is required, init_returns_none is forbidden."""
    config = LinterConfig()
    assert config.returns_none is Policy.REQUIRED
    assert config.init_returns_none is Policy.FORBIDDEN


def test_parse_policies() -> None:
    """returns_none and init_returns_none: parsed into Policy members."""
    config = _parse_toml_config({"returns_none": "optional", "init_returns_none": "required"})
    assert config.returns_none is Policy.OPTIONAL
    assert config.init_returns_none is Policy.REQUIRED


def test_parse_policy_forbidden_allowed_on_returns_descriptions() -> None:
    """returns_descriptions = forbidden: accepted, the value is meaningful there."""
    config = _parse_toml_config({"returns_descriptions": "forbidden"})
    assert config.returns_descriptions is Policy.FORBIDDEN


def test_parse_policy_invalid_value() -> None:
    """Unknown policy value: raises ValueError naming the key and the accepted values."""
    with pytest.raises(ValueError, match="'returns_none': invalid value 'maybe', expected one of required, forbidden, optional"):
        _parse_toml_config({"returns_none": "maybe"})


def test_option_values_reflect_config() -> None:
    """option_values: returns every option of OPTIONS_REGISTRY with its current value."""
    config = _parse_toml_config({"exclude_empty_init_method": False, "summary_max_length": 72, "scope": {"modules": False}})
    values = config.option_values()
    assert set(values) == set(OPTIONS_REGISTRY)
    assert values["exclude_empty_init_method"] == "false"
    assert values["summary_max_length"] == "72"
    assert values["scope.modules"] == "false"
    assert values["style"] == "google"


def test_always_on_rule_stays_enabled_when_not_selected() -> None:
    """A rule listed in ALWAYS_ON: is_rule_enabled returns True even when not selected."""
    config = _parse_toml_config({"select": ["docstring_exists"]})
    for rule in ALWAYS_ON:
        assert rule not in config.enabled_rules
        assert config.is_rule_enabled(rule)


# ---------------------------------------------------------------------------
# convention
# ---------------------------------------------------------------------------


def test_convention_defaults_to_strict() -> None:
    """No convention key: strict convention, same settings as the built-in defaults."""
    config = _parse_toml_config({})
    assert config.convention == "strict"
    assert config.policy_values() == LinterConfig().policy_values()
    assert config.enabled_rules == LinterConfig().enabled_rules


def test_convention_google_sets_defaults() -> None:
    """Convention = 'google': relaxed policies, no blank line before the closing quotes, two rules off."""
    config = _parse_toml_config({"convention": "google"})
    assert config.returns_none is Policy.OPTIONAL
    assert config.init_returns_none is Policy.OPTIONAL
    assert config.documented_types is Policy.OPTIONAL
    assert config.raises_section is Policy.OPTIONAL
    assert config.attributes_section is Policy.OPTIONAL
    assert config.blank_lines_before_closing_quotes == 0
    assert config.type_matching == "lenient"
    assert config.exclude_dunder_methods is True
    assert config.exclude_private is True
    assert config.exclude_overridden is True
    assert config.properties_as_attributes is True
    assert config.init_args_location == "either"
    assert config.documented_stars is Policy.REQUIRED
    assert config.sections_optional_on_one_liners is True
    assert "imperative_mood" not in config.enabled_rules
    assert "return_type_annotation" not in config.enabled_rules
    assert "raises_extraneous" not in config.enabled_rules
    assert "args_order" in config.enabled_rules


def test_convention_explicit_keys_win() -> None:
    """Convention = 'google' with explicit keys: the keys of the file override the convention."""
    config = _parse_toml_config({"convention": "google", "documented_types": "required", "blank_lines_before_closing_quotes": 1})
    assert config.documented_types is Policy.REQUIRED
    assert config.blank_lines_before_closing_quotes == 1
    assert config.returns_none is Policy.OPTIONAL


def test_convention_ignore_applies_on_top() -> None:
    """Convention = 'google' with ignore: rules removed from the convention set, disabled ones stay off."""
    enabled = _parse_toml_config({"convention": "google", "ignore": ["args_order"]}).enabled_rules
    assert "args_order" not in enabled
    assert "imperative_mood" not in enabled


def test_convention_select_all_enables_everything() -> None:
    """Convention = 'google' with select = ['ALL']: every rule is enabled, the explicit key wins."""
    config = _parse_toml_config({"convention": "google", "select": ["ALL"]})
    assert config.enabled_rules == sorted(RULES_REGISTRY)


def test_convention_unknown() -> None:
    """Convention = 'numpy': raises ValueError listing the accepted conventions."""
    with pytest.raises(ValueError, match=re.escape("'convention': invalid value 'numpy', expected one of strict, google.")):
        _parse_toml_config({"convention": "numpy"})


def test_convention_rejected_in_override() -> None:
    """Convention in an override: rejected, it sets the defaults of the whole run."""
    with pytest.raises(ValueError, match="'convention' cannot be set per path"):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "convention": "google"}]})


def test_convention_listed_in_option_values() -> None:
    """option_values: reports the active convention."""
    assert _parse_toml_config({"convention": "google"}).option_values()["convention"] == "google"


# ---------------------------------------------------------------------------
# docstring exemptions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("option", ["exclude_dunder_methods", "exclude_private", "exclude_overridden", "properties_as_attributes", "sections_optional_on_one_liners"])
def test_exemption_options(option: str) -> None:
    """Exemption option: off by default, set from the file, allowed in an override."""
    assert getattr(_parse_toml_config({}), option) is False
    assert getattr(_parse_toml_config({option: True}), option) is True
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], option: True}]})
    assert getattr(config.for_path("tests/test_foo.py"), option) is True


def test_init_args_location() -> None:
    """init_args_location: 'init' by default, accepts class and either, rejects other values."""
    assert _parse_toml_config({}).init_args_location == "init"
    assert _parse_toml_config({"init_args_location": "class"}).init_args_location == "class"
    with pytest.raises(ValueError, match=re.escape("'init_args_location': invalid value 'both', expected one of init, class, either.")):
        _parse_toml_config({"init_args_location": "both"})


# ---------------------------------------------------------------------------
# type_matching
# ---------------------------------------------------------------------------


def test_type_matching_default_strict() -> None:
    """No type_matching key: strict comparison."""
    assert _parse_toml_config({}).type_matching == "strict"


def test_type_matching_set() -> None:
    """type_matching = 'equivalent': stored as is and reported by option_values."""
    config = _parse_toml_config({"type_matching": "equivalent"})
    assert config.type_matching == "equivalent"
    assert config.option_values()["type_matching"] == "equivalent"


def test_type_matching_invalid() -> None:
    """type_matching = 'loose': raises ValueError listing the accepted levels."""
    with pytest.raises(ValueError, match=re.escape("'type_matching': invalid value 'loose', expected one of strict, equivalent, lenient.")):
        _parse_toml_config({"type_matching": "loose"})


def test_type_matching_in_override() -> None:
    """type_matching in an override: applied to the matching files only."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "type_matching": "lenient"}]})
    assert config.for_path("tests/test_foo.py").type_matching == "lenient"
    assert config.for_path("src/foo.py").type_matching == "strict"


# ---------------------------------------------------------------------------
# value types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"workers": "4"}, "'workers': expected an integer, got '4'"),
        ({"summary_max_length": True}, "'summary_max_length': expected an integer, got True"),
        ({"exclude_empty_init_method": "no"}, "'exclude_empty_init_method': expected true or false, got 'no'"),
        ({"exclude": "src"}, "'exclude': expected a list of strings, got 'src'"),
        ({"select": "ALL"}, "'select': expected a list of strings, got 'ALL'"),
        ({"ignore": ["imperative_mood", 3]}, "'ignore': expected a list of strings"),
        ({"scope": "all"}, "'scope': expected a table, got 'all'"),
        ({"scope": {"modules": "yes"}}, "'scope.modules': expected true or false, got 'yes'"),
        ({"overrides": ["tests/**"]}, "'overrides': expected an array of tables"),
    ],
)
def test_parse_rejects_wrong_value_type(data: dict[str, object], message: str) -> None:
    """Value of the wrong TOML type: raises ValueError naming the key and the value."""
    with pytest.raises(ValueError, match=re.escape(message)):
        _parse_toml_config(data)


def test_parse_override_rejects_wrong_value_type() -> None:
    """Option of the wrong type in an override: raises ValueError naming the override."""
    with pytest.raises(ValueError, match=re.escape("override ['tests/**']: 'summary_max_length': expected an integer, got 'x'")):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "summary_max_length": "x"}]})


def test_parse_override_rejects_string_paths() -> None:
    """Paths given as a string in an override: raises ValueError."""
    with pytest.raises(ValueError, match=re.escape("override: 'paths': expected a list of strings")):
        _parse_toml_config({"overrides": [{"paths": "tests/**"}]})


def test_parse_override_option_clamped() -> None:
    """summary_max_length = -5 in an override: clamped to 1, like at the top level."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "summary_max_length": -5}]})
    assert config.for_path("tests/test_foo.py").summary_max_length == 1


# ---------------------------------------------------------------------------
# unknown keys and rules
# ---------------------------------------------------------------------------


def test_parse_unknown_key() -> None:
    """Key absent from the registries: raises ValueError naming it."""
    with pytest.raises(ValueError, match="unknown configuration key 'param_order'"):
        _parse_toml_config({"param_order": True})


def test_parse_unknown_keys_are_all_reported() -> None:
    """Several unknown keys: all of them are named in the message."""
    with pytest.raises(ValueError, match="unknown configuration keys 'allow_oneliner', 'summary_punctuation'"):
        _parse_toml_config({"allow_oneliner": True, "summary_punctuation": True})


def test_parse_unknown_scope_key() -> None:
    """Unknown key under scope: raises ValueError naming the section."""
    with pytest.raises(ValueError, match="scope: unknown configuration key 'function'"):
        _parse_toml_config({"scope": {"function": True}})


def test_parse_unknown_rule_in_select() -> None:
    """Unknown rule name in select: raises ValueError naming it."""
    with pytest.raises(ValueError, match="select: unknown rule 'param_order'"):
        _parse_toml_config({"select": ["args_order", "param_order"]})


def test_parse_unknown_rule_in_ignore() -> None:
    """Unknown rule name in ignore: raises ValueError naming it."""
    with pytest.raises(ValueError, match="ignore: unknown rule 'docstring_exist'"):
        _parse_toml_config({"ignore": ["docstring_exist"]})


def test_parse_select_all_is_accepted() -> None:
    """Select = ALL: the wildcard is not treated as a rule name."""
    config = _parse_toml_config({"select": ["ALL"]})
    assert set(config.enabled_rules) == set(RULES_REGISTRY)


def test_parse_ignore_always_on_rule() -> None:
    """Always-on rule in ignore: raises ValueError instead of silently doing nothing."""
    with pytest.raises(ValueError, match="ignore: 'blank_lines' cannot be ignored"):
        _parse_toml_config({"ignore": ["blank_lines"]})


# ---------------------------------------------------------------------------
# overrides
# ---------------------------------------------------------------------------


def test_parse_override_policy_and_option() -> None:
    """Override carrying a policy and an option: both are parsed."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "args_section": "optional", "summary_max_length": 120}]})
    assert len(config.overrides) == 1
    assert config.overrides[0].paths == ["tests/**"]
    assert config.overrides[0].values["args_section"] is Policy.OPTIONAL
    assert config.overrides[0].values["summary_max_length"] == 120


def test_parse_override_without_paths() -> None:
    """Override missing its paths list: raises ValueError."""
    with pytest.raises(ValueError, match="non-empty 'paths'"):
        _parse_toml_config({"overrides": [{"args_section": "optional"}]})


def test_parse_override_run_level_key() -> None:
    """Override carrying a run-level key: raises ValueError naming the key."""
    with pytest.raises(ValueError, match="'exclude' cannot be set per path"):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "exclude": ["x"]}]})


def test_parse_override_unknown_key() -> None:
    """Override carrying an unknown key: raises ValueError naming the override."""
    with pytest.raises(ValueError, match=r"override \['tests/\*\*'\]: unknown configuration key 'allow_oneliner'"):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "allow_oneliner": True}]})


def test_parse_override_unknown_rule() -> None:
    """Override ignoring an unknown rule: raises ValueError naming the override."""
    with pytest.raises(ValueError, match=r"override \['tests/\*\*'\]: ignore: unknown rule 'param_order'"):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "ignore": ["param_order"]}]})


def test_parse_override_invalid_policy_value() -> None:
    """Override carrying an invalid policy value: raises ValueError naming the key."""
    with pytest.raises(ValueError, match="'args_section': invalid value 'maybe'"):
        _parse_toml_config({"overrides": [{"paths": ["tests/**"], "args_section": "maybe"}]})


def test_for_path_without_override_returns_self() -> None:
    """No override declared: for_path returns the very same config object."""
    config = LinterConfig()
    assert config.for_path("src/foo.py") is config


def test_for_path_applies_matching_override() -> None:
    """Matching override: the policy is overridden, the base config is left untouched."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "args_section": "optional"}]})
    resolved = config.for_path("tests/linter/test_foo.py")
    assert resolved.args_section is Policy.OPTIONAL
    assert config.args_section is Policy.REQUIRED


def test_for_path_ignores_non_matching_override() -> None:
    """Override whose patterns do not match: the base config is returned as is."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "args_section": "optional"}]})
    assert config.for_path("src/foo.py").args_section is Policy.REQUIRED


def test_for_path_last_override_wins() -> None:
    """Two matching overrides: the last declared one wins."""
    config = _parse_toml_config(
        {
            "overrides": [
                {"paths": ["tests/**"], "args_section": "optional"},
                {"paths": ["tests/integration/**"], "args_section": "forbidden"},
            ]
        }
    )
    assert config.for_path("tests/integration/test_x.py").args_section is Policy.FORBIDDEN
    assert config.for_path("tests/unit/test_y.py").args_section is Policy.OPTIONAL


def test_for_path_earlier_override_not_merged() -> None:
    """Two matching overrides: only the last one applies, the earlier keys are dropped."""
    config = _parse_toml_config(
        {
            "overrides": [
                {"paths": ["tests/**"], "summary_max_length": 120, "ignore": ["imperative_mood"]},
                {"paths": ["tests/integration/**"], "args_section": "forbidden"},
            ]
        }
    )
    resolved = config.for_path("tests/integration/test_x.py")
    assert resolved.args_section is Policy.FORBIDDEN
    assert resolved.summary_max_length == LinterConfig().summary_max_length
    assert "imperative_mood" in resolved.enabled_rules


def test_for_path_ignore_removes_from_inherited_rules() -> None:
    """Ignore key in an override: the rule is removed from the inherited set."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "ignore": ["imperative_mood"]}]})
    resolved = config.for_path("tests/test_foo.py")
    assert "imperative_mood" not in resolved.enabled_rules
    assert "imperative_mood" in config.enabled_rules


def test_for_path_select_replaces_inherited_rules() -> None:
    """Select key in an override: the inherited set is replaced by the listed rules."""
    config = _parse_toml_config({"overrides": [{"paths": ["tests/**"], "select": ["docstring_exists"]}]})
    assert config.for_path("tests/test_foo.py").enabled_rules == ["docstring_exists"]


def test_for_path_override_select_all() -> None:
    """Select = ['ALL'] in an override: every rule is enabled on the matching files."""
    config = _parse_toml_config({"ignore": ["imperative_mood"], "overrides": [{"paths": ["tests/**"], "select": ["ALL"]}]})
    assert config.for_path("tests/test_foo.py").enabled_rules == sorted(RULES_REGISTRY)


def test_for_path_patterns_relative_to_base_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run from a subdirectory: the override pattern is matched relative to base_dir, not to the current directory."""
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path / "src")
    config = _parse_toml_config({"overrides": [{"paths": ["src/**"], "args_section": "optional"}]})
    config.base_dir = tmp_path
    assert config.for_path("foo.py").args_section is Policy.OPTIONAL


def test_for_path_file_outside_base_dir(tmp_path: Path) -> None:
    """File outside base_dir: no override applies, even with a catch-all pattern."""
    config = _parse_toml_config({"overrides": [{"paths": ["**"], "args_section": "optional"}]})
    config.base_dir = tmp_path / "project"
    assert config.for_path(str(tmp_path / "other" / "foo.py")) is config


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_missing_explicit_file(tmp_path: Path) -> None:
    """Explicit path that does not exist: raises ValueError naming the path."""
    with pytest.raises(ValueError, match=r"config file not found: .*nonexistent\.toml"):
        load_config(str(tmp_path / "nonexistent.toml"))


def test_load_config_explicit_directory(tmp_path: Path) -> None:
    """Explicit path that is a directory: raises ValueError."""
    with pytest.raises(ValueError, match="config file not found"):
        load_config(str(tmp_path))


def test_load_config_base_dir_is_config_directory(tmp_path: Path) -> None:
    """Explicit config file: base_dir is the resolved directory holding it."""
    (tmp_path / "tools").mkdir()
    f = tmp_path / "tools" / "linter.toml"
    f.write_text("", encoding="utf-8")
    config, _ = load_config(str(tmp_path / "tools" / ".." / "tools" / "linter.toml"))
    assert config.base_dir == (tmp_path / "tools").resolve()


def test_load_config_toml_without_section(tmp_path: Path) -> None:
    """Explicit pyproject.toml with no [tool.docstring-linter] section: raises ValueError."""
    f = tmp_path / "pyproject.toml"
    f.write_text("[tool.ruff]\nline-length = 100\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"no \[tool.docstring-linter\] section"):
        load_config(str(f))


def test_load_config_auto_discover(tmp_path: Path) -> None:
    """No explicit path: load_config walks up directories to find pyproject.toml."""
    f = tmp_path / "pyproject.toml"
    f.write_text("[tool.docstring-linter]\nworkers = 2\n", encoding="utf-8")
    subdir = tmp_path / "src" / "mymodule"
    subdir.mkdir(parents=True)

    old_cwd = Path.cwd()
    try:
        os.chdir(subdir)
        config, config_file = load_config()
        assert config.workers == 2
        assert config_file == f
    finally:
        os.chdir(old_cwd)


def test_load_config_toml_with_section(tmp_path: Path) -> None:
    """pyproject.toml with [tool.docstring-linter] section: config is populated."""
    f = tmp_path / "pyproject.toml"
    f.write_text('[tool.docstring-linter]\nselect = ["ALL"]\nworkers = 4\n', encoding="utf-8")
    config, config_file = load_config(str(f))
    assert config.workers == 4
    assert "returns_match" in config.enabled_rules
    assert config_file == f


def test_load_config_standalone_toml(tmp_path: Path) -> None:
    """.docstring-linter.toml with flat config: parsed directly without [tool.docstring-linter]."""
    f = tmp_path / ".docstring-linter.toml"
    f.write_text('workers = 3\nselect = ["ALL"]\n', encoding="utf-8")
    config, config_file = load_config(str(f))
    assert config.workers == 3
    assert "returns_match" in config.enabled_rules
    assert config_file == f


def test_load_config_custom_named_toml(tmp_path: Path) -> None:
    """Explicitly passed non-pyproject.toml file: parsed directly regardless of name."""
    f = tmp_path / "my-linter.toml"
    f.write_text("workers = 5\n", encoding="utf-8")
    config, config_file = load_config(str(f))
    assert config.workers == 5
    assert config_file == f


def test_load_config_auto_discover_standalone(tmp_path: Path) -> None:
    """No explicit path: .docstring-linter.toml discovered when no pyproject.toml present."""
    f = tmp_path / ".docstring-linter.toml"
    f.write_text("workers = 7\n", encoding="utf-8")
    subdir = tmp_path / "src"
    subdir.mkdir()

    old_cwd = Path.cwd()
    try:
        os.chdir(subdir)
        config, config_file = load_config()
        assert config.workers == 7
        assert config_file == f
    finally:
        os.chdir(old_cwd)


def test_load_config_pyproject_takes_priority_over_standalone(tmp_path: Path) -> None:
    """Both pyproject.toml and .docstring-linter.toml present: pyproject.toml wins."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.docstring-linter]\nworkers = 1\n", encoding="utf-8")
    (tmp_path / ".docstring-linter.toml").write_text("workers = 9\n", encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        config, config_file = load_config()
        assert config.workers == 1
        assert config_file == pyproject
    finally:
        os.chdir(old_cwd)
