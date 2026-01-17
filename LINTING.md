# Linting and Code Quality Configuration

This document describes the linting and code quality tools configured for the EngageRunner project.

## Overview

The project uses a comprehensive set of linting tools to ensure code quality, type safety, and maintainability:

- **Ruff**: Fast Python linter and formatter with 38+ rule sets enabled
- **MyPy**: Static type checker in strict mode
- **pytest**: Testing framework with asyncio support

## Quick Start

### Installation

```bash
# Install all dependencies including dev tools
uv sync

# Verify installation
uv run ruff --version
uv run mypy --version
uv run pytest --version

# Keep uv updated to latest version
uv self update
```

### Running Linting

#### Basic Commands:

```bash
# Run Ruff linting
uv run ruff check .

# Run Ruff with automatic fixes
uv run ruff check . --fix

# Format code with Ruff
uv run ruff format .

# Run type checking with MyPy
uv run mypy src/

# Run all linting checks
uv run ruff check . && uv run mypy src/

# Run tests
uv run pytest tests/

# Run tests with coverage
uv run pytest tests/ --cov=engagerunner --cov-report=term-missing
```

#### Advanced Options:

```bash
# Show detailed linting output
uv run ruff check . --output-format=full

# Run Ruff with unsafe fixes enabled
uv run ruff check . --fix --unsafe-fixes

# Run specific Ruff rules only
uv run ruff check . --select=F,E,W

# Run MyPy with verbose output
uv run mypy src/ --verbose

# Run MyPy on specific file
uv run mypy src/engagerunner/cli.py
```

## Tool Configuration

<details>
<summary><strong>Ruff Configuration</strong></summary>

Ruff is configured in `pyproject.toml` with 38+ comprehensive rule sets:

**Core Rules:**
- **F**: Pyflakes - basic error detection
- **E, W**: pycodestyle errors and warnings
- **I**: isort - import sorting
- **N**: pep8-naming
- **UP**: pyupgrade - modernize Python code

**Async & Best Practices:**
- **ASYNC**: flake8-async - async/await best practices
- **B**: flake8-bugbear - common bugs and design issues
- **A**: flake8-builtins - avoid shadowing builtins
- **C4**: flake8-comprehensions - better comprehensions

**Type Checking & Imports:**
- **TCH**: flake8-type-checking - TYPE_CHECKING blocks
- **TID**: flake8-tidy-imports
- **ICN**: flake8-import-conventions
- **FA**: flake8-future-annotations

**Logging & Debugging:**
- **LOG**: flake8-logging - logging best practices
- **G**: flake8-logging-format
- **T10**: flake8-debugger - no debugger statements
- **T20**: flake8-print - no print statements

**Code Quality:**
- **SIM**: flake8-simplify - simplification suggestions
- **PIE**: flake8-pie - misc lints
- **RET**: flake8-return - return statement best practices
- **ARG**: flake8-unused-arguments
- **SLF**: flake8-self - private member access

**Testing & Comments:**
- **PT**: flake8-pytest-style
- **TD**: flake8-todos - TODO comment quality
- **FIX**: flake8-fixme - FIXME/XXX/TODO tracking
- **ERA**: eradicate - no commented-out code

**Advanced:**
- **PL**: Pylint
- **TRY**: tryceratops - exception handling
- **PERF**: Perflint - performance anti-patterns
- **FURB**: refurb - modernization suggestions
- **RUF**: Ruff-specific rules
- **DTZ**: flake8-datetimez - datetime timezone safety
- **PTH**: flake8-use-pathlib - prefer pathlib
- **SLOT**: flake8-slots
- **RSE**: flake8-raise
- **Q**: flake8-quotes
- **PYI**: flake8-pyi - type stub files
- **ISC**: flake8-implicit-str-concat
- **YTT**: flake8-2020 - Python 2020 checks
- **FLY**: flynt - f-string conversion

**Disabled Rules:**
- `ISC001`: Conflicts with formatter
- `COM812`: Conflicts with formatter

**Per-File Ignores:**
- `tests/**/*.py`: Allow assert, unused arguments, magic values
- `main.py`: Allow print statements
- `src/engagerunner/cli.py`: Allow print for CLI output

**Configuration:**
- Line length: 100
- Target version: Python 3.13
- Preview mode: enabled

</details>

<details>
<summary><strong>MyPy Configuration</strong></summary>

MyPy is configured in **strict mode** with all strict type checking enabled:

**Strict Mode Enables:**
- `warn_unused_configs`: Warn about unused config options
- `disallow_any_generics`: Disallow generic types without type parameters
- `disallow_subclassing_any`: Disallow subclassing Any
- `disallow_untyped_calls`: Disallow calling untyped functions
- `disallow_untyped_defs`: Require type hints on all functions
- `disallow_incomplete_defs`: Require all parameters to have type hints
- `check_untyped_defs`: Check untyped function definitions
- `disallow_untyped_decorators`: Require type hints on decorators
- `warn_redundant_casts`: Warn about unnecessary type casts
- `warn_unused_ignores`: Warn about unused type ignore comments
- `warn_return_any`: Warn when returning Any from typed function
- `no_implicit_reexport`: Require explicit re-exports
- `strict_equality`: Enforce strict equality checks
- `strict_concatenate`: Strict checking of concatenation

**Additional Strict Settings:**
- `warn_unreachable`: Warn about unreachable code
- `warn_no_return`: Warn about functions that don't return
- `show_error_codes`: Show error codes in output
- `show_error_context`: Show error context
- `pretty`: Pretty print output

**Library Overrides:**
Third-party libraries without type stubs have `ignore_missing_imports = true`:
- `browser_use.*`: Browser automation library
- `langchain_anthropic.*`: LangChain Anthropic integration

</details>

<details>
<summary><strong>Testing Configuration</strong></summary>

**pytest:**
- Test paths: `tests/`
- Asyncio mode: `auto` (automatic async test detection)
- Plugins: pytest-asyncio, pytest-cov, pytest-anyio

**Running Tests:**
```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with coverage
uv run pytest tests/ --cov=engagerunner --cov-report=term-missing

# Run with coverage HTML report
uv run pytest tests/ --cov=engagerunner --cov-report=html
```

</details>

## IDE Integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit"
        }
    },
    "python.linting.mypyEnabled": true,
    "python.linting.mypyArgs": [
        "--strict",
        "--show-error-codes"
    ]
}
```

### PyCharm

1. **Install Ruff plugin:**
   - Settings → Plugins → Search "Ruff" → Install

2. **Configure MyPy:**
   - Settings → Tools → External Tools → Add MyPy
   - Program: `uv`
   - Arguments: `run mypy src/`
   - Working directory: `$ProjectFileDir$`

3. **Enable format on save:**
   - Settings → Tools → Actions on Save
   - Enable "Reformat code" and "Optimize imports"

## Troubleshooting

### Common Issues

1. **MyPy errors with external libraries:**
   - Check the `[tool.mypy.overrides]` section in `pyproject.toml`
   - Libraries without type stubs (browser_use, langchain_anthropic) are already configured to ignore missing imports
   - For new libraries, add them to the overrides section

2. **Ruff formatting conflicts:**
   - Run `uv run ruff format .` to fix formatting issues
   - Check that your editor uses the same Ruff version
   - Use `uv run ruff check . --fix` for auto-fixable issues

3. **Type ignore comments:**
   - Use for unavoidable third-party library issues: `# type: ignore[call-overload]`
   - Always include specific error codes: `# type: ignore[no-any-return]`
   - Document why the ignore is needed in complex cases

### Ignoring Rules

To ignore specific rules in code:

```python
# Ignore specific Ruff rule
some_code  # noqa: E501

# Ignore multiple Ruff rules
some_code  # noqa: E501, F401

# Ignore MyPy error with specific code
some_code  # type: ignore[attr-defined]

# Ignore entire line for MyPy
some_code  # type: ignore
```

## Best Practices

1. **Run linting before committing:**
   ```bash
   uv run ruff check . --fix && uv run mypy src/
   ```

2. **Format code regularly:**
   ```bash
   uv run ruff format .
   ```

3. **Use type hints consistently:**
   ```python
   def process_data(data: list[str]) -> dict[str, int]:
       """Process data and return counts.

       Args:
           data: List of string items

       Returns:
           Dictionary mapping items to counts
       """
       return {item: data.count(item) for item in set(data)}
   ```

4. **Follow logging best practices:**
   ```python
   # Good - lazy % formatting
   logger.info("Processing %d items", len(items))

   # Bad - f-string in logging
   logger.info(f"Processing {len(items)} items")  # noqa: G004
   ```

5. **Use pathlib for file operations:**
   ```python
   from pathlib import Path

   # Good
   config_file = Path("config.yaml")
   with config_file.open(encoding="utf-8") as f:
       data = f.read()

   # Bad
   with open("config.yaml") as f:  # Missing encoding
       data = f.read()
   ```

6. **Use timezone-aware datetime:**
   ```python
   from datetime import UTC, datetime

   # Good
   now = datetime.now(UTC)

   # Bad
   now = datetime.now()  # No timezone
   ```

7. **Prefer modern enum types:**
   ```python
   from enum import StrEnum

   # Good
   class Status(StrEnum):
       ACTIVE = "active"
       INACTIVE = "inactive"

   # Old style
   class Status(str, Enum):  # Use StrEnum instead
       ACTIVE = "active"
   ```

8. **Keep functions small and focused:**
   - Aim for functions under 20-30 lines
   - Single responsibility principle
   - Extract complex logic into helper functions

9. **Write descriptive docstrings:**
   ```python
   def calculate_engagement_score(
       comments: list[Comment],
       weights: dict[str, float] | None = None,
   ) -> float:
       """Calculate engagement score based on comment metrics.

       Args:
           comments: List of comments to analyze
           weights: Optional custom weights for scoring

       Returns:
           Engagement score between 0.0 and 100.0

       Raises:
           ValueError: If comments list is empty
       """
       if not comments:
           raise ValueError("Cannot calculate score for empty comment list")
       # Implementation...
   ```

10. **Use meaningful variable names:**
    ```python
    # Good
    user_comment_count = len(user_comments)
    max_retry_attempts = 3

    # Bad
    c = len(u)
    n = 3
    ```

## Configuration Files

- `pyproject.toml`: Main configuration for Ruff, MyPy, and pytest
- `.python-version`: Python version specification for uv
- `uv.lock`: Locked dependency versions

## Contributing

When contributing to the project:

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run linting checks:**
   ```bash
   uv run ruff check . --fix
   uv run ruff format .
   uv run mypy src/
   ```

3. **Run tests:**
   ```bash
   uv run pytest tests/ -v
   ```

4. **Verify all checks pass:**
   ```bash
   uv run ruff check . && uv run mypy src/ && uv run pytest tests/
   ```

5. **Commit changes following conventional commits:**
   ```
   feat: add new platform adapter
   fix: resolve type errors in config loader
   docs: update linting documentation
   test: add tests for comment parsing
   ```

## Continuous Integration

For CI environments, use the following commands:

```bash
# Install dependencies
uv sync

# Run all checks
uv run ruff check .
uv run mypy src/
uv run pytest tests/ --cov=engagerunner --cov-report=xml

# Generate coverage report
uv run pytest tests/ --cov=engagerunner --cov-report=html
```

## Summary

The EngageRunner project enforces high code quality standards through:

- **Comprehensive linting** with 38+ Ruff rule sets covering errors, style, security, and performance
- **Strict type checking** with MyPy ensuring type safety across the codebase
- **Automated testing** with pytest and asyncio support
- **Modern Python practices** (Python 3.13+, pathlib, StrEnum, timezone-aware datetime)

This ensures maintainable, secure, and high-quality code throughout the project.
