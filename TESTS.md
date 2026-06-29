# Test Plan

This file lists the 236 tests of the `docstring-linter` project. Each entry shows the test file, the function name, and a description of the case covered. Tests are organized by tested module and by rule or feature.

## test_parser.py -- GoogleStyleParser

### parse (via public API)

| Fichier | Fonction | Description |
|---|---|---|
| `test_docstring_parser.py` | `test_parse_empty_docstring` | Empty docstring: returns empty ParsedDocstring with no fields set. |
| `test_docstring_parser.py` | `test_parse_oneliner` | One-liner docstring: summary is set, no other fields. |
| `test_docstring_parser.py` | `test_parse_summary_and_description` | Summary + blank line + description: both summary and description are set. |
| `test_docstring_parser.py` | `test_parse_arg_with_type_and_description` | Arg with type and description: all fields populated. |
| `test_docstring_parser.py` | `test_parse_arg_without_type` | Arg without type annotation: type_annotation is None. |
| `test_docstring_parser.py` | `test_parse_arg_multiline_description` | Arg with continuation line: description is concatenated. |
| `test_docstring_parser.py` | `test_parse_multiple_args` | Multiple args: all are returned in order. |
| `test_docstring_parser.py` | `test_parse_returns_with_type_and_description` | Standard Returns line: type and description are extracted. |
| `test_docstring_parser.py` | `test_parse_returns_none_keyword` | Returns section containing only 'None': type_annotation is 'None', description is None. |
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

### parse_file

| Fichier | Fonction | Description |
|---|---|---|
| `test_ast_parser.py` | `test_parse_file_returns_module_entity` | Any Python file produces a MODULE entity as the first result, with its docstring. |
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
| `rules/test_rules_docstring.py` | `test_summary_exists_present` | Summary present: no error. |
| `rules/test_rules_docstring.py` | `test_summary_exists_missing` | No summary in parsed_doc: returns summary_exists error. |

### summary_punctuation

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_punctuation_present` | Summary ending with period: no error. |
| `rules/test_rules_docstring.py` | `test_summary_punctuation_missing_period` | Summary without period: returns summary_punctuation error. |

### return_type_annotation

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_return_type_annotation_present` | Function with -> int annotation: no error. |
| `rules/test_rules_args.py` | `test_return_type_annotation_missing` | Function without -> annotation: returns return_type_annotation error. |
| `rules/test_rules_args.py` | `test_return_type_annotation_not_checked_for_class` | Class entity: return_type_annotation rule is not applied. |

### args_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_args_match_correct` | Arg matches signature and docstring perfectly: no error. |
| `rules/test_rules_args.py` | `test_args_match_missing_from_docstring` | Arg in signature but not in docstring: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_extra_in_docstring` | Arg in docstring but not in signature: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_type_mismatch` | Arg type in docstring differs from signature: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_missing_type_in_docstring` | Arg missing type in docstring: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_missing_description_in_docstring` | Arg with no description in docstring: returns args_match error. |
| `rules/test_rules_args.py` | `test_args_match_no_sig_args_no_doc_args` | No args in signature and no args in docstring: no error. |
| `rules/test_rules_args.py` | `test_args_match_doc_arg_extra_via_detailed_path` | Arg in sig and doc but extra doc arg: reports the extra. |

### duplicate_arg

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_duplicate_arg_detected` | Arg documented twice: duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_no_duplicate` | All args unique: no duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_no_args` | No args: no duplicate_arg error. |
| `rules/test_rules_args.py` | `test_duplicate_arg_disabled` | Rule disabled: duplicate not reported. |

### param_order

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_param_order_wrong_order` | Args in docstring in different order than signature: param_order error. |
| `rules/test_rules_args.py` | `test_param_order_correct` | Args in docstring match signature order: no error. |
| `rules/test_rules_args.py` | `test_param_order_no_args` | No args: no error. |
| `rules/test_rules_args.py` | `test_param_order_disabled` | Rule disabled: wrong order not reported. |

### returns_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_returns_section_correct` | Returns section matches signature: no error. |
| `rules/test_rules_args.py` | `test_returns_section_missing` | Function with return type but no Returns section: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_type_mismatch` | Returns section type differs from signature: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_missing_type_in_docstring` | Returns section present but no type declared: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_none_oneliner_exempt_by_default` | One-liner docstring -> None: exempt by default (returns_none_oneliner off). |
| `rules/test_rules_args.py` | `test_returns_section_none_init_exempt_by_default` | __init__ -> None: exempt from returns_section by default (returns_none_init off). |
| `rules/test_rules_args.py` | `test_returns_none_oneliner_required_when_rule_enabled` | One-liner -> None with returns_none_oneliner enabled: returns section required. |

### raises_match

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_raises_match_correct` | Raise matches code and docstring: no error. |
| `rules/test_rules_args.py` | `test_raises_match_undocumented` | Raise in code but not in docstring: returns raises_match error. |
| `rules/test_rules_args.py` | `test_raises_match_phantom_documented` | Raise in docstring but not in code: returns raises_match error. |

### yields_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_args.py` | `test_yields_section_missing` | Generator without Yields section: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_section_missing_type` | Generator with Yields section but no type: returns yields_section error. |
| `rules/test_rules_args.py` | `test_yields_section_correct` | Generator with correct Yields section: no error. |
| `rules/test_rules_args.py` | `test_yields_section_not_applied_to_non_generator` | Non-generator function: yields_section rule is not applied. |
| `rules/test_rules_args.py` | `test_returns_section_error_when_generator_has_returns` | Generator with Returns section instead of Yields: returns returns_section error. |
| `rules/test_rules_args.py` | `test_returns_section_exempt_for_generator_without_returns` | Generator without Returns section: returns_section rule is not triggered. |

### attributes_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_attributes.py` | `test_attributes_section_correct` | Attribute with type and description: no error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_missing` | Class with no Attributes section: returns attributes_section error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_missing_type` | Attribute without type in docstring: returns attributes_section error. |
| `rules/test_rules_attributes.py` | `test_attributes_section_missing_description` | Attribute without description in docstring: returns attributes_section error. |

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
| `rules/test_rules_structure.py` | `test_empty_section_detected` | Args section with no content: returns empty_section error. |

### blank_line_before_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_blank_line_before_section_present` | Section header preceded by blank line: no error. |
| `rules/test_rules_structure.py` | `test_blank_line_before_section_missing` | Section header not preceded by blank line: returns blank_line_before_section error. |
| `rules/test_rules_structure.py` | `test_blank_line_before_section_first_line_skipped` | Section header on first line of docstring: rule skips it. |

### blank_line_after_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_blank_line_after_section_present` | Blank line between sections: no error. |
| `rules/test_rules_structure.py` | `test_blank_line_after_section_missing` | Two consecutive sections without blank line between them: returns blank_line_after_section error. |

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

### summary_first_line

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_docstring.py` | `test_summary_first_line_correct` | raw_docstring starts with summary text: no error. |
| `rules/test_rules_docstring.py` | `test_summary_first_line_wrong` | raw_docstring starts with newline: returns summary_first_line error. |

### closing_quotes_blank_line

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_closing_quotes_blank_line_correct` | Exactly one blank line before closing quotes: no error. |
| `rules/test_rules_structure.py` | `test_closing_quotes_blank_line_missing` | No blank line before closing quotes: returns closing_quotes_blank_line error. |
| `rules/test_rules_structure.py` | `test_closing_quotes_two_blank_lines` | Two blank lines before closing quotes: returns closing_quotes_blank_line error. |
| `rules/test_rules_structure.py` | `test_closing_quotes_one_liner_skipped` | One-liner docstring: closing_quotes_blank_line rule not applied. |
| `rules/test_rules_structure.py` | `test_closing_quotes_module_skipped` | Module entity: closing_quotes_blank_line rule not applied. |

### no_blank_line_in_section

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_structure.py` | `test_no_blank_line_in_args_section` | Blank line between two Args entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_raises_section` | Blank line between two Raises entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_attributes_section` | Blank line between two Attributes entries: returns no_blank_line_in_section error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_section_correct` | No blank lines between Args entries: no error. |
| `rules/test_rules_structure.py` | `test_no_blank_line_in_example_ignored` | Blank line inside Example section: not flagged (rule only applies to Args/Attributes/Raises). |

### validate_entity

| Fichier | Fonction | Description |
|---|---|---|
| `rules/test_rules_validate.py` | `test_empty_init_excluded_when_configured` | Empty __init__ with exclude_empty_init=True: no errors even with missing docstring. |
| `rules/test_rules_validate.py` | `test_empty_init_not_excluded_when_flag_false` | Empty __init__ with exclude_empty_init=False: docstring_exists is still checked. |
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
| `test_cli.py` | `test_list_rules_output` | --list-rules: all rules appear in output grouped by category. |

---

## test_reporter.py -- reporter

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
| `test_reporter.py` | `test_report_rules_all_categories_present` | All category names appear in output. |
| `test_reporter.py` | `test_report_rules_all_rules_present` | All rule identifiers appear in output. |
| `test_reporter.py` | `test_report_rules_enabled_rule_shows_checkmark` | Enabled rule shows checkmark marker. |
| `test_reporter.py` | `test_report_rules_disabled_rule_shows_cross` | Disabled rule shows cross marker. |
| `test_reporter.py` | `test_report_rules_off_by_default_label` | Rule in off_by_default shows '(disabled by default)' label. |

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
| `test_config.py` | `test_parse_exclude_empty_init_false` | exclude_empty_init = false: config.exclude_empty_init is False. |
| `test_config.py` | `test_parse_workers` | Workers = 4: config.workers is 4. |
| `test_config.py` | `test_parse_workers_zero_allowed` | Workers = 0: config.workers is 0 (auto-detect at runtime). |
| `test_config.py` | `test_parse_scope_modules_false` | scope.modules = false: config.check_modules is False. |
| `test_config.py` | `test_parse_scope_all_false` | All scope flags set to false: all check_* fields are False. |
| `test_config.py` | `test_parse_exclude_patterns` | Exclude = ['test_*']: config.exclude_patterns is set. |
| `test_config.py` | `test_parse_ignore_placeholder_docstrings` | ignore_placeholder_docstrings = true: config flag is True. |
| `test_config.py` | `test_parse_summary_max_length` | summary_max_length = 72: config.summary_max_length is 72. |
| `test_config.py` | `test_parse_summary_max_length_minimum_one` | summary_max_length = 0: clamped to 1. |

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
