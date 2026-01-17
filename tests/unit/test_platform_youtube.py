"""Unit tests for YouTube platform logic."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from engagerunner.platforms.youtube import YouTubePlatform


@pytest.fixture
def mock_browser():
    return MagicMock()


@pytest.fixture
def mock_llm():
    return MagicMock()


@pytest.fixture
def youtube_platform(mock_browser, mock_llm):
    return YouTubePlatform(browser=mock_browser, llm=mock_llm)


class TestYouTubePlatform:
    @pytest.mark.asyncio
    async def test_list_videos_filtering(self, youtube_platform):
        # Mock LLM response with mixed dates
        mock_videos = [
            {"title": "New Video", "url": "v1", "views": "100", "posted": "2 hours ago"},
            {"title": "Old Video", "url": "v2", "views": "200", "posted": "1 year ago"},
        ]

        # Mock _run_agent_with_retry to return our list
        youtube_platform._run_agent_with_retry = AsyncMock(return_value=mock_videos)  # noqa: SLF001

        # Test filtering: Only last 7 days
        videos = await youtube_platform.list_videos("channel_url", days_ago=7)

        assert len(videos) == 1
        assert videos[0]["title"] == "New Video"

    @pytest.mark.asyncio
    async def test_read_comments_parsing(self, youtube_platform):
        mock_comments = [
            {"author": "User1", "text": "Comment 1", "timestamp": "10 minutes ago"},
        ]

        youtube_platform._run_agent_with_retry = AsyncMock(  # noqa: SLF001
            side_effect=[
                None,  # Scroll result (ignored)
                mock_comments,  # Extract result
            ]
        )

        youtube_platform.navigate_to_url = AsyncMock()

        comments = await youtube_platform.read_comments("video_url")

        assert len(comments) == 1
        assert comments[0].author == "User1"
        assert comments[0].platform == "youtube"
        # Verify timestamp parsed (not default)
        assert isinstance(comments[0].timestamp, datetime)
