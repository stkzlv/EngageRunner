"""Integration tests for orchestration logic."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engagerunner.cli import engage_with_scenario
from engagerunner.models import Comment, Platform


@pytest.mark.asyncio
async def test_engage_with_scenario_flow(mock_config):
    """Test full engagement flow with mocked dependencies."""
    with (
        patch("engagerunner.cli.load_config", return_value=mock_config),
        patch("engagerunner.cli.ChromeController") as mock_controller_cls,
        patch("engagerunner.cli.get_playwright_page") as mock_get_page,
        patch("engagerunner.cli.YouTubePlatform") as mock_platform_cls,
        patch("engagerunner.cli.RateLimiter") as mock_rate_limiter_cls,
        patch("engagerunner.cli.EngagementState") as mock_state_cls,
    ):
        # Setup Controller
        controller_instance = mock_controller_cls.return_value
        controller_instance.ensure_browser = AsyncMock(return_value="http://localhost:9222")
        controller_instance.cleanup = AsyncMock()

        # Setup Playwright page mock
        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_page = MagicMock()
        mock_get_page.return_value = (mock_playwright, mock_browser, mock_page)

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
        platform_instance.heart_comment = AsyncMock(return_value=True)

        # Setup State
        state_instance = mock_state_cls.return_value
        state_instance.is_comment_processed.return_value = False

        # Run
        await engage_with_scenario("test-profile", "test-scenario")

        # Verify interactions
        assert controller_instance.ensure_browser.called
        assert mock_get_page.called
        assert platform_instance.list_videos.called
        assert platform_instance.read_comments.call_count == 2  # 2 videos
        # Action depends on scenario config (like in mock_config)
        assert platform_instance.like_comment.call_count == 4  # 2 videos * 2 comments
        assert state_instance.save.call_count == 4
        assert controller_instance.cleanup.called


@pytest.mark.asyncio
async def test_engage_with_heart_action():
    """Test engagement with heart action (channel owner)."""
    mock_config = MagicMock()
    mock_config.profiles = {"test-profile": MagicMock(channel_url="https://youtube.com/@test")}
    mock_config.scenarios = {
        "heart-scenario": MagicMock(
            discovery=MagicMock(method="recent_posts", limit=1),
            actions=[MagicMock(type="heart")],  # Heart action
            max_comments_per_video=1,
        )
    }

    with (
        patch("engagerunner.cli.load_config", return_value=mock_config),
        patch("engagerunner.cli.ChromeController") as mock_controller_cls,
        patch("engagerunner.cli.get_playwright_page") as mock_get_page,
        patch("engagerunner.cli.YouTubePlatform") as mock_platform_cls,
        patch("engagerunner.cli.RateLimiter") as mock_rate_limiter_cls,
        patch("engagerunner.cli.EngagementState") as mock_state_cls,
    ):
        # Setup mocks
        controller_instance = mock_controller_cls.return_value
        controller_instance.ensure_browser = AsyncMock(return_value="http://localhost:9222")
        controller_instance.cleanup = AsyncMock()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_get_page.return_value = (mock_playwright, mock_browser, MagicMock())

        rate_limiter_instance = mock_rate_limiter_cls.return_value
        rate_limiter_instance.wait_if_needed = AsyncMock()

        platform_instance = mock_platform_cls.return_value
        platform_instance.list_videos = AsyncMock(return_value=[{"url": "v1", "title": "Video"}])
        platform_instance.read_comments = AsyncMock(
            return_value=[
                Comment(
                    id="c1",
                    author="user",
                    text="comment",
                    timestamp=datetime.now(UTC),
                    platform=Platform.YOUTUBE,
                )
            ]
        )
        platform_instance.heart_comment = AsyncMock(return_value=True)
        platform_instance.like_comment = AsyncMock(return_value=True)

        state_instance = mock_state_cls.return_value
        state_instance.is_comment_processed.return_value = False

        # Run
        await engage_with_scenario("test-profile", "heart-scenario")

        # Verify heart was called, not like
        assert platform_instance.heart_comment.call_count == 1
        assert platform_instance.like_comment.call_count == 0


@pytest.mark.asyncio
async def test_engage_dry_run_no_actions(mock_config):
    """Test dry run mode doesn't execute actual actions."""
    with (
        patch("engagerunner.cli.load_config", return_value=mock_config),
        patch("engagerunner.cli.ChromeController") as mock_controller_cls,
        patch("engagerunner.cli.get_playwright_page") as mock_get_page,
        patch("engagerunner.cli.YouTubePlatform") as mock_platform_cls,
        patch("engagerunner.cli.RateLimiter"),
        patch("engagerunner.cli.EngagementState") as mock_state_cls,
    ):
        controller_instance = mock_controller_cls.return_value
        controller_instance.ensure_browser = AsyncMock(return_value="http://localhost:9222")
        controller_instance.cleanup = AsyncMock()

        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_get_page.return_value = (mock_playwright, mock_browser, MagicMock())

        platform_instance = mock_platform_cls.return_value
        platform_instance.list_videos = AsyncMock(return_value=[{"url": "v1", "title": "Video"}])
        platform_instance.read_comments = AsyncMock(
            return_value=[
                Comment(
                    id="c1",
                    author="user",
                    text="comment",
                    timestamp=datetime.now(UTC),
                    platform=Platform.YOUTUBE,
                )
            ]
        )
        platform_instance.like_comment = AsyncMock(return_value=True)

        state_instance = mock_state_cls.return_value
        state_instance.is_comment_processed.return_value = False

        # Run in dry-run mode
        await engage_with_scenario("test-profile", "test-scenario", dry_run=True)

        # Verify no actual actions were taken
        assert platform_instance.like_comment.call_count == 0
        assert state_instance.save.call_count == 0
