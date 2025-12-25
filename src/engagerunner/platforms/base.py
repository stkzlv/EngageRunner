"""Base platform interface."""

from abc import ABC, abstractmethod

from browser_use import Browser

from engagerunner.models import Comment, Platform


class BasePlatform(ABC):
    """Base class for platform-specific implementations."""

    platform: Platform

    def __init__(self, browser: Browser) -> None:
        """Initialize platform adapter.

        Args:
            browser: Browser instance to use
        """
        self.browser = browser

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
    async def post_reply(self, comment_id: str, text: str) -> bool:
        """Post a reply to a specific comment.

        Args:
            comment_id: ID of the comment to reply to
            text: Reply text

        Returns:
            True if successful, False otherwise
        """
