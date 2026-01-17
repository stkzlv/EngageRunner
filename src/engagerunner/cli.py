"""Command-line interface for EngageRunner."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from playwright.async_api import async_playwright

from engagerunner import __version__

if TYPE_CHECKING:
    from playwright.async_api import Browser, Page, Playwright
from engagerunner.browser.controller import ChromeController
from engagerunner.config import create_default_config, load_config
from engagerunner.models import ActionType, DiscoveryMethod, EngagementTask, Platform, Scenario
from engagerunner.platforms import YouTubePlatform
from engagerunner.utils.safety import RateLimiter
from engagerunner.utils.state import EngagementState

logger = logging.getLogger(__name__)


async def get_playwright_page(
    cdp_url: str,
) -> tuple[Playwright, Browser, Page]:
    """Connect Playwright to Chrome via CDP and return a page.

    Args:
        cdp_url: Chrome DevTools Protocol URL (e.g., http://localhost:9222)

    Returns:
        Tuple of (playwright, browser, page)
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp(cdp_url)

    # Get existing page or create new one
    if browser.contexts and browser.contexts[0].pages:
        page = browser.contexts[0].pages[0]
    else:
        context = await browser.new_context()
        page = await context.new_page()

    return playwright, browser, page


async def list_channel_videos(profile_name: str, max_videos: int) -> None:
    """List videos from a channel.

    Args:
        profile_name: Browser profile to use
        max_videos: Maximum number of videos to list
    """
    config = load_config()

    if profile_name not in config.profiles:
        logger.error("Profile '%s' not found in config", profile_name)
        sys.exit(1)

    profile = config.profiles[profile_name]

    if not profile.channel_url:
        logger.error("Profile '%s' does not have a channel_url configured", profile_name)
        sys.exit(1)

    controller = ChromeController()
    playwright = None
    browser = None

    try:
        cdp_url = await controller.ensure_browser()
        playwright, browser, page = await get_playwright_page(cdp_url)
        platform = YouTubePlatform(page)

        logger.info("Fetching videos from %s", profile.channel_url)
        videos = await platform.list_videos(profile.channel_url, max_videos)

        if videos:
            print(f"\nFound {len(videos)} videos:")
            for i, video in enumerate(videos, 1):
                print(f"\n{i}. {video.get('title', 'Unknown title')}")
                print(f"   URL: {video.get('url', 'N/A')}")
                print(f"   Views: {video.get('views', 'N/A')}")
                print(f"   Posted: {video.get('posted', 'N/A')}")
        else:
            print("No videos found")

    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        await controller.cleanup()


def _get_discovery_params(discovery: DiscoveryMethod) -> tuple[int, int | None]:
    """Get video discovery parameters from scenario.

    Args:
        discovery: Discovery method configuration

    Returns:
        Tuple of (max_videos, days_ago)
    """
    days_ago = None
    max_videos = discovery.limit

    if discovery.method == "recent_days":
        days_ago = discovery.limit
        max_videos = 100  # Get many, filter by date
    elif discovery.method == "all_posts":
        max_videos = 999  # Get all available

    return max_videos, days_ago


async def _process_video_comments(  # noqa: PLR0913, PLR0917
    platform: YouTubePlatform,
    video: dict[str, Any],
    scenario: Scenario,
    video_idx: int,
    total_videos: int,
    rate_limiter: RateLimiter,
    state: EngagementState,
    *,
    dry_run: bool = False,
) -> int:
    """Process comments for a single video.

    Args:
        platform: Platform instance
        video: Video dict with url, title, etc.
        scenario: Scenario configuration
        video_idx: Video index (1-based)
        total_videos: Total number of videos
        rate_limiter: Rate limiter instance
        state: State manager instance
        dry_run: If True, log actions without executing them

    Returns:
        Number of comments successfully processed
    """
    video_url = video.get("url")
    if not video_url:
        logger.warning("Video %d has no URL, skipping", video_idx)
        return 0

    print(f"[{video_idx}/{total_videos}] {video.get('title', 'Unknown')[:60]}...")
    logger.info("Processing %s", video_url)

    comments = await platform.read_comments(video_url, scenario.max_comments_per_video)

    if not comments:
        print("  No comments found")
        return 0

    print(f"  Found {len(comments)} comments")

    processed = 0
    for action in scenario.actions:
        if action.type in {"like", "heart"}:
            for idx, comment in enumerate(comments, 1):
                # Check state
                if state.is_comment_processed(comment.id):
                    logger.debug("Skipping processed comment %s", comment.id)
                    continue

                if dry_run:
                    preview = comment.text[:40].replace("\n", " ")
                    print(f"  [DRY-RUN] Would {action.type}: {comment.author} - {preview}...")
                    processed += 1
                    continue

                # Rate Limit
                await rate_limiter.wait_if_needed()

                success = await platform.like_comment(idx)
                if success:
                    print(f"  SUCCESS Liked: {comment.author}")
                    state.mark_comment_processed(comment.id)
                    state.save()
                    processed += 1
                else:
                    print(f"  FAILURE Failed to like: {comment.author}")

    return processed


async def engage_with_scenario(  # noqa: PLR0914
    profile_name: str, scenario_name: str, *, dry_run: bool = False
) -> None:
    """Execute engagement scenario on a profile.

    Args:
        profile_name: Browser profile to use
        scenario_name: Scenario configuration to execute
        dry_run: If True, log actions without executing them
    """
    config = load_config()

    if profile_name not in config.profiles:
        logger.error("Profile '%s' not found in config", profile_name)
        sys.exit(1)

    if scenario_name not in config.scenarios:
        logger.error("Scenario '%s' not found in config", scenario_name)
        sys.exit(1)

    profile = config.profiles[profile_name]
    scenario = config.scenarios[scenario_name]

    if not profile.channel_url:
        logger.error("Profile '%s' does not have a channel_url configured", profile_name)
        sys.exit(1)

    controller = ChromeController()

    # Initialize safety tools
    rate_limiter = RateLimiter(
        actions_per_minute=10,
        min_delay=2.0,
        max_delay=5.0,
    )
    state = EngagementState()

    playwright = None
    browser = None

    try:
        cdp_url = await controller.ensure_browser()
        playwright, browser, page = await get_playwright_page(cdp_url)
        platform = YouTubePlatform(page)

        # Get discovery parameters
        max_videos, days_ago = _get_discovery_params(scenario.discovery)

        logger.info(
            "Fetching videos using method=%s, limit=%d",
            scenario.discovery.method,
            scenario.discovery.limit,
        )
        videos = await platform.list_videos(
            profile.channel_url, max_videos=max_videos, days_ago=days_ago
        )

        if not videos:
            logger.warning("No videos found")
            return

        # Limit videos based on discovery method
        if scenario.discovery.method == "recent_posts":
            videos = videos[: scenario.discovery.limit]

        mode_str = " [DRY-RUN]" if dry_run else ""
        print(f"\nProcessing {len(videos)} videos with scenario '{scenario_name}'{mode_str}")
        print(f"   Discovery: {scenario.discovery.method} (limit: {scenario.discovery.limit})")
        print(f"   Actions: {', '.join(a.type for a in scenario.actions)}")
        print(f"   Max comments/video: {scenario.max_comments_per_video}\n")

        total_processed = 0
        for i, video in enumerate(videos, 1):
            processed = await _process_video_comments(
                platform, video, scenario, i, len(videos), rate_limiter, state, dry_run=dry_run
            )
            total_processed += processed

        if dry_run:
            print(f"\n[DRY-RUN] Would have processed {total_processed} comments.")
        else:
            print(f"\nEngagement complete! Processed {total_processed} comments.")

    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        await controller.cleanup()


def auto_engage(
    profile_name: str,  # noqa: ARG001
    max_videos: int,  # noqa: ARG001
    max_comments_per_video: int,  # noqa: ARG001
) -> None:
    """Legacy auto-engage command."""
    print("Deprecated. Use 'engage' command with a scenario.")
    sys.exit(1)


async def run_task(task: EngagementTask, profile_name: str) -> None:
    """Execute an engagement task.

    Args:
        task: Task to execute
        profile_name: Browser profile to use
    """
    config = load_config()

    if profile_name not in config.profiles:
        logger.error("Profile '%s' not found in config", profile_name)
        sys.exit(1)

    controller = ChromeController()
    playwright = None
    browser = None

    try:
        cdp_url = await controller.ensure_browser()
        playwright, browser, page = await get_playwright_page(cdp_url)

        if task.platform == Platform.YOUTUBE:
            platform = YouTubePlatform(page)
        else:
            logger.error("Platform %s not supported yet", task.platform)
            sys.exit(1)

        if task.action == ActionType.READ:
            comments = await platform.read_comments(str(task.video_url), task.max_comments)
            logger.info("Retrieved %d comments", len(comments))
            for comment in comments:
                print(f"\n{comment.author}: {comment.text}")
        elif task.action == ActionType.RESPOND:
            logger.info("Response functionality coming soon")

    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        await controller.cleanup()


def main() -> None:
    """Main CLI entry point."""
    # Load config first to set up logging
    config = load_config()
    logging.basicConfig(level=logging.INFO, format=config.settings.log_format)

    parser = argparse.ArgumentParser(
        description="EngageRunner - AI-powered social media engagement"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Init command
    init_parser = subparsers.add_parser("init", help="Create default configuration file")
    init_parser.add_argument(
        "--output", "-o", default="config.yaml", help="Output path for config file"
    )

    # Read command
    read_parser = subparsers.add_parser("read", help="Read comments from a video")
    read_parser.add_argument("url", help="Video URL")
    read_parser.add_argument(
        "--profile",
        "-p",
        default=config.defaults.profile_name,
        help="Profile to use",
    )
    read_parser.add_argument(
        "--max",
        "-m",
        type=int,
        default=config.defaults.max_comments,
        help="Maximum comments to read",
    )

    # List videos command
    list_parser = subparsers.add_parser("list-videos", help="List videos from a channel")
    list_parser.add_argument(
        "--profile",
        "-p",
        default=config.defaults.profile_name,
        help="Profile to use",
    )
    list_parser.add_argument(
        "--max",
        "-m",
        type=int,
        default=config.defaults.max_videos,
        help="Maximum videos to list",
    )

    # Engage command (new scenario-based)
    engage_parser = subparsers.add_parser("engage", help="Execute engagement scenario on a profile")
    engage_parser.add_argument(
        "--profile",
        "-p",
        default=config.defaults.profile_name,
        help="Profile to use",
    )
    engage_parser.add_argument(
        "--scenario",
        "-s",
        required=True,
        help="Scenario to execute",
    )
    engage_parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Log actions without executing them",
    )

    # Legacy auto-engage command
    auto_engage_parser = subparsers.add_parser(
        "auto-engage", help="[LEGACY] Automatically react to comments on recent videos"
    )
    auto_engage_parser.add_argument(
        "--profile",
        "-p",
        default=config.defaults.profile_name,
        help="Profile to use",
    )
    auto_engage_parser.add_argument(
        "--max-videos",
        type=int,
        default=config.defaults.max_videos_auto_engage,
        help="Maximum videos to process",
    )
    auto_engage_parser.add_argument(
        "--max-comments",
        type=int,
        default=config.defaults.max_comments_auto_engage,
        help="Maximum comments per video to react to",
    )

    args = parser.parse_args()

    if args.command == "init":
        create_default_config(args.output)
        print(f"Created default configuration at {args.output}")
    elif args.command == "list-videos":
        asyncio.run(list_channel_videos(args.profile, args.max))
    elif args.command == "engage":
        asyncio.run(engage_with_scenario(args.profile, args.scenario, dry_run=args.dry_run))
    elif args.command == "auto-engage":
        auto_engage(args.profile, args.max_videos, args.max_comments)
    elif args.command == "read":
        task = EngagementTask(
            platform=Platform.YOUTUBE,
            video_url=args.url,
            action=ActionType.READ,
            max_comments=args.max,
        )
        asyncio.run(run_task(task, args.profile))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
