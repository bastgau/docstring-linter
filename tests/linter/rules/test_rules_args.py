"""Tests for rules/args.py -- return type, args match, returns section, raises match."""

from linter.config import Policy
from linter.models import ArgInfo, DocstringArg, DocstringRaise, DocstringReturn, NodeType, ParsedDocstring, RaiseInfo

from linter.rules import validate_entity

from .conftest import _class, _func, _neutral, _policy_only, _rule_only  # pyright: ignore[reportPrivateUsage]

# ---------------------------------------------------------------------------
# Rule => return_type_annotation
# ---------------------------------------------------------------------------


def test_return_type_annotation_missing() -> None:
    """Function without -> annotation: returns return_type_annotation error."""
    entity = _func(return_type=None)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("return_type_annotation"))
    assert len(errors) == 1
    assert errors[0].rule == "return_type_annotation"


def test_return_type_annotation_present() -> None:
    """Function with -> int annotation: no error."""
    entity = _func(return_type="int")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int")), _rule_only("return_type_annotation"))
    assert not errors


def test_return_type_annotation_not_checked_for_class() -> None:
    """Class entity: return_type_annotation rule is not applied."""
    entity, doc = _class()
    doc.attributes = []
    errors = validate_entity(entity, doc, _rule_only("return_type_annotation"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => args_match
# ---------------------------------------------------------------------------


def test_args_section_required_missing() -> None:
    """Policy required, arg in signature but not in docstring: returns args_section error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("args_section", Policy.REQUIRED))
    assert any(e.rule == "args_section" and "x" in e.message for e in errors)


def test_args_section_optional_missing() -> None:
    """Policy optional, arg in signature but not in docstring: no error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("args_section", Policy.OPTIONAL))
    assert not errors


def test_args_section_optional_still_checks_documented_args() -> None:
    """Policy optional, a documented arg with a wrong type: args_match still reports it."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation="str", description="A value.")])
    cfg = _neutral(enabled_rules=["args_match"], args_section=Policy.OPTIONAL)
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "args_match" and "type mismatch" in e.message for e in errors)


def test_args_section_forbidden_present() -> None:
    """Policy forbidden, documented args: returns args_section error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation="int", description="A value.")])
    errors = validate_entity(entity, doc, _policy_only("args_section", Policy.FORBIDDEN))
    assert any(e.rule == "args_section" and "not allowed" in e.message for e in errors)


def test_args_section_starred_args_documented() -> None:
    """*args and **kwargs documented with their stars: no error."""
    entity = _func(args=[ArgInfo(name="*rest", type_annotation="str"), ArgInfo(name="**opts", type_annotation="object")])
    doc = ParsedDocstring(
        summary="Do something.",
        args=[
            DocstringArg(name="*rest", type_annotation="str", description="Fragments."),
            DocstringArg(name="**opts", type_annotation="object", description="Options."),
        ],
    )
    errors = validate_entity(entity, doc, _neutral(args_section=Policy.REQUIRED, documented_types=Policy.REQUIRED))
    assert not errors


def test_args_section_starred_args_undocumented() -> None:
    """**kwargs in signature but not documented: returns args_section error."""
    entity = _func(args=[ArgInfo(name="**opts", type_annotation="object")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("args_section", Policy.REQUIRED))
    assert any(e.rule == "args_section" and "**opts" in e.message for e in errors)


def test_args_match_extra_in_docstring() -> None:
    """Arg in docstring but not in signature: returns args_match error."""
    entity = _func(args=[])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="ghost", type_annotation="str", description="A ghost arg.")])
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert any("ghost" in e.message and "not in signature" in e.message for e in errors)


def test_args_match_type_mismatch() -> None:
    """Arg type in docstring differs from signature: returns args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation="str", description="A value.")])
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert any("type mismatch" in e.message for e in errors)


def test_args_match_missing_type_in_docstring() -> None:
    """Arg missing type in docstring: returns args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation=None, description="A value.")])
    errors = validate_entity(entity, doc, _neutral(documented_types=Policy.REQUIRED))
    assert any(e.rule == "args_match" and "missing type" in e.message for e in errors)


def test_args_match_type_optional() -> None:
    """Policy optional, arg documented without a type: no args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation=None, description="A value.")])
    errors = validate_entity(entity, doc, _neutral(documented_types=Policy.OPTIONAL))
    assert not any(e.rule == "args_match" for e in errors)


def test_args_match_type_forbidden() -> None:
    """Policy forbidden, arg documented with a type: returns args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation="int", description="A value.")])
    errors = validate_entity(entity, doc, _neutral(documented_types=Policy.FORBIDDEN))
    assert any(e.rule == "args_match" and "must not declare a type" in e.message for e in errors)


def test_args_match_correct() -> None:
    """Arg matches signature and docstring perfectly: no error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(summary="Do something.", args=[DocstringArg(name="x", type_annotation="int", description="A value.")])
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert not errors


def test_args_match_missing_description_in_docstring() -> None:
    """Arg with no description in docstring: returns args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(
        summary="Do something.",
        args=[DocstringArg(name="x", type_annotation="int", description=None)],
    )
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "args_match" and "missing description" in e.message for e in errors)


def test_args_match_no_sig_args_no_doc_args() -> None:
    """No args in signature and no args in docstring: no error."""
    entity = _func(args=[])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("args_match"))
    assert not errors


def test_args_match_doc_arg_extra_via_detailed_path() -> None:
    """Arg in sig and doc but extra doc arg: reports the extra."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    doc = ParsedDocstring(
        summary="Do something.",
        args=[
            DocstringArg(name="x", type_annotation="int", description="A value."),
            DocstringArg(name="extra", type_annotation="str", description="Ghost."),
        ],
    )
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert any("extra" in e.message and "not in signature" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Rule => returns_section
# ---------------------------------------------------------------------------


def test_returns_section_required_missing() -> None:
    """Policy required, return type but no Returns section: returns returns_section error."""
    entity = _func(return_type="int")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("returns_section", Policy.REQUIRED))
    assert any(e.rule == "returns_section" and "Missing" in e.message for e in errors)


def test_returns_section_optional_missing() -> None:
    """Policy optional, return type but no Returns section: no error."""
    entity = _func(return_type="int")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("returns_section", Policy.OPTIONAL))
    assert not errors


def test_returns_section_optional_still_checks_type() -> None:
    """Policy optional, a Returns section with a wrong type: returns_match still reports it."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="str"))
    errors = validate_entity(entity, doc, _neutral(returns_section=Policy.OPTIONAL))
    assert any(e.rule == "returns_match" for e in errors)


def test_returns_section_forbidden_present() -> None:
    """Policy forbidden, Returns section present: returns returns_section error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int", description="Result."))
    errors = validate_entity(entity, doc, _policy_only("returns_section", Policy.FORBIDDEN))
    assert any(e.rule == "returns_section" and "not allowed" in e.message for e in errors)


def test_returns_section_correct() -> None:
    """Returns section matches signature: no error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int", description="The result."))
    errors = validate_entity(entity, doc, _policy_only("returns_section", Policy.REQUIRED))
    assert not errors


def test_returns_section_ignores_none_return_type() -> None:
    """Function -> None without Returns section: returns_section does not flag it."""
    entity = _func(return_type="None")
    cfg = _neutral(returns_section=Policy.REQUIRED, returns_none=Policy.OPTIONAL)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), cfg)
    assert not errors


# ---------------------------------------------------------------------------
# Rule => returns_match
# ---------------------------------------------------------------------------


def test_returns_match_mismatch() -> None:
    """Returns section type differs from signature: returns returns_match error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="str"))
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "returns_match" and "mismatch" in e.message for e in errors)


def test_returns_match_missing_type() -> None:
    """Returns section present but no type declared: returns returns_match error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation=None))
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "returns_match" and "Missing type" in e.message for e in errors)


def test_returns_match_no_section_no_error() -> None:
    """No Returns section: returns_match does not flag a missing section."""
    entity = _func(return_type="int")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _neutral())
    assert not errors


def test_returns_match_cannot_be_disabled() -> None:
    """Rule listed in ignore: the type mismatch is still reported, the rule is always on."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="str"))
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "returns_match" for e in errors)


def test_returns_match_missing_description() -> None:
    """Policy required, Returns section without a description: returns returns_match error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int"))
    errors = validate_entity(entity, doc, _neutral(returns_descriptions=Policy.REQUIRED))
    assert any(e.rule == "returns_match" and "Missing description" in e.message for e in errors)


def test_returns_match_none_exempt_from_description() -> None:
    """Policy required, 'Returns: None': the description is not demanded."""
    entity = _func(return_type="None")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, _neutral(returns_descriptions=Policy.REQUIRED))
    assert not errors


def test_returns_descriptions_optional() -> None:
    """Policy optional: a Returns line without description is accepted."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int"))
    errors = validate_entity(entity, doc, _neutral(returns_descriptions=Policy.OPTIONAL))
    assert not errors


def test_returns_descriptions_forbidden() -> None:
    """Policy forbidden: a Returns line carrying a description is reported."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int", description="The result."))
    errors = validate_entity(entity, doc, _neutral(returns_descriptions=Policy.FORBIDDEN))
    assert any(e.rule == "returns_match" and "must not carry a description" in e.message for e in errors)


def test_returns_match_correct() -> None:
    """Returns section type matches signature: no returns_match error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int", description="The result."))
    errors = validate_entity(entity, doc, _neutral())
    assert not errors


# ---------------------------------------------------------------------------
# Policy => returns_none
# ---------------------------------------------------------------------------


def test_returns_none_required_missing() -> None:
    """Policy required, no Returns section: returns returns_none error."""
    entity = _func(return_type="None", docstring="Do something.\n\nArgs:\n    x (int): X.\n", raw_docstring="Do something.\n\nArgs:\n    x (int): X.\n")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _neutral(returns_none=Policy.REQUIRED))
    assert any(e.rule == "returns_none" and "Missing" in e.message for e in errors)


def test_returns_none_required_present() -> None:
    """Policy required, Returns: None section present: no error."""
    entity = _func(return_type="None")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, _neutral(returns_none=Policy.REQUIRED))
    assert not errors


def test_returns_none_required_flags_oneliner() -> None:
    """Policy required, one-liner docstring cannot hold the section: returns returns_none error."""
    entity = _func(return_type="None", docstring="Do something.", raw_docstring="Do something.")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _neutral(returns_none=Policy.REQUIRED))
    assert any(e.rule == "returns_none" for e in errors)


def test_returns_none_forbidden_present() -> None:
    """Policy forbidden, Returns: None section present: returns returns_none error."""
    entity = _func(return_type="None")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, _neutral(returns_none=Policy.FORBIDDEN))
    assert any(e.rule == "returns_none" and "not allowed" in e.message for e in errors)


def test_returns_none_forbidden_missing() -> None:
    """Policy forbidden, no Returns section: no error."""
    entity = _func(return_type="None")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _neutral(returns_none=Policy.FORBIDDEN))
    assert not errors


def test_returns_none_optional_accepts_both() -> None:
    """Policy optional: section present or absent, no error either way."""
    entity = _func(return_type="None")
    cfg = _neutral(returns_none=Policy.OPTIONAL)
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="None"))
    assert not validate_entity(entity, ParsedDocstring(summary="Do something."), cfg)
    assert not validate_entity(entity, doc, cfg)


def test_returns_none_skips_init() -> None:
    """__init__ -> None is not covered by the returns_none policy."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    cfg = _neutral(returns_none=Policy.REQUIRED, init_returns_none=Policy.OPTIONAL)
    errors = validate_entity(entity, ParsedDocstring(summary="Init."), cfg)
    assert not errors


def test_returns_none_skips_generator() -> None:
    """Generator is not covered by the returns_none policy."""
    entity = _func(return_type="None", is_generator=True)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _neutral(returns_none=Policy.REQUIRED))
    assert not errors


def test_returns_none_skipped_when_returns_section_forbidden() -> None:
    """returns_section forbidden: the returns_none policy is not applied."""
    entity = _func(return_type="None")
    cfg = _neutral(returns_section=Policy.FORBIDDEN, returns_none=Policy.REQUIRED)
    assert not validate_entity(entity, ParsedDocstring(summary="Do something."), cfg)


# ---------------------------------------------------------------------------
# Policy => init_returns_none
# ---------------------------------------------------------------------------


def test_init_returns_none_required_missing() -> None:
    """Policy required, __init__ without Returns section: returns init_returns_none error."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD, docstring="Init.\n\nArgs:\n    x (int): X.\n", raw_docstring="Init.\n\nArgs:\n    x (int): X.\n")
    errors = validate_entity(entity, ParsedDocstring(summary="Init."), _neutral(init_returns_none=Policy.REQUIRED))
    assert any(e.rule == "init_returns_none" and "Missing" in e.message for e in errors)


def test_init_returns_none_required_present() -> None:
    """Policy required, __init__ with Returns: None section: no error."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    doc = ParsedDocstring(summary="Init.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, _neutral(init_returns_none=Policy.REQUIRED))
    assert not errors


def test_init_returns_none_forbidden_present() -> None:
    """Policy forbidden, __init__ with Returns: None section: returns init_returns_none error."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    doc = ParsedDocstring(summary="Init.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, _policy_only("init_returns_none", Policy.FORBIDDEN))
    assert any(e.rule == "init_returns_none" and "not allowed" in e.message for e in errors)


def test_init_returns_none_optional_accepts_both() -> None:
    """Policy optional: section present or absent on __init__, no error either way."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    cfg = _neutral(init_returns_none=Policy.OPTIONAL)
    doc = ParsedDocstring(summary="Init.", returns=DocstringReturn(type_annotation="None"))
    assert not validate_entity(entity, ParsedDocstring(summary="Init."), cfg)
    assert not validate_entity(entity, doc, cfg)


def test_init_returns_none_skipped_when_returns_section_forbidden() -> None:
    """returns_section forbidden: the init_returns_none policy is not applied."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    cfg = _neutral(returns_section=Policy.FORBIDDEN, init_returns_none=Policy.REQUIRED)
    assert not validate_entity(entity, ParsedDocstring(summary="Init."), cfg)


# ---------------------------------------------------------------------------
# Rule => raises_match
# ---------------------------------------------------------------------------


def test_raises_section_required_undocumented() -> None:
    """Policy required, raise in code but not documented: returns raises_section error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("raises_section", Policy.REQUIRED))
    assert any(e.rule == "raises_section" and "ValueError" in e.message and "not documented" in e.message for e in errors)


def test_raises_section_optional_undocumented() -> None:
    """Policy optional, raise in code but not documented: no error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("raises_section", Policy.OPTIONAL))
    assert not errors


def test_raises_section_optional_still_checks_documented() -> None:
    """Policy optional, an exception documented but never raised: raises_match still reports it."""
    entity = _func(raises=[])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="TypeError", description="Never.")])
    cfg = _neutral(enabled_rules=["raises_match"], raises_section=Policy.OPTIONAL)
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "raises_match" and "TypeError" in e.message for e in errors)


def test_raises_section_forbidden_present() -> None:
    """Policy forbidden, documented exceptions: returns raises_section error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError", description="On error.")])
    errors = validate_entity(entity, doc, _policy_only("raises_section", Policy.FORBIDDEN))
    assert any(e.rule == "raises_section" and "not allowed" in e.message for e in errors)


def test_raises_match_phantom_documented() -> None:
    """Raise in docstring but not in code: returns raises_match error."""
    entity = _func(raises=[])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError", description="If invalid.")])
    errors = validate_entity(entity, doc, _rule_only("raises_match"))
    assert any("ValueError" in e.message and "not raised" in e.message for e in errors)


def test_raises_match_missing_description() -> None:
    """Exception documented without a description: returns raises_match error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError", description=None)])
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "raises_match" and "missing description" in e.message for e in errors)


def test_raises_match_correct() -> None:
    """Raise matches code and docstring: no error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError", description="If invalid.")])
    errors = validate_entity(entity, doc, _rule_only("raises_match"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => yields_section
# ---------------------------------------------------------------------------


def test_yields_section_required_missing() -> None:
    """Policy required, generator without Yields section: returns yields_section error."""
    entity = _func(is_generator=True)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("yields_section", Policy.REQUIRED))
    assert any(e.rule == "yields_section" and "Missing" in e.message for e in errors)


def test_yields_section_optional_missing() -> None:
    """Policy optional, generator without Yields section: no error."""
    entity = _func(is_generator=True)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("yields_section", Policy.OPTIONAL))
    assert not errors


def test_yields_section_forbidden_present() -> None:
    """Policy forbidden, Yields section present: returns yields_section error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str", description="A line."))
    errors = validate_entity(entity, doc, _policy_only("yields_section", Policy.FORBIDDEN))
    assert any(e.rule == "yields_section" and "not allowed" in e.message for e in errors)


def test_yields_match_missing_type() -> None:
    """Yields section without a type: returns yields_match error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation=None))
    cfg = _neutral(yields_section=Policy.OPTIONAL)
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "yields_match" and "Missing type" in e.message for e in errors)


def test_yields_match_missing_description() -> None:
    """Yields section without a description: returns yields_match error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str", description=None))
    cfg = _neutral(yields_section=Policy.OPTIONAL, returns_descriptions=Policy.REQUIRED)
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "yields_match" and "Missing description" in e.message for e in errors)


def test_yields_section_correct() -> None:
    """Generator with correct Yields section: no error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str", description="A line."))
    errors = validate_entity(entity, doc, _neutral(yields_section=Policy.REQUIRED))
    assert not errors


def test_yields_section_not_applied_to_non_generator() -> None:
    """Non-generator function: the yields_section policy is not applied."""
    entity = _func(is_generator=False)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _policy_only("yields_section", Policy.REQUIRED))
    assert not errors


def test_returns_section_error_when_generator_has_returns() -> None:
    """Generator with Returns section instead of Yields: returns returns_section error."""
    entity = _func(is_generator=True, return_type="Iterator[str]")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="Iterator[str]"))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
    assert any(e.rule == "returns_section" and "Yields" in e.message for e in errors)


def test_returns_section_exempt_for_generator_without_returns() -> None:
    """Generator without Returns section: the returns_section policy is not triggered."""
    entity = _func(is_generator=True, return_type="Iterator[str]")
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str", description="A line."))
    errors = validate_entity(entity, doc, _policy_only("returns_section", Policy.REQUIRED))
    assert not errors


# ---------------------------------------------------------------------------
# duplicate_arg
# ---------------------------------------------------------------------------


def test_duplicate_arg_detected() -> None:
    """Arg documented twice: duplicate_arg error."""
    entity = _func(docstring="Do something.")
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="x", type_annotation="int", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("duplicate_arg"))
    assert any(e.rule == "duplicate_arg" and "x" in e.message for e in errors)


def test_duplicate_arg_no_duplicate() -> None:
    """All args unique: no duplicate_arg error."""
    entity = _func(docstring="Do something.")
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="y", type_annotation="str", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _neutral())
    assert not any(e.rule == "duplicate_arg" for e in errors)


def test_duplicate_arg_no_args() -> None:
    """No args: no duplicate_arg error."""
    entity = _func(docstring="Do something.")
    errors = validate_entity(entity, ParsedDocstring(), _rule_only("duplicate_arg"))
    assert not any(e.rule == "duplicate_arg" for e in errors)


def test_duplicate_arg_cannot_be_disabled() -> None:
    """Rule listed in ignore: duplicate is still reported, the rule is always on."""
    entity = _func(docstring="Do something.")
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="x", type_annotation="int", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _neutral())
    assert any(e.rule == "duplicate_arg" for e in errors)


# ---------------------------------------------------------------------------
# args_order
# ---------------------------------------------------------------------------


def test_args_order_wrong_order() -> None:
    """Args in docstring in different order than signature: args_order error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="y", type_annotation="str", description="Second."),
            DocstringArg(name="x", type_annotation="int", description="First."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("args_order"))
    assert any(e.rule == "args_order" for e in errors)


def test_args_order_correct() -> None:
    """Args in docstring match signature order: no error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="y", type_annotation="str", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("args_order"))
    assert not any(e.rule == "args_order" for e in errors)


def test_args_order_no_args() -> None:
    """No args: no error."""
    entity = _func(args=[])
    errors = validate_entity(entity, ParsedDocstring(), _rule_only("args_order"))
    assert not any(e.rule == "args_order" for e in errors)


def test_args_order_disabled() -> None:
    """Rule disabled: wrong order not reported."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="y", type_annotation="str", description="Second."),
            DocstringArg(name="x", type_annotation="int", description="First."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert not any(e.rule == "args_order" for e in errors)
