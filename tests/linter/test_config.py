"""Tests for config module."""

import os
from pathlib import Path

import pytest
from linter.config import (
    OFF_BY_DEFAULT,
    RULES_REGISTRY,
    DocstringStyle,
    LinterConfig,
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
    """Select = ['ALL'] + ignore = ['args_match']: all rules except args_match."""
    config = _parse_toml_config({"select": ["ALL"], "ignore": ["args_match"]})
    assert "args_match" not in config.enabled_rules
    assert "docstring_exists" in config.enabled_rules


def test_parse_select_explicit_list() -> None:
    """Select = ['docstring_exists', 'args_match']: only those two rules enabled."""
    config = _parse_toml_config({"select": ["docstring_exists", "args_match"]})
    assert config.enabled_rules == ["args_match", "docstring_exists"]


def test_parse_ignore_only() -> None:
    """Ignore only (no select): starts from default set minus ignored rules."""
    config = _parse_toml_config({"ignore": ["args_match"]})
    assert "args_match" not in config.enabled_rules
    assert "docstring_exists" in config.enabled_rules


def test_parse_select_unknown_rule_ignored() -> None:
    """Select with an unknown rule name: unknown rule is silently ignored."""
    config = _parse_toml_config({"select": ["docstring_exists", "nonexistent_rule"]})
    assert "nonexistent_rule" not in config.enabled_rules
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
    """Style = 'unknown': raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid DocstringStyle"):
        _parse_toml_config({"style": "unknown"})


# ---------------------------------------------------------------------------
# _parse_toml_config -- other fields
# ---------------------------------------------------------------------------


def test_parse_exclude_empty_init_false() -> None:
    """exclude_empty_init = false: config.exclude_empty_init is False."""
    config = _parse_toml_config({"exclude_empty_init": False})
    assert config.exclude_empty_init is False


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


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_no_file_returns_default(tmp_path: Path) -> None:
    """Explicit path that does not exist: returns default LinterConfig."""
    config, config_file = load_config(str(tmp_path / "nonexistent.toml"))
    assert config.style == DocstringStyle.GOOGLE
    assert config.enabled_rules == LinterConfig().enabled_rules
    assert config_file is None


def test_load_config_toml_without_section_returns_default(tmp_path: Path) -> None:
    """pyproject.toml with no [tool.docstring-linter] section: returns default config."""
    f = tmp_path / "pyproject.toml"
    f.write_text("[tool.ruff]\nline-length = 100\n", encoding="utf-8")
    config, config_file = load_config(str(f))
    assert config.style == DocstringStyle.GOOGLE
    assert config_file is None


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
    assert "without_returns_none_init" in config.enabled_rules
    assert config_file == f


def test_load_config_standalone_toml(tmp_path: Path) -> None:
    """.docstring-linter.toml with flat config: parsed directly without [tool.docstring-linter]."""
    f = tmp_path / ".docstring-linter.toml"
    f.write_text('workers = 3\nselect = ["ALL"]\n', encoding="utf-8")
    config, config_file = load_config(str(f))
    assert config.workers == 3
    assert "without_returns_none_init" in config.enabled_rules
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
