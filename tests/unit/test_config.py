"""Unit tests for configuration."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

from engagerunner.config import create_default_config, load_config
from engagerunner.models import Config


def test_create_default_config() -> None:
    """Test creating default configuration."""
    with NamedTemporaryFile(mode="w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        temp_path = Path(f.name)

    try:
        create_default_config(temp_path)
        assert temp_path.exists()

        # Verify file content
        with temp_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "youtube-main" in data["profiles"]
        assert data["llm"]["provider"] == "openrouter"
        assert data["llm"]["model"] == "meta-llama/llama-4-maverick:free"
    finally:
        temp_path.unlink()


def test_load_nonexistent_config() -> None:
    """Test loading config (will use config.yaml if present, otherwise defaults)."""
    config = load_config()
    assert isinstance(config, Config)
    # Should always have openrouter provider
    assert config.llm.provider == "openrouter"
    # Model could be from config.yaml or default - just verify it's a string
    assert isinstance(config.llm.model, str)
    assert len(config.llm.model) > 0
    # This test just verifies config loads successfully
