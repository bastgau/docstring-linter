#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

print_rule "sync develop"

# Step 1: Check for uncommitted changes
# Prevents accidental data loss by ensuring working directory is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  failure -n "uncommitted changes present -- aborting to avoid data loss"
  exit 1
fi

# Step 2: Ensure we're on develop branch
# Switch to develop if not already on it
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$CURRENT_BRANCH" != "develop" ]]; then
  info "Switching to develop..."
  git checkout develop
fi

# Step 3: Fetch latest changes from remote
# Update our knowledge of origin/main and origin/develop
git fetch origin main develop

# Step 4: Compare commit SHAs
# Quick check if branches are already in sync (same commits)
MAIN_SHA="$(git rev-parse origin/main)"
DEVELOP_SHA="$(git rev-parse origin/develop)"

if [[ "$MAIN_SHA" == "$DEVELOP_SHA" ]]; then
  skip -a -n "develop is already in sync with origin/main"
  exit 0
fi

# Step 5: Check for local-only commits on develop
# Ensures local develop doesn't have commits not yet pushed to origin
LOCAL_ONLY="$(git log origin/develop..develop --oneline 2>/dev/null)"
if [[ -n "$LOCAL_ONLY" ]]; then
  printf "\n"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$LOCAL_ONLY"
  failure -n -a "local develop has commits not on origin/develop -- aborting to avoid data loss"
  exit 1
fi

# Step 6: Compare content (tree hashes)
# Tree hash represents the actual file content, independent of commit history
# If trees match but SHAs differ, it means commits were rewritten (rebased)
MAIN_TREE="$(git rev-parse "origin/main^{tree}")"
DEVELOP_TREE="$(git rev-parse "origin/develop^{tree}")"

if [[ "$MAIN_TREE" == "$DEVELOP_TREE" ]]; then
  info "develop has same content as main (tree match), but different commit history"
  info "This typically happens after a rebase. Syncing..."
  info "Resetting develop to origin/main..."
  git reset --hard origin/main
  info "Force-pushing develop..."
  git push --force-with-lease origin develop
  success "develop is now in sync with main"
  exit 0
fi

# Step 7: Check for develop-only commits at origin
# These might be legitimate new commits or duplicates from a rebase
REMOTE_ONLY="$(git log origin/main..origin/develop --oneline 2>/dev/null)"
if [[ -n "$REMOTE_ONLY" ]]; then
  printf "\n"
  while IFS= read -r line; do
    print_detail "$line"
  done <<< "$REMOTE_ONLY"

  # Step 8: Detect if develop-only commits are actually duplicates
  # Compare commit messages to identify rebased/cherry-picked commits
  info "Checking if commits are duplicates (rebase/cherry-pick)..."
  MAIN_COMMITS="$(git log origin/main --format='%B' | head -100)"

  DUPLICATES=0
  while IFS= read -r line; do
    COMMIT_MSG="${line#* }"
    if echo "$MAIN_COMMITS" | grep -q "$COMMIT_MSG"; then
      DUPLICATES=$((DUPLICATES + 1))
    fi
  done <<< "$REMOTE_ONLY"

  # Step 9: If duplicates found, sync safely
  # Rebase creates commits with same message but different SHA
  if [[ $DUPLICATES -gt 0 ]]; then
    info "$DUPLICATES commits on develop appear to be duplicates from main (likely rebase)"
    info "Resetting develop to origin/main..."
    git reset --hard origin/main
    info "Force-pushing develop..."
    git push --force-with-lease origin develop
    success "develop is now in sync with main (removed duplicate commits)"
    exit 0
  fi

  # Step 10: Reject if commits are genuinely unique
  # Prevents losing work that hasn't been merged to main yet
  failure -n -a "origin/develop has unique commits not on origin/main -- aborting to avoid data loss"
  exit 1
fi

# Step 11: Final sync when develop is simply behind main
# Normal case: develop doesn't have commits main doesn't have
info "Resetting develop to origin/main..."
git reset --hard origin/main

# Step 12: Force-push to origin
# Safe because we've verified no data loss and --force-with-lease prevents race conditions
info "Force-pushing develop..."
git push --force-with-lease origin develop

success "develop is now in sync with main"
