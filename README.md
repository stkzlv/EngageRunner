# EngageRunner

AI-powered agent for social media engagement automation using browser-use library. Automates reading and responding to comments on YouTube (with Instagram and TikTok planned).

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Description

EngageRunner is a Python-based automation tool that uses AI agents to interact with social media platforms. It leverages the browser-use library for realistic browser automation and supports multiple LLM providers (Claude, GPT) for intelligent comment responses.

**Current Status:** v0.1.0 - YouTube comment reading (first iteration)

## Features

### Current (v0.1.0)
- ✅ YouTube comment extraction with metadata (author, text, timestamp)
- ✅ Browser profile management with session persistence
- ✅ CLI interface for command-line operation
- ✅ Configurable LLM provider support (Claude/GPT)

### Planned
- 🔄 Automated comment responses (template and LLM-generated)
- 🔄 Instagram and TikTok platform support
- 🔄 Multi-account management
- 🔄 Sentiment analysis and filtering
- 🔄 Response scheduling and rate limiting

## Installation

### Prerequisites
- Python 3.13+
- uv (package manager)
- Chrome browser with saved login sessions

### Steps

1. Clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/EngageRunner.git
cd EngageRunner
```

2. Install dependencies:
```bash
uv sync
uv run playwright install
```

3. Create configuration file:
```bash
uv run engagerunner init
```

4. Set up environment variables:
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

## Usage

### Initialize Configuration

Create a default `config.yaml`:
```bash
uv run engagerunner init
```

### Read Comments

Extract comments from a YouTube video:
```bash
uv run engagerunner read "https://youtube.com/watch?v=VIDEO_ID" --max 20
```

### CLI Options

```bash
# Read comments with custom profile
uv run engagerunner read URL --profile youtube-main --max 10

# Show version
uv run engagerunner --version

# Help
uv run engagerunner --help
```

## Configuration

Edit `config.yaml` to customize settings:

```yaml
profiles:
  youtube-main:
    platform: youtube
    chrome_profile_path: ~/.config/google-chrome/Profile1

llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  # API key loaded from ANTHROPIC_API_KEY env var

settings:
  headless: false  # Set to true for headless operation
  timeout: 30
```

### Browser Profile Setup

1. Open Chrome with a specific profile
2. Log in to YouTube and save credentials
3. Find profile path:
   - Linux: `~/.config/google-chrome/Profile X`
   - macOS: `~/Library/Application Support/Google/Chrome/Profile X`
   - Windows: `%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Profile X`
4. Update `chrome_profile_path` in config

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, workflow, and guidelines.

Quick start:
```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Lint code
uv run ruff check .
uv run mypy .
```

## Deployment

Not yet applicable - this is a local automation tool. See [VERSIONING.md](VERSIONING.md) for release roadmap.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Resources

- [Documentation](docs/) (coming soon)
- [Requirements](REQUIREMENTS.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Versioning Strategy](VERSIONING.md)
- [browser-use Documentation](https://docs.browser-use.com)
