"""Reporter for the docstring linter.

Format lint results for CLI output with ANSI colors
and JSON export for CI/CD integration.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.models import LintError


class Colors:
    """Define ANSI color codes for terminal output.

    Attributes:
        RED (str): Red color code.
        YELLOW (str): Yellow color code.
        GREEN (str): Green color code.
        CYAN (str): Cyan color code.
        BOLD (str): Bold style code.
        DIM (str): Dim style code.
        RESET (str): Reset all styles code.

    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def report_cli(errors: list[LintError], files_checked: int) -> None:
    """Print lint results to stdout with colors.

    Args:
        errors (list[LintError]): List of lint errors to display.
        files_checked (int): Total number of files checked.

    Returns:
        None: This function prints to stdout.

    """
    if not errors:
        print(f"{files_checked} files checked, 0 errors.")
        return

    by_file: dict[str, list[LintError]] = {}
    for error in errors:
        by_file.setdefault(error.filepath, []).append(error)

    print()
    for filepath, file_errors in sorted(by_file.items()):
        print(f"{Colors.BOLD}{filepath}{Colors.RESET}")
        for error in sorted(file_errors, key=lambda e: e.line):
            print(f"  {Colors.DIM}L{error.line:<4}{Colors.RESET} {Colors.CYAN}{error.entity_name}{Colors.RESET} {Colors.RED}[{error.rule}]{Colors.RESET} {error.message}")
        print()

    file_count = len(by_file)
    error_count = len(errors)
    print(
        f"{Colors.RED}{Colors.BOLD}✗ {error_count} error{'s' if error_count > 1 else ''}{Colors.RESET} "
        f"{Colors.DIM}in {file_count} file{'s' if file_count > 1 else ''} "
        f"({files_checked} files checked).{Colors.RESET}\n"
    )


def report_json(errors: list[LintError], files_checked: int) -> None:
    """Print lint results as JSON to stdout.

    Args:
        errors (list[LintError]): List of lint errors to serialize.
        files_checked (int): Total number of files checked.

    Returns:
        None: This function prints to stdout.

    """
    report = {
        "summary": {
            "files_checked": files_checked,
            "total_errors": len(errors),
            "files_with_errors": len({e.filepath for e in errors}),
        },
        "errors": [
            {
                "filepath": e.filepath,
                "line": e.line,
                "entity_name": e.entity_name,
                "node_type": e.node_type.value,
                "rule": e.rule,
                "message": e.message,
            }
            for e in sorted(errors, key=lambda e: (e.filepath, e.line))
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


def report_github_annotations(errors: list[LintError], files_checked: int) -> None:
    """Print lint results as GitHub Actions annotations to stdout.

    Args:
        errors (list[LintError]): List of lint errors to format.
        files_checked (int): Total number of files checked.

    Returns:
        None: This function prints to stdout.

    """
    for e in sorted(errors, key=lambda e: (e.filepath, e.line)):
        print(f"::error file={e.filepath},line={e.line},title={e.rule}::{e.message}")

    error_count = len(errors)
    file_count = len({e.filepath for e in errors})
    if error_count == 0:
        print(f"{files_checked} files checked, 0 errors.")
    else:
        print(f"{error_count} error{'s' if error_count > 1 else ''} in {file_count} file{'s' if file_count > 1 else ''} ({files_checked} files checked).")


def report_rules(categories: dict[str, list[str]], registry: dict[str, str], off_by_default: frozenset[str], enabled: frozenset[str]) -> None:
    """Print all rules grouped by category with colors and current enabled status.

    Args:
        categories (dict[str, list[str]]): Category name to rule identifiers.
        registry (dict[str, str]): Rule identifier to description.
        off_by_default (frozenset[str]): Rules disabled by default.
        enabled (frozenset[str]): Rules enabled in the current config.

    Returns:
        None: This function prints to stdout.

    """
    total = len(registry)
    off = len(off_by_default)
    print(f"\n{Colors.BOLD}docstring-linter rules{Colors.RESET}  {Colors.DIM}{total} rules ({total - off} enabled by default, {off} disabled by default){Colors.RESET}\n")
    for category, rules in categories.items():
        print(f"  {Colors.BOLD}{Colors.CYAN}{category}{Colors.RESET}")
        for rule in rules:
            description = registry[rule]
            is_enabled = rule in enabled
            status = f"{Colors.GREEN}✔{Colors.RESET}" if is_enabled else f"{Colors.RED}✘{Colors.RESET}"
            opt_in = f"  {Colors.YELLOW}(disabled by default){Colors.RESET}" if rule in off_by_default else ""
            name_style = Colors.BOLD if is_enabled else Colors.DIM
            print(f"    {status} {name_style}{rule:<35}{Colors.RESET} {Colors.DIM}{description}{Colors.RESET}{opt_in}")
        print()
