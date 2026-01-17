"""Comment data model."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from engagerunner.models.platform import Platform


class Comment(BaseModel):
    """Represents a social media comment."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "UgxKREPPE9JmPKmqPsB4AaABAg",
                "author": "example_user",
                "text": "Great video!",
                "timestamp": "2025-01-15T10:30:00Z",
                "reply_count": 3,
                "platform": "youtube",
                "url": "https://youtube.com/watch?v=example#comment-123",
            }
        }
    )

    id: str = Field(..., description="Unique identifier for the comment")
    author: str = Field(..., description="Username of the comment author")
    text: str = Field(..., description="Comment text content")
    timestamp: datetime = Field(..., description="When the comment was posted")
    reply_count: int = Field(default=0, description="Number of replies to this comment")
    platform: Platform = Field(..., description="Platform where the comment was posted")
    url: str | None = Field(default=None, description="URL to the comment")
