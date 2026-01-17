"""Chrome process controller for managing browser sessions."""

import asyncio
import logging
import platform
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from playwright.async_api import Browser

logger = logging.getLogger(__name__)

HTTP_OK = 200


class ChromeController:
    """Manages the Chrome browser process and CDP connection.

    Handles the "Profile Locked" issue by:
    1. Checking if Chrome is already debugging on port 9222.
    2. Connecting to it if yes.
    3. Launching a new instance if no.
    """

    def __init__(
        self,
        cdp_port: int = 9222,
        chrome_path: str | None = None,
        user_data_dir: Path | None = None,
        profile_directory: str | None = None,
    ) -> None:
        """Initialize the controller.

        Args:
            cdp_port: The remote debugging port (default 9222).
            chrome_path: Custom path to Chrome executable.
            user_data_dir: Path to Chrome user data directory.
            profile_directory: Name of the profile directory (e.g., "Default").
        """
        self.cdp_port = cdp_port
        self.chrome_path = chrome_path or self._find_chrome_executable()
        self.user_data_dir = user_data_dir.expanduser() if user_data_dir else None
        self.profile_directory = profile_directory
        self._process: subprocess.Popen[bytes] | None = None
        self._playwright_browser: Browser | None = None
        self._is_external_process = False

    async def ensure_browser(self) -> str:
        """Ensure a Chrome instance is running and return the CDP URL.

        Returns:
            The CDP connection URL (e.g., "http://localhost:9222").
        """
        if await self._is_cdp_port_open():
            logger.info("Connecting to existing Chrome instance on port %d", self.cdp_port)
            self._is_external_process = True
            return f"http://localhost:{self.cdp_port}"

        logger.info("Launching new Chrome instance on port %d...", self.cdp_port)
        await self._launch_chrome()
        return f"http://localhost:{self.cdp_port}"

    async def cleanup(self) -> None:
        """Clean up resources.

        Only terminates the process if we launched it ourselves.
        """
        if self._playwright_browser:
            await self._playwright_browser.close()

        if not self._is_external_process and self._process:
            logger.info("Terminating Chrome subprocess...")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Chrome did not exit gracefully, killing...")
                self._process.kill()

    async def _is_cdp_port_open(self) -> bool:
        """Check if the CDP port is accepting connections."""
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(f"http://localhost:{self.cdp_port}/json/version", timeout=1.0) as resp,
            ):
                return resp.status == HTTP_OK
        except (TimeoutError, aiohttp.ClientError):
            return False

    async def _launch_chrome(self) -> None:
        """Launch a new Chrome process with remote debugging enabled."""
        if not self.chrome_path:
            msg = "Chrome executable not found"
            raise RuntimeError(msg)

        cmd = [
            self.chrome_path,
            f"--remote-debugging-port={self.cdp_port}",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if self.user_data_dir:
            cmd.append(f"--user-data-dir={self.user_data_dir}")

        if self.profile_directory:
            cmd.append(f"--profile-directory={self.profile_directory}")

        logger.debug("Executing Chrome command: %s", " ".join(cmd))

        # Launch as subprocess
        # Using create_subprocess_exec would be better but requires command list expansion
        # For now, sticking to Popen as it's easier to manage the background process life
        self._process = subprocess.Popen(  # noqa: ASYNC220
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for CDP to be ready
        for _ in range(20):  # 20 attempts * 0.5s = 10s timeout
            if await self._is_cdp_port_open():
                logger.info("Chrome launched and CDP is ready.")
                return
            await asyncio.sleep(0.5)

        # If we get here, it failed
        if self._process:
            self._process.terminate()
        msg = "Chrome failed to start or open CDP port"
        raise RuntimeError(msg)

    @staticmethod
    def _find_chrome_executable() -> str:
        """Find the Chrome executable path based on OS."""
        system = platform.system()
        paths: list[str] = []

        if system == "Linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        elif system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]

        for path in paths:
            if Path(path).exists():
                return path

        # Fallback to PATH
        if shutil.which("google-chrome"):
            return "google-chrome"
        if shutil.which("chrome"):
            return "chrome"
        if shutil.which("chromium"):
            return "chromium"

        msg = "Could not find Chrome executable. Please specify chrome_path."
        raise RuntimeError(msg)
