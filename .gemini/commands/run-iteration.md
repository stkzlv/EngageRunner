# Run Iteration Playbook

Start a new development iteration with a feature branch.

## Arguments
- `$ARGUMENTS` - Main objective for the iteration.

## Process
1. Read `REQUIREMENTS.md` and `GEMINI.md` for guidelines.
2. Pull latest main: `git checkout main && git pull origin main`.
3. Create feature branch with descriptive name.
4. Push branch: `git push -u origin <branch-name>`.
5. Confirm ready to begin implementation.

## Branch Naming Conventions
- `feature/` - New features (e.g., `feature/youtube-discovery`).
- `bugfix/` - Bug fixes (e.g., `bugfix/rate-limiter-logic`).
- `hotfix/` - Critical fixes (e.g., `hotfix/chrome-connection-error`).
- `docs/` - Documentation updates (e.g., `docs/update-requirements`).

## Branch Name Guidelines
- Use lowercase with hyphens.
- Keep names short but descriptive.
- Derive from objective (e.g., "Add user auth" → `feature/user-authentication`).

## Example
```bash
# Objective: "Add rate limiting for engagement"
# Branch: feature/engagement-rate-limiting

git checkout main
git pull origin main
git checkout -b feature/engagement-rate-limiting
git push -u origin feature/engagement-rate-limiting
```

## After Branch Creation
- Summarize the objective.
- Confirm branch is ready.
- Ask if user wants to proceed with implementation.