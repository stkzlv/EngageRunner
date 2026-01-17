# EngageRunner Project Memory

## 1. Project Overview

**EngageRunner** is an automated, AI-powered social media engagement agent. It impersonates a user by leveraging a pre-authenticated, local Chrome profile to interact with platforms like YouTube. The primary goal is to automate repetitive engagement tasks like reacting to new comments, ensuring no audience interaction is missed.

**Core Philosophy**:
*   **"Bring Your Own Profile" (BYOP):** No complex login scripts or 2FA handling. We piggyback on your legitimate, logged-in session.
*   **Safety First:** Actions are rate-limited, randomized, and tracked to prevent spam detection.
*   **Local Execution:** Everything runs on your machine; your credentials never leave your local Chrome profile.

**Tech Stack**: Python 3.13+, uv, browser-use, Playwright, Pydantic, PyYAML.

---

## 2. Team Norms & Development Workflow

### GitHub Flow
1.  **Branching**: Create feature branches from `main`.
    *   `feature/your-feature-name` (New features)
    *   `bugfix/issue-description` (Bug fixes)
    *   `docs/update-description` (Documentation)
2.  **Commits**:
    *   Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.
    *   Use **Imperative Mood**: "Add rate limiter" (not "Added").
    *   **Atomic**: Keep commits focused on a single logical change.
3.  **Pull Requests**:
    *   Push branch to origin.
    *   Open PR against `main`.
    *   **CI Checks**: All linting (`ruff`, `mypy`) and tests (`pytest`) must pass.
    *   **Merge**: Squash merge to `main` to maintain a clean history.

---

## 3. Execution Modes

### 🔍 Explain Mode
**Trigger:** "explain", "investigate", "analyze", "what does"
- Read and analyze relevant code.
- Provide clear explanations with examples.
- **Do NOT modify any files.**
- Ask clarifying questions if scope is unclear.

### 📝 Plan Mode
**Trigger:** "plan", "design", "propose", "how would"
- Create a detailed implementation plan (e.g., in `IMPLEMENTATION_PLAN.md`).
- List all files to be created or modified.
- Identify potential risks or breaking changes.
- **Do NOT implement anything.**
- Wait for explicit approval before proceeding.

### 🚀 Implement Mode
**Trigger:** "implement", "execute", "do it", "approved"
**Prerequisite:** A plan must exist from Plan Mode.
- Follow the approved plan step by step.
- Create checkpoints before major changes.
- Report progress after each significant step.
- Stop and ask if encountering unexpected issues.

---

## 4. Coding Standards & Style

- **Linting:** Adhere to `ruff` formatting (100 chars).
- **Typing:** Modern Python typing (strict mode MyPy). All data structures must be defined as **Pydantic models**.
- **Naming:** `snake_case` (functions/vars), `PascalCase` (classes), `UPPER_CASE` (constants).
- **Error Handling:** Specific exceptions, structured logging.
- **Async:** Prefer `async/await` for I/O bound operations.
- **Emojis:** Do NOT use emojis in source code (comments, strings, or logs). Use plain text instead.

---

## 5. System Design & Architecture

### Core Pipeline (`src/engagerunner/`)
- **CLI (`cli.py`):** Main entry point.
- **Scenario Runner:** Executes defined engagement scenarios.
- **Platform Drivers (`platforms/`):** Platform-specific discovery and actions.
- **Browser Engine (`browser/`):** Manages Chrome/CDP connection.
- **Safety Utilities (`utils/`):** `RateLimiter`, `EngagementState`, `TimeParser`.

### Data Flow
`Config (YAML -> Pydantic)` -> `Browser Engine` -> `Platform Driver` -> `Discover` -> `Filter` -> `Execute Actions` -> `Update State`.

### Directory Structure
```
src/engagerunner/
├── browser/       # Chrome connection logic
├── platforms/     # YouTube, etc. (Platform adapters)
├── utils/         # Safety, Time parsing, Logging
├── config.py      # Pydantic models for config
├── cli.py         # Entry point
└── __init__.py
```

---

## 6. Essential Commands

### Core Workflows
```bash
# Run a specific engagement scenario
uv run engagerunner run <scenario_name>
```

### Quality Assurance
```bash
uv sync                      # Install dependencies
uv run ruff check . --fix    # Lint
uv run ruff format .         # Format
uv run mypy src/             # Type check
uv run pytest tests/         # Test
```

---

## 7. Agent Maintenance & Verification

### 7.1 Verification Loop
Before executing complex tasks:
1.  **Audit Source**: List `src/engagerunner/` subdirectories.
2.  **Verify Deps**: Read `pyproject.toml`.
3.  **Command Check**: Check `[project.scripts]` and `pyproject.toml` config.

### 7.2 Self-Update Instructions
Update this file when:
- Structural changes occur.
- New standard workflows or tech are added.
- Coding standards evolve.

---

## 8. Standard Operating Procedures (Playbooks)

When requested to perform standard tasks, consult the detailed playbooks in `.gemini/commands/`:

*   **Bump Version**: `.gemini/commands/bump-version.md`
*   **Commit Changes**: `.gemini/commands/commit.md`
*   **Release**: `.gemini/commands/release.md`
*   **Run Iteration**: `.gemini/commands/run-iteration.md`
*   **Run Linters**: `.gemini/commands/run-linters.md`
*   **Update Config**: `.gemini/commands/update-config.md`
*   **Update Docs**: `.gemini/commands/update-docs.md`
*   **Update PR**: `.gemini/commands/update-pr.md`
*   **Update Tests**: `.gemini/commands/update-tests.md`

---

## 9. Important Notes

- **Never modify `.env` files** or expose secrets.
- **Do not commit generated files** (e.g., `uv.lock` is fine, but build artifacts are not).
- **Ask for clarification** rather than making assumptions.
- **Prefer incremental changes** over large rewrites.
- **Always explain reasoning** for non-obvious decisions.