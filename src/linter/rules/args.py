"""Rules related to function arguments, return types, and raises."""

from typing import TYPE_CHECKING

from linter.config import Policy

from ._base import make_error

if TYPE_CHECKING:
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


def check_args_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the Args section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None:
        return []

    if policy is Policy.FORBIDDEN:
        if parsed_doc.args:
            return [make_error(entity, "args_section", "'Args:' section is not allowed.")]
        return []

    if policy is Policy.OPTIONAL:
        return []

    documented = {a.name for a in parsed_doc.args}
    return [make_error(entity, "args_section", f"Arg '{arg.name}' in signature but not documented.") for arg in entity.args if arg.name not in documented]


def check_args_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None, types: Policy) -> list[LintError]:
    """Check documented args against the signature.

    Only covers what the docstring declares. Undocumented args are
    reported by the args_section policy.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        types (Policy): Policy for the type between parentheses.

    Returns:
        list[LintError]: Errors for phantom, mistyped, or undescribed args.

    """
    if parsed_doc is None or not parsed_doc.args:
        return []

    errors: list[LintError] = []
    sig_args = {a.name: a for a in entity.args}

    for doc_arg in parsed_doc.args:
        sig_arg = sig_args.get(doc_arg.name)

        if sig_arg is None:
            errors.append(make_error(entity, "args_match", f"Arg '{doc_arg.name}' documented but not in signature."))
            continue

        if types is Policy.REQUIRED and doc_arg.type_annotation is None:
            errors.append(make_error(entity, "args_match", f"Arg '{doc_arg.name}' missing type. Expected '({sig_arg.type_annotation})'."))

        if types is Policy.FORBIDDEN and doc_arg.type_annotation is not None:
            errors.append(make_error(entity, "args_match", f"Arg '{doc_arg.name}' must not declare a type."))

        if doc_arg.type_annotation and sig_arg.type_annotation and doc_arg.type_annotation != sig_arg.type_annotation:
            errors.append(make_error(entity, "args_match", f"Arg '{doc_arg.name}' type mismatch: signature='{sig_arg.type_annotation}', docstring='{doc_arg.type_annotation}'."))

        if not doc_arg.description:
            errors.append(make_error(entity, "args_match", f"Arg '{doc_arg.name}' missing description."))

    return errors


def _is_init(entity: CodeEntity) -> bool:
    """Check whether an entity is an __init__ method.

    Args:
        entity (CodeEntity): Entity to check.

    Returns:
        bool: True if the entity is an __init__ method.

    """
    return entity.name.endswith(".__init__") or entity.name == "__init__"


def _generator_returns_error(entity: CodeEntity, parsed_doc: ParsedDocstring) -> list[LintError]:
    """Reject a Returns section on a generator, whatever the policy.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring): Parsed docstring.

    Returns:
        list[LintError]: Error if the generator documents Returns.

    """
    if parsed_doc.returns is None:
        return []
    return [make_error(entity, "returns_section", "Generator function must use 'Yields:' instead of 'Returns:'.")]


def check_returns_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the Returns section.

    Only covers non-None return types. The -> None cases are owned by
    the returns_none and init_returns_none policies.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None:
        return []

    if entity.is_generator:
        return _generator_returns_error(entity, parsed_doc)

    if not entity.return_type or entity.return_type == "None" or policy is Policy.OPTIONAL:
        return []

    if policy is Policy.REQUIRED and parsed_doc.returns is None:
        return [make_error(entity, "returns_section", f"Missing 'Returns:' section. Signature declares -> {entity.return_type}.")]
    if policy is Policy.FORBIDDEN and parsed_doc.returns is not None:
        return [make_error(entity, "returns_section", "'Returns:' section is not allowed.")]
    return []


def check_returns_none(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the 'Returns: None' policy to -> None functions.

    Does not apply to __init__ methods, handled by check_init_returns_none.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None or entity.return_type != "None" or entity.is_generator or _is_init(entity):
        return []

    if policy is Policy.REQUIRED and parsed_doc.returns is None:
        return [make_error(entity, "returns_none", "Missing 'Returns: None' section. Signature declares -> None.")]
    if policy is Policy.FORBIDDEN and parsed_doc.returns is not None:
        return [make_error(entity, "returns_none", "'Returns: None' is not allowed on a -> None function.")]
    return []


def check_init_returns_none(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the 'Returns: None' policy to __init__ methods.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None or entity.return_type != "None" or entity.is_generator or not _is_init(entity):
        return []

    if policy is Policy.REQUIRED and parsed_doc.returns is None:
        return [make_error(entity, "init_returns_none", "Missing 'Returns: None' section on __init__ method.")]
    if policy is Policy.FORBIDDEN and parsed_doc.returns is not None:
        return [make_error(entity, "init_returns_none", "'Returns: None' is not allowed on __init__ methods.")]
    return []


def check_returns_type_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that an existing Returns section matches the signature type.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if the Returns type is wrong or missing.

    """
    errors: list[LintError] = []

    if parsed_doc is None or parsed_doc.returns is None or not entity.return_type or entity.is_generator:
        return errors

    if parsed_doc.returns.type_annotation and parsed_doc.returns.type_annotation != entity.return_type:
        errors.append(make_error(entity, "returns_type_match", f"Return type mismatch: signature='{entity.return_type}', docstring='{parsed_doc.returns.type_annotation}'."))

    if not parsed_doc.returns.type_annotation:
        errors.append(make_error(entity, "returns_type_match", f"Missing type in 'Returns:'. Expected '{entity.return_type}'."))

    return errors


def check_yields_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the Yields section of generators.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None or not entity.is_generator:
        return []

    if policy is Policy.REQUIRED and parsed_doc.yields is None:
        return [make_error(entity, "yields_section", "Missing 'Yields:' section. Function contains a yield statement.")]
    if policy is Policy.FORBIDDEN and parsed_doc.yields is not None:
        return [make_error(entity, "yields_section", "'Yields:' section is not allowed.")]
    return []


def check_yields_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check that an existing Yields section declares a type and a description.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors if the Yields type or description is missing.

    """
    if parsed_doc is None or parsed_doc.yields is None:
        return []

    errors: list[LintError] = []

    if not parsed_doc.yields.type_annotation:
        errors.append(make_error(entity, "yields_match", "Missing type in 'Yields:'."))

    if not parsed_doc.yields.description:
        errors.append(make_error(entity, "yields_match", "Missing description in 'Yields:'."))

    return errors


def check_args_order(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
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
        return [make_error(entity, "args_order", f"Args order in docstring differs from signature. Expected: {expected}. Got: {got}.")]
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


def check_raises_section(entity: CodeEntity, parsed_doc: ParsedDocstring | None, policy: Policy) -> list[LintError]:
    """Apply the presence policy to the Raises section.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.
        policy (Policy): Policy to apply.

    Returns:
        list[LintError]: Errors if the policy is violated.

    """
    if parsed_doc is None:
        return []

    if policy is Policy.FORBIDDEN:
        if parsed_doc.raises:
            return [make_error(entity, "raises_section", "'Raises:' section is not allowed.")]
        return []

    if policy is Policy.OPTIONAL:
        return []

    documented = {r.exception_type for r in parsed_doc.raises}
    return [make_error(entity, "raises_section", f"'{exc}' raised in code but not documented in 'Raises:'.") for exc in sorted({r.exception_type for r in entity.raises} - documented)]


def check_raises_match(entity: CodeEntity, parsed_doc: ParsedDocstring | None) -> list[LintError]:
    """Check documented exceptions against the raise statements in the code.

    Only covers what the docstring declares. Undocumented raises are
    reported by the raises_section policy.

    Args:
        entity (CodeEntity): Entity to check.
        parsed_doc (ParsedDocstring | None): Parsed docstring.

    Returns:
        list[LintError]: Errors for exceptions never raised or left undescribed.

    """
    if parsed_doc is None or not parsed_doc.raises:
        return []

    code_raises = {r.exception_type for r in entity.raises}
    errors = [make_error(entity, "raises_match", f"'{exc}' documented in 'Raises:' but not raised in code.") for exc in sorted({r.exception_type for r in parsed_doc.raises} - code_raises)]
    errors.extend(make_error(entity, "raises_match", f"'{doc_raise.exception_type}' missing description in 'Raises:'.") for doc_raise in parsed_doc.raises if not doc_raise.description)
    return errors
