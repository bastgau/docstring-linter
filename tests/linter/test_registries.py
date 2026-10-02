"""Consistency tests between the rule and policy registries, the config, the rules package, the docs and TESTS.md."""

import ast
import dataclasses
import re
from pathlib import Path

from linter.config import (
    ALWAYS_ON,
    CONFIG_KEYS,
    CONVENTIONS,
    OPTIONS_REGISTRY,
    OVERRIDABLE_OPTIONS,
    POLICIES_REGISTRY,
    RULES_CATEGORIES,
    RULES_REGISTRY,
    SCOPE_KEYS,
    TYPED_OPTIONS,
    LinterConfig,
    Policy,
)

_ROOT = Path(__file__).resolve().parents[2]


def _doc_headings() -> set[str]:
    """Collect the identifiers named by the headings of the docs pages, code blocks excluded."""
    names: set[str] = set()
    for page in (_ROOT / "docs").glob("*.md"):
        text = re.sub(r"^```.*?^```", "", page.read_text(encoding="utf-8"), flags=re.DOTALL | re.MULTILINE)
        for heading in re.findall(r"^#+ (.+)$", text, flags=re.MULTILINE):
            names.update(name.strip().strip("`") for name in heading.split(","))
    return names


def test_every_rule_in_exactly_one_category() -> None:
    """Each rule of RULES_REGISTRY appears in one category of RULES_CATEGORIES, and nothing else does."""
    categorized = [rule for rules in RULES_CATEGORIES.values() for rule in rules]
    assert sorted(categorized) == sorted(RULES_REGISTRY)


def test_rule_subsets_are_registered_rules() -> None:
    """ALWAYS_ON and the rules each convention disables only name registered rules, never an always-on one."""
    assert ALWAYS_ON.issubset(RULES_REGISTRY)
    for convention in CONVENTIONS.values():
        assert convention.disabled_rules.issubset(RULES_REGISTRY)
        assert convention.disabled_rules.isdisjoint(ALWAYS_ON)


def test_every_policy_is_a_config_field() -> None:
    """Each policy of POLICIES_REGISTRY is a LinterConfig field holding a Policy."""
    defaults = {field.name: field.default for field in dataclasses.fields(LinterConfig)}
    for policy in POLICIES_REGISTRY:
        assert isinstance(defaults.get(policy), Policy), policy


def test_every_rule_and_policy_documented() -> None:
    """Each rule and policy has a heading of its own in the docs pages."""
    missing = (set(RULES_REGISTRY) | set(POLICIES_REGISTRY)) - _doc_headings()
    assert not missing


def test_every_rule_reported_by_the_rules_package() -> None:
    """Each rule identifier is written as a string literal in the rules package, where errors are made."""
    source = "".join(path.read_text(encoding="utf-8") for path in (_ROOT / "src" / "linter" / "rules").glob("*.py"))
    missing = [rule for rule in RULES_REGISTRY if f'"{rule}"' not in source]
    assert not missing


def test_every_listed_option_is_a_typed_config_field() -> None:
    """Each option shown by --list-rules is a LinterConfig field, typed unless it is the convention or a scope flag."""
    fields = {field.name for field in dataclasses.fields(LinterConfig)}
    scope_options = {f"scope.{key}" for key in SCOPE_KEYS}
    assert {f"check_{key}" for key in SCOPE_KEYS} <= fields
    assert set(OPTIONS_REGISTRY) - scope_options <= fields
    # workers is typed but not listed: it changes how the run goes, not what is checked
    assert set(OPTIONS_REGISTRY) - scope_options - {"convention"} == TYPED_OPTIONS - {"workers"}


def test_every_config_key_documented() -> None:
    """The key table of docs/configuration.md has one row per accepted key, scope flags spelled out."""
    text = (_ROOT / "docs" / "configuration.md").read_text(encoding="utf-8")
    table = text[text.index("### Available keys") : text.index("### Exclusion patterns")]
    rows = set(re.findall(r"^\| `([\w.]+)` \|", table, flags=re.MULTILINE))
    assert rows == (CONFIG_KEYS - {"scope", "overrides"}) | {f"scope.{key}" for key in SCOPE_KEYS}


def test_override_options_documented() -> None:
    """The override section of docs/configuration.md names exactly the options an override may carry."""
    text = (_ROOT / "docs" / "configuration.md").read_text(encoding="utf-8")
    line = next(line for line in text.splitlines() if line.startswith("- An override may carry"))
    assert set(re.findall(r"`(\w+)`", line)) == OVERRIDABLE_OPTIONS


def test_every_test_function_listed_in_tests_md() -> None:
    """TESTS.md has one row per test function of tests/linter, and no row for a missing one."""
    tests_dir = _ROOT / "tests" / "linter"
    functions = {
        (path.relative_to(tests_dir).as_posix(), node.name)
        for path in tests_dir.rglob("test_*.py")
        for node in ast.parse(path.read_text(encoding="utf-8")).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
    rows = set(re.findall(r"^\| `([\w/]+\.py)` \| `(\w+)` \|", (_ROOT / "TESTS.md").read_text(encoding="utf-8"), flags=re.MULTILINE))
    assert sorted(functions - rows) == []
    assert sorted(rows - functions) == []
