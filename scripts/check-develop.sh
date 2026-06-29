#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

print_rule "check develop sync with main"

# Step 1: Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  failure -n "uncommitted changes present"
  exit 1
fi

# Step 2: Ensure we're on develop branch
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$CURRENT_BRANCH" != "develop" ]]; then
  info "Switching to develop..."
  git checkout develop
fi

# Step 3: Fetch latest changes from remote
git fetch origin main develop

# Step 4: Get the tip commits
MAIN_SHA="$(git rev-parse origin/main)"
DEVELOP_SHA="$(git rev-parse origin/develop)"

# Step 5: If SHAs are identical, branches are in sync
if [[ "$MAIN_SHA" == "$DEVELOP_SHA" ]]; then
  skip -a -n "develop is in sync with main"
  exit 0
fi

# Step 6: Check if main is ahead of develop by only merge commits (releases)
MAIN_AHEAD="$(git log origin/develop..origin/main --oneline 2>/dev/null || echo "")"

if [[ -n "$MAIN_AHEAD" ]]; then
  printf "\n"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$MAIN_AHEAD"

  # Count merge commits vs total commits
  MERGE_ONLY_COUNT=$(git log origin/develop..origin/main --merges --oneline 2>/dev/null | wc -l)
  TOTAL_COUNT=$(echo "$MAIN_AHEAD" | wc -l)

  if [[ $MERGE_ONLY_COUNT -eq $TOTAL_COUNT ]]; then
    info "main is ahead of develop by release merge commits only"
    success "develop is in sync with main"
    exit 0
  fi

  failure -n -a "main has non-merge commits not on develop"
  exit 1
fi

# Step 7: Check if develop is ahead of main
DEVELOP_AHEAD="$(git log origin/main..origin/develop --oneline 2>/dev/null || echo "")"

if [[ -n "$DEVELOP_AHEAD" ]]; then
  printf "\n"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$DEVELOP_AHEAD"

  failure -n -a "develop has commits not on main"
  exit 1
fi

success "develop is in sync with main"
