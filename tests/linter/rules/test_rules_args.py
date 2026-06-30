"""Tests for rules/args.py -- return type, args match, returns section, raises match."""

from linter.models import ArgInfo, DocstringArg, DocstringRaise, DocstringReturn, NodeType, ParsedDocstring, RaiseInfo

from linter.rules import validate_entity

from .conftest import _cfg, _class, _func, _rule_only  # pyright: ignore[reportPrivateUsage]

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


def test_args_match_missing_from_docstring() -> None:
    """Arg in signature but not in docstring: returns args_match error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("args_match"))
    assert any(e.rule == "args_match" and "x" in e.message for e in errors)


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
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert any("missing type" in e.message for e in errors)


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
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert any("missing description" in e.message for e in errors)


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


def test_returns_section_missing() -> None:
    """Function with return type but no Returns section: returns returns_section error."""
    entity = _func(return_type="int")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("returns_section"))
    assert any(e.rule == "returns_section" and "Missing" in e.message for e in errors)


def test_returns_section_type_mismatch() -> None:
    """Returns section type differs from signature: returns returns_section error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="str"))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
    assert any("mismatch" in e.message for e in errors)


def test_returns_section_missing_type_in_docstring() -> None:
    """Returns section present but no type declared: returns returns_section error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation=None))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
    assert any("Missing type" in e.message for e in errors)


def test_without_returns_none_init_no_returns_ok_when_enabled() -> None:
    """__init__ -> None without Returns section: no error (rule enabled, default)."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    cfg = _cfg(enabled_rules=["returns_section", "without_returns_none_init"])
    errors = validate_entity(entity, ParsedDocstring(summary="Init."), cfg)
    assert not errors


def test_without_returns_none_init_forbidden_when_enabled() -> None:
    """__init__ -> None with rule enabled: documenting Returns: None is an error."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD)
    cfg = _cfg(enabled_rules=["returns_section", "without_returns_none_init"])
    doc = ParsedDocstring(summary="Init.", returns=DocstringReturn(type_annotation="None"))
    errors = validate_entity(entity, doc, cfg)
    assert any(e.rule == "without_returns_none_init" and "not allowed" in e.message for e in errors)


def test_without_returns_none_init_required_when_disabled() -> None:
    """__init__ -> None with rule disabled: missing Returns section is an error."""
    entity = _func(name="MyClass.__init__", return_type="None", node_type=NodeType.METHOD, docstring="Init.\n\nArgs:\n    x (int): X.\n", raw_docstring="Init.\n\nArgs:\n    x (int): X.\n")
    cfg = _cfg(enabled_rules=["returns_section"])
    errors = validate_entity(entity, ParsedDocstring(summary="Init."), cfg)
    assert any(e.rule == "returns_section" for e in errors)


def test_without_returns_none_oneliner_no_returns_ok_when_enabled() -> None:
    """One-liner -> None without Returns section: no error (rule enabled, default)."""
    entity = _func(return_type="None", docstring="Do something.", raw_docstring="Do something.")
    cfg = _cfg(enabled_rules=["returns_section", "without_returns_none_oneliner"])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), cfg)
    assert not errors


def test_returns_section_correct() -> None:
    """Returns section matches signature: no error."""
    entity = _func(return_type="int")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="int", description="The result."))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
    assert not errors


def test_without_returns_none_oneliner_required_when_disabled() -> None:
    """One-liner -> None with rule disabled: missing Returns section is an error."""
    entity = _func(return_type="None", docstring="Do something.", raw_docstring="Do something.")
    cfg = _cfg(enabled_rules=["returns_section"])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), cfg)
    assert any(e.rule == "returns_section" for e in errors)


# ---------------------------------------------------------------------------
# Rule => raises_match
# ---------------------------------------------------------------------------


def test_raises_match_undocumented() -> None:
    """Raise in code but not in docstring: returns raises_match error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("raises_match"))
    assert any("ValueError" in e.message and "not documented" in e.message for e in errors)


def test_raises_match_phantom_documented() -> None:
    """Raise in docstring but not in code: returns raises_match error."""
    entity = _func(raises=[])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError")])
    errors = validate_entity(entity, doc, _rule_only("raises_match"))
    assert any("ValueError" in e.message and "not raised" in e.message for e in errors)


def test_raises_match_correct() -> None:
    """Raise matches code and docstring: no error."""
    entity = _func(raises=[RaiseInfo(exception_type="ValueError")])
    doc = ParsedDocstring(summary="Do something.", raises=[DocstringRaise(exception_type="ValueError")])
    errors = validate_entity(entity, doc, _rule_only("raises_match"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => yields_section
# ---------------------------------------------------------------------------


def test_yields_section_missing() -> None:
    """Generator without Yields section: returns yields_section error."""
    entity = _func(is_generator=True)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("yields_section"))
    assert any(e.rule == "yields_section" and "Missing" in e.message for e in errors)


def test_yields_section_missing_type() -> None:
    """Generator with Yields section but no type: returns yields_section error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation=None))
    errors = validate_entity(entity, doc, _rule_only("yields_section"))
    assert any(e.rule == "yields_section" and "Missing type" in e.message for e in errors)


def test_yields_section_correct() -> None:
    """Generator with correct Yields section: no error."""
    entity = _func(is_generator=True)
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str", description="A line."))
    errors = validate_entity(entity, doc, _rule_only("yields_section"))
    assert not errors


def test_yields_section_not_applied_to_non_generator() -> None:
    """Non-generator function: yields_section rule is not applied."""
    entity = _func(is_generator=False)
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("yields_section"))
    assert not errors


def test_returns_section_error_when_generator_has_returns() -> None:
    """Generator with Returns section instead of Yields: returns returns_section error."""
    entity = _func(is_generator=True, return_type="Iterator[str]")
    doc = ParsedDocstring(summary="Do something.", returns=DocstringReturn(type_annotation="Iterator[str]"))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
    assert any(e.rule == "returns_section" and "Yields" in e.message for e in errors)


def test_returns_section_exempt_for_generator_without_returns() -> None:
    """Generator without Returns section: returns_section rule is not triggered."""
    entity = _func(is_generator=True, return_type="Iterator[str]")
    doc = ParsedDocstring(summary="Do something.", yields=DocstringReturn(type_annotation="str"))
    errors = validate_entity(entity, doc, _rule_only("returns_section"))
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
    errors = validate_entity(entity, doc, _rule_only("duplicate_arg"))
    assert not errors


def test_duplicate_arg_no_args() -> None:
    """No args: no duplicate_arg error."""
    entity = _func(docstring="Do something.")
    errors = validate_entity(entity, ParsedDocstring(), _rule_only("duplicate_arg"))
    assert not errors


def test_duplicate_arg_disabled() -> None:
    """Rule disabled: duplicate not reported."""
    entity = _func(docstring="Do something.")
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="x", type_annotation="int", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert not any(e.rule == "duplicate_arg" for e in errors)


# ---------------------------------------------------------------------------
# param_order
# ---------------------------------------------------------------------------


def test_param_order_wrong_order() -> None:
    """Args in docstring in different order than signature: param_order error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="y", type_annotation="str", description="Second."),
            DocstringArg(name="x", type_annotation="int", description="First."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("param_order"))
    assert any(e.rule == "param_order" for e in errors)


def test_param_order_correct() -> None:
    """Args in docstring match signature order: no error."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="x", type_annotation="int", description="First."),
            DocstringArg(name="y", type_annotation="str", description="Second."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("param_order"))
    assert not errors


def test_param_order_no_args() -> None:
    """No args: no error."""
    entity = _func(args=[])
    errors = validate_entity(entity, ParsedDocstring(), _rule_only("param_order"))
    assert not errors


def test_param_order_disabled() -> None:
    """Rule disabled: wrong order not reported."""
    entity = _func(args=[ArgInfo(name="x", type_annotation="int"), ArgInfo(name="y", type_annotation="str")])
    doc = ParsedDocstring(
        args=[
            DocstringArg(name="y", type_annotation="str", description="Second."),
            DocstringArg(name="x", type_annotation="int", description="First."),
        ]
    )
    errors = validate_entity(entity, doc, _rule_only("args_match"))
    assert not any(e.rule == "param_order" for e in errors)
