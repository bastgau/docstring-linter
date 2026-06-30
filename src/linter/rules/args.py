"""Rules related to function arguments, return types, and raises."""

from typing import TYPE_CHECKING

from ._base import make_error

if TYPE_CHECKING:
    from linter.config import LinterConfig
    from linter.models import CodeEntity, LintError, ParsedDocstring


def check_return_type_annotation(entity: CodeEntity) -> list[LintError]:
    """Check that function or method has -> type annotation.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        list[LintError]: Errors if return type annotation is missing.

    """
    if entity.return_type is None:
        return [make_error(entity, "return_type_annotation", "Missing return type annotation (-> type) in signature.")]
    return []


def check_args_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check bijection between signature args and docstring Args section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors for mismatched, missing, or extra args.

    """
    errors: list[LintError] = []
    if not entity.args:
        if parsed_doc and parsed_doc.args:
            errors.extend(make_error(entity, "args_match", f"Arg '{doc_arg.name}' documented but not in signature.") for doc_arg in parsed_doc.args)
        return errors

    if parsed_doc is None or not parsed_doc.args:
        errors.extend(make_error(entity, "args_match", f"Arg '{arg.name}' in signature but not documented.") for arg in entity.args)
        return errors

    sig_args = {a.name: a for a in entity.args}
    doc_args = {a.name: a for a in parsed_doc.args}

    for name, sig_arg in sig_args.items():
        if name not in doc_args:
            errors.append(make_error(entity, "args_match", f"Arg '{name}' in signature but not documented."))
            continue

        doc_arg = doc_args[name]

        if doc_arg.type_annotation is None:
            errors.append(make_error(entity, "args_match", f"Arg '{name}' missing type. Expected '({sig_arg.type_annotation})'."))

        if doc_arg.type_annotation and sig_arg.type_annotation and doc_arg.type_annotation != sig_arg.type_annotation:
            errors.append(make_error(entity, "args_match", f"Arg '{name}' type mismatch: signature='{sig_arg.type_annotation}', docstring='{doc_arg.type_annotation}'."))

        if not doc_arg.description:
            errors.append(make_error(entity, "args_match", f"Arg '{name}' missing description."))

    errors.extend(make_error(entity, "args_match", f"Arg '{name}' documented but not in signature.") for name in doc_args if name not in sig_args)

    return errors


def check_returns_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, config: LinterConfig) -> list[LintError]:  # noqa: C901
    """Check that Returns section exists and has correct type.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        config (LinterConfig): Linter configuration.

    Returns:
        list[LintError]: Errors if Returns section is missing or wrong.

    """
    errors: list[LintError] = []

    if parsed_doc is None:
        return errors

    if entity.is_generator:
        if parsed_doc.returns is not None:
            errors.append(make_error(entity, "returns_section", "Generator function must use 'Yields:' instead of 'Returns:'."))
        return errors

    if entity.return_type == "None":
        is_init = entity.name.endswith(".__init__") or entity.name == "__init__"
        is_one_liner = entity.docstring is not None and "\n" not in entity.docstring

        if is_init and config.is_rule_enabled("without_returns_none_init"):
            if parsed_doc.returns is not None:
                errors.append(make_error(entity, "without_returns_none_init", "'Returns: None' is not allowed on __init__ methods."))
            return errors

        if is_one_liner and config.is_rule_enabled("allow_oneliner"):
            return errors

    if entity.return_type and parsed_doc.returns is None:
        errors.append(make_error(entity, "returns_section", f"Missing 'Returns:' section. Signature declares -> {entity.return_type}."))
        return errors

    if entity.return_type and parsed_doc.returns and parsed_doc.returns.type_annotation and parsed_doc.returns.type_annotation != entity.return_type:
        errors.append(make_error(entity, "returns_section", f"Return type mismatch: signature='{entity.return_type}', docstring='{parsed_doc.returns.type_annotation}'."))

    if entity.return_type and parsed_doc.returns and not parsed_doc.returns.type_annotation:
        errors.append(make_error(entity, "returns_section", f"Missing type in 'Returns:'. Expected '{entity.return_type}'."))

    return errors


def check_yields_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that Yields section exists for generator functions.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if Yields section is missing or incomplete.

    """
    errors: list[LintError] = []

    if parsed_doc is None or not entity.is_generator:
        return errors

    if parsed_doc.yields is None:
        errors.append(make_error(entity, "yields_section", "Missing 'Yields:' section. Function contains a yield statement."))
        return errors

    if not parsed_doc.yields.type_annotation:
        errors.append(make_error(entity, "yields_section", "Missing type in 'Yields:'."))

    return errors


def check_param_order(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that Args section order matches the signature order.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if documented args are in a different order.

    """
    if parsed_doc is None or not parsed_doc.args or not entity.args:
        return []

    sig_names = [a.name for a in entity.args]
    doc_names = [a.name for a in parsed_doc.args if a.name in sig_names]

    if doc_names != sig_names[: len(doc_names)]:
        expected = ", ".join(sig_names)
        got = ", ".join(doc_names)
        return [make_error(entity, "param_order", f"Args order in docstring differs from signature. Expected: {expected}. Got: {got}.")]
    return []


def check_duplicate_arg(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check for duplicate argument entries in the Args section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors for each argument documented more than once.

    """
    if parsed_doc is None:
        return []

    seen: set[str] = set()
    errors: list[LintError] = []
    for arg in parsed_doc.args:
        if arg.name in seen:
            errors.append(make_error(entity, "duplicate_arg", f"Arg '{arg.name}' documented more than once in 'Args:'."))
        seen.add(arg.name)
    return errors


def check_raises_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check bijection between raise statements and Raises section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors for undocumented or phantom raises.

    """
    errors: list[LintError] = []

    code_raises = {r.exception_type for r in entity.raises}
    doc_raises: set[str] = {r.exception_type for r in parsed_doc.raises} if parsed_doc else set()

    errors.extend(make_error(entity, "raises_match", f"'{exc}' raised in code but not documented in 'Raises:'.") for exc in sorted(code_raises - doc_raises))
    errors.extend(make_error(entity, "raises_match", f"'{exc}' documented in 'Raises:' but not raised in code.") for exc in sorted(doc_raises - code_raises))

    return errors
