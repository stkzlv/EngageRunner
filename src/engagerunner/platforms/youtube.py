"""YouTube platform implementation using direct Playwright automation."""

import asyncio
import logging
import re
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from engagerunner.models import Comment, Platform
from engagerunner.platforms.base import BasePlatform
from engagerunner.utils.time_parser import parse_relative_time

logger = logging.getLogger(__name__)

# YouTube CSS selectors
SELECTORS = {
    # Channel videos/shorts page
    "video_item": "ytd-rich-item-renderer",
    # Comments section
    "comments_section": "ytd-comments",
    "comment_thread": "ytd-comment-thread-renderer",
    "comment_author": "#author-text",
    "comment_text": "#content-text",
    "comment_timestamp": ".published-time-text a, #published-time-text",
    "comment_like_button": "#like-button button, ytd-toggle-button-renderer#like-button button",
    # Alternative selectors for different YouTube layouts
    "comment_like_aria": '[aria-label*="like" i]',
}

# Timeouts in milliseconds
NAVIGATION_TIMEOUT = 30000
SCROLL_PAUSE = 1500
ELEMENT_TIMEOUT = 5000


class YouTubePlatform(BasePlatform):
    """YouTube-specific platform implementation using direct Playwright."""

    platform = Platform.YOUTUBE

    def __init__(self, page: Page) -> None:
        """Initialize YouTube platform.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)
        self._current_comments: list[dict[str, Any]] = []
        self._is_short: bool = False

    async def _scroll_page(self, times: int = 3) -> None:
        """Scroll the page to load dynamic content.

        Args:
            times: Number of scroll iterations
        """
        for i in range(times):
            await self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            await asyncio.sleep(SCROLL_PAUSE / 1000)
            logger.debug("Scroll %d/%d complete", i + 1, times)

    async def _wait_for_selector(self, selector: str, wait_timeout: int = ELEMENT_TIMEOUT) -> bool:
        """Wait for a selector to appear.

        Args:
            selector: CSS selector
            wait_timeout: Timeout in milliseconds

        Returns:
            True if element found, False otherwise
        """
        try:
            await self.page.wait_for_selector(selector, timeout=wait_timeout)
        except PlaywrightTimeout:
            logger.debug("Selector not found: %s", selector)
            return False
        else:
            return True

    async def list_videos(
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
            List of video dictionaries with 'title', 'url', 'views', 'posted'
        """
        videos_url = f"{channel_url.rstrip('/')}/videos"
        logger.info("Navigating to %s", videos_url)

        await self.page.goto(videos_url, timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
        await asyncio.sleep(2)  # Wait for YouTube SPA to stabilize
        await self._wait_for_selector(SELECTORS["video_item"])

        # Scroll to load more videos
        scroll_times = max(3, max_videos // 10)
        await self._scroll_page(scroll_times)

        # Extract video data using JavaScript (handles both regular videos and Shorts)
        videos = await self.page.evaluate(
            """(maxVideos) => {
            const items = document.querySelectorAll('ytd-rich-item-renderer');
            const videos = [];

            for (let i = 0; i < Math.min(items.length, maxVideos); i++) {
                const item = items[i];
                const html = item.innerHTML;

                // Check for Shorts
                const shortsLink = item.querySelector('a[href*="/shorts/"]');
                if (shortsLink) {
                    const href = shortsLink.getAttribute('href') || '';
                    const titleEl = item.querySelector('span.yt-core-attributed-string');
                    videos.push({
                        title: titleEl?.textContent?.trim() || 'Short',
                        url: 'https://www.youtube.com' + href,
                        views: '',
                        posted: '',
                        type: 'short'
                    });
                    continue;
                }

                // Check for regular videos
                const videoLink = item.querySelector('#video-title, a[href*="/watch?v="]');
                if (videoLink) {
                    const href = videoLink.getAttribute('href') || '';
                    const metaSpans = item.querySelectorAll('#metadata-line span');
                    videos.push({
                        title: videoLink.textContent?.trim() || '',
                        url: href.startsWith('http') ? href : 'https://www.youtube.com' + href,
                        views: metaSpans[0]?.textContent?.trim() || '',
                        posted: metaSpans[1]?.textContent?.trim() || '',
                        type: 'video'
                    });
                }
            }
            return videos;
        }""",
            max_videos,
        )

        logger.info("Extracted %d videos", len(videos))

        # Filter by date if requested
        if days_ago and videos:
            cutoff_date = datetime.now(UTC) - timedelta(days=days_ago)
            filtered = []

            for video in videos:
                posted_str = video.get("posted", "")
                try:
                    posted_date = parse_relative_time(posted_str)
                    if posted_date >= cutoff_date:
                        filtered.append(video)
                    else:
                        title = video.get("title", "")[:30]
                        logger.debug("Skipping old video: %s (%s)", title, posted_str)
                except Exception:
                    logger.warning("Could not parse date: %s", posted_str)

            logger.info("Filtered to %d videos (last %d days)", len(filtered), days_ago)
            videos = filtered

        return cast("list[dict[str, Any]]", videos)

    async def navigate_to_url(self, url: str) -> None:
        """Navigate to a YouTube video URL.

        Args:
            url: YouTube video URL
        """
        logger.info("Navigating to %s", url)
        await self.page.goto(url, timeout=NAVIGATION_TIMEOUT)

    async def _open_shorts_comments(self) -> bool:
        """Open the comments panel for a YouTube Short.

        Returns:
            True if panel opened successfully, False otherwise
        """
        try:
            comments_btn = self.page.locator('button[aria-label="View comments"]')
            if await comments_btn.count() > 0:
                await comments_btn.first.click()
                await asyncio.sleep(2)
                # Wait for panel to open
                panel_sel = '[target-id="engagement-panel-comments-section"]'
                await self._wait_for_selector(panel_sel, wait_timeout=5000)
                return True
        except Exception:
            logger.debug("Failed to open Shorts comments panel")
        return False

    async def read_comments(self, url: str, max_comments: int = 10) -> list[Comment]:
        """Read comments from a YouTube video or Short.

        Args:
            url: YouTube video URL
            max_comments: Maximum number of comments to retrieve

        Returns:
            List of Comment objects
        """
        logger.info("Reading comments from %s", url)
        is_short = "/shorts/" in url
        self._is_short = is_short

        # Navigate to video
        await self.navigate_to_url(url)

        if is_short:
            # Shorts: open comments panel
            if not await self._open_shorts_comments():
                logger.warning("Could not open Shorts comments panel")
                return []
            await asyncio.sleep(1)
        else:
            # Regular video: scroll to load comments
            await self._scroll_page(2)
            await self._wait_for_selector(SELECTORS["comments_section"], wait_timeout=10000)
            await self._scroll_page(max(2, max_comments // 5))

        # Extract comment data using JavaScript
        # For Shorts, look inside the engagement panel; for regular videos, the whole page
        comment_data = await self.page.evaluate(
            """(args) => {
            const { maxComments, isShort } = args;

            // For Shorts, scope to the comments panel
            let container = document;
            if (isShort) {
                const sel = '[target-id="engagement-panel-comments-section"]';
                const panel = document.querySelector(sel);
                if (panel) container = panel;
            }

            const threads = container.querySelectorAll('ytd-comment-thread-renderer');
            const comments = [];

            for (let i = 0; i < Math.min(threads.length, maxComments); i++) {
                const thread = threads[i];
                const authorEl = thread.querySelector('#author-text');
                const textEl = thread.querySelector('#content-text');
                const timeEl = thread.querySelector('.published-time-text a, #published-time-text');
                const commentId = thread.getAttribute('id') || `comment_${i}`;

                comments.push({
                    id: commentId,
                    author: authorEl?.textContent?.trim() || 'Unknown',
                    text: textEl?.textContent?.trim() || '',
                    timestamp: timeEl?.textContent?.trim() || ''
                });
            }
            return comments;
        }""",
            {"maxComments": max_comments, "isShort": is_short},
        )

        # Store for later reference (like_comment uses position)
        self._current_comments = comment_data

        # Convert to Comment objects
        comments = []
        for i, c in enumerate(comment_data):
            try:
                timestamp_str = c.get("timestamp", "0 seconds ago")
                # Clean up timestamp (remove "edited" suffix if present)
                timestamp_str = re.sub(r"\s*\(edited\)\s*", "", timestamp_str)
                timestamp = parse_relative_time(timestamp_str)

                comment_id = c.get("id", f"comment_{i}_{hash(c.get('text', ''))}")

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
                logger.exception("Error creating comment object for index %d", i)

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

        try:
            # For Shorts, scope to the comments panel
            if self._is_short:
                panel_sel = '[target-id="engagement-panel-comments-section"]'
                thread_sel = f"{panel_sel} {SELECTORS['comment_thread']}"
            else:
                thread_sel = SELECTORS["comment_thread"]

            threads = self.page.locator(thread_sel)
            thread_count = await threads.count()

            if comment_index < 1 or comment_index > thread_count:
                logger.error("Comment index %d out of range (1-%d)", comment_index, thread_count)
                return False

            thread = threads.nth(comment_index - 1)

            # Scroll element into view
            await thread.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)

            # Find and click the like button within this comment
            like_button = thread.locator(SELECTORS["comment_like_button"]).first

            if await like_button.count() == 0:
                # Try alternative selector
                like_button = thread.locator(SELECTORS["comment_like_aria"]).first

            if await like_button.count() == 0:
                logger.error("Like button not found for comment %d", comment_index)
                return False

            await like_button.click()
            logger.info("Successfully liked comment %d", comment_index)
        except Exception:
            logger.exception("Failed to like comment %d", comment_index)
            return False
        else:
            return True

    async def post_reply(  # noqa: PLR6301
        self,
        comment_id: str,  # noqa: ARG002
        text: str,  # noqa: ARG002
    ) -> bool:
        """Post a reply to a YouTube comment.

        Note: This is a Phase 2 feature, not implemented in MVP.

        Args:
            comment_id: YouTube comment ID
            text: Reply text

        Returns:
            True if successful, False otherwise
        """
        logger.warning("post_reply is not implemented in MVP (requires LLM for Phase 2)")
        return False
