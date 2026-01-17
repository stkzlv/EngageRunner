"""Chrome CDP controller for connecting to browser sessions."""

import logging

import aiohttp

logger = logging.getLogger(__name__)

HTTP_OK = 200
DEFAULT_CDP_PORT = 9222


class ChromeController:
    """Connects to an existing Chrome instance via CDP.

    Requires Chrome to be running with remote debugging enabled:
        google-chrome --remote-debugging-port=9222
    """

    def __init__(self, cdp_port: int = DEFAULT_CDP_PORT) -> None:
        """Initialize the controller.

        Args:
            cdp_port: The remote debugging port (default 9222).
        """
        self.cdp_port = cdp_port

    async def ensure_browser(self) -> str:
        """Connect to Chrome and return the CDP URL.

        Returns:
            The CDP connection URL (e.g., "http://localhost:9222").

        Raises:
            RuntimeError: If Chrome is not running with CDP enabled.
        """
        if await self._is_cdp_available():
            logger.info("Connected to Chrome on port %d", self.cdp_port)
            return f"http://localhost:{self.cdp_port}"

        msg = (
            f"Chrome not found on port {self.cdp_port}. "
            f"Start Chrome with: google-chrome --remote-debugging-port={self.cdp_port}"
        )
        raise RuntimeError(msg)

    async def cleanup(self) -> None:
        """Clean up resources. No-op since we don't own the browser."""

    async def _is_cdp_available(self) -> bool:
        """Check if CDP is accepting connections."""
        try:
            timeout = aiohttp.ClientTimeout(total=2)
            async with (
                aiohttp.ClientSession(timeout=timeout) as session,
                session.get(f"http://localhost:{self.cdp_port}/json/version") as resp,
            ):
                return resp.status == HTTP_OK
        except (TimeoutError, aiohttp.ClientError):
            return False
