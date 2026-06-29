#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

print_rule "sync develop"

if ! git diff --quiet || ! git diff --cached --quiet; then
  failure -n "uncommitted changes present -- aborting to avoid data loss"
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$CURRENT_BRANCH" != "develop" ]]; then
  info "Switching to develop..."
  git checkout develop
fi

git fetch origin main develop

MAIN_SHA="$(git rev-parse origin/main)"
DEVELOP_SHA="$(git rev-parse origin/develop)"

if [[ "$MAIN_SHA" == "$DEVELOP_SHA" ]]; then
  skip -a -n "develop is already in sync with origin/main"
  exit 0
fi

LOCAL_ONLY="$(git log origin/develop..develop --oneline 2>/dev/null)"
if [[ -n "$LOCAL_ONLY" ]]; then
  failure "local develop has commits not on origin/develop -- aborting to avoid data loss"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$LOCAL_ONLY"
  exit 1
fi

REMOTE_ONLY="$(git log origin/main..origin/develop --oneline 2>/dev/null)"
if [[ -n "$REMOTE_ONLY" ]]; then
  failure "origin/develop has commits not on origin/main -- aborting to avoid data loss"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$REMOTE_ONLY"
  exit 1
fi

info "Resetting develop to origin/main..."
git reset --hard origin/main

info "Force-pushing develop..."
git push --force-with-lease origin develop

success "develop is now in sync with main"
