"""Time parsing utilities for relative timestamps."""

import logging
import re
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)


def parse_relative_time(relative_str: str) -> datetime:
    """Parse YouTube relative time strings to actual datetime.

    Examples:
        "2 hours ago" -> datetime 2 hours before now
        "3 days ago" -> datetime 3 days before now
        "1 week ago" -> datetime 7 days before now
        "2 months ago" -> datetime 60 days before now (approximate)

    Args:
        relative_str: The relative time string (e.g., "2 hours ago").

    Returns:
        The estimated datetime in UTC. Defaults to current time if parsing fails.
    """
    now = datetime.now(UTC)
    relative_str = relative_str.lower().strip()

    # Handle "Just now" or similar
    if relative_str in {"just now", "moments ago"}:
        return now

    match = re.match(r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago", relative_str)

    if not match:
        logger.warning("Could not parse time string: '%s'. Defaulting to now.", relative_str)
        return now

    amount = int(match.group(1))
    unit = match.group(2)

    delta_map = {
        "second": timedelta(seconds=amount),
        "minute": timedelta(minutes=amount),
        "hour": timedelta(hours=amount),
        "day": timedelta(days=amount),
        "week": timedelta(weeks=amount),
        "month": timedelta(days=amount * 30),  # Approximate
        "year": timedelta(days=amount * 365),  # Approximate
    }

    return now - delta_map.get(unit, timedelta())
