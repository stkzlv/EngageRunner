"""Engagement task model."""

from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field, HttpUrl

from engagerunner.models.platform import Platform


class ActionType(StrEnum):
    """Types of engagement actions."""

    READ = "read"
    RESPOND = "respond"


class EngagementTask(BaseModel):
    """Defines an engagement task to be performed."""

    platform: Platform = Field(..., description="Target platform")
    video_url: HttpUrl = Field(..., description="URL of the video/post to engage with")
    action: ActionType = Field(..., description="Action to perform")
    response_template: str | None = Field(
        default=None, description="Template for responses (if action is respond)"
    )
    max_comments: int = Field(default=10, description="Maximum number of comments to process")

    class Config:
        """Pydantic configuration."""

        json_schema_extra: ClassVar[dict[str, dict[str, str | int | None]]] = {
            "example": {
                "platform": "youtube",
                "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "action": "read",
                "response_template": None,
                "max_comments": 10,
            }
        }
