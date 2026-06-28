"""CLI entry point for the docstring linter.

Provide command-line interface with argparse, supporting file and
directory scanning, config loading, and output options.
"""

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from linter.ast_parser import parse_file
from linter.config import OFF_BY_DEFAULT, RULES_CATEGORIES, RULES_REGISTRY, DocstringStyle, LinterConfig, load_config
from linter.docstring_parser import get_parser
from linter.models import LintError, NodeType
from linter.reporter import report_cli, report_github_annotations, report_json, report_rules
from linter.rules import validate_entity


def collect_python_files(paths: list[str], exclude_patterns: list[str]) -> list[str]:
    """Collect all .py files from given paths, respecting exclusions.

    Args:
        paths (list[str]): File or directory paths to scan.
        exclude_patterns (list[str]): Glob patterns to exclude.

    Returns:
        list[str]: Sorted list of Python file paths.

    """
    files: list[str] = []

    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == ".py":
            if not _is_excluded(path, exclude_patterns):
                files.append(str(path))
        elif path.is_dir():
            files.extend(sorted(str(py_file) for py_file in path.rglob("*.py") if not _is_excluded(py_file, exclude_patterns)))

    return files


def _is_excluded(path: Path, patterns: list[str]) -> bool:
    """Check if a file path matches any exclusion pattern.

    Args:
        path (Path): File path to check.
        patterns (list[str]): Glob patterns to match against.

    Returns:
        bool: True if the path matches any exclusion pattern.

    """
    for pattern in patterns:
        if path.match(pattern):
            return True
        # literal patterns (no glob chars) are also matched against directory parts
        if "*" not in pattern and "?" not in pattern and pattern in path.parts:
            return True
    return False


def lint_file(filepath: str, config: LinterConfig) -> list[LintError]:
    """Lint a single Python file and return errors.

    Args:
        filepath (str): Path to the Python file to lint.
        config (LinterConfig): Linter configuration.

    Returns:
        list[LintError]: List of lint errors found.

    """
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


def _lint_file_safe(filepath: str, config: LinterConfig) -> tuple[str, list[LintError], str | None]:
    """Lint a file and catch errors for safe parallel execution.

    Args:
        filepath (str): Path to the Python file.
        config (LinterConfig): Linter configuration.

    Returns:
        tuple[str, list[LintError], str | None]: Filepath, errors, and optional error message.

    """
    try:
        return filepath, lint_file(filepath, config), None
    except SyntaxError as e:
        return filepath, [], f"Syntax error in {filepath}: {e}"
    except ValueError as e:
        return filepath, [], f"Configuration error for {filepath}: {e}"


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


def run(paths: list[str], config: LinterConfig) -> int:
    """Collect files, lint them, and report results.

    Args:
        paths (list[str]): File or directory paths to lint.
        config (LinterConfig): Linter configuration.

    Returns:
        int: Exit code -- 0 if no errors, 1 otherwise.

    """
    files = collect_python_files(paths, config.exclude_patterns)
    if not files:
        print("No Python files found.")
        return 0

    all_errors: list[LintError] = []
    workers = _resolve_workers(config.workers)

    if workers <= 1 or len(files) == 1:
        for filepath in files:
            _, errors, err_msg = _lint_file_safe(filepath, config)
            if err_msg:
                print(err_msg)
            all_errors.extend(errors)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_lint_file_safe, fp, config): fp for fp in files}
            for future in as_completed(futures):
                _, errors, err_msg = future.result()
                if err_msg:
                    print(err_msg)
                all_errors.extend(errors)

    if config.output_format == "json":
        report_json(all_errors, len(files))
    elif config.output_format == "github-annotations":
        report_github_annotations(all_errors, len(files))
    else:
        report_cli(all_errors, len(files))

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
    parser.add_argument("--format", choices=["text", "json", "github-annotations"], default=None, help="Output format (default: text).")
    parser.add_argument("--exclude", nargs="*", default=None, help="Glob patterns to exclude (overrides pyproject.toml).")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel workers (0 = auto, 1 = sequential). Overrides pyproject.toml.")
    return parser


def main() -> None:
    """Parse CLI arguments, load config, and delegate to run()."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    config, config_file = load_config(args.config)
    config = merge_cli_into_config(config, args)

    if args.list_rules:
        report_rules(RULES_CATEGORIES, RULES_REGISTRY, OFF_BY_DEFAULT, frozenset(config.enabled_rules))
        sys.exit(0)

    if not args.paths:
        parser.error("the following arguments are required: paths")

    if config.output_format == "text":
        if config_file is not None:
            print(f"Config: {config_file}")
        else:
            print("Config: defaults (no config file found)")
        print()

    sys.exit(run(args.paths, config))


if __name__ == "__main__":
    main()
