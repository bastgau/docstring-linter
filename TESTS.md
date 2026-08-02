# Test Plan

This file lists the 349 tests of the `docstring-linter` project. Each entry shows the test file, the function name, and a description of the case covered. Tests are organized by tested module and by rule or feature.

## test_parser.py -- GoogleStyleParser

### parse (via public API)

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_parse_empty_docstring` | Empty docstring: returns empty ParsedDocstring with no fields set. |
| `test_docstring_parser.py` | `test_parse_oneliner` | One-liner docstring: summary is set, no other fields. |
| `test_docstring_parser.py` | `test_parse_summary_and_description` | Summary + blank line + description: both summary and description are set. |
| `test_docstring_parser.py` | `test_parse_arg_with_type_and_description` | Arg with type and description: all fields populated. |
| `test_docstring_parser.py` | `test_parse_arg_without_type` | Arg without type annotation: type_annotation is None. |
| `test_docstring_parser.py` | `test_parse_arg_without_colon` | Typed arg missing its colon: name and type are read, description is empty. |
| `test_docstring_parser.py` | `test_parse_arg_multiline_description` | Arg with continuation line: description is concatenated. |
| `test_docstring_parser.py` | `test_parse_arg_with_stars` | Starred args: the stars are kept in the parsed name. |
| `test_docstring_parser.py` | `test_parse_multiple_args` | Multiple args: all are returned in order. |
| `test_docstring_parser.py` | `test_parse_returns_with_type_and_description` | Standard Returns line: type and description are extracted. |
| `test_docstring_parser.py` | `test_parse_returns_none_keyword` | Returns section containing only 'None': type_annotation is 'None', description is None. |
| `test_docstring_parser.py` | `test_parse_returns_bare_type` | Returns section holding a bare type, no colon: type is read, description is None. |
| `test_docstring_parser.py` | `test_parse_returns_bare_description` | Returns section holding prose, no colon: description is read, type is None. |
| `test_docstring_parser.py` | `test_parse_no_returns_section` | Docstring without Returns section: returns field is None. |
| `test_docstring_parser.py` | `test_parse_raises_single` | Single Raises entry: exception_type and description populated. |
| `test_docstring_parser.py` | `test_parse_raises_multiline_description` | Raises entry with continuation line: description is concatenated. |
| `test_docstring_parser.py` | `test_parse_raises_multiple` | Multiple Raises entries: all are returned. |
| `test_docstring_parser.py` | `test_parse_attributes_with_type` | Attribute with type and description: all fields populated. |
| `test_docstring_parser.py` | `test_parse_attributes_without_type` | Attribute without type annotation: type_annotation is None. |
| `test_docstring_parser.py` | `test_parse_attributes_multiline_description` | Attribute with continuation line: description is concatenated. |
| `test_docstring_parser.py` | `test_parse_attributes_multiple` | Multiple attributes: all are returned in order. |
| `test_docstring_parser.py` | `test_parse_example_section` | Docstring with Example section: examples list is populated. |
| `test_docstring_parser.py` | `test_parse_examples_section` | Docstring with Examples section (plural): examples list is populated. |
| `test_docstring_parser.py` | `test_parse_unknown_section_ignored` | Unknown section name: not parsed, does not affect other fields. |
| `test_docstring_parser.py` | `test_unknown_section_known_not_flagged` | Known section: not captured in unknown_sections. |
| `test_docstring_parser.py` | `test_unknown_section_multiple` | Multiple unknown sections in parsed docstring: all captured. |
| `test_docstring_parser.py` | `test_parse_lowercase_section_not_recognized` | Lowercase section name (args: instead of Args:): not recognized, no args parsed. |

### style

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_parser_style_property` | Style property: returns DocstringStyle.GOOGLE. |

### get_parser

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_get_parser_google` | get_parser(GOOGLE): returns a GoogleStyleParser instance. |
| `test_docstring_parser.py` | `test_get_parser_unsupported` | get_parser with unsupported style: raises ValueError with style name. |

---

## test_ast_parser.py -- ast_parser

### _extract_args

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_args_no_args` | Only self in signature: returns empty list because self is always skipped. |
| `test_ast_parser.py` | `test_extract_args_positional_with_type_and_default` | Positional arg with type annotation and default value: all three fields are populated. |
| `test_ast_parser.py` | `test_extract_args_positional_without_type` | Positional arg with no type annotation: type_annotation is None. |
| `test_ast_parser.py` | `test_extract_args_positional_without_default` | Positional arg with no default value: default is None. |
| `test_ast_parser.py` | `test_extract_args_keyword_only` | Keyword-only arg (after bare *): extracted with correct name and type. |
| `test_ast_parser.py` | `test_extract_args_keyword_only_with_default` | Keyword-only arg with a default value: default is correctly extracted. |
| `test_ast_parser.py` | `test_extract_args_skips_self_and_cls` | Both self and cls are always excluded from the result, regardless of position. |
| `test_ast_parser.py` | `test_extract_args_skips_cls_in_kwonly` | Keyword-only arg named cls is excluded, just like in positional position. |
| `test_ast_parser.py` | `test_extract_args_mixed_positional_and_keyword_only` | Mix of positional and keyword-only args: both are returned in declaration order. |
| `test_ast_parser.py` | `test_extract_args_vararg_and_kwarg` | *args and **kwargs are extracted with their stars in the name. |
| `test_ast_parser.py` | `test_extract_args_vararg_without_annotation` | *args without annotation: type_annotation is None. |
| `test_ast_parser.py` | `test_extract_args_positional_only` | Positional-only args (before /): extracted with name and type. |
| `test_ast_parser.py` | `test_extract_args_positional_only_skips_self` | self in positional-only position: excluded like elsewhere. |
| `test_ast_parser.py` | `test_extract_args_positional_only_default_alignment` | Defaults align by the end of posonlyargs + args combined. |
| `test_ast_parser.py` | `test_extract_args_positional_only_with_default` | Positional-only arg with a default: default is correctly extracted. |

### _extract_raises

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_raises_none` | Function with no raise statements: returns empty list. |
| `test_ast_parser.py` | `test_extract_raises_simple_call` | Raise ValueError("msg"): detected by the exception class name. |
| `test_ast_parser.py` | `test_extract_raises_bare_name` | Raise err where err is a plain name (not a call): the name itself is recorded. |
| `test_ast_parser.py` | `test_extract_raises_bare_raise_ignored` | Bare re-raise (raise with no argument): ignored because there is no exception type. |
| `test_ast_parser.py` | `test_extract_raises_deduplicates` | Same exception raised twice: appears only once in the result list. |
| `test_ast_parser.py` | `test_extract_raises_multiple_distinct` | Two different exceptions raised: both are present in the result. |

### _is_empty_init

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_is_empty_init_pass_only` | __init__(self) with only a pass statement: classified as empty. |
| `test_ast_parser.py` | `test_is_empty_init_docstring_only` | __init__(self) with only a docstring: classified as empty (docstring is not logic). |
| `test_ast_parser.py` | `test_is_empty_init_with_positional_arg` | __init__(self, name: str): has a real positional arg, not empty. |
| `test_ast_parser.py` | `test_is_empty_init_with_kwonly_arg` | __init__(self, *, name: str): has a keyword-only arg, not empty. |
| `test_ast_parser.py` | `test_is_empty_init_with_body` | __init__(self) with self.x = 1 in the body: has real statements, not empty. |

### _extract_class_attributes

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_class_attributes_annotations` | Class-level annotations are extracted as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_self_assignments` | self.x assignments in __init__ are extracted as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_dedup_and_order` | Class annotations and __init__ assignments merge without duplicates, in first-seen order. |
| `test_ast_parser.py` | `test_extract_class_attributes_skips_dunder` | Dunder assignments like __slots__ are not treated as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_skips_constants` | All-uppercase names (constants) are not treated as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_none` | Class with no attributes: returns empty list. |

### parse_file

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_parse_file_returns_module_entity` | Any Python file produces a MODULE entity as the first result, with its docstring. |
| `test_ast_parser.py` | `test_parse_file_extracts_function` | Top-level function: extracted as a FUNCTION entity with the function name. |
| `test_ast_parser.py` | `test_parse_file_extracts_method` | Method inside a class: extracted as a METHOD entity named ClassName.method_name. |
| `test_ast_parser.py` | `test_parse_file_sets_is_empty_init` | __init__ with no args and pass body: is_empty_init is True on the extracted entity. |
| `test_ast_parser.py` | `test_parse_file_syntax_error` | File with invalid Python syntax: SyntaxError is raised and not swallowed. |
| `test_ast_parser.py` | `test_is_generator_with_yield` | Function with yield: is_generator is True. |
| `test_ast_parser.py` | `test_is_generator_with_yield_from` | Function with yield from: is_generator is True. |
| `test_ast_parser.py` | `test_is_generator_without_yield` | Function without yield: is_generator is False. |

---

## test_rules/ -- rules

### docstring_exists

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_docstring_exists_present` | Valid docstring: no docstring_exists error. |
| `rules/test_rules_docstring.py` | `test_docstring_exists_missing` | Missing docstring: returns docstring_exists error. |
| `rules/test_rules_docstring.py` | `test_docstring_exists_empty` | Empty docstring (whitespace only): returns docstring_exists error. |

### summary_exists

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_exists_cannot_be_disabled` | Rule listed in ignore: the missing summary is still reported, the rule is always on. |
| `rules/test_rules_docstring.py` | `test_summary_exists_present` | Summary present: no error. |
| `rules/test_rules_docstring.py` | `test_summary_exists_missing` | No summary in parsed_doc: returns summary_exists error. |

### summary_final_period (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_final_period_required_missing` | Policy required, summary without period: returns summary_final_period error. |
| `rules/test_rules_docstring.py` | `test_summary_final_period_required_present` | Policy required, summary ending with period: no error. |
| `rules/test_rules_docstring.py` | `test_summary_final_period_forbidden_present` | Policy forbidden, summary ending with period: returns summary_final_period error. |
| `rules/test_rules_docstring.py` | `test_summary_final_period_forbidden_missing` | Policy forbidden, summary without period: no error. |
| `rules/test_rules_docstring.py` | `test_summary_final_period_optional_accepts_both` | Policy optional: period present or absent, no error either way. |

### return_type_annotation

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_return_type_annotation_present` | Function with -> int annotation: no error. |
| `rules/test_rules_args.py` | `test_return_type_annotation_missing` | Function without -> annotation: returns return_type_annotation error. |
| `rules/test_rules_args.py` | `test_return_type_annotation_not_checked_for_class` | Class entity: return_type_annotation rule is not applied. |

### args_section (policy) / args_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_args_section_required_missing` | Policy required, arg in signature but not in docstring: returns args_section error. |
| `rules/test_rules_args.py` | `test_args_section_optional_missing` | Policy optional, arg in signature but not in docstring: no error. |
| `rules/test_rules_args.py` | `test_args_section_optional_still_checks_documented_args` | Policy optional, a documented arg with a wrong type: args_match still reports it. |
| `rules/test_rules_args.py` | `test_args_section_forbidden_present` | Policy forbidden, documented args: returns args_section error. |
| `rules/test_rules_args.py` | `test_args_section_starred_args_documented` | *args and **kwargs documented with their stars: no error. |
| `rules/test_rules_args.py` | `test_args_section_starred_args_undocumented` | **kwargs in signature but not documented: returns args_section error. |
| `rules/test_rules_args.py` | `test_args_match_extra_in_docstring` | Arg in docstring but not in signature: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_type_mismatch` | Arg type in docstring differs from signature: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_missing_type_in_docstring` | Policy required, arg missing type in docstring: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_type_optional` | Policy optional, arg documented without a type: no args_match error. |
| `rules/test_rules_args.py` | `test_args_match_type_forbidden` | Policy forbidden, arg documented with a type: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_correct` | Arg matches signature and docstring perfectly: no error. |
| `rules/test_rules_args.py` | `test_args_match_missing_description_in_docstring` | Arg with no description in docstring: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_no_sig_args_no_doc_args` | No args in signature and no args in docstring: no error. |
| `rules/test_rules_args.py` | `test_args_match_doc_arg_extra_via_detailed_path` | Arg in sig and doc but extra doc arg: reports the extra. |

### duplicate_arg

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_duplicate_arg_detected` | Arg documented twice: duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_no_duplicate` | All args unique: no duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_no_args` | No args: no duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_cannot_be_disabled` | Rule listed in ignore: duplicate is still reported, the rule is always on. |

### args_order

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_args_order_wrong_order` | Args in docstring in different order than signature: args_order error. |
| `rules/test_rules_args.py` | `test_args_order_correct` | Args in docstring match signature order: no error. |
| `rules/test_rules_args.py` | `test_args_order_no_args` | No args: no error. |
| `rules/test_rules_args.py` | `test_args_order_disabled` | Rule disabled: wrong order not reported. |

### returns_section (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_returns_section_required_missing` | Policy required, return type but no Returns section: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_optional_missing` | Policy optional, return type but no Returns section: no error. |
| `rules/test_rules_args.py` | `test_returns_section_optional_still_checks_type` | Policy optional, a Returns section with a wrong type: returns_match still reports it. |
| `rules/test_rules_args.py` | `test_returns_section_forbidden_present` | Policy forbidden, Returns section present: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_correct` | Returns section matches signature: no error. |
| `rules/test_rules_args.py` | `test_returns_section_ignores_none_return_type` | Function -> None without Returns section: returns_section does not flag it. |
| `rules/test_rules_args.py` | `test_returns_section_error_when_generator_has_returns` | Generator documenting Returns: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_exempt_for_generator_without_returns` | Generator without Returns section: the returns_section policy is not triggered. |

### returns_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_returns_match_mismatch` | Returns section type differs from signature: returns returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_missing_type` | Returns section present but no type declared: returns returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_no_section_no_error` | No Returns section: returns_match does not flag a missing section. |
| `rules/test_rules_args.py` | `test_returns_match_missing_description` | Policy required, Returns section without a description: returns returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_none_exempt_from_description` | Policy required, 'Returns: None': the description is not demanded. |
| `rules/test_rules_args.py` | `test_returns_descriptions_optional` | Policy optional: a Returns line without description is accepted. |
| `rules/test_rules_args.py` | `test_returns_descriptions_forbidden` | Policy forbidden: a Returns line carrying a description is reported. |
| `rules/test_rules_args.py` | `test_returns_match_correct` | Returns section type matches signature: no returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_cannot_be_disabled` | Rule listed in ignore: the type mismatch is still reported, the rule is always on. |

### returns_none (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_returns_none_required_missing` | Policy required, no Returns section: returns returns_none error. |
| `rules/test_rules_args.py` | `test_returns_none_required_present` | Policy required, Returns: None section present: no error. |
| `rules/test_rules_args.py` | `test_returns_none_required_flags_oneliner` | Policy required, one-liner docstring cannot hold the section: returns returns_none error. |
| `rules/test_rules_args.py` | `test_returns_none_forbidden_present` | Policy forbidden, Returns: None section present: returns returns_none error. |
| `rules/test_rules_args.py` | `test_returns_none_forbidden_missing` | Policy forbidden, no Returns section: no error. |
| `rules/test_rules_args.py` | `test_returns_none_optional_accepts_both` | Policy optional: section present or absent, no error either way. |
| `rules/test_rules_args.py` | `test_returns_none_skips_init` | __init__ -> None is not covered by the returns_none policy. |
| `rules/test_rules_args.py` | `test_returns_none_skips_generator` | Generator is not covered by the returns_none policy. |

### init_returns_none (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_init_returns_none_required_missing` | Policy required, __init__ without Returns section: returns init_returns_none error. |
| `rules/test_rules_args.py` | `test_init_returns_none_required_present` | Policy required, __init__ with Returns: None section: no error. |
| `rules/test_rules_args.py` | `test_init_returns_none_forbidden_present` | Policy forbidden (default), __init__ with Returns: None section: returns init_returns_none error. |
| `rules/test_rules_args.py` | `test_init_returns_none_optional_accepts_both` | Policy optional: section present or absent on __init__, no error either way. |

### raises_section (policy) / raises_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_raises_section_required_undocumented` | Policy required, raise in code but not documented: returns raises_section error. |
| `rules/test_rules_args.py` | `test_raises_section_optional_undocumented` | Policy optional, raise in code but not documented: no error. |
| `rules/test_rules_args.py` | `test_raises_section_optional_still_checks_documented` | Policy optional, an exception documented but never raised: raises_match still reports it. |
| `rules/test_rules_args.py` | `test_raises_section_forbidden_present` | Policy forbidden, documented exceptions: returns raises_section error. |
| `rules/test_rules_args.py` | `test_raises_match_phantom_documented` | Raise in docstring but not in code: returns raises_match error. |
| `rules/test_rules_args.py` | `test_raises_match_missing_description` | Exception documented without a description: returns raises_match error. |
| `rules/test_rules_args.py` | `test_raises_match_correct` | Raises section matches the code: no error. |

### yields_section (policy) / yields_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_yields_section_required_missing` | Policy required, generator without Yields section: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_section_optional_missing` | Policy optional, generator without Yields section: no error. |
| `rules/test_rules_args.py` | `test_yields_section_forbidden_present` | Policy forbidden, Yields section present: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_match_missing_type` | Yields section without a type: returns yields_match error. |
| `rules/test_rules_args.py` | `test_yields_match_missing_description` | Yields section without a description: returns yields_match error. |
| `rules/test_rules_args.py` | `test_yields_section_correct` | Generator with correct Yields section: no error. |
| `rules/test_rules_args.py` | `test_yields_section_not_applied_to_non_generator` | Non-generator function: the yields_section policy is not applied. |

### attributes_section (policy) / attributes_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_attributes.py` | `test_attributes_section_required_missing` | Policy required, class with attributes but no Attributes section: returns an error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_optional_missing` | Policy optional, class with attributes but no Attributes section: no error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_forbidden_present` | Policy forbidden, Attributes section present: returns an error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_attribute_not_documented` | Policy required, class attribute missing from the section: returns an error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_no_attributes_no_error` | Class with no attributes and no Attributes section: no error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_correct` | Attribute with type and description: no error. |
| `rules/test_rules_attributes.py` | `test_attributes_match_missing_type` | Policy required, attribute without type in docstring: returns attributes_match error. |
| `rules/test_rules_attributes.py` | `test_attributes_match_type_forbidden` | Policy forbidden, attribute documented with a type: returns attributes_match error. |
| `rules/test_rules_attributes.py` | `test_attributes_match_missing_description` | Attribute without description in docstring: returns attributes_match error. |
| `rules/test_rules_attributes.py` | `test_attributes_match_phantom_documented` | Attribute documented but not a class attribute: returns attributes_match error. |
| `rules/test_rules_attributes.py` | `test_attributes_match_checked_when_section_optional` | Policy optional: a documented attribute is still checked. |

### indentation

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_indentation_consistent` | Normal Google-style docstring with 2 levels: no indentation error. |
| `rules/test_rules_structure.py` | `test_indentation_inconsistent` | More than 2 indent levels in docstring: returns indentation error. |
| `rules/test_rules_structure.py` | `test_indentation_one_liner_skipped` | One-liner docstring: indentation rule skips it, no error. |

### section_capitalization

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_section_capitalization_correct` | Correctly capitalized section 'Args:': no error. |
| `rules/test_rules_structure.py` | `test_section_capitalization_wrong` | Lowercase section header 'args:': returns section_capitalization error. |

### section_order

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_section_order_correct` | Args before Returns: no section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_wrong` | Returns before Args: returns section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_single_section_ok` | Only one recognized section: no section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_unknown_section_ignored` | Unknown section between known sections: order check skips it. |

### unknown_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_unknown_section_detected` | Section name not in recognized list: unknown_section error. |
| `rules/test_rules_docstring.py` | `test_unknown_section_multiple` | Multiple unknown sections: one error per section. |
| `rules/test_rules_docstring.py` | `test_unknown_section_none` | No unknown sections: no error. |
| `rules/test_rules_docstring.py` | `test_unknown_section_disabled` | Rule disabled: unknown section not reported. |

### empty_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_empty_section_with_content` | Args section with content: no empty_section error. |
| `rules/test_rules_structure.py` | `test_empty_section_cannot_be_disabled` | Rule listed in ignore: the empty section is still reported, the rule is always on. |
| `rules/test_rules_structure.py` | `test_empty_section_detected` | Args section with no content: returns empty_section error. |

### blank_lines

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_blank_lines_after_summary_missing` | Description glued to the summary: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_after_summary_present` | One blank line between summary and description: no blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_after_summary_too_many` | Two blank lines between summary and description: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_after_summary_only_summary` | Docstring limited to a summary: the gap is not checked. |
| `rules/test_rules_structure.py` | `test_blank_lines_after_summary_section_follows` | Summary followed by a section header: governed by blank_lines_before_section only. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_section_default_missing` | Default of 1, no blank line before a section header: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_section_default_present` | Default of 1, one blank line before each section header: no error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_section_zero` | Configured to 0, no blank line before a section header: no error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_section_zero_but_gap_present` | Configured to 0, a blank line before a section header: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_section_two` | Configured to 2, only one blank line before a section header: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_section_on_first_line_skipped` | Section header on the first line of the docstring: not counted. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_closing_quotes_default_missing` | Default of 1, no blank line before the closing quotes: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_closing_quotes_default_present` | Default of 1, one blank line before the closing quotes: no error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_closing_quotes_too_many` | Default of 1, two blank lines before the closing quotes: returns blank_lines error. |
| `rules/test_rules_structure.py` | `test_blank_lines_before_closing_quotes_zero` | Configured to 0, no blank line before the closing quotes: no error. |
| `rules/test_rules_structure.py` | `test_blank_lines_cannot_be_disabled` | Rule listed in ignore: a wrong blank line count is still reported, the rule is always on. |
| `rules/test_rules_structure.py` | `test_blank_lines_one_liner_skipped` | One-liner docstring: the closing quotes count is not checked. |
| `rules/test_rules_structure.py` | `test_blank_lines_module_skipped` | Module entity: the closing quotes count is not checked. |

### imperative_mood

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_imperative_mood_correct` | Summary starting with imperative verb 'Return': no error. |
| `rules/test_rules_docstring.py` | `test_imperative_mood_third_person` | Summary starting with third-person verb 'Returns': returns imperative_mood error. |
| `rules/test_rules_docstring.py` | `test_imperative_mood_ies_form` | Summary starting with 'Identifies' (ies->y): returns imperative_mood error. |
| `rules/test_rules_docstring.py` | `test_imperative_mood_ches_form` | Summary starting with 'Dispatches' (ches->Dispatch): returns imperative_mood error. |
| `rules/test_rules_docstring.py` | `test_imperative_mood_es_after_consonant` | Summary starting with 'Compresses' (es after consonant): returns imperative_mood error. |
| `rules/test_rules_docstring.py` | `test_imperative_mood_exception_word` | Summary starting with 'This' (in exceptions list): no error. |

### summary_too_long

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_too_long_exceeds_limit` | Summary longer than max_length: returns summary_too_long error. |
| `rules/test_rules_docstring.py` | `test_summary_too_long_at_limit` | Summary exactly at max_length: no error. |
| `rules/test_rules_docstring.py` | `test_summary_too_long_custom_limit` | Summary exceeds custom max_length of 40: returns error. |
| `rules/test_rules_docstring.py` | `test_summary_too_long_no_summary` | No summary: summary_too_long rule not triggered. |

### summary_on_first_line (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_on_first_line_required_wrong` | Policy required, raw_docstring starts with newline: returns summary_on_first_line error. |
| `rules/test_rules_docstring.py` | `test_summary_on_first_line_required_correct` | Policy required, raw_docstring starts with summary text: no error. |
| `rules/test_rules_docstring.py` | `test_summary_on_first_line_forbidden_wrong` | Policy forbidden, summary on the opening quotes line: returns summary_on_first_line error. |
| `rules/test_rules_docstring.py` | `test_summary_on_first_line_forbidden_correct` | Policy forbidden, summary on the next line: no error. |
| `rules/test_rules_docstring.py` | `test_summary_on_first_line_optional_accepts_both` | Policy optional: summary on either line, no error. |

### entry_spacing

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_entry_spacing_canonical` | Entry written 'name (type): description': no error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_missing_space_before_parenthesis` | Entry written 'name(type): description': returns entry_spacing error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_space_before_colon` | Entry written 'name (type) : description': returns entry_spacing error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_no_space_after_colon` | Entry written 'name (type):description': returns entry_spacing error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_missing_colon` | Entry written 'name (type)' without its colon: returns entry_spacing error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_untyped_entry` | Entry without a type: the canonical form drops the parenthesis. |
| `rules/test_rules_structure.py` | `test_entry_spacing_starred_entry` | Starred entry written canonically: no error. |
| `rules/test_rules_structure.py` | `test_entry_spacing_ignores_continuation_lines` | Continuation line of a description: not read as an entry. |
| `rules/test_rules_structure.py` | `test_entry_spacing_ignores_other_sections` | Returns section content: not read as an entry. |
| `rules/test_rules_structure.py` | `test_entry_spacing_cannot_be_disabled` | Rule listed in ignore: the bad spacing is still reported, the rule is always on. |

### no_blank_line_in_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_no_blank_line_in_section_cannot_be_disabled` | Rule listed in ignore: the blank line between entries is still reported, the rule is always on. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_args_section` | Blank line between two Args entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_raises_section` | Blank line between two Raises entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_attributes_section` | Blank line between two Attributes entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_section_correct` | No blank lines between Args entries: no error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_example_ignored` | Blank line inside Example section: not flagged (rule only applies to Args/Attributes/Raises). |

### description_section (policy)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_description_section_required_missing` | Policy required, docstring without description: returns description_section error. |
| `rules/test_rules_docstring.py` | `test_description_section_required_present` | Policy required, docstring with a description: no error. |
| `rules/test_rules_docstring.py` | `test_description_section_forbidden_present` | Policy forbidden, docstring with a description: returns description_section error. |
| `rules/test_rules_docstring.py` | `test_description_section_optional_by_default` | Default config: neither presence nor absence of a description is reported. |

### examples_section / notes_section / todo_section (policies)

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_examples_section_required_missing` | Policy required, no Example section: returns examples_section error. |
| `rules/test_rules_structure.py` | `test_examples_section_required_present_plural` | Policy required, an Examples section: the plural spelling is accepted. |
| `rules/test_rules_structure.py` | `test_examples_section_forbidden_present` | Policy forbidden, an Example section: returns examples_section error. |
| `rules/test_rules_structure.py` | `test_notes_section_forbidden_present` | Policy forbidden, a Note section: returns notes_section error. |
| `rules/test_rules_structure.py` | `test_todo_section_forbidden_present` | Policy forbidden, a Todo section: returns todo_section error. |
| `rules/test_rules_structure.py` | `test_named_sections_optional_by_default` | Default config: Example, Note and Todo sections are neither required nor rejected. |

### validate_entity

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_validate.py` | `test_empty_init_method_excluded_when_configured` | Empty __init__ with exclude_empty_init_method=True: no errors even with missing docstring. |
| `rules/test_rules_validate.py` | `test_empty_init_method_not_excluded_when_flag_false` | Empty __init__ with exclude_empty_init_method=False: docstring_exists is still checked. |
| `rules/test_rules_validate.py` | `test_empty_init_method_docstring_still_checked` | Empty __init__ with exclude_empty_init_method=True: an existing docstring is still checked. |
| `rules/test_rules_validate.py` | `test_empty_init_module_excluded_when_configured` | Empty __init__.py with exclude_empty_init_module=True: no errors even with missing docstring. |
| `rules/test_rules_validate.py` | `test_empty_init_module_not_excluded_when_flag_false` | Empty __init__.py with exclude_empty_init_module=False: docstring_exists is still checked. |
| `rules/test_rules_validate.py` | `test_docstring_placeholder_ignored_when_configured` | Placeholder '...' with ignore_placeholder_docstrings=True: no errors. |
| `rules/test_rules_validate.py` | `test_docstring_placeholder_error_when_not_ignored` | Placeholder '...' without ignore flag: returns docstring_exists error. |
| `rules/test_rules_validate.py` | `test_disabled_rule_not_checked` | When all rules are disabled: no error for missing docstring. |
| `rules/test_rules_validate.py` | `test_imperative_mood_skipped_for_module` | Module node type: imperative_mood rule is not applied (plural nouns like 'Rules' are valid). |
| `rules/test_rules_validate.py` | `test_method_node_type_triggers_function_rules` | METHOD node type: function-level rules like return_type_annotation are applied. |

---

## test_cli.py -- CLI

### collect_python_files

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_collect_single_file` | Single .py file path: returns that file. |
| `test_cli.py` | `test_collect_non_py_file_ignored` | Non-.py file: not collected. |
| `test_cli.py` | `test_collect_excluded_file_skipped` | Single file matching exclusion pattern: not collected. |
| `test_cli.py` | `test_collect_directory_recursive` | Directory with nested .py files: all collected. |
| `test_cli.py` | `test_collect_venv_excluded_by_literal_pattern` | File inside a .venv directory: excluded by literal pattern matching path parts. |
| `test_cli.py` | `test_collect_pycache_excluded_by_literal_pattern` | File inside __pycache__: excluded by literal pattern matching path parts. |

### lint_file

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_lint_file_scope_modules_false` | check_modules=False: module entity is skipped, no module-level errors. |
| `test_cli.py` | `test_lint_file_scope_functions_false` | check_functions=False: function entities are skipped. |
| `test_cli.py` | `test_lint_file_syntax_error_raises` | SyntaxError in file: lint_file raises SyntaxError. |

### merge_cli_into_config

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_merge_style_override` | --style google: overrides config.style. |
| `test_cli.py` | `test_merge_exclude_override` | --exclude test_*: overrides config.exclude_patterns. |
| `test_cli.py` | `test_merge_format_json` | --format json: sets output_format to json. |
| `test_cli.py` | `test_merge_format_github_annotations` | --format github-annotations: sets output_format to github-annotations. |
| `test_cli.py` | `test_merge_workers_override` | --workers 4: sets config.workers to 4. |
| `test_cli.py` | `test_merge_workers_negative_clamped_to_zero` | --workers -1: clamped to 0 (auto-detect). |
| `test_cli.py` | `test_merge_no_overrides_leaves_defaults` | No CLI overrides: config unchanged from defaults. |

### run

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_run_no_files_returns_zero` | No .py files found: run returns 0. |
| `test_cli.py` | `test_run_valid_file_returns_zero` | Valid file with no errors: run returns 0. |
| `test_cli.py` | `test_run_invalid_file_returns_one` | File with lint errors: run returns 1. |
| `test_cli.py` | `test_run_syntax_error_returns_zero` | File with SyntaxError: error is caught, run returns 0 (no lint errors). |
| `test_cli.py` | `test_run_with_json_output` | Run with output_format=json: JSON report is printed to stdout. |

### main / --list-rules

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_main_invalid_config_value` | Invalid value in the config file: prints a configuration error and exits with 2. |
| `test_cli.py` | `test_list_rules_output` | --list-rules: configurable rules appear grouped by category, always-on rules do not. |

---

## test_reporter.py -- reporter

### report_traceback

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_traceback_no_errors` | No errors: prints summary with 0 errors. |
| `test_reporter.py` | `test_report_traceback_location_header` | With errors: prints one clickable header with the absolute path per entity. |
| `test_reporter.py` | `test_report_traceback_groups_errors_by_entity` | Two errors on the same entity: a single header followed by both messages. |
| `test_reporter.py` | `test_report_traceback_separate_entities` | Errors on different lines: one header each. |

### report_cli

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_cli_no_errors` | No errors: prints summary with 0 errors. |
| `test_reporter.py` | `test_report_cli_with_errors` | With errors: prints each error and a summary line. |
| `test_reporter.py` | `test_report_cli_single_error_grammar` | Single error: summary says 'error' not 'errors'. |
| `test_reporter.py` | `test_report_cli_multiple_files` | Errors in multiple files: each file is printed separately. |

### report_json

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_json_no_errors` | No errors: JSON output has total_errors=0 and empty errors list. |
| `test_reporter.py` | `test_report_json_with_errors` | With errors: JSON output contains error details with all expected fields. |
| `test_reporter.py` | `test_report_json_sorted_by_file_and_line` | Errors are sorted by filepath then line in the JSON output. |

### report_github_annotations

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_github_annotations_no_errors` | No errors: summary line only. |
| `test_reporter.py` | `test_report_github_annotations_format` | Single error: annotation followed by summary. |
| `test_reporter.py` | `test_report_github_annotations_sorted` | Multiple errors: sorted by filepath then line, summary at end. |

### report_rules

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_rules_all_categories_present` | Category names with at least one configurable rule appear in output. |
| `test_reporter.py` | `test_report_rules_all_rules_present` | All configurable rule identifiers appear in output. |
| `test_reporter.py` | `test_report_rules_enabled_rule_shows_checkmark` | Enabled rule shows checkmark marker. |
| `test_reporter.py` | `test_report_rules_disabled_rule_shows_cross` | Disabled rule shows cross marker. |
| `test_reporter.py` | `test_report_rules_off_by_default_label` | Rule in off_by_default shows '(disabled by default)' label. |
| `test_reporter.py` | `test_report_rules_always_on_hidden` | Rule in always_on is not listed and is not counted in the header. |
| `test_reporter.py` | `test_report_rules_category_hidden_when_all_rules_always_on` | Category whose rules are all always on: the category is not printed. |
| `test_reporter.py` | `test_report_policies_all_policies_present` | All policy identifiers and their values appear in output. |
| `test_reporter.py` | `test_report_policies_optional_value` | Policy set to optional shows its value on the matching line. |
| `test_reporter.py` | `test_report_options_all_options_present` | All option identifiers and their values appear in output. |
| `test_reporter.py` | `test_report_options_value_on_matching_line` | Each option value is printed on the line of its option. |

---

## test_config.py -- configuration

### LinterConfig defaults

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_default_config_style` | Default config: style is GOOGLE. |
| `test_config.py` | `test_default_config_rules_exclude_off_by_default` | Default config: OFF_BY_DEFAULT rules are not in enabled_rules. |
| `test_config.py` | `test_default_config_all_other_rules_enabled` | Default config: all rules except OFF_BY_DEFAULT are enabled. |
| `test_config.py` | `test_default_config_exclude_patterns_include_common_dirs` | Default config: exclude_patterns includes .venv, .git, __pycache__, .tox. |

### is_rule_enabled

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_is_rule_enabled_true` | is_rule_enabled returns True for a rule in enabled_rules. |
| `test_config.py` | `test_is_rule_enabled_false` | is_rule_enabled returns False for a rule not in enabled_rules. |

### _parse_toml_config

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_parse_select_all` | Select = ['ALL']: all rules in RULES_REGISTRY are enabled. |
| `test_config.py` | `test_parse_select_all_with_ignore` | Select = ['ALL'] + ignore = ['args_match']: all rules except args_match. |
| `test_config.py` | `test_parse_select_explicit_list` | Select = ['docstring_exists', 'args_match']: only those two rules enabled. |
| `test_config.py` | `test_parse_ignore_only` | Ignore only (no select): starts from default set minus ignored rules. |
| `test_config.py` | `test_parse_select_unknown_rule_ignored` | Select with an unknown rule name: unknown rule is silently ignored. |
| `test_config.py` | `test_parse_no_select_no_ignore` | Empty data: enabled_rules matches default config. |
| `test_config.py` | `test_parse_style_google` | Style = 'google': config.style is DocstringStyle.GOOGLE. |
| `test_config.py` | `test_parse_style_unknown` | Style = 'unknown': raises ValueError. |
| `test_config.py` | `test_parse_exclude_empty_init_method_false` | exclude_empty_init_method = false: config.exclude_empty_init_method is False. |
| `test_config.py` | `test_parse_exclude_empty_init_module_false` | exclude_empty_init_module = false: config.exclude_empty_init_module is False. |
| `test_config.py` | `test_parse_workers` | Workers = 4: config.workers is 4. |
| `test_config.py` | `test_parse_workers_zero_allowed` | Workers = 0: config.workers is 0 (auto-detect at runtime). |
| `test_config.py` | `test_parse_scope_modules_false` | scope.modules = false: config.check_modules is False. |
| `test_config.py` | `test_parse_scope_all_false` | All scope flags set to false: all check_* fields are False. |
| `test_config.py` | `test_parse_exclude_patterns` | Exclude = ['test_*']: config.exclude_patterns is set. |
| `test_config.py` | `test_parse_ignore_placeholder_docstrings` | ignore_placeholder_docstrings = true: config flag is True. |
| `test_config.py` | `test_parse_summary_max_length` | summary_max_length = 72: config.summary_max_length is 72. |
| `test_config.py` | `test_parse_summary_max_length_minimum_one` | summary_max_length = 0: clamped to 1. |
| `test_config.py` | `test_parse_blank_lines_options` | blank_lines_before_section and blank_lines_before_closing_quotes: parsed as integers. |
| `test_config.py` | `test_parse_blank_lines_options_minimum_zero` | Negative blank line counts: clamped to 0. |
| `test_config.py` | `test_default_policies` | Default config: returns_none is required, init_returns_none is forbidden. |
| `test_config.py` | `test_parse_policies` | returns_none and init_returns_none: parsed into Policy members. |
| `test_config.py` | `test_parse_policy_invalid_value` | Unknown policy value: raises ValueError. |
| `test_config.py` | `test_parse_policy_forbidden_allowed_on_returns_descriptions` | returns_descriptions = forbidden: accepted, the value is meaningful there. |
| `test_config.py` | `test_option_values_reflect_config` | option_values: returns every option of OPTIONS_REGISTRY with its current value. |
| `test_config.py` | `test_always_on_rule_stays_enabled_when_ignored` | A rule listed in ALWAYS_ON: is_rule_enabled returns True even when ignored. |

### load_config

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_load_config_toml_without_section_returns_default` | pyproject.toml with no [tool.docstring-linter] section: returns default config. |
| `test_config.py` | `test_load_config_toml_with_section` | pyproject.toml with [tool.docstring-linter] section: config is populated. |
| `test_config.py` | `test_load_config_no_file_returns_default` | Explicit path that does not exist: returns default LinterConfig. |
| `test_config.py` | `test_load_config_auto_discover` | No explicit path: load_config walks up directories to find pyproject.toml. |
| `test_config.py` | `test_load_config_auto_discover` | No explicit path from subdirectory: pyproject.toml found by walking up. |
| `test_config.py` | `test_load_config_standalone_toml` | .docstring-linter.toml with flat config: parsed directly without [tool.docstring-linter]. |
| `test_config.py` | `test_load_config_custom_named_toml` | Explicitly passed non-pyproject.toml file: parsed directly regardless of name. |
| `test_config.py` | `test_load_config_auto_discover_standalone` | No explicit path: .docstring-linter.toml discovered when no pyproject.toml present. |
| `test_config.py` | `test_load_config_pyproject_takes_priority_over_standalone` | Both pyproject.toml and .docstring-linter.toml present: pyproject.toml wins. |

---

## test_models.py -- models

| Fichier | Fonction | Description |
|---|---|---|
| `test_models.py` | `test_lint_error_str` | LintError.__str__ formats as filepath:line: entity_name - [rule] message. |

---

## test_integration.py -- end-to-end

### lint_file (via subprocess)

| Fichier | Fonction | Description |
|---|---|---|
| `test_integration.py` | `test_lint_file_valid_returns_no_errors` | Valid well-documented file: lint_file returns no errors. |
| `test_integration.py` | `test_lint_file_invalid_returns_errors` | File with missing Args and Returns sections: lint_file returns errors. |
| `test_integration.py` | `test_lint_file_syntax_error_propagates` | File with SyntaxError: lint_file raises SyntaxError. |

### CLI (via subprocess)

| Fichier | Fonction | Description |
|---|---|---|
| `test_integration.py` | `test_cli_valid_file_exit_zero` | CLI on valid file: exits with code 0. |
| `test_integration.py` | `test_cli_invalid_file_exit_one` | CLI on file with errors: exits with code 1. |
| `test_integration.py` | `test_collect_python_files_finds_all_py` | Directory with multiple .py files: collect_python_files returns all of them. |
| `test_integration.py` | `test_collect_python_files_exclude_pattern` | Directory with exclusion pattern: matching files are not collected. |
| `test_integration.py` | `test_cli_list_rules_exit_zero` | --list-rules: exits with code 0 and prints rule names. |
| `test_integration.py` | `test_cli_syntax_error_no_crash` | CLI on file with SyntaxError: does not crash, prints error message, exits 0. |
| `test_integration.py` | `test_cli_json_output_valid_file` | --format json on valid file: JSON report printed to stdout with 0 errors. |
| `test_integration.py` | `test_cli_json_output_invalid_file` | --format json on file with errors: JSON report on stdout with errors. |
| `test_integration.py` | `test_cli_github_annotations_valid_file` | --format github-annotations on valid file: no output, exit 0. |
| `test_integration.py` | `test_cli_github_annotations_invalid_file` | --format github-annotations on file with errors: annotations on stdout, exit 1. |
