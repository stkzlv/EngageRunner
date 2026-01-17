# EngageRunner Project Memory

## Project Overview

**EngageRunner** is an AI-powered social media engagement automation tool that uses browser-use for realistic browser automation. It automates reading and responding to comments on YouTube (with Instagram and TikTok planned).

**Core Philosophy**:
- **"Bring Your Own Profile" (BYOP):** No login scripts or 2FA handling. Uses your legitimate, logged-in Chrome session.
- **Safety First:** Actions are rate-limited, randomized, and tracked to prevent spam detection.
- **Local Execution:** Everything runs locally; credentials never leave your Chrome profile.

**Tech Stack**: Python 3.13+, uv, browser-use, Playwright, Pydantic, PyYAML.

---

## Essential Commands

```bash
# Start Chrome with remote debugging (required before running commands)
google-chrome --remote-debugging-port=9222

# Core workflow
uv run engagerunner list-videos --max 10            # List videos from channel
uv run engagerunner read <VIDEO_URL> --max 20       # Read comments from video
uv run engagerunner engage -s simple_engagement     # Execute engagement scenario
uv run engagerunner engage -s simple_engagement -n  # Dry-run (no actions)

# Quality assurance
uv sync                       # Install dependencies
uv run ruff check . --fix     # Lint with auto-fix
uv run ruff format .          # Format code
uv run mypy src/              # Type check (strict mode)
uv run pytest tests/          # Run tests
```

---

## Code Standards

- **Line Length**: 100 characters (ruff)
- **Typing**: Modern Python typing, strict MyPy mode, Pydantic models for all data structures
- **Naming**: `snake_case` (functions/vars), `PascalCase` (classes), `UPPER_CASE` (constants)
- **Error Handling**: Specific exceptions, structured logging
- **Async**: Prefer `async/await` for I/O-bound operations
- **Emojis**: Do NOT use emojis in source code, comments, or logs

---

## Development Guidelines

- Use uv for dependency management
- Use imperative commit messages (e.g., "Add rate limiter")
- **Never mention Claude Code or AI tools in git commit messages or PR descriptions**
- Create implementation plans for features/fixes before coding
- Prefer incremental changes over large rewrites

**Important Documentation**:
- **CONTRIBUTING.md**: GitHub Flow workflow, branch naming, code style
- **REQUIREMENTS.md**: MVP scope and success criteria
- **VERSIONING.md**: Semantic versioning rules, release process

---

## Git Commit & PR Guidelines

**Commit Messages**:
- Use imperative mood (e.g., "Add feature", not "Added feature")
- Keep first line under 50 characters
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- **Never mention authors, Claude Code, or AI assistants**

**Pull Request Descriptions**:
- **Never mention Claude Code or AI tools**
- Focus on what changed, why, and how to test
- Use PR template if available

---

## Development Workflow (GitHub Flow)

### Branch Management

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

**Branch Naming**:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `docs/` - Documentation updates

### Quality Gates (Before PR)

```bash
uv run ruff check .           # Lint
uv run ruff format --check .  # Format check
uv run mypy src/              # Type check
uv run pytest tests/          # Tests
```

### Merge Process

- Squash merge for clean history
- All CI checks must pass
- Address review feedback

---

## System Architecture

```
src/engagerunner/
├── browser/           # Chrome CDP connection (controller.py)
├── platforms/         # Platform adapters (youtube.py, base.py)
├── models/            # Pydantic models (config, comment, task)
├── utils/             # Safety utilities (rate_limiter, state, time_parser)
├── config.py          # YAML + env config loading
├── llm.py             # LLM factory with retry/fallback
├── cli.py             # CLI entry point
└── __init__.py
```

**Data Flow**:
`Config (YAML -> Pydantic)` -> `Browser Engine` -> `Platform Driver` -> `Discover` -> `Filter` -> `Execute Actions` -> `Update State`

---

## Standard Operating Procedures

When performing standard tasks, consult the playbooks in `.claude/commands/`:

| Task | Playbook |
|------|----------|
| Bump Version | `.claude/commands/bump-version.md` |
| Commit Changes | `.claude/commands/commit.md` |
| Release | `.claude/commands/release.md` |
| Run Iteration | `.claude/commands/run-iteration.md` |
| Run Linters | `.claude/commands/run-linters.md` |
| Update Config | `.claude/commands/update-config.md` |
| Update Docs | `.claude/commands/update-docs.md` |
| Update PR | `.claude/commands/update-pr.md` |
| Update Tests | `.claude/commands/update-tests.md` |

---

## Release Process

**Version Bumping** (Semantic Versioning):
- **Major** (1.0.0 -> 2.0.0): Breaking API changes
- **Minor** (0.1.0 -> 0.2.0): New features (backward compatible)
- **Patch** (0.1.0 -> 0.1.1): Bug fixes only

**Steps**:
1. Update version in `pyproject.toml` and `src/engagerunner/__init__.py`
2. Update `CHANGELOG.md` following Keep a Changelog format
3. Commit: `git commit -m "Bump version to X.Y.Z"`
4. Merge PR to main
5. Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. Push tag to trigger CI release workflow

---

## Available MCP Servers

### Context7 Server
- **Purpose**: Library documentation lookup
- **Tools**: `resolve-library-id`, `query-docs`
- **Usage**: Get up-to-date docs for browser-use, Playwright, Pydantic, etc.

### GitHub Server
- **Purpose**: Repository management and automation
- **Capabilities**: Issues, PRs, code search, workflow automation

---

## Important Notes

- **Never modify `.env` files** or expose secrets
- **Do not commit generated files** (build artifacts, `.pyc`)
- **Ask for clarification** rather than making assumptions
- **Prefer incremental changes** over large rewrites
- **Always explain reasoning** for non-obvious decisions
- **Run linters** before committing any changes
