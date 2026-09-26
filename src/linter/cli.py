"""CLI entry point for the docstring linter.

Provide command-line interface with argparse, supporting file and
directory scanning, config loading, and output options.
"""

import argparse
import itertools
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from linter.ast_parser import parse_file
from linter.config import ALWAYS_ON, OFF_BY_DEFAULT, OPTIONS_REGISTRY, POLICIES_REGISTRY, RULES_CATEGORIES, RULES_REGISTRY, DocstringStyle, LinterConfig, load_config, path_matches
from linter.docstring_parser import get_parser
from linter.models import LintError, NodeType
from linter.reporter import report_cli, report_github_annotations, report_json, report_options, report_overrides, report_policies, report_rules, report_statistics, report_traceback
from linter.rules import validate_entity


def collect_python_files(paths: list[str], exclude_patterns: list[str], base_dir: Path) -> list[str]:
    """Collect all .py files from given paths, respecting exclusions.

    Args:
        paths (list[str]): File or directory paths to scan.
        exclude_patterns (list[str]): Glob patterns to exclude.
        base_dir (Path): Absolute directory the patterns are relative to.

    Returns:
        list[str]: Sorted list of Python file paths.

    """
    files: list[str] = []

    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == ".py":
            if not _is_excluded(path, exclude_patterns, base_dir):
                files.append(str(path))
        elif path.is_dir():
            files.extend(sorted(str(py_file) for py_file in path.rglob("*.py") if not _is_excluded(py_file, exclude_patterns, base_dir)))

    return files


def _is_excluded(path: Path, patterns: list[str], base_dir: Path) -> bool:
    """Check if a file path matches any exclusion pattern.

    A pattern matches the end of the path (test_*.py), the whole path
    relative to the base directory (tests/**), or, when it carries no
    wildcard, any directory or file name along the path (.venv).

    Args:
        path (Path): File path to check.
        patterns (list[str]): Glob patterns to match against.
        base_dir (Path): Absolute directory the whole-path patterns are relative to.

    Returns:
        bool: True if the path matches any exclusion pattern.

    """
    for pattern in patterns:
        if path.match(pattern):
            return True
        # literal patterns (no glob chars) are also matched against directory parts
        if "*" not in pattern and "?" not in pattern and pattern in path.parts:
            return True
    return path_matches(str(path), patterns, base_dir)


def lint_file(filepath: str, config: LinterConfig) -> list[LintError]:
    """Lint a single Python file and return errors.

    Args:
        filepath (str): Path to the Python file to lint.
        config (LinterConfig): Linter configuration, before per-path overrides.

    Returns:
        list[LintError]: List of lint errors found.

    """
    config = config.for_path(filepath)
    parser = get_parser(config.style)
    entities = parse_file(filepath)
    errors: list[LintError] = []

    for entity in entities:
        if entity.node_type == NodeType.MODULE and not config.check_modules:
            continue
        if entity.node_type == NodeType.CLASS and not config.check_classes:
            continue
        if entity.node_type == NodeType.FUNCTION and not config.check_functions:
            continue
        if entity.node_type == NodeType.METHOD and not config.check_methods:
            continue

        parsed_doc = None
        if entity.docstring:
            parsed_doc = parser.parse(entity.docstring)

        entity_errors = validate_entity(entity, parsed_doc, config)
        errors.extend(entity_errors)

    return errors


def merge_cli_into_config(config: LinterConfig, args: argparse.Namespace) -> LinterConfig:
    """Override TOML config with explicit CLI arguments.

    Args:
        config (LinterConfig): Base config loaded from TOML.
        args (argparse.Namespace): Parsed CLI arguments.

    Returns:
        LinterConfig: Updated configuration object.

    """
    if args.style:
        config.style = DocstringStyle(args.style)

    if args.exclude is not None:
        config.exclude_patterns = args.exclude

    if args.format is not None:
        config.output_format = args.format

    if args.workers is not None:
        config.workers = max(0, args.workers)

    return config


def _lint_file_safe(filepath: str, config: LinterConfig) -> tuple[list[LintError], str | None]:
    """Lint a file, turning an unreadable or unparsable file into a failure message.

    Args:
        filepath (str): Path to the Python file.
        config (LinterConfig): Linter configuration.

    Returns:
        tuple[list[LintError], str | None]: Errors, and the failure message if the file could not be analysed.

    """
    try:
        return lint_file(filepath, config), None
    except SyntaxError as e:
        return [], f"Syntax error in {filepath}: {e}"
    except (UnicodeDecodeError, OSError) as e:
        return [], f"Cannot read {filepath}: {e}"


def _resolve_workers(workers: int) -> int:
    """Resolve worker count (0 = auto-detect CPU count).

    Args:
        workers (int): Configured worker count.

    Returns:
        int: Resolved worker count.

    """
    if workers == 0:
        return os.cpu_count() or 1
    return workers


def _report(errors: list[LintError], files_checked: int, output_format: str, *, statistics: bool) -> None:
    """Print the lint results in the requested format.

    Args:
        errors (list[LintError]): Lint errors found.
        files_checked (int): Total number of files checked.
        output_format (str): Output format name.
        statistics (bool): Report the number of errors per rule instead of each error.

    Returns:
        None

    """
    if statistics:
        report_statistics(errors, files_checked)
    elif output_format == "json":
        report_json(errors, files_checked)
    elif output_format == "github-annotations":
        report_github_annotations(errors, files_checked)
    elif output_format == "text":
        report_cli(errors, files_checked)
    else:
        report_traceback(errors, files_checked)


def run(paths: list[str], config: LinterConfig, *, statistics: bool = False) -> int:
    """Collect files, lint them, and report results.

    Args:
        paths (list[str]): File or directory paths to lint.
        config (LinterConfig): Linter configuration.
        statistics (bool): Report the number of errors per rule instead of each error.

    Returns:
        int: Exit code -- 0 if no errors, 1 on lint errors, 2 if a path is missing or a file could not be analysed.

    """
    missing = [path for path in paths if not Path(path).exists()]
    if missing:
        for path in missing:
            print(f"Path not found: {path}", file=sys.stderr)
        return 2

    files = collect_python_files(paths, config.exclude_patterns, config.base_dir)
    if not files:
        print("No Python files found.")
        return 0

    workers = _resolve_workers(config.workers)

    if workers <= 1 or len(files) == 1:
        results = [_lint_file_safe(filepath, config) for filepath in files]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_lint_file_safe, files, itertools.repeat(config)))

    failures = [message for _, message in results if message]
    for message in failures:
        print(message, file=sys.stderr)

    all_errors = [error for errors, _ in results for error in errors]

    _report(all_errors, len(files), config.output_format, statistics=statistics)

    if failures:
        return 2
    return 1 if all_errors else 0


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser.

    """
    parser = argparse.ArgumentParser(
        prog="docstring-linter",
        description="Validate Python docstrings against style conventions.",
    )
    parser.add_argument("paths", nargs="*", help="Files or directories to lint.")
    parser.add_argument("--list-rules", action="store_true", help="List all available rules and exit.")
    parser.add_argument("--config", default=None, help="Path to pyproject.toml (default: auto-detect).")
    parser.add_argument("--style", choices=[s.value for s in DocstringStyle], default=None, help=argparse.SUPPRESS)
    parser.add_argument("--format", choices=["traceback", "text", "json", "github-annotations"], default=None, help="Output format (default: traceback).")
    parser.add_argument("--exclude", nargs="*", default=None, help="Glob patterns to exclude (overrides pyproject.toml).")
    parser.add_argument("--statistics", action="store_true", help="Report the number of errors per rule instead of each error (traceback and text formats).")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel workers (0 = auto, 1 = sequential). Overrides pyproject.toml.")
    return parser


def _main() -> int:
    """Parse CLI arguments, load config, and delegate to run().

    Returns:
        int: Exit code.

    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    try:
        config, config_file = load_config(args.config)
        config = merge_cli_into_config(config, args)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    if args.list_rules:
        report_rules(RULES_CATEGORIES, RULES_REGISTRY, OFF_BY_DEFAULT, ALWAYS_ON, frozenset(config.enabled_rules))
        report_policies(POLICIES_REGISTRY, config.policy_values())
        report_options(OPTIONS_REGISTRY, config.option_values())
        report_overrides(config.overrides, config.policy_values() | config.option_values())
        return 0

    if not args.paths:
        parser.error("the following arguments are required: paths")

    if args.statistics and config.output_format not in ("text", "traceback"):
        print(f"--statistics is not available with the {config.output_format} format.", file=sys.stderr)
        return 2

    if config.output_format in ("text", "traceback"):
        if config_file is not None:
            print(f"Config: {config_file}")
        else:
            print("Config: defaults (no config file found)")

    return run(args.paths, config, statistics=args.statistics)


def main() -> None:
    """Run the CLI and exit with its code, quietly if the output pipe closes early.

    Returns:
        None

    """
    try:
        code = _main()
        # flush here so that a closed pipe raises inside the try block
        sys.stdout.flush()
    except BrokenPipeError:
        # Python flushes stdout again at exit: point it to devnull to avoid a second error
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    sys.exit(code)


if __name__ == "__main__":
    main()
