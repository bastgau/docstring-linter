"""Consistency tests between the rule and policy registries, the config, the rules package and the docs."""

import dataclasses
import re
from pathlib import Path

from linter.config import ALWAYS_ON, CONVENTIONS, POLICIES_REGISTRY, RULES_CATEGORIES, RULES_REGISTRY, LinterConfig, Policy

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
