"""Configuration models."""

from pathlib import Path

from pydantic import BaseModel, Field

from engagerunner.models.platform import Platform


class BrowserProfile(BaseModel):
    """Browser profile configuration."""

    platform: Platform = Field(..., description="Platform this profile is for")
    chrome_profile_path: Path = Field(..., description="Path to Chrome profile directory")


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(default="anthropic", description="LLM provider (anthropic or openai)")
    model: str = Field(default="claude-sonnet-4-20250514", description="Model identifier")
    api_key: str | None = Field(default=None, description="API key (from env if not provided)")


class Settings(BaseModel):
    """General application settings."""

    headless: bool = Field(default=False, description="Run browser in headless mode")
    timeout: int = Field(default=30, description="Default timeout in seconds")


class Config(BaseModel):
    """Main application configuration."""

    profiles: dict[str, BrowserProfile] = Field(
        default_factory=dict, description="Named browser profiles"
    )
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    settings: Settings = Field(default_factory=Settings, description="General settings")
