"""Command-line interface for EngageRunner."""

import argparse
import asyncio
import logging
import sys

from engagerunner import __version__, create_llm
from engagerunner.browser import ProfileManager
from engagerunner.config import create_default_config, load_config
from engagerunner.models import ActionType, EngagementTask, Platform
from engagerunner.platforms import YouTubePlatform

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    # Get channel URL from profile
    if not profile.channel_url:
        logger.error("Profile '%s' does not have a channel_url configured", profile_name)
        sys.exit(1)

    manager = ProfileManager(headless=config.settings.headless, timeout=config.settings.timeout)
    llm = create_llm(config.llm)

    try:
        browser = await manager.get_browser(profile_name, profile.chrome_profile_path)
        platform = YouTubePlatform(browser, llm)

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
            print("No videos found or extraction needs implementation")

    finally:
        await manager.close_all()


async def auto_engage(profile_name: str, max_videos: int, max_comments_per_video: int) -> None:
    """Automatically engage with comments on recent videos.

    Args:
        profile_name: Browser profile to use
        max_videos: Maximum number of videos to process
        max_comments_per_video: Maximum comments per video to react to
    """
    config = load_config()

    if profile_name not in config.profiles:
        logger.error("Profile '%s' not found in config", profile_name)
        sys.exit(1)

    profile = config.profiles[profile_name]

    if not profile.auto_react:
        logger.warning("auto_react is disabled for this profile. Enable it in config.yaml")
        sys.exit(1)

    if not profile.channel_url:
        logger.error("Profile '%s' does not have a channel_url configured", profile_name)
        sys.exit(1)

    manager = ProfileManager(headless=config.settings.headless, timeout=config.settings.timeout)
    llm = create_llm(config.llm)

    try:
        browser = await manager.get_browser(profile_name, profile.chrome_profile_path)
        platform = YouTubePlatform(browser, llm)

        logger.info("Fetching videos from %s", profile.channel_url)
        videos = await platform.list_videos(profile.channel_url, max_videos)

        if not videos:
            logger.warning("No videos found")
            return

        print(f"\nProcessing {len(videos)} videos...")

        for i, video in enumerate(videos, 1):
            video_url = video.get("url")
            if not video_url:
                logger.warning("Video %d has no URL, skipping", i)
                continue

            print(f"\n[{i}/{len(videos)}] {video.get('title', 'Unknown title')}")
            logger.info("Reading comments from %s", video_url)

            comments = await platform.read_comments(video_url, max_comments_per_video)

            if not comments:
                logger.info("No comments found on this video")
                continue

            print(f"  Found {len(comments)} comments, reacting...")

            for comment in comments:
                success = await platform.react_to_comment(comment.text, profile.reaction_emoji)
                if success:
                    print(f"  ✓ Reacted to: {comment.author}")
                else:
                    print(f"  ✗ Failed to react to: {comment.author}")

    finally:
        await manager.close_all()


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

    profile = config.profiles[profile_name]
    manager = ProfileManager(headless=config.settings.headless, timeout=config.settings.timeout)

    # Create LLM instance from config
    llm = create_llm(config.llm)

    try:
        browser = await manager.get_browser(profile_name, profile.chrome_profile_path)

        if task.platform == Platform.YOUTUBE:
            platform = YouTubePlatform(browser, llm)
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
        await manager.close_all()


def main() -> None:
    """Main CLI entry point."""
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
    read_parser.add_argument("--profile", "-p", default="youtube-main", help="Profile to use")
    read_parser.add_argument("--max", "-m", type=int, default=10, help="Maximum comments to read")

    # List videos command
    list_parser = subparsers.add_parser("list-videos", help="List videos from a channel")
    list_parser.add_argument("--profile", "-p", default="youtube-main", help="Profile to use")
    list_parser.add_argument("--max", "-m", type=int, default=20, help="Maximum videos to list")

    # Auto-engage command
    engage_parser = subparsers.add_parser(
        "auto-engage", help="Automatically react to comments on recent videos"
    )
    engage_parser.add_argument("--profile", "-p", default="youtube-main", help="Profile to use")
    engage_parser.add_argument(
        "--max-videos", type=int, default=5, help="Maximum videos to process"
    )
    engage_parser.add_argument(
        "--max-comments", type=int, default=10, help="Maximum comments per video to react to"
    )

    args = parser.parse_args()

    if args.command == "init":
        create_default_config(args.output)
        print(f"Created default configuration at {args.output}")
    elif args.command == "list-videos":
        asyncio.run(list_channel_videos(args.profile, args.max))
    elif args.command == "auto-engage":
        asyncio.run(auto_engage(args.profile, args.max_videos, args.max_comments))
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
