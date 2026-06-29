#!/usr/bin/env bash

BLUE=$'\033[34m'
GRAY=$'\033[0;90m'
GREEN=$'\033[32m'
# shellcheck disable=SC2034
MAGENTA=$'\033[0;35m'
# shellcheck disable=SC2034
PURPLE=$'\033[1;35m'
RED=$'\033[31m'
YELLOW=$'\033[33m'
NC=$'\033[0m'

print_section() {
  local message="$1"
  local before="${2:-false}"
  local after="${3:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n'
  fi

  printf '%s> %s%s\n' "${YELLOW}" "$message" "${NC}"

  if [[ "$after" == "true" ]]; then
    printf '\n'
  fi

  return 0
}

print_info() {
  local tag="$1"
  local message="$2"
  local before="${3:-false}"
  local after="${4:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n'
  fi

  printf '%s[%s]%s %s\n' "${BLUE}" "$tag" "${NC}" "$message"

  if [[ "$after" == "true" ]]; then
    printf '\n'
  fi

  return 0
}

print_success() {
  local tag="$1"
  local message="$2"
  local before="${3:-false}"
  local after="${4:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n'
  fi

  printf '%s[%s]%s %s✓ %s%s\n' "${BLUE}" "$tag" "${NC}" "${GREEN}" "$message" "${NC}"

  if [[ "$after" == "true" ]]; then
    printf '\n'
  fi

  return 0
}

print_warning() {
  local tag="$1"
  local message="$2"
  local before="${3:-false}"
  local after="${4:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n'
  fi

  printf '%s[%s]%s %s! %s%s\n' "${BLUE}" "$tag" "${NC}" "${YELLOW}" "$message" "${NC}"

  if [[ "$after" == "true" ]]; then
    printf '\n'
  fi

  return 0
}

print_error() {
  local tag="$1"
  local message="$2"
  local before="${3:-false}"
  local after="${4:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n' >&2
  fi

  printf '%s[%s]%s %s✗ %s%s\n' "${BLUE}" "$tag" "${NC}" "${RED}" "$message" "${NC}" >&2

  if [[ "$after" == "true" ]]; then
    printf '\n' >&2
  fi

  return 0
}

print_detail() {
  local message="$1"
  local before="${2:-false}"
  local after="${3:-false}"

  if [[ "$before" == "true" ]]; then
    printf '\n'
  fi

  printf '%s  -> %s%s\n' "${GRAY}" "$message" "${NC}"

  if [[ "$after" == "true" ]]; then
    printf '\n'
  fi

  return 0
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

print_rule() {
  local label="$1"
  local width=44
  local label_len=$(( ${#label} + 4 ))
  local dashes=$(( width - label_len ))
  printf '\n%s── %s%s %s' "${BLUE}" "${NC}" "$label" "${BLUE}"
  printf '%0.s─' $(seq 1 "$dashes")
  printf '%s\n\n' "${NC}"
}

# ── Aliases ────────────────────────────────────────────────────────────────────

title() {
  local before=false
  local message=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -a) before=true; shift ;;
      *)  message="$1"; shift ;;
    esac
  done
  print_section "$message" "$before"
}

info() {
  local before=false after=false
  local message=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -n) after=true;  shift ;;
      -a) before=true; shift ;;
      *)  message="$1"; shift ;;
    esac
  done
  print_info "info" "$message" "$before" "$after"
}

success() {
  local before=false after=false
  local message=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -n) after=true;  shift ;;
      -a) before=true; shift ;;
      *)  message="$1"; shift ;;
    esac
  done
  print_success "ok" "$message" "$before" "$after"
}

failure() {
  local before=false after=false
  local message=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -n) after=true;  shift ;;
      -a) before=true; shift ;;
      *)  message="$1"; shift ;;
    esac
  done
  print_error "error" "$message" "$before" "$after"
}

skip() {
  local before=false after=false
  local message=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -n) after=true;  shift ;;
      -a) before=true; shift ;;
      *)  message="$1"; shift ;;
    esac
  done
  print_info "skip" "$message" "$before" "$after"
}

require_command() {
  local command_name="$1"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    print_error "deps" "Missing required command: $command_name"
    exit 1
  fi

  return 0
}
