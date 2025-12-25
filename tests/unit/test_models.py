"""Unit tests for data models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from engagerunner.models import ActionType, Comment, EngagementTask, Platform


def test_comment_creation() -> None:
    """Test creating a valid Comment object."""
    comment = Comment(
        id="test123",
        author="test_user",
        text="Great content!",
        timestamp=datetime.now(UTC),
        reply_count=5,
        platform=Platform.YOUTUBE,
    )

    assert comment.id == "test123"
    assert comment.author == "test_user"
    assert comment.platform == Platform.YOUTUBE


def test_comment_validation() -> None:
    """Test Comment validation."""
    with pytest.raises(ValidationError):
        Comment(
            id="test123",
            author="test_user",
            text="Great content!",
            timestamp="invalid_timestamp",  # type: ignore
            platform=Platform.YOUTUBE,
        )


def test_engagement_task_creation() -> None:
    """Test creating an EngagementTask."""
    task = EngagementTask(
        platform=Platform.YOUTUBE,
        video_url="https://youtube.com/watch?v=test",  # type: ignore[arg-type]
        action=ActionType.READ,
        max_comments=10,
    )

    assert task.platform == Platform.YOUTUBE
    assert task.action == ActionType.READ
    assert task.max_comments == 10
    assert task.response_template is None
