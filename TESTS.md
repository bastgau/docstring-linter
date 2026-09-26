# Test Plan

This file lists the 576 tests of the `docstring-linter` project. Each entry shows the test file, the function name, and a description of the case covered. Tests are organized by tested module and by rule or feature.

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
| `test_docstring_parser.py` | `test_parse_returns_prose_with_colon` | Returns line whose text before the colon is prose: the whole line is the description. |
| `test_docstring_parser.py` | `test_parse_returns_continuation_lines` | Returns description spread over several lines: the lines are joined. |
| `test_docstring_parser.py` | `test_parse_returns_single_word_prose` | Returns section holding a single word that is not a type: read as the description. |
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
| `test_docstring_parser.py` | `test_unknown_section_detected` | Section name not in known list: captured in unknown_sections. |
| `test_docstring_parser.py` | `test_unknown_section_known_not_flagged` | Known section: not captured in unknown_sections. |
| `test_docstring_parser.py` | `test_unknown_section_multiple` | Multiple unknown sections in parsed docstring: all captured. |
| `test_docstring_parser.py` | `test_parse_alias_read_as_canonical` | Parameters: alias of Args, its entries are parsed as args and it is not unknown. |
| `test_docstring_parser.py` | `test_parse_args_and_other_parameters_joined` | Args and Other Parameters sections: entries of both end up in args. |
| `test_docstring_parser.py` | `test_parse_keyword_args` | Keyword Arguments: entries parsed into keyword_args, not into args. |
| `test_docstring_parser.py` | `test_parse_free_text_sections` | Warning and See Also: known sections, neither unknown nor merged into the description. |
| `test_docstring_parser.py` | `test_parse_note_and_notes_distinct` | Note and Notes: two known sections, neither is an alias nor unknown. |
| `test_docstring_parser.py` | `test_parse_exceptions_is_unknown` | Exceptions: not a Napoleon section, reported as unknown and not read as Raises. |
| `test_docstring_parser.py` | `test_parse_lowercase_section_not_recognized` | Lowercase section name (args: instead of Args:): not recognized, no args parsed. |

### style

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_parser_style_property` | Style property: returns DocstringStyle.GOOGLE. |

### get_parser

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_get_parser_google` | get_parser(GOOGLE): returns a GoogleStyleParser instance. |

---

## test_ast_parser.py -- ast_parser

### _extract_args

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_args_no_args` | Method with only self in its signature: returns empty list because the first parameter is skipped. |
| `test_ast_parser.py` | `test_extract_args_positional_with_type_and_default` | Positional arg with type annotation and default value: all three fields are populated. |
| `test_ast_parser.py` | `test_extract_args_positional_without_type` | Positional arg with no type annotation: type_annotation is None. |
| `test_ast_parser.py` | `test_extract_args_positional_without_default` | Positional arg with no default value: default is None. |
| `test_ast_parser.py` | `test_extract_args_keyword_only` | Keyword-only arg (after bare *): extracted with correct name and type. |
| `test_ast_parser.py` | `test_extract_args_keyword_only_with_default` | Keyword-only arg with a default value: default is correctly extracted. |
| `test_ast_parser.py` | `test_extract_args_skips_first_param_whatever_its_name` | Method: the first positional parameter is dropped by position, not by name. |
| `test_ast_parser.py` | `test_extract_args_keeps_self_and_cls_names_on_functions` | Plain function: parameters named self or cls are regular parameters. |
| `test_ast_parser.py` | `test_extract_args_skips_only_the_first_param` | Method with a second parameter named cls: only the first parameter is dropped. |
| `test_ast_parser.py` | `test_extract_args_mixed_positional_and_keyword_only` | Mix of positional and keyword-only args: both are returned in declaration order. |
| `test_ast_parser.py` | `test_extract_args_vararg_and_kwarg` | *args and **kwargs are extracted with their stars in the name. |
| `test_ast_parser.py` | `test_extract_args_vararg_without_annotation` | *args without annotation: type_annotation is None. |
| `test_ast_parser.py` | `test_extract_args_positional_only` | Positional-only args (before /): extracted with name and type. |
| `test_ast_parser.py` | `test_extract_args_positional_only_skips_self` | self in positional-only position: excluded like elsewhere. |
| `test_ast_parser.py` | `test_extract_args_positional_only_default_alignment` | Defaults align by the end of posonlyargs + args combined. |
| `test_ast_parser.py` | `test_extract_args_positional_only_with_default` | Positional-only arg with a default: default is correctly extracted. |

### _scan_body -- raises

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_raises_none` | Function with no raise statements: returns empty list. |
| `test_ast_parser.py` | `test_extract_raises_simple_call` | Raise ValueError("msg"): detected by the exception class name. |
| `test_ast_parser.py` | `test_extract_raises_variable_ignored` | Raise err where err is a variable, not bound by an except clause: ignored. |
| `test_ast_parser.py` | `test_extract_raises_bare_class_name` | Raise ValueError without call: the class name is recorded. |
| `test_ast_parser.py` | `test_extract_raises_lowercase_factory_ignored` | Raise make_error('x'): a lowercase callable is not an exception class, ignored. |
| `test_ast_parser.py` | `test_extract_raises_bare_raise_ignored` | Bare raise outside any handler: ignored because there is no exception type. |
| `test_ast_parser.py` | `test_extract_raises_deduplicates` | Same exception raised twice: appears only once in the result list. |
| `test_ast_parser.py` | `test_extract_raises_multiple_distinct` | Two different exceptions raised: both are present in the result. |
| `test_ast_parser.py` | `test_scan_body_reraise_of_caught_name` | Raise err inside 'except ValueError as err': reported as ValueError, not as err. |
| `test_ast_parser.py` | `test_scan_body_reraise_of_caught_tuple` | Raise err inside 'except (KeyError, mod.Error) as err': every caught type is reported. |
| `test_ast_parser.py` | `test_scan_body_bare_raise_in_handler` | Bare raise inside 'except (KeyError, mod.Error)': every caught type is reported. |
| `test_ast_parser.py` | `test_scan_body_bare_raise_in_nested_handler` | Bare raise in a handler nested in another: reports the inner caught type only. |
| `test_ast_parser.py` | `test_scan_body_bare_raise_in_untyped_handler_ignored` | Bare raise inside a bare 'except:': ignored because no type is caught. |
| `test_ast_parser.py` | `test_scan_body_dotted_exception` | Raise errors.ValidationError(...): reported by its last name segment. |
| `test_ast_parser.py` | `test_scan_body_lowercase_attribute_ignored` | Raise self.error: not an exception class name, ignored. |
| `test_ast_parser.py` | `test_scan_body_nested_function_ignored` | Raise and yield inside a nested function or lambda: not attributed to the outer function. |
| `test_ast_parser.py` | `test_scan_body_source_order` | Several raises: reported in source order, with the line of the first occurrence. |

### _is_empty_init

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_is_empty_init_pass_only` | __init__(self) with only a pass statement: classified as empty. |
| `test_ast_parser.py` | `test_is_empty_init_docstring_only` | __init__(self) with only a docstring: classified as empty (docstring is not logic). |
| `test_ast_parser.py` | `test_is_empty_init_with_positional_arg` | __init__(self, name: str): has a real positional arg, not empty. |
| `test_ast_parser.py` | `test_is_empty_init_with_kwonly_arg` | __init__(self, *, name: str): has a keyword-only arg, not empty. |
| `test_ast_parser.py` | `test_is_empty_init_with_body` | __init__(self) with self.x = 1 in the body: has real statements, not empty. |
| `test_ast_parser.py` | `test_is_empty_init_with_star_args` | __init__ taking *args or **kwargs: has parameters, not empty (2 cases). |

### _extract_class_attributes

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_extract_class_attributes_annotations` | Class-level annotations are extracted as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_self_assignments` | self.x assignments in __init__ are extracted as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_dedup_and_order` | Class annotations and __init__ assignments merge without duplicates, in first-seen order. |
| `test_ast_parser.py` | `test_extract_class_attributes_skips_dunder` | Dunder assignments like __slots__ are not treated as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_skips_constants` | All-uppercase names (constants) are not treated as attributes. |
| `test_ast_parser.py` | `test_extract_class_attributes_none` | Class with no attributes: returns empty list. |
| `test_ast_parser.py` | `test_extract_class_attributes_tuple_self_assignment` | self.a, *self.b = ... in __init__: every unpacked self attribute is extracted. |
| `test_ast_parser.py` | `test_extract_class_attributes_tuple_class_assignment` | a, b = ... in the class body: both names are extracted. |
| `test_ast_parser.py` | `test_extract_class_attributes_ignores_nested_function` | self.x assigned inside a function nested in __init__: not a class attribute. |

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
| `test_ast_parser.py` | `test_is_generator_nested_generator_not_propagated` | Function defining a nested generator: the outer function is not a generator. |
| `test_ast_parser.py` | `test_parse_file_functions_under_compound_statements` | Functions defined under if, else, try, except, with and match: all extracted. |
| `test_ast_parser.py` | `test_parse_file_method_under_if_in_class` | Method defined under an if inside a class body: extracted as a method of that class. |
| `test_ast_parser.py` | `test_parse_file_skips_overload_stubs` | @overload and @typing.overload stubs: not extracted, the implementation is. |
| `test_ast_parser.py` | `test_parse_file_staticmethod_keeps_first_param` | @staticmethod: the first parameter is a regular parameter, even when named self. |
| `test_ast_parser.py` | `test_parse_file_skips_main_guard_body` | Functions and classes under 'if __name__ == "__main__":': skipped, the else branch is kept. |
| `test_ast_parser.py` | `test_parse_file_records_decorators` | Decorators: recorded by their last name segment, sorted, attribute and call forms included. |
| `test_ast_parser.py` | `test_parse_file_links_class_and_init` | Class with __init__: the class carries the __init__ parameters, __init__ carries the class docstring. |

## test_end_to_end.py -- lint_file on real sources

| Fichier | Fonction | Description |
|---|---|---|
| `test_end_to_end.py` | `test_nested_generator_does_not_make_outer_a_generator` | Function defining a nested generator: documented with Returns, no error. |
| `test_end_to_end.py` | `test_reraise_of_caught_exception` | Raise err inside 'except ValueError as err': ValueError documented, no error. |
| `test_end_to_end.py` | `test_bare_reraise_requires_caught_exception` | Bare raise inside 'except ValueError': ValueError must be documented. |
| `test_end_to_end.py` | `test_tuple_self_assignment_requires_attributes` | self.a, self.b = ... in __init__: both attributes must be documented. |
| `test_end_to_end.py` | `test_dotted_exception` | Raise errors.ValidationError: documented by short or dotted name, no error. |
| `test_end_to_end.py` | `test_undocumented_dotted_exception_reported` | Raise errors.ValidationError without Raises section: reported by raises_section. |
| `test_end_to_end.py` | `test_function_under_if_is_linted` | Function defined under an if block: linted like a top-level function. |
| `test_end_to_end.py` | `test_metaclass_first_parameter_not_required` | Metaclass __new__(mcs, ...): mcs is not required in Args. |
| `test_end_to_end.py` | `test_staticmethod_first_parameter_required` | @staticmethod: the first parameter must be documented like any other. |
| `test_end_to_end.py` | `test_overload_stubs_not_linted` | @overload stubs without docstring: only the documented implementation is linted. |
| `test_end_to_end.py` | `test_main_guard_not_linted` | Demo code under 'if __name__ == "__main__":' without docstrings: no error. |
| `test_end_to_end.py` | `test_variable_raise_not_required_in_raises` | Raise of a variable holding an exception: nothing to document, no error. |
| `test_end_to_end.py` | `test_google_convention_accepts_google_guide_style` | Google guide layout (untyped Args, no Returns: None, descriptive mood): no error under convention google. |
| `test_end_to_end.py` | `test_strict_convention_rejects_google_guide_style` | Same source under the strict default: the house rules the google convention relaxes are reported. |
| `test_end_to_end.py` | `test_google_convention_accepts_napoleon_types` | Optional parameter documented '(int, optional)', forward reference, untyped Returns: no error under google. |
| `test_end_to_end.py` | `test_strict_convention_reports_implicit_none` | Same kind of source under strict: '(int, optional)' for Optional[int] and the untyped Returns are reported. |
| `test_end_to_end.py` | `test_propagated_exception_reported_under_strict` | Exception documented but raised by a callee: raises_extraneous under the strict default. |
| `test_end_to_end.py` | `test_propagated_exception_accepted_under_google` | Same source under convention google, blank line kept before the quotes: raises_extraneous is off, no error. |
| `test_end_to_end.py` | `test_napoleon_sections` | Keyword Args, Warning and See Also: **kwargs documented, no unknown section, no error. |
| `test_end_to_end.py` | `test_parameters_alias` | Parameters instead of Args: arguments count as documented, section_alias is the only error. |
| `test_end_to_end.py` | `test_exemptions_off_by_default` | Strict default: dunder, private, overridden and property methods are all checked. |
| `test_end_to_end.py` | `test_exemptions_enabled` | All four options on: none of those entities is reported. |
| `test_end_to_end.py` | `test_exempted_docstring_still_checked` | Dunder with a docstring under exclude_dunder_methods: the docstring content is still checked. |
| `test_end_to_end.py` | `test_init_args_in_class_rejected_by_default` | Parameters documented in the class, init_args_location = 'init' (default): __init__ lacks a docstring. |
| `test_end_to_end.py` | `test_init_args_in_class_accepted` | Parameters documented in the class, location class or either: no error (2 cases). |
| `test_end_to_end.py` | `test_init_args_in_class_checked` | Class Args missing a parameter, location either: the parameter is reported on the class. |
| `test_end_to_end.py` | `test_init_args_either_falls_back_to_init` | Class without Args, location either: __init__ is checked as usual and needs its docstring. |
| `test_end_to_end.py` | `test_init_args_short_init_docstring` | __init__ with a docstring but no Args, class with Args, location either: no error. |
| `test_end_to_end.py` | `test_init_args_mixed` | Args in the class and in __init__, location either: reported as mixed on __init__. |
| `test_end_to_end.py` | `test_init_args_class_location_rejects_init_args` | Args only in __init__, location class: reported on __init__, and missing on the class. |
| `test_end_to_end.py` | `test_one_liners_need_sections_by_default` | One-line docstrings on annotated functions, option off (strict default): every missing section is reported. |
| `test_end_to_end.py` | `test_one_liners_sections_optional` | Same functions, sections_optional_on_one_liners on: no error. |
| `test_end_to_end.py` | `test_one_liner_without_annotations_still_checked` | One-line docstring on a function missing an annotation: sections still required. |
| `test_end_to_end.py` | `test_multi_line_docstring_still_checked` | Docstring with a description but no section: not a one-liner, sections still required. |

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

### type comparison

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_types.py` | `test_types_match` | Each level accepts what the previous one accepts, and real differences are always reported (20 cases). |

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
| `rules/test_rules_args.py` | `test_args_section_kwargs_documented_by_keyword_args` | **kwargs in the signature and a Keyword Args section: **kwargs counts as documented. |
| `rules/test_rules_args.py` | `test_args_match_keyword_arg_missing_description` | Keyword Args entry without a description: returns args_match error, its name is not compared with the signature. |
| `rules/test_rules_args.py` | `test_documented_stars_policy` | Starred parameter documented with or without stars: one explicit error when the policy is not met, nothing else (6 cases). |
| `rules/test_rules_args.py` | `test_documented_stars_on_plain_parameter` | Plain parameter documented with a star: reported whatever the policy (3 cases). |
| `rules/test_rules_args.py` | `test_documented_stars_order_uses_bare_names` | Starless entry in signature order: no args_order error. |
| `rules/test_rules_args.py` | `test_documented_stars_duplicate` | 'items' then '*items' in the same section: reported as a duplicate. |
| `rules/test_rules_args.py` | `test_returns_match_missing_type` | documented_types = required, Returns section without a type: returns returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_type_optional` | documented_types = optional, Returns section without a type: no returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_type_forbidden` | documented_types = forbidden, Returns line carrying a type: returns returns_match error. |
| `rules/test_rules_args.py` | `test_returns_match_type_forbidden_allows_none` | documented_types = forbidden, 'Returns: None': None is the whole line, no error. |
| `rules/test_rules_args.py` | `test_returns_match_type_matching_levels` | Signature Optional[str], docstring 'str \| None': a mismatch only at the strict level (3 cases). |
| `rules/test_rules_args.py` | `test_args_match_type_matching_levels` | Signature 'int \| None': each level accepts what the previous ones accept, and more (5 cases). |
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
| `rules/test_rules_args.py` | `test_raises_section_optional_still_checks_documented` | Policy optional, an exception documented but never raised: raises_extraneous still reports it. |
| `rules/test_rules_args.py` | `test_raises_section_forbidden_present` | Policy forbidden, documented exceptions: returns raises_section error. |
| `rules/test_rules_args.py` | `test_raises_extraneous_documented_not_raised` | Raise in docstring but not in code: returns raises_extraneous error. |
| `rules/test_rules_args.py` | `test_raises_extraneous_disabled` | Rule off, exception documented but propagated from a callee: no error. |
| `rules/test_rules_args.py` | `test_raises_match_missing_description` | Exception documented without a description: returns raises_match error. |
| `rules/test_rules_args.py` | `test_raises_match_correct` | Raises section matches the code: no error. |

### yields_section (policy) / yields_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_yields_section_required_missing` | Policy required, generator without Yields section: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_section_optional_missing` | Policy optional, generator without Yields section: no error. |
| `rules/test_rules_args.py` | `test_yields_section_forbidden_present` | Policy forbidden, Yields section present: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_match_missing_type` | documented_types = required, Yields section without a type: returns yields_match error. |
| `rules/test_rules_args.py` | `test_yields_match_type_optional` | documented_types = optional, Yields section without a type: no yields_match type error. |
| `rules/test_rules_args.py` | `test_yields_match_type_forbidden` | documented_types = forbidden, Yields line carrying a type: returns yields_match error. |
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
| `rules/test_rules_structure.py` | `test_indentation_under_indented_section_line` | Line of a section indented by 2 spaces: returns one indentation error for the section. |
| `rules/test_rules_structure.py` | `test_indentation_first_entry_not_at_four` | First Args entry indented by 8 spaces: returns indentation error. |
| `rules/test_rules_structure.py` | `test_indentation_multiline_entry` | Entry description continued on deeper lines: no indentation error. |
| `rules/test_rules_structure.py` | `test_indentation_description_block_ignored` | Indented code block in the description, outside any section: no indentation error. |
| `rules/test_rules_structure.py` | `test_indentation_one_liner_skipped` | One-liner docstring: indentation rule skips it, no error. |

### section_capitalization

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_section_capitalization_correct` | Correctly capitalized section 'Args:': no error. |
| `rules/test_rules_structure.py` | `test_section_capitalization_multi_word` | Multi-word Napoleon header 'See also:': returns section_capitalization error expecting 'See Also:'. |

### section_alias

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_section_alias_reported` | Napoleon alias used as a header: returns section_alias error naming the canonical spelling (5 cases). |
| `rules/test_rules_structure.py` | `test_section_alias_disabled` | Alias used, rule off: no section_alias error. |
| `rules/test_rules_structure.py` | `test_section_capitalization_wrong` | Lowercase section header 'args:': returns section_capitalization error. |

### section_order

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_section_order_correct` | Args before Returns: no section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_wrong` | Returns before Args: returns section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_single_section_ok` | Only one recognized section: no section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_unknown_section_ignored` | Unknown section between known sections: order check skips it. |
| `rules/test_rules_structure.py` | `test_section_order_alias_and_free_text` | Parameters placed like Args, Warning anywhere: no section_order error. |
| `rules/test_rules_structure.py` | `test_section_order_alias_out_of_place` | Return before Parameters: section_order error listing canonical names. |
| `rules/test_rules_structure.py` | `test_empty_free_text_section` | Empty See Also section: returns empty_section error, free-text sections are known sections. |
| `rules/test_rules_structure.py` | `test_entry_spacing_in_alias_section` | Badly spaced entry under Parameters: entry_spacing applies to aliases of Args. |

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
| `rules/test_rules_structure.py` | `test_closing_quotes_on_text_line` | Multi-line docstring closed on the line of its last text: one error saying so, whatever the configured count (2 cases). |
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
| `rules/test_rules_docstring.py` | `test_imperative_mood_suggestion` | Third-person verb, irregular or not: the suggested base form is a real verb (6 cases). |
| `rules/test_rules_docstring.py` | `test_imperative_mood_not_a_verb` | Plural noun, word ending in s, or token that is not a word: no imperative_mood error (10 cases). |
| `rules/test_rules_docstring.py` | `test_imperative_mood_skips_classes` | Class docstring starting with a third-person verb: not checked, the rule targets functions and methods. |
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
| `rules/test_rules_structure.py` | `test_examples_section_required_missing` | Policy required, no Examples section: returns examples_section error. |
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
| `test_cli.py` | `test_collect_recursive_glob_excluded` | Pattern tests/**: every file under tests/ is excluded, at any depth. |
| `test_cli.py` | `test_collect_directory_glob_excluded` | Pattern src/gen/*.py: files directly under src/gen/ are excluded, others kept. |

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
| `test_cli.py` | `test_run_syntax_error_returns_two` | File with SyntaxError: reported on stderr, run returns 2. |
| `test_cli.py` | `test_run_syntax_error_keeps_json_valid` | File with SyntaxError under --format json: stdout stays valid JSON, run returns 2. |
| `test_cli.py` | `test_run_undecodable_file_returns_two` | File that is not valid UTF-8: reported as unreadable on stderr, run returns 2. |
| `test_cli.py` | `test_run_failure_wins_over_lint_errors` | One unparsable file and one file with lint errors: run returns 2. |
| `test_cli.py` | `test_run_missing_path_returns_two` | Path that does not exist: reported on stderr, run returns 2 without linting. |
| `test_cli.py` | `test_run_parallel_workers` | Two workers on two files: errors from every file are collected. |
| `test_cli.py` | `test_run_with_json_output` | Run with output_format=json: JSON report is printed to stdout. |
| `test_cli.py` | `test_run_statistics_counts_errors_per_rule` | Run with statistics: one count per rule instead of each error, same exit code. |

### main / --list-rules

| Fichier | Fonction | Description |
|---|---|---|
| `test_cli.py` | `test_main_invalid_config_value` | Invalid value in the config file: prints a configuration error and exits with 2. |
| `test_cli.py` | `test_main_missing_config_file` | --config pointing to a missing file: prints a configuration error and exits with 2. |
| `test_cli.py` | `test_main_statistics_rejected_with_json` | --statistics with a machine-readable format: error on stderr and exit 2. |
| `test_cli.py` | `test_main_from_subdirectory_uses_config_directory` | Run from src/ with the config at the root: exclude and override patterns still apply from the root. |
| `test_cli.py` | `test_list_rules_output` | --list-rules: every rule appears, always-on rules in their own section after the categories. |

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

### report_statistics

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_statistics_no_errors` | No errors: prints summary with 0 errors. |
| `test_reporter.py` | `test_report_statistics_sorted_by_count_then_rule` | Most frequent rule first, ties in alphabetical order, counts right-aligned. |

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

### report_overrides

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_overrides_nothing_printed_when_empty` | No override declared: nothing is printed. |
| `test_reporter.py` | `test_report_overrides_shows_paths_and_delta` | Override declared: paths, changed values and the base value appear. |

### report_rules

| Fichier | Fonction | Description |
|---|---|---|
| `test_reporter.py` | `test_report_rules_all_categories_present` | Category names with at least one configurable rule appear in output. |
| `test_reporter.py` | `test_report_rules_all_rules_present` | All configurable rule identifiers appear in output. |
| `test_reporter.py` | `test_report_rules_enabled_rule_shows_checkmark` | Enabled rule shows checkmark marker. |
| `test_reporter.py` | `test_report_rules_disabled_rule_shows_cross` | Disabled rule shows cross marker. |
| `test_reporter.py` | `test_report_rules_off_by_default_label` | Rule in off_by_default shows '(disabled by default)' label. |
| `test_reporter.py` | `test_report_rules_always_on_listed_separately` | Rule in always_on: listed after the categories, not counted as configurable. |
| `test_reporter.py` | `test_report_rules_category_hidden_when_all_rules_always_on` | Category whose rules are all always on: the category is not printed. |
| `test_reporter.py` | `test_report_policies_all_policies_present` | All policy identifiers and their values appear in output. |
| `test_reporter.py` | `test_report_policies_optional_value` | Policy set to optional shows its value on the matching line. |
| `test_reporter.py` | `test_report_options_all_options_present` | All option identifiers and their values appear in output. |
| `test_reporter.py` | `test_report_options_value_on_matching_line` | Each option value is printed on the line of its option. |
| `test_reporter.py` | `test_report_single_file_singular` | One file checked: the summary says '1 file checked'. |
| `test_reporter.py` | `test_report_github_annotations_escaped` | Message and properties escaped as @actions/core does: %, line breaks, and in properties ':' and ','. |
| `test_reporter.py` | `test_report_no_color_when_not_a_terminal` | Output captured, not a terminal: no ANSI escape sequence at all. |
| `test_reporter.py` | `test_colors_follow_terminal_and_no_color` | Colors on a terminal only, and off when NO_COLOR holds a non-empty value (4 cases). |

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
| `test_config.py` | `test_parse_select_all_with_ignore` | Select = ['ALL'] + ignore = ['imperative_mood']: all rules except imperative_mood. |
| `test_config.py` | `test_parse_select_explicit_list` | Select = ['docstring_exists', 'args_match']: only those two rules enabled. |
| `test_config.py` | `test_parse_ignore_only` | Ignore only (no select): starts from default set minus ignored rules. |
| `test_config.py` | `test_parse_no_select_no_ignore` | Empty data: enabled_rules matches default config. |
| `test_config.py` | `test_parse_style_google` | Style = 'google': config.style is DocstringStyle.GOOGLE. |
| `test_config.py` | `test_parse_style_unknown` | Style = 'unknown': raises ValueError listing the accepted styles. |
| `test_config.py` | `test_parse_style_without_parser` | Style = 'numpy': rejected at load time, no parser implements it. |
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
| `test_config.py` | `test_parse_policy_invalid_value` | Unknown policy value: raises ValueError naming the key and the accepted values. |
| `test_config.py` | `test_parse_policy_forbidden_allowed_on_returns_descriptions` | returns_descriptions = forbidden: accepted, the value is meaningful there. |
| `test_config.py` | `test_option_values_reflect_config` | option_values: returns every option of OPTIONS_REGISTRY with its current value. |
| `test_config.py` | `test_always_on_rule_stays_enabled_when_not_selected` | A rule listed in ALWAYS_ON: is_rule_enabled returns True even when not selected. |

### unknown keys and rules

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_parse_unknown_key` | Key absent from the registries: raises ValueError naming it. |
| `test_config.py` | `test_parse_unknown_keys_are_all_reported` | Several unknown keys: all of them are named in the message. |
| `test_config.py` | `test_parse_unknown_scope_key` | Unknown key under scope: raises ValueError naming the section. |
| `test_config.py` | `test_parse_unknown_rule_in_select` | Unknown rule name in select: raises ValueError naming it. |
| `test_config.py` | `test_parse_unknown_rule_in_ignore` | Unknown rule name in ignore: raises ValueError naming it. |
| `test_config.py` | `test_parse_select_all_is_accepted` | Select = ALL: the wildcard is not treated as a rule name. |
| `test_config.py` | `test_parse_ignore_always_on_rule` | Always-on rule in ignore: raises ValueError instead of silently doing nothing. |

### overrides

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_parse_override_policy_and_option` | Override carrying a policy and an option: both are parsed. |
| `test_config.py` | `test_parse_override_without_paths` | Override missing its paths list: raises ValueError. |
| `test_config.py` | `test_parse_override_run_level_key` | Override carrying a run-level key: raises ValueError naming the key. |
| `test_config.py` | `test_parse_override_unknown_key` | Override carrying an unknown key: raises ValueError naming the override. |
| `test_config.py` | `test_parse_override_unknown_rule` | Override ignoring an unknown rule: raises ValueError naming the override. |
| `test_config.py` | `test_parse_override_invalid_policy_value` | Override carrying an invalid policy value: raises ValueError naming the key. |
| `test_config.py` | `test_for_path_without_override_returns_self` | No override declared: for_path returns the very same config object. |
| `test_config.py` | `test_for_path_applies_matching_override` | Matching override: the policy is overridden, the base config is left untouched. |
| `test_config.py` | `test_for_path_ignores_non_matching_override` | Override whose patterns do not match: the base config is returned as is. |
| `test_config.py` | `test_for_path_last_override_wins` | Two matching overrides: the last declared one wins. |
| `test_config.py` | `test_for_path_ignore_removes_from_inherited_rules` | Ignore key in an override: the rule is removed from the inherited set. |
| `test_config.py` | `test_for_path_select_replaces_inherited_rules` | Select key in an override: the inherited set is replaced by the listed rules. |
| `test_config.py` | `test_for_path_override_select_all` | Select = ['ALL'] in an override: every rule is enabled on the matching files. |
| `test_config.py` | `test_for_path_patterns_relative_to_base_dir` | Run from a subdirectory: the override pattern is matched relative to base_dir, not to the current directory. |
| `test_config.py` | `test_for_path_file_outside_base_dir` | File outside base_dir: no override applies, even with a catch-all pattern. |

### convention

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_convention_defaults_to_strict` | No convention key: strict convention, same settings as the built-in defaults. |
| `test_config.py` | `test_convention_google_sets_defaults` | Convention = 'google': relaxed policies, no blank line before the closing quotes, two rules off. |
| `test_config.py` | `test_convention_explicit_keys_win` | Convention = 'google' with explicit keys: the keys of the file override the convention. |
| `test_config.py` | `test_convention_ignore_applies_on_top` | Convention = 'google' with ignore: rules removed from the convention set, disabled ones stay off. |
| `test_config.py` | `test_convention_select_all_enables_everything` | Convention = 'google' with select = ['ALL']: every rule is enabled, the explicit key wins. |
| `test_config.py` | `test_convention_unknown` | Convention = 'numpy': raises ValueError listing the accepted conventions. |
| `test_config.py` | `test_convention_rejected_in_override` | Convention in an override: rejected, it sets the defaults of the whole run. |
| `test_config.py` | `test_convention_listed_in_option_values` | option_values: reports the active convention. |

### docstring exemptions

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_exemption_options` | Exemption option: off by default, set from the file, allowed in an override (5 cases). |
| `test_config.py` | `test_init_args_location` | init_args_location: 'init' by default, accepts class and either, rejects other values. |

### type_matching

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_type_matching_default_strict` | No type_matching key: strict comparison. |
| `test_config.py` | `test_type_matching_set` | type_matching = 'equivalent': stored as is and reported by option_values. |
| `test_config.py` | `test_type_matching_invalid` | type_matching = 'loose': raises ValueError listing the accepted levels. |
| `test_config.py` | `test_type_matching_in_override` | type_matching in an override: applied to the matching files only. |

### value types

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_parse_rejects_wrong_value_type` | Value of the wrong TOML type: raises ValueError naming the key and the value (9 cases). |
| `test_config.py` | `test_parse_override_rejects_wrong_value_type` | Option of the wrong type in an override: raises ValueError naming the override. |
| `test_config.py` | `test_parse_override_rejects_string_paths` | Paths given as a string in an override: raises ValueError. |
| `test_config.py` | `test_parse_override_option_clamped` | summary_max_length = -5 in an override: clamped to 1, like at the top level. |

### load_config

| Fichier | Fonction | Description |
|---|---|---|
| `test_config.py` | `test_load_config_toml_without_section` | Explicit pyproject.toml with no [tool.docstring-linter] section: raises ValueError. |
| `test_config.py` | `test_load_config_toml_with_section` | pyproject.toml with [tool.docstring-linter] section: config is populated. |
| `test_config.py` | `test_load_config_missing_explicit_file` | Explicit path that does not exist: raises ValueError naming the path. |
| `test_config.py` | `test_load_config_explicit_directory` | Explicit path that is a directory: raises ValueError. |
| `test_config.py` | `test_load_config_base_dir_is_config_directory` | Explicit config file: base_dir is the resolved directory holding it. |
| `test_config.py` | `test_load_config_auto_discover` | No explicit path: load_config walks up directories to find pyproject.toml. |
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
| `test_integration.py` | `test_cli_syntax_error_no_crash` | CLI on file with SyntaxError: does not crash, prints error message on stderr, exits 2. |
| `test_integration.py` | `test_cli_json_output_valid_file` | --format json on valid file: JSON report printed to stdout with 0 errors. |
| `test_integration.py` | `test_cli_json_output_invalid_file` | --format json on file with errors: JSON report on stdout with errors. |
| `test_integration.py` | `test_cli_github_annotations_valid_file` | --format github-annotations on valid file: no output, exit 0. |
| `test_integration.py` | `test_cli_github_annotations_invalid_file` | --format github-annotations on file with errors: annotations on stdout, exit 1. |
