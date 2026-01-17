# Run Linters Playbook

Run linters and fix all issues. Don't stop until all issues are fixed.

## Process
1. Read `LINTING.md` for project linting guidelines.
2. Run Ruff check: `uv run ruff check .`.
3. Fix auto-fixable issues: `uv run ruff check --fix .`.
4. Format code: `uv run ruff format .`.
5. Run MyPy: `uv run mypy src/`.
6. Verify all passes: `uv run ruff check . && uv run mypy src/`.

## Commands
```bash
uv run ruff check .       # Lint check
uv run ruff check --fix . # Auto-fix what's possible
uv run ruff format .      # Format code
uv run mypy src/          # Type check (strict)
```

## Auto-Fix Workflow
```bash
uv run ruff format .      # Fix formatting
uv run ruff check --fix . # Fix linting violations
uv run mypy src/          # Check types
```

## Guidelines
- Fix issues in order: formatting → linting → type errors.
- Use `# noqa: RULE` sparingly and document why.
- For type errors, prefer fixing over `# type: ignore`.
- Read `LINTING.md` for tool-specific configurations.

## Checklist
- [ ] `uv run ruff check .` passes.
- [ ] `uv run ruff format .` check passes.
- [ ] `uv run mypy src/` passes (strict mode).
- [ ] No new `# noqa` or `# type: ignore` without justification.