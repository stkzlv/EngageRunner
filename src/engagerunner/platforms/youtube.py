"YouTube platform implementation."

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from browser_use import Agent

from engagerunner.llm import RetryLLM
from engagerunner.models import Comment, Platform
from engagerunner.platforms.base import BasePlatform
from engagerunner.utils.time_parser import parse_relative_time

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

    async def list_videos(  # noqa: PLR0912
        self,
        channel_url: str,
        max_videos: int = 20,
        days_ago: int | None = None,
    ) -> list[dict[str, Any]]:
        """List videos from a YouTube channel.

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to retrieve
            days_ago: If provided, only return videos from last N days

        Returns:
            List of video dictionaries with 'title', 'url', 'views', 'posted', 'url'
        """
        logger.info("Listing up to %s videos from %s", max_videos, channel_url)

        # Navigate to channel videos tab
        videos_url = f"{channel_url}/videos"
        await self._run_agent_with_retry(
            f"Navigate to {videos_url} and scroll down to load at least {max_videos} videos"
        )

        # Build extraction task
        task = (
            f"Extract the first {max_videos} video elements from this YouTube channel page. "
            f"For each video, find and extract:\n"
            f"- title: The video title text\n"
            f"- url: The full video URL (starts with https://www.youtube.com/watch?v=)\n"
            f"- views: View count as text (e.g., '1.2M views')\n"
            f"- posted: When it was posted (e.g., '2 days ago', '1 week ago')\n\n"
            f"IMPORTANT: Return ONLY a valid JSON array. Each object must have all 4 fields.\n"
            f"Example: [{{'title':'...','url':'https://...','views':'...','posted':'...'}}]\n"
        )

        # Extract video information
        result = await self._run_agent_with_retry(task)

        # Handle browser-use AgentHistoryList return type
        if hasattr(result, "final_result") and result.final_result():
            result = result.final_result()
        elif hasattr(result, "history") and result.history:
            # Fallback to last history message if available
            result = result.history[-1].result

        # Parse the result
        videos: list[dict[str, Any]] = []
        try:
            if isinstance(result, str):
                # Try to extract JSON from the response
                start = result.find("[")
                end = result.rfind("]") + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    videos = json.loads(json_str)
                else:
                    logger.warning("No JSON array found in result: %s", result[:200])
                    return []
            elif isinstance(result, list):
                videos = result
            else:
                logger.warning("Unexpected result type: %s", type(result))
                return []
        except json.JSONDecodeError:
            logger.exception("Failed to parse video list as JSON: %s", result[:200])
            return []
        except Exception:
            logger.exception("Unexpected error parsing videos")
            return []

        # Filter by date if requested using Python logic (not LLM)
        if days_ago:
            cutoff_date = datetime.now(UTC) - timedelta(days=days_ago)
            filtered_videos = []

            for video in videos:
                posted_str = video.get("posted", "")
                try:
                    posted_date = parse_relative_time(posted_str)
                    if posted_date >= cutoff_date:
                        filtered_videos.append(video)
                    else:
                        logger.debug("Skipping old video: %s (%s)", video.get("title"), posted_str)
                except Exception:
                    logger.warning("Could not parse date for video: %s", posted_str)
                    # Include it just in case if date parsing fails? No, safer to exclude.
                    continue

            logger.info("Filtered %d videos based on %d days limit", len(videos), days_ago)
            videos = filtered_videos

        logger.info("Extracted %d videos", len(videos))
        return videos

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

        # Scroll to load comments
        await self._run_agent_with_retry(
            "Scroll down to the comments section and wait for comments to load. "
            "Scroll a few more times to load more comments."
        )

        # Extract comments
        task = (
            f"Extract the first {max_comments} comments from the YouTube video. "
            f"For each comment, get:\n"
            f"- author: The username who posted the comment\n"
            f"- text: The full comment text\n"
            f"- timestamp: When it was posted (e.g., '2 hours ago', '1 day ago')\n\n"
            f"IMPORTANT: Return ONLY a valid JSON array. Each object must have all 3 fields.\n"
            f"Example: [{{'author':'...','text':'...','timestamp':'...'}}]\n"
        )

        result = await self._run_agent_with_retry(task)

        # Handle browser-use AgentHistoryList return type
        if hasattr(result, "final_result") and result.final_result():
            result = result.final_result()
        elif hasattr(result, "history") and result.history:
            result = result.history[-1].result

        # Parse the result
        comment_data = []
        try:
            if isinstance(result, str):
                start = result.find("[")
                end = result.rfind("]") + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    comment_data = json.loads(json_str)
                else:
                    logger.warning("No JSON array found in result: %s", result[:200])
                    return []
            elif isinstance(result, list):
                comment_data = result
            else:
                logger.warning("Unexpected result type: %s", type(result))
                return []
        except json.JSONDecodeError:
            logger.exception("Failed to parse comments as JSON: %s", result[:200])
            return []
        except Exception:
            logger.exception("Unexpected error parsing comments")
            return []

        # Convert to Comment objects with real timestamps
        comments = []
        for i, c in enumerate(comment_data):
            try:
                timestamp_str = c.get("timestamp", "0 seconds ago")
                timestamp = parse_relative_time(timestamp_str)

                # Generate a semi-stable ID if possible, or fallback
                # TODO(@user): Extract real comment ID from DOM in future (FIX002, TD003)
                comment_id = f"comment_{i}_{hash(c.get('text', ''))}"

                comments.append(
                    Comment(
                        id=comment_id,
                        author=c.get("author", "Unknown"),
                        text=c.get("text", ""),
                        timestamp=timestamp,
                        platform=Platform.YOUTUBE,
                        url=url,
                    )
                )
            except Exception:
                logger.exception("Error creating comment object")
                continue

        logger.info("Extracted %d comments", len(comments))
        return comments

    async def like_comment(self, comment_index: int = 1) -> bool:
        """Like a YouTube comment by its position.

        Args:
            comment_index: Position of the comment (1-based, 1=first comment)

        Returns:
            True if successful, False otherwise
        """
        logger.info("Liking comment at position %d", comment_index)

        # YouTube "Like" button for comments
        try:
            await self._run_agent_with_retry(
                f"Find the comment number {comment_index} (counting from the top) "
                f"and click the thumbs up (like) button on it. "
                f"The like button is usually on the left side below the comment text."
            )
        except Exception:
            logger.exception("Failed to like comment %d", comment_index)
            return False

        logger.info("Successfully liked comment %d", comment_index)
        return True

    async def post_reply(self, comment_id: str, text: str) -> bool:
        """Post a reply to a YouTube comment.

        Args:
            comment_id: YouTube comment ID (currently unused, relies on context)
            text: Reply text

        Returns:
            True if successful, False otherwise
        """
        logger.info("Posting reply to comment %s", comment_id)

        try:
            await self._run_agent_with_retry(
                f"Find the comment associated with this ID (or the one we just focused on) "
                f"and post a reply with the text: '{text}'. "
                f"Click the reply button, type the text, and submit."
            )
        except Exception:
            logger.exception("Failed to post reply")
            return False
        else:
            logger.info("Reply posted successfully")
            return True
