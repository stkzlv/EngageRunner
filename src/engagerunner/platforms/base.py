"""Base platform interface."""

from abc import ABC, abstractmethod

from playwright.async_api import Page

from engagerunner.models import Comment, Platform


class BasePlatform(ABC):
    """Base class for platform-specific implementations.

    Uses direct Playwright automation for MVP actions (no LLM required).
    """

    platform: Platform

    def __init__(self, page: Page) -> None:
        """Initialize platform adapter.

        Args:
            page: Playwright Page instance connected via CDP
        """
        self.page = page

    @abstractmethod
    async def list_videos(
        self, channel_url: str, max_videos: int = 20, days_ago: int | None = None
    ) -> list[dict[str, str]]:
        """List videos from a channel.

        Args:
            channel_url: Channel URL
            max_videos: Maximum number of videos to retrieve
            days_ago: If provided, only return videos from last N days

        Returns:
            List of video dictionaries with 'title', 'url', 'views', 'posted'
        """

    @abstractmethod
    async def navigate_to_url(self, url: str) -> None:
        """Navigate to the specified URL.

        Args:
            url: URL to navigate to
        """

    @abstractmethod
    async def read_comments(self, url: str, max_comments: int = 10) -> list[Comment]:
        """Read comments from a post/video.

        Args:
            url: URL of the post/video
            max_comments: Maximum number of comments to retrieve

        Returns:
            List of Comment objects
        """

    @abstractmethod
    async def like_comment(self, comment_index: int = 1) -> bool:
        """Like a comment by its position.

        Args:
            comment_index: Position of the comment (1-based)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def heart_comment(self, comment_index: int = 1) -> bool:
        """Heart a comment (channel owner only).

        Args:
            comment_index: Position of the comment (1-based)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def post_reply(self, comment_id: str, text: str) -> bool:
        """Post a reply to a specific comment.

        Args:
            comment_id: ID of the comment to reply to
            text: Reply text

        Returns:
            True if successful, False otherwise
        """
