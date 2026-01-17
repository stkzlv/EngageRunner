"""Safety utilities for rate limiting and ban prevention."""

import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limit actions to avoid detection."""

    def __init__(
        self,
        actions_per_minute: int = 10,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            actions_per_minute: Maximum allowed actions per minute.
            min_delay: Minimum delay in seconds between actions.
            max_delay: Maximum delay in seconds between actions (jitter).
        """
        self.actions_per_minute = actions_per_minute
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.action_times: list[datetime] = []

    async def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded, and add jitter."""
        now = datetime.now(UTC)

        # Prune history: Remove actions older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self.action_times = [t for t in self.action_times if t > cutoff]

        # Check frequency limit
        if len(self.action_times) >= self.actions_per_minute:
            # Wait until the oldest action expires from the window
            oldest_action = self.action_times[0]
            wait_until = oldest_action + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                logger.warning(
                    "Rate limit reached (%d/min). Cooling down for %.1fs...",
                    self.actions_per_minute,
                    wait_seconds,
                )
                await asyncio.sleep(wait_seconds)

        # Apply random jitter delay
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug("Sleeping for %.2fs (safety jitter)...", delay)
        await asyncio.sleep(delay)

        # Record this action
        self.action_times.append(datetime.now(UTC))
