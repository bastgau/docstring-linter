# Git Workflow Guide

Complete end-to-end procedure for managing features, develop, and main branches with a clean history.

## Prerequisites

- Rebase and merge enabled on GitHub (no merge commits)
- Git configured with your name and email
- Main branch protected (PRs required, approvals required)

## 1. Create a new feature

```bash
# Update develop from origin
git checkout develop
git pull origin develop

# Create a feature branch from develop
git checkout -b feature/my-awesome-feature
```

**Naming convention:** `feature/description-in-kebab-case`

## 2. Develop on the feature

```bash
# Make changes, commit regularly with clear messages
git add .
git commit -m "feat: add awesome functionality"
git commit -m "test: add tests for awesome feature"
git commit -m "docs: update README with examples"

# Push the feature
git push -u origin feature/my-awesome-feature
```

**Commit rules:**
- Format: `type: subject` (feat, fix, docs, style, refactor, test, chore)
- Subject in lowercase, 15-100 characters, no trailing period
- 1 commit per logical change (no "fix typo" after a big commit)

## 3. Clean up the feature before PR (optional but recommended)

If you have work-in-progress commits ("wip", "debug", etc.), squash them before the PR:

```bash
# Check the history
git log develop..HEAD --oneline

# Interactive rebase to clean up
git rebase -i develop
# Mark commits to squash with 's' (squash)
# Merge the commit messages

# Force push to the feature (only if it's your solo branch)
git push --force-with-lease origin feature/my-awesome-feature
```

## 4. Create PR feature → develop

### Via CLI:
```bash
gh pr create \
  --title "feat: add awesome functionality" \
  --body "## Summary
  
Add awesome functionality to the project.

- Implement core feature
- Add comprehensive tests
- Update documentation" \
  --base develop \
  --assignee your-username
```

### Via GitHub UI:
1. Go to https://github.com/bastgau/docstring-linter/pulls
2. Click "New pull request"
3. Base: `develop`, Compare: `feature/my-awesome-feature`
4. Fill in title and description
5. Assign to yourself

## 5. Revisions and changes on the PR

```bash
# On your machine, the feature is already checked out
git add .
git commit -m "fix: address review feedback"

# Push again
git push origin feature/my-awesome-feature
```

**Important:** Do not rebase during an active PR (it rewrites history). Make normal commits instead.

## 6. Merge the PR feature → develop

**Via GitHub UI (recommended):**
1. Once approved, click "Rebase and merge"
2. Let GitHub apply the rebase automatically
3. Delete the feature branch after merge

**Via CLI:**
```bash
gh pr merge <PR_NUMBER> --rebase --delete-branch
```

**Result:** The feature commits are replayed on develop with new SHAs.

## 7. Update your local copy after merge

```bash
# Fetch changes
git fetch origin

# Delete the local feature branch
git branch -d feature/my-awesome-feature

# Or if Git refuses (branch not merged):
git branch -D feature/my-awesome-feature

# Switch to develop and update
git checkout develop
git pull origin develop
```

## 8. Sync develop with main (before opening the release PR)

Before creating a PR develop → main, make sure develop is clean:

```bash
# Check status
git checkout develop
git status  # Must be clean

# Fetch latest changes
git fetch origin

# Use the sync script (if develop has no extra commits)
./scripts/sync-develop.sh
```

**If sync-develop.sh fails:** It means develop has commits that main doesn't have, which is normal for a release. Continue to the next step.

## 9. Create PR develop → main (Release)

```bash
# Make sure you're on develop
git checkout develop

# Create the PR via CLI
gh pr create \
  --title "Release v0.5.0" \
  --body "## Summary

Release v0.5.0 with improvements and bug fixes.

- Add feature X
- Fix bug Y
- Improve performance Z" \
  --base main \
  --assignee your-username \
  --label "pr:release"
```

## 10. Merge the PR develop → main

**Via GitHub UI:**
1. Wait for approvals and CI
2. Click "Rebase and merge"
3. GitHub replays develop commits on main
4. DO NOT delete develop (it's the development branch)

**Via CLI:**
```bash
gh pr merge <PR_NUMBER> --rebase
```

**Important:** Do not delete develop!

## 11. Sync develop with main after release

Once main has been updated (rebased), resync develop:

```bash
git checkout develop
git fetch origin

# Get changes from main
git reset --hard origin/main

# Push the reset to develop
git push --force-with-lease origin develop
```

**Result:** develop and main have exactly the same commits and SHAs.

## 12. Tag the release (after merge to main)

```bash
# Create an annotated tag
git tag -a v0.5.0 -m "Release version 0.5.0"

# Push the tag
git push origin v0.5.0
```

GitHub Actions CI/CD will automatically create a release from the tag.

## Complete workflow summary

```
feature/my-feature
    ↓ (rebase and merge)
develop ← develop receives the rebased commits
    ↓ (after several features)
main ← develop merges into main via rebase
    ↓ (reset develop to sync)
develop ← develop becomes identical to main
    ↓ (tag created)
GitHub Release created automatically
    ↓ (create next feature)
feature/next-feature (from develop)
    ...
```

## Key points

1. **Feature:** Normal development, regular commits
2. **PR feature → develop:** Rebase, can squash before if needed
3. **develop:** Accumulates features until a release
4. **PR develop → main:** Rebase, creates the main history
5. **Resync:** Reset develop to main after merge
6. **Tag:** Create releases via tags

## Useful commands

```bash
# View history by branch
git log --graph --oneline --all

# Check which commits are ahead/behind
git log main..develop --oneline
git log develop..main --oneline

# Clean up deleted branches on origin
git fetch origin --prune

# Check changes before push
git diff origin/develop..HEAD --stat
```

## Troubleshooting

### Q: Conflict during rebase
```bash
# Resolve conflicts
git status  # see conflicted files
# Edit files and resolve
git add .
git rebase --continue
```

### Q: Rebase went wrong
```bash
# Abort the rebase
git rebase --abort
```

### Q: Feature is behind develop
```bash
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
git push --force-with-lease origin feature/my-feature
```

### Q: sync-develop.sh refuses to sync
```bash
# Check what's blocking
git log origin/main..origin/develop --oneline
# If expected (release in progress), ignore and continue manually
git checkout develop
git fetch origin
git reset --hard origin/main
git push --force-with-lease origin develop
```

## GitHub configuration

For the workflow to work optimally:

1. **Branch protection rules (main):**
   - Require pull request reviews before merging
   - Require status checks to pass
   - Require branches to be up to date before merging

2. **Merge button settings:**
   - ✓ Allow rebase merging
   - ✗ Disallow merge commits
   - ✗ Disallow squash merging (optional, can squash for features)

3. **Delete head branch:** Automatically delete branches after merge
