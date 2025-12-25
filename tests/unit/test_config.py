"""Unit tests for configuration."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from engagerunner.config import create_default_config, load_config
from engagerunner.models import Config


def test_create_default_config() -> None:
    """Test creating default configuration."""
    with NamedTemporaryFile(mode="w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        temp_path = Path(f.name)

    try:
        create_default_config(temp_path)
        assert temp_path.exists()

        config = load_config(temp_path)
        assert isinstance(config, Config)
        assert "youtube-main" in config.profiles
        assert config.llm.provider == "anthropic"
    finally:
        temp_path.unlink()


def test_load_nonexistent_config() -> None:
    """Test loading config when file doesn't exist."""
    config = load_config("nonexistent.yaml")
    assert isinstance(config, Config)
    assert len(config.profiles) == 0
