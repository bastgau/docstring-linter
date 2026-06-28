# scripts/

## install.sh

Installs all project tooling and hooks. Run once after cloning.

```bash
bash scripts/install.sh
```

Steps performed in order:

1. **uv** - installs the package manager via the official installer if not already present, then adds `~/.local/bin` to `PATH` and sources the virtual environment in `~/.bashrc`.
2. **dotenv-linter** - installs the `.env` file linter to `/usr/local/bin` (requires `sudo`).
3. **dev dependencies** - runs `uv sync --group dev` to install all Python dev dependencies.
4. **pre-commit hooks** - runs `uv run prek install` to register the pre-commit hooks defined in `.pre-commit-config.yaml`.

---

## lint-application.sh

Lints the application source code and shell scripts.

```bash
bash scripts/lint-application.sh
```

Runs two passes via `lint-common.sh`:

| Pass | Target | Tools |
|------|--------|-------|
| 1 | `$PYTHONPATH` | `ruff` (lint), `ruff-format` (format), `pylint`, `pyright`, `docstring-linter` |
| 2 | `$PYTHONPATH` + `$PYTESTPATH` | `vulture` |
| 3 | `$ROOT_WORKSPACE_DIRECTORY` | `shellcheck` |

Requires the environment variables `PYTHONPATH`, `PYTESTPATH`, and `ROOT_WORKSPACE_DIRECTORY` to be set.

---

## lint-tests.sh

Lints the test suite and runs tests with coverage.

```bash
bash scripts/lint-tests.sh
```

Runs one pass via `lint-common.sh`:

| Target | Tools |
|--------|-------|
| `$PYTESTPATH` | `ruff` (lint), `ruff-format` (format check), `pylint`, `pytest` (no coverage), `coverage` (with branch coverage report) |

Requires the environment variable `PYTESTPATH` to be set.

---

## lint-common.sh

Internal script called by `lint-application.sh` and `lint-tests.sh`. Not intended to be called directly, but it can be.

```bash
bash scripts/lint-common.sh --path PATH --tools TOOL1,TOOL2,...
```

Available tools: `ruff`, `ruff-format`, `pylint`, `pyright`, `docstring-linter`, `vulture`, `pytest`, `coverage`, `shellcheck`.

Each tool runs via `uv run`. All tools must pass; if any fail the script exits with a non-zero status and reports the number of failed checks.
