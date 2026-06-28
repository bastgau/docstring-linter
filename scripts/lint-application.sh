#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ALL_FILES_FLAG=""
if [[ "${1:-}" == "--all-files" ]]; then
  ALL_FILES_FLAG="--all-files"
fi

_exit=0
bash "$SCRIPT_DIR/lint-common.sh" \
  --path "$PYTHONPATH" \
  --tools "ruff,ruff-format,pylint,pyright,docstring-linter" \
  ${ALL_FILES_FLAG:+"$ALL_FILES_FLAG"} || _exit=$?

if [[ $_exit -ne 0 ]]; then
  printf '\nPress any key to continue...'
  read -r -n1 -s
  printf '\n'
fi

printf '\n%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n' $'\033[0;90m' $'\033[0m'

bash "$SCRIPT_DIR/lint-common.sh" \
  --path "$ROOT_WORKSPACE_DIRECTORY" \
  --tools "shellcheck" \
  ${ALL_FILES_FLAG:+"$ALL_FILES_FLAG"}

printf '\n'
