# Release Procedure

## Branches

| Branch | Purpose |
|--------|---------|
| `develop` | Day-to-day development |
| `fix/*` | Targeted bug fixes |
| `main` | Stable branch — releases only |

## Beta Release

Beta releases are created from `develop` or a `fix/*` branch.

```bash
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

The CI pipeline will run lint and tests, then create a GitHub pre-release with the changelog since the previous tag.

## Stable Release

Stable releases are created from `main` only. Merge `develop` or a `fix/*` branch into `main` via pull request first.

```bash
git tag v1.0.0
git push origin v1.0.0
```

The CI pipeline will run lint and tests, then create a GitHub release with the changelog since the last stable release (beta tags are ignored).

## Tag Format

| Type | Format | Example |
|------|--------|---------|
| Stable | `vMAJOR.MINOR.PATCH` | `v1.0.0` |
| Beta | `vMAJOR.MINOR.PATCH-beta.N` | `v1.0.0-beta.1` |

## Notes

- The version in `pyproject.toml` is not updated manually — the actual version is read from the Git tag at build time by the CI pipeline.
- Never create a stable release tag from `develop` or a `fix/*` branch.
- Always create releases by pushing a Git tag — never use the GitHub interface to create a release directly, as it will be skipped by the CI pipeline.
