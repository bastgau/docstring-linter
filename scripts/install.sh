#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

print_header() {
  printf '\n'
  printf '%sDescription: Installs uv, dotenv-linter, dev dependencies and pre-commit hooks%s\n' "${YELLOW}" "${NC}"
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

install_uv() {
  print_rule "uv"
  printf '\n'
  if ! have_cmd uv; then
    printf '%sCommand : $ curl -LsSf https://astral.sh/uv/install.sh | sh%s\n' "${GRAY}" "${NC}"
    printf '\n'
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
      export PATH="$HOME/.local/bin:$PATH"
      printf '\n'
      print_success "uv" "Installation successful"
    else
      print_error "uv" "Installation failed"; exit 1
    fi
  else
    print_info "uv" "Nothing to do (uv already installed)"
  fi
}

install_dotenv_linter() {
  print_rule "dotenv-linter"
  printf '\n'
  if ! have_cmd dotenv-linter; then
    printf '%sCommand : $ curl -sSfL https://raw.githubusercontent.com/dotenv-linter/dotenv-linter/master/install.sh | sudo sh%s\n' "${GRAY}" "${NC}"
    printf '\n'
    if curl -sSfL https://raw.githubusercontent.com/dotenv-linter/dotenv-linter/master/install.sh | sudo sh -s -- -b /usr/local/bin; then
      printf '\n'
      print_success "dotenv-linter" "Installation successful"
    else
      print_error "dotenv-linter" "Installation failed"; exit 1
    fi
  else
    print_info "dotenv-linter" "Nothing to do (dotenv-linter already installed)"
  fi
}

install_dev_deps() {
  print_rule "dev dependencies"
  printf '\n'
  printf '%sCommand : $ uv sync --group dev%s\n' "${GRAY}" "${NC}"
  printf '\n'
  if uv sync --group dev; then
    printf '\n'
    print_success "dev dependencies" "Installation successful"
  else
    print_error "dev dependencies" "Installation failed"; exit 1
  fi
}

install_precommit() {
  print_rule "pre-commit hooks"
  printf '\n'
  printf '%sCommand : $ uv run prek install%s\n' "${GRAY}" "${NC}"
  printf '\n'
  if uv run prek install; then
    printf '\n'
    print_success "pre-commit hooks" "Installation successful"
  else
    print_error "pre-commit hooks" "Installation failed"; exit 1
  fi
}

print_header

install_uv
install_dotenv_linter

ACTIVATE_LINE="source ${UV_PROJECT_ENVIRONMENT}/bin/activate"
grep -qxF "$ACTIVATE_LINE" "$HOME/.bashrc" || echo "$ACTIVATE_LINE" >> "$HOME/.bashrc"

install_dev_deps
install_precommit

printf '\n'
