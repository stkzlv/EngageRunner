"""Browser profile management."""

import logging
from pathlib import Path

from browser_use import Browser, BrowserConfig

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

        config = BrowserConfig(
            headless=self.headless,
            disable_security=False,
            extra_chromium_args=[
                f"--user-data-dir={chrome_profile_path}" if chrome_profile_path else "",
            ],
        )

        browser = Browser(config=config)  # type: ignore[call-overload]
        self._browsers[profile_name] = browser
        logger.info("Created browser instance '%s'", profile_name)
        return browser  # type: ignore[no-any-return]

    async def close_all(self) -> None:
        """Close all browser instances."""
        for name, browser in self._browsers.items():
            try:
                await browser.close()  # type: ignore[attr-defined]
                logger.info("Closed browser '%s'", name)
            except Exception:
                logger.exception("Error closing browser '%s'", name)
        self._browsers.clear()
