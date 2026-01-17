# Release Playbook

Merge PR and create release tag. CI/CD handles the rest.

## Process
1. Verify version bumped in `pyproject.toml` and `CHANGELOG.md` updated.
2. Merge PR on GitHub.
3. Switch to main and pull: `git checkout main && git pull origin main`.
4. Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
5. Push tag: `git push origin vX.Y.Z`.

## What CI/CD Does Automatically
GitHub Workflows in `.github/workflows/` (e.g., `release.yml`) trigger on `v*` tags and:
- Run tests and linting.
- Create GitHub Release with artifacts.

## Tag Format
- Use `v` prefix: `v0.1.0`, `v1.0.0`.
- Follow semantic versioning.
- Use annotated tags (not lightweight).

## Pre-Release Tags
For pre-releases, use suffixes:
- Alpha: `v1.0.0-alpha.1`
- Beta: `v1.0.0-beta.1`
- Release candidate: `v1.0.0-rc.1`

## Verification
After push, check:
- GitHub Actions: `.github/workflows/release.yml` runs.
- GitHub Releases page for new release.

## Rules
- Never create release manually—let CI/CD handle it.
- Ensure `CHANGELOG.md` has entry for version (used for release notes).
- Only tag commits that pass all CI checks.