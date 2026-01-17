# EngageRunner

Local automation tool for YouTube channel engagement. Likes and hearts comments on your videos using your existing Chrome profile.

## Features

- **Heart comments** - Channel owner's "thank you" badge (default action)
- **Like comments** - Standard thumbs-up (optional)
- **YouTube Shorts support** - Automatic fallback for Shorts comment panels
- **Rate limiting** - Randomized delays to avoid detection
- **State tracking** - Never processes the same comment twice
- **Dry-run mode** - Preview actions without executing

## Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Chrome browser with your YouTube account logged in

### Installation

```bash
git clone https://github.com/stkzlv/EngageRunner.git
cd EngageRunner
uv sync
uv run playwright install chromium
```

### Setup Chrome Profile

Chrome 136+ requires a separate profile directory for remote debugging:

```bash
# One-time setup: copy your Chrome profile
mkdir -p ~/.engagerunner/chrome-profile
cp -r ~/.config/google-chrome/Default ~/.engagerunner/chrome-profile/

# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.engagerunner/chrome-profile
```

### Usage

```bash
# List recent videos from your channel
uv run engagerunner list-videos --max 10

# Read comments from a video
uv run engagerunner read "https://youtube.com/watch?v=VIDEO_ID" --max 20

# Engage with comments (heart them)
uv run engagerunner engage -s simple_engagement

# Preview without taking action
uv run engagerunner engage -s simple_engagement --dry-run
```

## Configuration

Edit `config.yaml`:

```yaml
profiles:
  youtube-main:
    platform: youtube
    channel_url: https://www.youtube.com/@YourChannel

scenarios:
  simple_engagement:
    discovery:
      method: recent_days
      limit: 7
    actions:
      - type: heart  # or "like"
    max_comments_per_video: 10
```

## Documentation

- [Requirements](REQUIREMENTS.md) - MVP scope and success criteria
- [Contributing](CONTRIBUTING.md) - Development workflow
- [Versioning](VERSIONING.md) - Release process

## License

MIT
