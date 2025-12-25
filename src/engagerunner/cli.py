"""Command-line interface for EngageRunner."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from engagerunner import __version__
from engagerunner.browser import ProfileManager
from engagerunner.config import create_default_config, load_config
from engagerunner.models import ActionType, EngagementTask, Platform
from engagerunner.platforms import YouTubePlatform

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_task(task: EngagementTask, profile_name: str, config_path: Path) -> None:
    """Execute an engagement task.

    Args:
        task: Task to execute
        profile_name: Browser profile to use
        config_path: Path to configuration file
    """
    config = load_config(config_path)

    if profile_name not in config.profiles:
        logger.error("Profile '%s' not found in config", profile_name)
        sys.exit(1)

    profile = config.profiles[profile_name]
    manager = ProfileManager(headless=config.settings.headless, timeout=config.settings.timeout)

    try:
        browser = await manager.get_browser(profile_name, profile.chrome_profile_path)

        if task.platform == Platform.YOUTUBE:
            platform = YouTubePlatform(browser)
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
    read_parser.add_argument("--config", "-c", default="config.yaml", help="Path to config file")

    args = parser.parse_args()

    if args.command == "init":
        create_default_config(args.output)
        print(f"Created default configuration at {args.output}")
    elif args.command == "read":
        task = EngagementTask(
            platform=Platform.YOUTUBE,
            video_url=args.url,
            action=ActionType.READ,
            max_comments=args.max,
        )
        asyncio.run(run_task(task, args.profile, Path(args.config)))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
