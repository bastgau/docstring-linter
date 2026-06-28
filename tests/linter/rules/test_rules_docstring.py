"""Tests for rules/docstring.py -- docstring presence and summary rules."""

from linter.models import ParsedDocstring

from linter.rules import validate_entity

from .conftest import _cfg, _func, _rule_only  # pyright: ignore[reportPrivateUsage]

# ---------------------------------------------------------------------------
# Rule => docstring_exists
# ---------------------------------------------------------------------------


def test_docstring_exists_missing() -> None:
    """Missing docstring: returns docstring_exists error."""
    entity = _func(docstring=None, raw_docstring=None)
    errors = validate_entity(entity, None, _rule_only("docstring_exists"))
    assert len(errors) == 1
    assert errors[0].rule == "docstring_exists"
    assert "Missing" in errors[0].message


def test_docstring_exists_empty() -> None:
    """Empty docstring (whitespace only): returns docstring_exists error."""
    entity = _func(docstring="   ", raw_docstring="   ")
    errors = validate_entity(entity, None, _rule_only("docstring_exists"))
    assert len(errors) == 1
    assert "empty" in errors[0].message.lower()


def test_docstring_exists_present() -> None:
    """Valid docstring: no docstring_exists error."""
    entity = _func()
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("docstring_exists"))
    assert not errors


def test_docstring_placeholder_ignored_when_configured() -> None:
    """Placeholder '...' with ignore_placeholder_docstrings=True: no errors."""
    entity = _func(docstring="...", raw_docstring="...")
    cfg = _cfg(ignore_placeholder_docstrings=True, enabled_rules=["docstring_exists"])
    errors = validate_entity(entity, None, cfg)
    assert not errors


def test_docstring_placeholder_error_when_not_ignored() -> None:
    """Placeholder '...' without ignore flag: returns docstring_exists error."""
    entity = _func(docstring="...", raw_docstring="...")
    cfg = _cfg(ignore_placeholder_docstrings=False, enabled_rules=["docstring_exists"])
    errors = validate_entity(entity, None, cfg)
    assert len(errors) == 1
    assert "Placeholder" in errors[0].message


# ---------------------------------------------------------------------------
# Rule => summary_exists
# ---------------------------------------------------------------------------


def test_summary_exists_missing() -> None:
    """No summary in parsed_doc: returns summary_exists error."""
    entity = _func()
    errors = validate_entity(entity, ParsedDocstring(summary=None), _rule_only("summary_exists"))
    assert len(errors) == 1
    assert errors[0].rule == "summary_exists"


def test_summary_exists_present() -> None:
    """Summary present: no error."""
    entity = _func()
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("summary_exists"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => summary_punctuation
# ---------------------------------------------------------------------------


def test_summary_punctuation_missing_period() -> None:
    """Summary without period: returns summary_punctuation error."""
    entity = _func(docstring="Do something", raw_docstring="Do something")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something"), _rule_only("summary_punctuation"))
    assert len(errors) == 1
    assert errors[0].rule == "summary_punctuation"


def test_summary_punctuation_present() -> None:
    """Summary ending with period: no error."""
    entity = _func()
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("summary_punctuation"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => summary_first_line
# ---------------------------------------------------------------------------


def test_summary_first_line_wrong() -> None:
    """raw_docstring starts with newline: returns summary_first_line error."""
    entity = _func(raw_docstring="\nDo something.\n")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("summary_first_line"))
    assert any(e.rule == "summary_first_line" for e in errors)


def test_summary_first_line_correct() -> None:
    """raw_docstring starts with summary text: no error."""
    entity = _func(raw_docstring="Do something.")
    errors = validate_entity(entity, ParsedDocstring(summary="Do something."), _rule_only("summary_first_line"))
    assert not errors


# ---------------------------------------------------------------------------
# Rule => imperative_mood
# ---------------------------------------------------------------------------


def test_imperative_mood_third_person() -> None:
    """Summary starting with third-person verb 'Returns': returns imperative_mood error."""
    entity = _func(docstring="Returns the result.", raw_docstring="Returns the result.")
    errors = validate_entity(entity, ParsedDocstring(summary="Returns the result."), _rule_only("imperative_mood"))
    assert any(e.rule == "imperative_mood" for e in errors)


def test_imperative_mood_correct() -> None:
    """Summary starting with imperative verb 'Return': no error."""
    entity = _func(docstring="Return the result.", raw_docstring="Return the result.")
    errors = validate_entity(entity, ParsedDocstring(summary="Return the result."), _rule_only("imperative_mood"))
    assert not errors


def test_imperative_mood_exception_word() -> None:
    """Summary starting with 'This' (in exceptions list): no error."""
    entity = _func(docstring="This is a helper.", raw_docstring="This is a helper.")
    errors = validate_entity(entity, ParsedDocstring(summary="This is a helper."), _rule_only("imperative_mood"))
    assert not errors


def test_imperative_mood_ies_form() -> None:
    """Summary starting with 'Identifies' (ies->y): returns imperative_mood error."""
    entity = _func(docstring="Identifies the value.", raw_docstring="Identifies the value.")
    errors = validate_entity(entity, ParsedDocstring(summary="Identifies the value."), _rule_only("imperative_mood"))
    assert any(e.rule == "imperative_mood" and "Identify" in e.message for e in errors)


def test_imperative_mood_ches_form() -> None:
    """Summary starting with 'Dispatches' (ches->Dispatch): returns imperative_mood error."""
    entity = _func(docstring="Dispatches the event.", raw_docstring="Dispatches the event.")
    errors = validate_entity(entity, ParsedDocstring(summary="Dispatches the event."), _rule_only("imperative_mood"))
    assert any(e.rule == "imperative_mood" and "Dispatch" in e.message for e in errors)


def test_imperative_mood_es_after_consonant() -> None:
    """Summary starting with 'Compresses' (es after consonant): returns imperative_mood error."""
    entity = _func(docstring="Compresses the data.", raw_docstring="Compresses the data.")
    errors = validate_entity(entity, ParsedDocstring(summary="Compresses the data."), _rule_only("imperative_mood"))
    assert any(e.rule == "imperative_mood" for e in errors)


# ---------------------------------------------------------------------------
# Rule => summary_too_long
# ---------------------------------------------------------------------------


def test_summary_too_long_exceeds_limit() -> None:
    """Summary longer than max_length: returns summary_too_long error."""
    summary = "A" * 81
    entity = _func(docstring=summary, raw_docstring=summary)
    cfg = _cfg(enabled_rules=["summary_too_long"], summary_max_length=80)
    errors = validate_entity(entity, ParsedDocstring(summary=summary), cfg)
    assert len(errors) == 1
    assert errors[0].rule == "summary_too_long"
    assert "81" in errors[0].message


def test_summary_too_long_at_limit() -> None:
    """Summary exactly at max_length: no error."""
    summary = "A" * 80
    entity = _func(docstring=summary, raw_docstring=summary)
    cfg = _cfg(enabled_rules=["summary_too_long"], summary_max_length=80)
    errors = validate_entity(entity, ParsedDocstring(summary=summary), cfg)
    assert not errors


def test_summary_too_long_custom_limit() -> None:
    """Summary exceeds custom max_length of 40: returns error."""
    summary = "A" * 41
    entity = _func(docstring=summary, raw_docstring=summary)
    cfg = _cfg(enabled_rules=["summary_too_long"], summary_max_length=40)
    errors = validate_entity(entity, ParsedDocstring(summary=summary), cfg)
    assert any(e.rule == "summary_too_long" and "41" in e.message for e in errors)


def test_summary_too_long_no_summary() -> None:
    """No summary: summary_too_long rule not triggered."""
    entity = _func()
    cfg = _cfg(enabled_rules=["summary_too_long"], summary_max_length=80)
    errors = validate_entity(entity, ParsedDocstring(summary=None), cfg)
    assert not errors


# ---------------------------------------------------------------------------
# unknown_section
# ---------------------------------------------------------------------------


def test_unknown_section_detected() -> None:
    """Section name not in recognized list: unknown_section error."""
    entity = _func(docstring="Do something.")
    cfg = _cfg(enabled_rules=["unknown_section"])
    errors = validate_entity(entity, ParsedDocstring(unknown_sections=["Arguments"]), cfg)
    assert any(e.rule == "unknown_section" and "Arguments" in e.message for e in errors)


def test_unknown_section_multiple() -> None:
    """Multiple unknown sections: one error per section."""
    entity = _func(docstring="Do something.")
    cfg = _cfg(enabled_rules=["unknown_section"])
    errors = validate_entity(entity, ParsedDocstring(unknown_sections=["Arguments", "Params"]), cfg)
    rules = [e.rule for e in errors]
    assert rules.count("unknown_section") == 2


def test_unknown_section_none() -> None:
    """No unknown sections: no error."""
    entity = _func(docstring="Do something.")
    cfg = _cfg(enabled_rules=["unknown_section"])
    errors = validate_entity(entity, ParsedDocstring(unknown_sections=[]), cfg)
    assert not errors


def test_unknown_section_disabled() -> None:
    """Rule disabled: unknown section not reported."""
    entity = _func(docstring="Do something.")
    cfg = _cfg(enabled_rules=[])
    errors = validate_entity(entity, ParsedDocstring(unknown_sections=["Arguments"]), cfg)
    assert not errors
