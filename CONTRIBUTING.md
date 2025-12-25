# Contributing to EngageRunner

We welcome contributions! This guide will help you get started with contributing to EngageRunner.

## Getting Started

### Prerequisites

- Python 3.13+
- uv for dependency management
- Playwright browsers (installed via browser-use)
- Git for version control

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/EngageRunner.git
   cd EngageRunner
   ```

3. Install development dependencies:
   ```bash
   uv sync
   uv run playwright install
   ```

4. Install pre-commit hooks (if configured):
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

EngageRunner follows **GitHub Flow** - a simple, branch-based workflow perfect for teams and projects that deploy regularly.

### GitHub Flow Process

1. **Create a branch** from `main` for your feature or bug fix:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

   **Branch naming conventions:**
   - `feature/` - New features
   - `bugfix/` - Bug fixes
   - `hotfix/` - Critical fixes
   - `docs/` - Documentation updates
   - `refactor/` - Code refactoring

2. **Make your changes** following our code style guidelines

3. **Test thoroughly** - ensure all checks pass:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy .
   ```

4. **Commit regularly** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "feat: Add YouTube comment extraction"
   ```

5. **Push your branch** and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub targeting the `main` branch

7. **Collaborate** - respond to feedback and make additional commits as needed

8. **Merge** - once approved, your PR will be merged via squash merge for clean history

### Code Style Guidelines

**Python Code Standards:**
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Use [mypy](https://mypy-lang.org/) for type checking

```bash
uv run ruff check .        # Lint code
uv run ruff format .       # Format code
uv run mypy .             # Type check
```

#### Code Standards
- **Naming Conventions**:
  - Variables/functions: `snake_case`
  - Classes/exceptions: `PascalCase`
  - Constants: `UPPER_CASE`
  - Descriptive, context-rich names

- **Type Annotations**: Use modern Python typing (`dict[str, Any]`, `| None`, union `|` syntax)
- **Error Handling**: Specific exceptions, structured logging, graceful degradation
- **Async Operations**: Use `asyncio.gather()`, proper context managers
- **Documentation**: Comprehensive docstrings for public functions, type hints for all parameters/returns

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: Add Instagram comment reader
fix: Handle YouTube lazy-loaded comments
docs: Update browser profile setup guide
refactor: Extract common platform navigation logic
```

### Testing

Write tests for all new functionality:

```bash
uv run pytest                    # Run all tests
uv run pytest tests/unit/        # Run unit tests only
uv run pytest --cov=src          # Run with coverage report
```

**Testing Requirements:**
- Unit tests for all business logic
- Integration tests for browser automation flows
- Maintain >80% code coverage
- All tests must pass before PR merge

## Submitting Changes

### Pull Request Process

1. Ensure your code passes all checks:
   ```bash
   uv run ruff check .
   uv run mypy .
   uv run pytest
   ```

2. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Open a Pull Request against the main repository's `main` branch

4. Ensure your PR:
   - Has a clear title using conventional commits format
   - Includes a detailed description of changes
   - References any related issues (#123)
   - Passes all CI checks
   - Includes tests for new functionality
   - Updates documentation if needed

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved and all checks pass, your PR will be merged

## Project Architecture

### Key Components
- `src/models/`: Pydantic data models (Comment, EngagementTask, etc.)
- `src/platforms/`: Platform-specific implementations (YouTube, Instagram, TikTok)
- `src/browser/`: Browser automation and profile management
- `src/llm/`: LLM integration for response generation
- `src/utils/`: Shared utilities

### Configuration
- Settings via `config.yaml` or environment variables
- Pydantic models for configuration validation
- Browser profiles for session persistence

### Architecture Principles
- **Modularity**: Platform-specific logic isolated in separate modules
- **Extensibility**: Easy to add new platforms via common interfaces
- **Type Safety**: Strong typing with Pydantic and mypy
- **Async-First**: Use asyncio for all I/O operations

## Common Development Tasks

### Adding a New Platform

1. Create platform module in `src/platforms/`:
   ```python
   from src.models import Comment, Platform
   from src.platforms.base import BasePlatform

   class TikTokPlatform(BasePlatform):
       platform = Platform.TIKTOK

       async def read_comments(self, url: str) -> list[Comment]:
           """TikTok-specific implementation"""
           pass

       async def post_reply(self, comment_id: str, text: str) -> bool:
           """Post a reply to a comment"""
           pass
   ```

2. Register in platform factory
3. Add platform-specific configuration
4. Write tests for new platform
5. Update documentation

### Adding New Features

1. **New LLM Provider**: Implement provider interface with fallback support
2. **New Response Strategy**: Extend response generation logic
3. **Enhanced Comment Filtering**: Add filtering criteria to Comment model
4. **Profile Management**: Extend browser profile configuration

## Security Guidelines

⚠️ **Important Security Practices:**

- **Never commit credentials** - Use environment variables or `.env` files (git-ignored)
- **Validate user input** - Sanitize URLs and user-provided data
- **Rate limiting** - Respect platform rate limits to avoid bans
- **Browser safety** - Run in sandboxed environment when possible
- **Dependency scanning** - Keep dependencies updated for security patches

## Getting Help

- Check existing [Issues](https://github.com/YOUR-USERNAME/EngageRunner/issues)
- Review [README.md](README.md) for project overview
- Review [REQUIREMENTS.md](REQUIREMENTS.md) for technical details
- Ask questions in issue discussions
- Join project discussions

## Code of Conduct

Be respectful and inclusive in all interactions. We want to maintain a welcoming environment for all contributors.

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Recognition

Contributors will be recognized in our changelog and repository. Thank you for helping make EngageRunner better!

## Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Python Packaging Guide](https://packaging.python.org/)
- [browser-use Documentation](https://docs.browser-use.com)

---

**Questions?** Open an issue or discussion on GitHub for contribution-related questions.
