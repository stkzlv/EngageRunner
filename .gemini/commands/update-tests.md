# Update Tests Playbook

Review and update project tests for quality and coverage.

## Process
1. Run tests with coverage: `uv run pytest tests/ --cov=engagerunner --cov-report=term-missing`.
2. Review coverage report for gaps.
3. Identify and remove outdated tests.
4. Verify tests against current codebase.
5. Add tests for uncovered critical paths.

## Commands
```bash
uv run pytest tests/          # Run all tests
uv run pytest tests/ --cov=engagerunner --cov-report=term-missing # With coverage
uv run pytest tests/path/to/test.py  # Run specific test
uv run pytest -k "test_name"         # Run by name pattern
```

## Coverage Report
- Terminal: Shows missing lines with `--cov-report=term-missing`.
- Check `pyproject.toml` for test configurations.

## Discover Test Structure
```bash
# List all test files
find tests/ -name "test_*.py"
```

## Best Practices
- Follow AAA pattern: Arrange, Act, Assert.
- Keep tests isolated and independent.
- Use fixtures for shared setup.
- Mock external dependencies (APIs, Browser).
- Mirror source structure in tests/.
- Name tests descriptively: `test_<function>_<scenario>_<expected>`.

## Review Checklist
- [ ] Remove tests for deleted code.
- [ ] Update tests for modified functions.
- [ ] Add tests for new functionality.
- [ ] Check for flaky tests (random failures).
- [ ] Verify mocks match current interfaces.