"""Unit tests for YouTube platform logic."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from engagerunner.models import Platform
from engagerunner.platforms.youtube import YouTubePlatform


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.evaluate = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.locator = MagicMock()
    return page


@pytest.fixture
def youtube_platform(mock_page):
    """Create YouTubePlatform with mock page."""
    return YouTubePlatform(page=mock_page)


class TestYouTubePlatform:
    def test_platform_type(self, youtube_platform):
        """Test platform is correctly identified as YouTube."""
        assert youtube_platform.platform == Platform.YOUTUBE

    @pytest.mark.asyncio
    async def test_list_videos_basic(self, youtube_platform, mock_page):
        """Test basic video listing from channel."""
        mock_videos = [
            {
                "title": "Video 1",
                "url": "https://youtube.com/watch?v=1",
                "views": "100",
                "posted": "2 hours ago",
                "type": "video",
            },
            {
                "title": "Video 2",
                "url": "https://youtube.com/watch?v=2",
                "views": "200",
                "posted": "1 day ago",
                "type": "video",
            },
        ]
        mock_page.evaluate.return_value = mock_videos

        videos = await youtube_platform.list_videos("https://youtube.com/@channel", max_videos=10)

        assert len(videos) == 2
        assert videos[0]["title"] == "Video 1"
        assert mock_page.goto.called

    @pytest.mark.asyncio
    async def test_list_videos_filtering_by_days(self, youtube_platform, mock_page):
        """Test filtering videos by days_ago parameter."""
        mock_videos = [
            {
                "title": "New Video",
                "url": "v1",
                "views": "100",
                "posted": "2 hours ago",
                "type": "video",
            },
            {
                "title": "Old Video",
                "url": "v2",
                "views": "200",
                "posted": "1 year ago",
                "type": "video",
            },
        ]
        mock_page.evaluate.return_value = mock_videos

        videos = await youtube_platform.list_videos("channel_url", days_ago=7)

        assert len(videos) == 1
        assert videos[0]["title"] == "New Video"

    @pytest.mark.asyncio
    async def test_read_comments_regular_video(self, youtube_platform, mock_page):
        """Test reading comments from a regular video."""
        mock_comments = [
            {"id": "c1", "author": "User1", "text": "Great video!", "timestamp": "10 minutes ago"},
            {"id": "c2", "author": "User2", "text": "Thanks!", "timestamp": "5 minutes ago"},
        ]
        mock_page.evaluate.return_value = mock_comments

        url = "https://youtube.com/watch?v=abc123"
        comments = await youtube_platform.read_comments(url, max_comments=10)

        assert len(comments) == 2
        assert comments[0].author == "User1"
        assert comments[0].text == "Great video!"
        assert comments[0].platform == Platform.YOUTUBE
        assert isinstance(comments[0].timestamp, datetime)

    @pytest.mark.asyncio
    async def test_read_comments_shorts_fallback(self, youtube_platform, mock_page):
        """Test Shorts URL falls back to watch URL when panel fails."""
        mock_comments = [
            {"id": "c1", "author": "User1", "text": "Nice short!", "timestamp": "1 hour ago"},
        ]

        # First evaluate for Shorts panel check, then for comments
        mock_page.evaluate.return_value = mock_comments

        # Simulate Shorts panel button not found
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator.return_value = mock_locator

        shorts_url = "https://youtube.com/shorts/abc123"
        await youtube_platform.read_comments(shorts_url, max_comments=10)

        # Should have navigated twice: first to shorts, then to watch URL
        assert mock_page.goto.call_count == 2
        # Second call should be to watch URL
        calls = mock_page.goto.call_args_list
        assert "watch?v=abc123" in str(calls[1])

    @pytest.mark.asyncio
    async def test_like_comment_success(self, youtube_platform, mock_page):
        """Test successfully liking a comment."""
        # Mock locator chain
        mock_threads = MagicMock()
        mock_threads.count = AsyncMock(return_value=3)
        mock_thread = MagicMock()
        mock_thread.scroll_into_view_if_needed = AsyncMock()
        mock_threads.nth.return_value = mock_thread

        mock_like_btn = MagicMock()
        mock_like_btn.count = AsyncMock(return_value=1)
        mock_like_btn.click = AsyncMock()
        mock_thread.locator.return_value.first = mock_like_btn

        mock_page.locator.return_value = mock_threads

        result = await youtube_platform.like_comment(1)

        assert result is True
        assert mock_like_btn.click.called

    @pytest.mark.asyncio
    async def test_like_comment_out_of_range(self, youtube_platform, mock_page):
        """Test liking comment with invalid index."""
        mock_threads = MagicMock()
        mock_threads.count = AsyncMock(return_value=2)
        mock_page.locator.return_value = mock_threads

        result = await youtube_platform.like_comment(5)  # Out of range

        assert result is False

    @pytest.mark.asyncio
    async def test_heart_comment_success(self, youtube_platform, mock_page):
        """Test successfully hearting a comment (channel owner action)."""
        # Mock locator chain
        mock_threads = MagicMock()
        mock_threads.count = AsyncMock(return_value=3)
        mock_thread = MagicMock()
        mock_thread.scroll_into_view_if_needed = AsyncMock()
        mock_threads.nth.return_value = mock_thread

        mock_heart_btn = MagicMock()
        mock_heart_btn.count = AsyncMock(return_value=1)
        mock_heart_btn.click = AsyncMock()
        mock_thread.locator.return_value.first = mock_heart_btn

        mock_page.locator.return_value = mock_threads

        result = await youtube_platform.heart_comment(1)

        assert result is True
        assert mock_heart_btn.click.called

    @pytest.mark.asyncio
    async def test_heart_comment_button_not_found(self, youtube_platform, mock_page):
        """Test heart fails when button not found (not channel owner)."""
        mock_threads = MagicMock()
        mock_threads.count = AsyncMock(return_value=2)
        mock_thread = MagicMock()
        mock_thread.scroll_into_view_if_needed = AsyncMock()
        mock_threads.nth.return_value = mock_thread

        # Heart button not found
        mock_heart_btn = MagicMock()
        mock_heart_btn.count = AsyncMock(return_value=0)
        mock_thread.locator.return_value.first = mock_heart_btn

        mock_page.locator.return_value = mock_threads

        result = await youtube_platform.heart_comment(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_post_reply_not_implemented(self, youtube_platform):
        """Test post_reply returns False (Phase 2 feature)."""
        result = await youtube_platform.post_reply("comment_id", "reply text")
        assert result is False

    @pytest.mark.asyncio
    async def test_navigate_to_url(self, youtube_platform, mock_page):
        """Test navigation to URL."""
        url = "https://youtube.com/watch?v=test"
        await youtube_platform.navigate_to_url(url)

        mock_page.goto.assert_called_once()
        call_args = mock_page.goto.call_args
        assert url in str(call_args)
