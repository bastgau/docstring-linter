#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ERRORS=0
TARGETS=()
TOOLS=""
ALL_FILES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)      TARGETS+=("$2"); shift 2 ;;
    --tools)     TOOLS="$2";      shift 2 ;;
    --all-files) ALL_FILES=true;  shift   ;;
    *)        printf '%sUnknown argument: %s%s\n' "${RED}" "$1" "${NC}"; exit 1 ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  printf '%s--path is required%s\n' "${RED}" "${NC}"
  printf '%sUsage: %s --path PATH [--path PATH2 ...] [--tools TOOL1,TOOL2,...] [--all-files]%s\n\n' "${GRAY}" "$(basename "$0")" "${NC}"
  exit 1
fi

print_header() {
  printf '\n'
  printf '%sTarget     : %s%s\n' "${YELLOW}" "${TARGETS[*]}" "${NC}"
  if [[ -n "$TOOLS" ]]; then
    printf '%sTools      : %s%s\n' "${YELLOW}" "${TOOLS//,/, }" "${NC}"
  fi
  if [[ "$ALL_FILES" == "true" ]]; then
    printf '%sScope      : all files%s\n' "${YELLOW}" "${NC}"
  else
    local _has_py_tool=false
    local _has_sh_tool=false
    local tool
    IFS=',' read -ra _tool_list <<< "$TOOLS"
    for tool in "${_tool_list[@]}"; do
      case "$tool" in
        shellcheck) _has_sh_tool=true ;;
        *) _has_py_tool=true ;;
      esac
    done

    local _display_files=()
    [[ "$_has_py_tool" == "true" ]] && _display_files+=("${_changed_files[@]}")
    [[ "$_has_sh_tool" == "true" ]] && _display_files+=("${_changed_sh_files[@]}")

    local total="${#_display_files[@]}"
    printf '%sScope      : git changed files (%s file%s)%s\n' "${YELLOW}" "$total" "$([[ $total -eq 1 ]] && printf '' || printf 's')" "${NC}"
    if [[ $total -gt 0 ]]; then
      printf '\n'
      for f in "${_display_files[@]}"; do
        printf '%s  %s%s\n' "${GRAY}" "$f" "${NC}"
      done
    fi
  fi
}

print_rule() {
  local label="$1"
  local width=44
  local label_len=$(( ${#label} + 4 ))
  local dashes=$(( width - label_len ))
  printf '\n%s── %s%s %s' "${BLUE}" "${NC}" "$label" "${BLUE}"
  printf '%0.s─' $(seq 1 "$dashes")
  printf '%s\n' "${NC}"
}

run_check() {
  local tool="$1"
  local label_cmd="$2"
  shift 2
  print_rule "$tool"
  printf '\n'
  printf '%sCommand : $ %s%s\n' "${GRAY}" "$label_cmd" "${NC}"
  case "$tool" in
    vulture|pytest|coverage)
      if [[ "$ALL_FILES" != "true" ]]; then
        printf '\n'
        printf '%sThis tool always runs on the full project, not just changed files.%s\n' "${RED}" "${NC}"
      fi
      ;;
  esac
  printf '\n'
  local output
  local exit_code=0
  output=$("$@" 2>&1) || exit_code=$?
  local filtered
  filtered=$(printf '%s\n' "$output" | grep -Ev '^-{10,}|has been rated' || true)
  local trimmed
  trimmed=$(printf '%s\n' "$filtered" | grep -v '^$' || true)
  if [[ -z "$trimmed" ]]; then
    printf 'All checks passed!\n'
  else
    printf '%s\n' "$filtered"
  fi
  printf '\n'
  if [[ $exit_code -ne 0 ]]; then
    failure "$tool reported issues"
    ERRORS=$((ERRORS + 1))
  else
    success "$tool passed"
  fi
}

_no_files_skip() {
  local tool="$1"
  print_rule "$tool"
  printf '\nNo changed files to check.\n\n'
  success "$tool passed"
}

_py_targets() {
  if [[ "$ALL_FILES" == "true" ]]; then
    printf '%s\n' "${TARGETS[@]}"
  elif [[ ${#_changed_files[@]} -gt 0 ]]; then
    printf '%s\n' "${_changed_files[@]}"
  fi
}

_sh_targets() {
  if [[ "$ALL_FILES" == "true" ]]; then
    find "${TARGETS[@]}" -name "*.sh" -type f | sort
  elif [[ ${#_changed_sh_files[@]} -gt 0 ]]; then
    printf '%s\n' "${_changed_sh_files[@]}"
  fi
}

run_tool() {
  local py_files=()
  local sh_files=()

  case "$1" in
    ruff|ruff-format|pylint|pyright|docstring-linter)
      mapfile -t py_files < <(_py_targets)
      if [[ "$ALL_FILES" != "true" && ${#py_files[@]} -eq 0 ]]; then
        case "$1" in
          ruff)             _no_files_skip "ruff (lint)" ;;
          ruff-format)      _no_files_skip "ruff (format)" ;;
          *)                _no_files_skip "$1" ;;
        esac
        return
      fi
      local scope
      scope="$([[ "$ALL_FILES" == "true" ]] && printf '<directory>' || printf '<files>')"
      case "$1" in
        ruff)             run_check "ruff (lint)"      "uv run ruff check $scope"      uv run ruff check "${py_files[@]}" ;;
        ruff-format)      run_check "ruff (format)"    "uv run ruff format $scope"     uv run ruff format "${py_files[@]}" ;;
        pylint)           run_check "pylint"            "uv run pylint $scope"          uv run pylint "${py_files[@]}" ;;
        pyright)          run_check "pyright"           "uv run pyright $scope"         uv run pyright "${py_files[@]}" ;;
        docstring-linter) run_check "docstring-linter" "uv run docstring-linter $scope" uv run docstring-linter "${py_files[@]}" ;;
      esac
      ;;
    vulture)   run_check "vulture"  "uv run vulture <directory>" uv run vulture "${TARGETS[@]}" "$ROOT_DIR/.vulture" ;;
    pytest)    run_check "pytest"   "uv run pytest"              uv run pytest --no-cov ;;
    coverage)  run_check "coverage" "uv run pytest --cov"        uv run pytest --cov --cov-branch --cov-report=term-missing -q --no-header ;;
    shellcheck)
      mapfile -t sh_files < <(_sh_targets)
      if [[ ${#sh_files[@]} -eq 0 ]]; then
        _no_files_skip "shellcheck"
      else
        local sh_scope
        sh_scope="$([[ "$ALL_FILES" == "true" ]] && printf '<directory>' || printf '<files>')"
        # shellcheck disable=SC2016
        run_check "shellcheck" "uv run shellcheck $sh_scope" bash -c 'out=""; for f in "$@"; do out+="$(shellcheck --severity=info "$f")"; done; [ -z "$out" ] || { printf "%s\n" "$out"; exit 1; }' _ "${sh_files[@]}"
      fi
      ;;
    *)
      printf '\n%sUnknown tool: %s%s\n' "${RED}" "$1" "${NC}"
      printf '\n%sAvailable: ruff, ruff-format, pylint, pyright, docstring-linter, vulture, pytest, coverage, shellcheck%s\n\n' "${GRAY}" "${NC}"
      exit 1
      ;;
  esac
}

cd "$ROOT_DIR"

uv sync -q

_changed_files=()
_changed_sh_files=()
if [[ "$ALL_FILES" != "true" ]]; then
  mapfile -t _git_changed < <(git diff --name-only --diff-filter=ACMR HEAD 2>/dev/null | sort)
  for f in "${_git_changed[@]}"; do
    abs="$ROOT_DIR/$f"
    [[ -f "$abs" ]] || continue
    for t in "${TARGETS[@]}"; do
      case "$abs" in
        "$t"*)
          [[ "$abs" == *.py ]] && _changed_files+=("$abs")
          [[ "$abs" == *.sh ]] && _changed_sh_files+=("$abs")
          break
          ;;
      esac
    done
  done
fi

print_header

if [[ -z "$TOOLS" ]]; then
  printf '%s--tools is required%s\n' "${RED}" "${NC}"
  printf '%sAvailable: ruff, ruff-format, pylint, pyright, docstring-linter, vulture, pytest, coverage, shellcheck%s\n\n' "${GRAY}" "${NC}"
  exit 1
fi

IFS=',' read -ra TOOL_LIST <<< "$TOOLS"
for tool in "${TOOL_LIST[@]}"; do
  run_tool "$tool"
done

if [[ $ERRORS -gt 0 ]]; then
  failure "$ERRORS check(s) failed" -a
  printf '\n'
  exit 1
fi
