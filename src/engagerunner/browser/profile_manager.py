"""Browser profile management."""

import logging
from pathlib import Path

from browser_use import Browser

logger = logging.getLogger(__name__)


class ProfileManager:
    """Manages browser profiles for different platforms."""

    def __init__(self, headless: bool = False, timeout: int = 30) -> None:
        """Initialize profile manager.

        Args:
            headless: Run browser in headless mode
            timeout: Default timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self._browsers: dict[str, Browser] = {}

    async def get_browser(
        self, profile_name: str, chrome_profile_path: Path | None = None
    ) -> Browser:
        """Get or create a browser instance with the specified profile.

        Args:
            profile_name: Name for this browser instance
            chrome_profile_path: Path to Chrome profile directory

        Returns:
            Browser instance
        """
        if profile_name in self._browsers:
            return self._browsers[profile_name]

        # Expand ~ and split into user_data_dir and profile_directory
        if chrome_profile_path:
            expanded_path = chrome_profile_path.expanduser()
            user_data_dir = expanded_path.parent
            profile_dir = expanded_path.name
        else:
            user_data_dir = None
            profile_dir = None

        browser = Browser(
            headless=self.headless,
            user_data_dir=user_data_dir,
            profile_directory=profile_dir,
        )
        self._browsers[profile_name] = browser
        logger.info("Created browser instance '%s'", profile_name)
        return browser

    async def close_all(self) -> None:
        """Close all browser instances."""
        for name, browser in self._browsers.items():
            try:
                await browser.stop()
                logger.info("Closed browser '%s'", name)
            except Exception:
                logger.exception("Error closing browser '%s'", name)
        self._browsers.clear()
