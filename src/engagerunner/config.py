"""Configuration loading and management."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from engagerunner.models import Config

# Load environment variables
load_dotenv()


def load_config(config_path: Path | str = "config.yaml") -> Config:
    """Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to configuration file

    Returns:
        Config object
    """
    config_file = Path(config_path)

    if config_file.exists():
        with Path(config_file).open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # Override with environment variables if present
    if "llm" in data and (api_key := os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        data["llm"]["api_key"] = api_key

    return Config(**data)


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
        "llm": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
        "settings": {"headless": False, "timeout": 30},
    }

    output_file = Path(output_path)
    with Path(output_file).open("w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
