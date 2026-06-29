#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

print_rule "sync develop"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$CURRENT_BRANCH" != "develop" ]]; then
  info "Switching to develop..."
  git checkout develop
fi

git fetch origin main

MAIN_SHA="$(git rev-parse origin/main)"
DEVELOP_SHA="$(git rev-parse origin/develop)"

if [[ "$MAIN_SHA" == "$DEVELOP_SHA" ]]; then
  skip -a -n "develop is already in sync with origin/main"
  exit 0
fi

info "Resetting develop to origin/main..."
git reset --hard origin/main

info "Force-pushing develop..."
git push --force-with-lease origin develop

success "develop is now in sync with main"
