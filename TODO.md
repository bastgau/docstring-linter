# TODO

Priorities range from 1 (low) to 10 (high).

## New rules

- [x] `args_order` -- check that the order of the entries in `Args:` matches the signature -- **7**
- [x] `unknown_section` -- report an unrecognized section (e.g. `Argument:` instead of `Args:`) -- **7**
- [x] `duplicate_arg` -- detect an argument documented twice in `Args:` -- **6**
- [x] `multiline_summary` -- forbid a summary spread over several lines -- **5**
  Covered by the parser, which cuts the summary at the first line, and by `blank_lines`, which requires the blank line before the description.
- [x] `raises_description` -- require a description in every `Raises:` entry -- **4**
  Covered by `raises_match`.
- [x] `entry_spacing` -- enforce the `name (type): description` form in `Args:`, `Attributes:` and `Raises:` -- **6**
- [x] `return_description` -- require a description in `Returns:`, not only a type -- **4**
  Covered by `returns_descriptions`, which governs `Returns:` and `Yields:`. The description of `Args:`, `Attributes:` and `Raises:` entries stays mandatory. `Returns: None` is exempt.
- [ ] `description_too_long` -- limit the length of description lines (configurable, like `summary_too_long`) -- **5**
- [ ] `no_trailing_whitespace` -- forbid trailing spaces in the docstring -- **4**

## CLI / config

- [x] `traceback` output format -- clickable `File "path", line N, in entity` header -- **7**
- [x] Reject unknown configuration keys -- **9**
  Unknown key at the top level, in `[scope]` or in an override, unknown rule name in `select` / `ignore`, always-on rule in `ignore`, invalid `style` or policy value: error on stderr and exit code 2 before any file is read.
- [x] Per-directory configuration -- `[[tool.docstring-linter.overrides]]` with `paths` -- **7**
  `full_match` globs, last matching block wins, `ignore` removes and `select` replaces, `scope.*` and run-level settings rejected in an override.
- [ ] `--quiet` -- print only the errors, without the summary and the config line -- **5**
- [ ] `--watch` -- rerun automatically on modified files -- **3**

## Parser

- [ ] `Raises:` entry reduced to a bare identifier, without a colon -- **3**
  `RuntimeError` alone is not recognized as an entry and is reported as undocumented. Accepting it would turn any one-word continuation line into an exception.
- [ ] `no_blank_line_in_section` works line by line -- **3**
  The rule does not tell the start of an entry from a continuation line, which prevents turning it into a configurable count like `blank_lines`.

## Documentation

- [x] Keep `TESTS.md` in sync with the test suite -- **6**
  Still written by hand, one row per test function; `tests/linter/test_registries.py` fails when a test function has no row or a row has no test.
- [ ] Align the version -- **5**
  `pyproject.toml` declares `0.1.0` while the tags go up to `v0.9.0`: the version is only set from the tag at build time. To be handled with the version management in CI/CD (review point OPS-04).

## Integration

- [ ] SARIF output -- standard format for GitHub pull request annotations -- **6**
- [x] Ready-to-use pre-commit hook -- `.pre-commit-hooks.yaml`, tested through `.pre-commit-config-hook.yaml` in CI -- **8**
- [ ] VS Code plugin -- show the errors inline in the editor -- **7**
- [x] GitHub Action -- ready-to-use action for CI workflows -- `action.yml` + `.github/workflows/` -- **8**
- [ ] Docstring coverage badge -- percentage of correctly documented functions -- **5**
