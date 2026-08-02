"""Reporter for the docstring linter.

Format lint results for CLI output with ANSI colors
and JSON export for CI/CD integration.
"""

import json
from pathlib import Path
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
        BLUE (str): Blue color code.
        WHITE (str): Bright white color code.
        BOLD (str): Bold style code.
        DIM (str): Dim style code.
        RESET (str): Reset all styles code.

    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def report_cli(errors: list[LintError], files_checked: int) -> None:
    """Print lint results to stdout with colors.

    Args:
        errors (list[LintError]): List of lint errors to display.
        files_checked (int): Total number of files checked.

    Returns:
        None

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


def report_traceback(errors: list[LintError], files_checked: int) -> None:
    """Print lint results as clickable traceback-style locations.

    Each entity produces one 'File "path", line N, in name' header followed by
    its errors, the format editors turn into a clickable link.

    Args:
        errors (list[LintError]): List of lint errors to display.
        files_checked (int): Total number of files checked.

    Returns:
        None

    """
    if not errors:
        print(f"{files_checked} files checked, 0 errors.")
        return

    by_entity: dict[tuple[str, int, str], list[LintError]] = {}
    for error in errors:
        by_entity.setdefault((error.filepath, error.line, error.entity_name), []).append(error)

    print()
    for (filepath, line, entity_name), entity_errors in sorted(by_entity.items()):
        location = f'{Colors.BOLD}{Colors.WHITE}File "{Path(filepath).resolve()}", line {line}{Colors.RESET}'
        print(f"{location}, in {Colors.BLUE}{entity_name}{Colors.RESET}")
        for error in entity_errors:
            print(f"    {Colors.RED}[{error.rule}]{Colors.RESET} {error.message}")
        print()

    file_count = len({e.filepath for e in errors})
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
        None

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
        None

    """
    for e in sorted(errors, key=lambda e: (e.filepath, e.line)):
        print(f"::error file={e.filepath},line={e.line},title={e.rule}::{e.message}")

    error_count = len(errors)
    file_count = len({e.filepath for e in errors})
    if error_count == 0:
        print(f"{files_checked} files checked, 0 errors.")
    else:
        print(f"{error_count} error{'s' if error_count > 1 else ''} in {file_count} file{'s' if file_count > 1 else ''} ({files_checked} files checked).")


def report_policies(registry: dict[str, str], values: dict[str, str]) -> None:
    """Print all style policies with their value in the current config.

    Args:
        registry (dict[str, str]): Policy identifier to description.
        values (dict[str, str]): Policy identifier to configured value.

    Returns:
        None

    """
    print(f"  {Colors.BOLD}{Colors.CYAN}Policies{Colors.RESET}  {Colors.DIM}required | forbidden | optional{Colors.RESET}")
    for policy, description in registry.items():
        value = values[policy]
        color = Colors.GREEN if value != "optional" else Colors.YELLOW
        print(f"    {color}{value:<10}{Colors.RESET} {Colors.BOLD}{policy:<35}{Colors.RESET} {Colors.DIM}{description}{Colors.RESET}")
    print()


def report_options(registry: dict[str, str], values: dict[str, str]) -> None:
    """Print the options that change what is checked, with their current value.

    Args:
        registry (dict[str, str]): Option identifier to description.
        values (dict[str, str]): Option identifier to configured value.

    Returns:
        None

    """
    print(f"  {Colors.BOLD}{Colors.CYAN}Options{Colors.RESET}  {Colors.DIM}settings that change what gets checked{Colors.RESET}")
    for option, description in registry.items():
        print(f"    {Colors.GREEN}{values[option]:<10}{Colors.RESET} {Colors.BOLD}{option:<35}{Colors.RESET} {Colors.DIM}{description}{Colors.RESET}")
    print()


def report_rules(categories: dict[str, list[str]], registry: dict[str, str], off_by_default: frozenset[str], always_on: frozenset[str], enabled: frozenset[str]) -> None:
    """Print the configurable rules grouped by category, with their enabled status.

    Rules that cannot be disabled are omitted: nothing can be done about them
    from the configuration file.

    Args:
        categories (dict[str, list[str]]): Category name to rule identifiers.
        registry (dict[str, str]): Rule identifier to description.
        off_by_default (frozenset[str]): Rules disabled by default.
        always_on (frozenset[str]): Rules that cannot be disabled, hidden from the listing.
        enabled (frozenset[str]): Rules enabled in the current config.

    Returns:
        None

    """
    total = len(registry) - len(always_on)
    off = len(off_by_default - always_on)
    print(f"\n{Colors.BOLD}docstring-linter rules{Colors.RESET}  {Colors.DIM}{total} configurable rules ({total - off} enabled by default, {off} disabled by default){Colors.RESET}\n")
    for category, rules in categories.items():
        listed = [rule for rule in rules if rule not in always_on]
        if not listed:
            continue
        print(f"  {Colors.BOLD}{Colors.CYAN}{category}{Colors.RESET}")
        for rule in listed:
            is_enabled = rule in enabled
            status = f"{Colors.GREEN}✔{Colors.RESET}" if is_enabled else f"{Colors.RED}✘{Colors.RESET}"
            opt_in = f"  {Colors.YELLOW}(disabled by default){Colors.RESET}" if rule in off_by_default else ""
            name_style = Colors.BOLD if is_enabled else Colors.DIM
            print(f"    {status} {name_style}{rule:<35}{Colors.RESET} {Colors.DIM}{registry[rule]}{Colors.RESET}{opt_in}")
        print()
