"""YouTube platform implementation."""

import logging
from typing import Any

from browser_use import Agent

from engagerunner.llm import RetryLLM
from engagerunner.models import Comment, Platform
from engagerunner.platforms.base import BasePlatform

logger = logging.getLogger(__name__)


class YouTubePlatform(BasePlatform):
    """YouTube-specific platform implementation."""

    platform = Platform.YOUTUBE

    async def _run_agent_with_retry(self, task: str) -> Any:
        """Run an agent task with automatic model fallback on errors.

        Args:
            task: Task description for the agent

        Returns:
            Agent result

        Raises:
            Exception: If all models fail
        """
        if not isinstance(self.llm, RetryLLM):
            # Direct LLM without retry support
            agent = Agent(task=task, llm=self.llm, browser=self.browser)  # type: ignore[var-annotated]
            return await agent.run()

        max_retries = self.llm.config.max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(
                    "Agent attempt %d/%d with model index %d",
                    attempt + 1,
                    max_retries,
                    self.llm.current_model_index,
                )
                agent = Agent(task=task, llm=self.llm, browser=self.browser)  # type: ignore[arg-type]
                return await agent.run()
            except Exception as e:
                last_error = e
                logger.warning("Agent failed (attempt %d/%d): %s", attempt + 1, max_retries, e)

                if attempt < max_retries - 1:
                    if not self.llm.try_next_model():
                        logger.exception("No more models available")
                        break
                    logger.info("Retrying with fallback model...")
                    continue

        logger.error("All retry attempts exhausted")
        raise last_error or RuntimeError("Agent execution failed")

    async def list_videos(self, channel_url: str, max_videos: int = 20) -> list[dict[str, Any]]:
        """List videos from a YouTube channel.

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to retrieve

        Returns:
            List of video dictionaries with 'title', 'url', 'views', 'posted'
        """
        logger.info("Listing up to %s videos from %s", max_videos, channel_url)

        # Navigate to channel videos tab
        videos_url = f"{channel_url}/videos"
        await self._run_agent_with_retry(f"Navigate to {videos_url} and wait for videos to load")

        # Extract video information
        result = await self._run_agent_with_retry(
            f"Extract information for the first {max_videos} videos. "
            f"For each video, get: title, URL, view count, and upload date. "
            f"Return as JSON array with objects containing 'title', 'url', 'views', 'posted'."
        )

        # For now, return placeholder - needs proper result parsing
        logger.warning("Video extraction needs proper result parsing")
        logger.info("Agent result: %s", result)

        return []

    async def navigate_to_url(self, url: str) -> None:
        """Navigate to a YouTube video URL.

        Args:
            url: YouTube video URL
        """
        logger.info("Navigating to %s", url)
        await self._run_agent_with_retry(
            f"Navigate to {url} and wait for the page to load completely"
        )

    async def read_comments(self, url: str, max_comments: int = 10) -> list[Comment]:
        """Read comments from a YouTube video.

        Args:
            url: YouTube video URL
            max_comments: Maximum number of comments to retrieve

        Returns:
            List of Comment objects
        """
        logger.info("Reading up to %s comments from %s", max_comments, url)

        # Navigate to video
        await self.navigate_to_url(url)

        # Use browser-use agent to scroll and extract comments
        await self._run_agent_with_retry(
            f"Scroll down to load the comments section. "
            f"Extract the first {max_comments} comments with their author names, "
            f"comment text, and timestamps. Return the data in JSON format."
        )

        # Parse the result and convert to Comment objects
        comments: list[Comment] = []

        # Note: This is a simplified implementation
        # In production, we would parse the actual response from the agent
        # For now, return empty list as placeholder
        logger.warning("Comment extraction needs implementation refinement")

        return comments

    async def react_to_comment(self, comment_text: str, emoji: str = "👍") -> bool:
        """React to a YouTube comment with an emoji.

        Args:
            comment_text: Text of the comment to find and react to
            emoji: Emoji to react with (default: thumbs up)

        Returns:
            True if successful, False otherwise
        """
        logger.info("Reacting to comment with %s", emoji)

        # YouTube supports "Like" button for comments
        # The emoji is just for config - we'll click the like button
        try:
            await self._run_agent_with_retry(
                f'Find the comment that says "{comment_text}" and click the like button on it. '
                f"Look for the thumbs up icon under the comment."
            )
        except Exception:
            logger.exception("Failed to react to comment")
            return False
        else:
            logger.info("Reaction posted successfully")
            return True

    async def post_reply(self, comment_id: str, text: str) -> bool:
        """Post a reply to a YouTube comment.

        Args:
            comment_id: YouTube comment ID
            text: Reply text

        Returns:
            True if successful, False otherwise
        """
        logger.info("Posting reply to comment %s", comment_id)

        try:
            await self._run_agent_with_retry(
                f"Find the comment with ID {comment_id} and post a reply with the text: '{text}'. "
                f"Click the reply button, type the text, and submit."
            )
        except Exception:
            logger.exception("Failed to post reply")
            return False
        else:
            logger.info("Reply posted successfully")
            return True
