"""Configuration loading and management."""

from pathlib import Path

import yaml

from engagerunner.models import Config


def load_config() -> Config:
    """Load configuration using Pydantic Settings.

    Loads config with the following priority (highest to lowest):
    1. Explicitly passed values (CLI args via init)
    2. Environment variables (ENGAGERUNNER_*, LLM_*, ANTHROPIC_API_KEY, OPENAI_API_KEY)
    3. .env file
    4. YAML config file (config.yaml)
    5. Default values

    Returns:
        Config object with merged settings from all sources
    """
    # Config will automatically load from env vars, .env file, and YAML
    return Config()


def create_default_config(output_path: Path | str = "config.yaml") -> None:
    """Create a default configuration file.

    Args:
        output_path: Where to save the config file
    """
    default_config = {
        "profiles": {
            "youtube-main": {
                "platform": "youtube",
                "chrome_profile_path": "~/.config/google-chrome/Profile1",
            }
        },
        "llm": {
            "provider": "openrouter",
            "model": "meta-llama/llama-4-maverick:free",
        },
        "settings": {"headless": False, "timeout": 30},
    }

    output_file = Path(output_path)
    with output_file.open("w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
