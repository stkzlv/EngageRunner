"""Configuration models."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source for YAML configuration files."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_file: Path | str | None = None):
        """Initialize YAML settings source.

        Args:
            settings_cls: Settings class to populate
            yaml_file: Path to YAML configuration file
        """
        super().__init__(settings_cls)
        self.yaml_file = Path(yaml_file) if yaml_file else Path("config.yaml")

    def get_field_value(  # noqa: PLR6301
        self, field: Any, field_name: str  # noqa: ARG002
    ) -> tuple[Any, str, bool]:
        """Not used - we load all data at once."""
        return None, "", False

    def __call__(self) -> dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary
        """
        if not self.yaml_file.exists():
            return {}

        with self.yaml_file.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}


class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="LLM_", extra="ignore")

    provider: str = Field(
        default="openrouter",
        description="LLM provider (openrouter, anthropic, or openai)",
    )
    model: str = Field(
        default="meta-llama/llama-4-maverick:free",
        description="Model identifier (use :free suffix for OpenRouter free models)",
    )
    fallback_models: list[str] = Field(
        default_factory=lambda: [
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
        ],
        description="List of fallback models to try if primary model fails",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries per model",
    )
    api_key: str | None = Field(default=None, description="API key (from env if not provided)")
    base_url: str | None = Field(
        default=None,
        description="Custom API base URL (auto-set for OpenRouter if not provided)",
    )


class Settings(BaseSettings):
    """General application settings."""

    model_config = SettingsConfigDict(env_prefix="ENGAGERUNNER_", extra="ignore")

    headless: bool = Field(default=False, description="Run browser in headless mode")
    timeout: int = Field(default=30, description="Default timeout in seconds")


class BrowserProfile(BaseSettings):
    """Browser profile configuration."""

    model_config = SettingsConfigDict(extra="ignore")

    platform: str = Field(..., description="Platform this profile is for")
    chrome_profile_path: Path = Field(..., description="Path to Chrome profile directory")

    # Optional platform-specific metadata
    channel_url: str | None = Field(default=None, description="YouTube channel URL")
    handle: str | None = Field(default=None, description="YouTube handle")
    profile_url: str | None = Field(default=None, description="Instagram/TikTok profile URL")

    # Auto-engagement settings
    auto_react: bool = Field(default=False, description="Automatically react to comments")
    reaction_emoji: str = Field(default="👍", description="Emoji to use for reactions")


class Config(BaseSettings):
    """Main application configuration.

    Config hierarchy (highest to lowest priority):
    1. CLI arguments (passed explicitly when creating instance)
    2. Environment variables (ENGAGERUNNER_*, LLM_*, ANTHROPIC_API_KEY, OPENAI_API_KEY)
    3. YAML config file (config.yaml by default)
    4. Default values
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    profiles: dict[str, BrowserProfile] = Field(
        default_factory=dict, description="Named browser profiles"
    )
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    settings: Settings = Field(default_factory=Settings, description="General settings")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources priority.

        Priority order (highest to lowest):
        1. init_settings (CLI args passed to constructor)
        2. env_settings (environment variables)
        3. dotenv_settings (.env file)
        4. yaml_settings (config.yaml)
        5. Default values in model

        Args:
            settings_cls: Settings class
            init_settings: Values passed to __init__
            env_settings: Environment variables
            dotenv_settings: .env file values
            file_secret_settings: Secrets files (unused)

        Returns:
            Tuple of settings sources in priority order
        """
        yaml_settings = YamlConfigSettingsSource(settings_cls)

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_settings,
        )

    def model_post_init(self, __context: Any, /) -> None:
        """Post-initialization hook to inject API keys and base URLs into LLM config.

        Automatically sets LLM API key from environment variables if not already set.
        Priority: OPENROUTER_API_KEY > ANTHROPIC_API_KEY > OPENAI_API_KEY

        Also auto-configures base_url for OpenRouter if not explicitly set.
        """
        if self.llm.api_key is None:
            api_key = (
                os.getenv("OPENROUTER_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )
            if api_key:
                # Create new LLMConfig with updated api_key and auto-configured base_url
                base_url = self.llm.base_url
                if base_url is None and self.llm.provider == "openrouter":
                    base_url = "https://openrouter.ai/api/v1"

                self.llm = LLMConfig(
                    provider=self.llm.provider,
                    model=self.llm.model,
                    api_key=api_key,
                    base_url=base_url,
                )
