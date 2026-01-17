"""Integration tests for orchestration logic."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from engagerunner.cli import engage_with_scenario
from engagerunner.models import Comment, Platform


@pytest.mark.asyncio
async def test_engage_with_scenario_flow(mock_config):
    # Mock dependencies
    with (
        patch("engagerunner.cli.load_config", return_value=mock_config),
        patch("engagerunner.cli.ChromeController") as mock_controller_cls,
        patch("engagerunner.cli.create_llm"),
        patch("engagerunner.cli.Browser") as mock_browser_cls,
        patch("engagerunner.cli.YouTubePlatform") as mock_platform_cls,
        patch("engagerunner.cli.RateLimiter") as mock_rate_limiter_cls,
        patch("engagerunner.cli.EngagementState") as mock_state_cls,
    ):
        # Setup Controller
        controller_instance = mock_controller_cls.return_value
        controller_instance.ensure_browser = AsyncMock(return_value="http://localhost:9222")
        controller_instance.cleanup = AsyncMock()

        # Setup Browser
        browser_instance = mock_browser_cls.return_value
        browser_instance.stop = AsyncMock()

        # Setup Rate Limiter
        rate_limiter_instance = mock_rate_limiter_cls.return_value
        rate_limiter_instance.wait_if_needed = AsyncMock()

        # Setup Platform
        platform_instance = mock_platform_cls.return_value
        platform_instance.list_videos = AsyncMock(
            return_value=[{"url": "v1", "title": "Video 1"}, {"url": "v2", "title": "Video 2"}]
        )

        platform_instance.read_comments = AsyncMock(
            return_value=[
                Comment(
                    id="c1",
                    author="a1",
                    text="t1",
                    timestamp=datetime.now(UTC),
                    platform=Platform.YOUTUBE,
                ),
                Comment(
                    id="c2",
                    author="a2",
                    text="t2",
                    timestamp=datetime.now(UTC),
                    platform=Platform.YOUTUBE,
                ),
            ]
        )

        platform_instance.like_comment = AsyncMock(return_value=True)

        # Setup State
        state_instance = mock_state_cls.return_value
        state_instance.is_comment_processed.return_value = False

        # Run
        await engage_with_scenario("test-profile", "test-scenario")

        # Verify interactions
        assert controller_instance.ensure_browser.called
        assert platform_instance.list_videos.called
        assert platform_instance.read_comments.call_count == 2  # 2 videos
        assert platform_instance.like_comment.call_count == 4  # 2 videos * 2 comments
        assert state_instance.save.call_count == 4
        assert controller_instance.cleanup.called
