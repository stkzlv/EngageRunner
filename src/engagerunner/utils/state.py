"""State management to track processed items and prevent duplicates."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EngagementState:
    """Tracks processed videos and comments to avoid duplicate interactions."""

    def __init__(self, state_file: Path | None = None) -> None:
        """Initialize state manager.

        Args:
            state_file: Path to JSON state file. Defaults to ~/.engagerunner/state.json.
        """
        if state_file:
            self.state_file = state_file
        else:
            self.state_file = Path.home() / ".engagerunner" / "state.json"

        self.processed_videos: set[str] = set()
        self.processed_comments: set[str] = set()
        self.last_run: datetime | None = None

        self._load()

    def _load(self) -> None:
        """Load state from disk."""
        if not self.state_file.exists():
            logger.debug("No state file found at %s. Starting fresh.", self.state_file)
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.processed_videos = set(data.get("processed_videos", []))
                self.processed_comments = set(data.get("processed_comments", []))

                last_run_str = data.get("last_run")
                if last_run_str:
                    self.last_run = datetime.fromisoformat(last_run_str)
            logger.info(
                "Loaded state: %d videos, %d comments processed.",
                len(self.processed_videos),
                len(self.processed_comments),
            )
        except (json.JSONDecodeError, OSError):
            logger.exception("Failed to load state file")

    def save(self) -> None:
        """Save state to disk."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            data: dict[str, Any] = {
                "processed_videos": list(self.processed_videos),
                "processed_comments": list(self.processed_comments),
                "last_run": datetime.now(UTC).isoformat(),
            }

            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug("State saved to %s", self.state_file)
        except OSError:
            logger.exception("Failed to save state file")

    def is_video_processed(self, video_url: str) -> bool:
        """Check if video was already processed."""
        return video_url in self.processed_videos

    def mark_video_processed(self, video_url: str) -> None:
        """Mark video as processed."""
        self.processed_videos.add(video_url)

    def is_comment_processed(self, comment_id: str) -> bool:
        """Check if comment was already engaged with."""
        return comment_id in self.processed_comments

    def mark_comment_processed(self, comment_id: str) -> None:
        """Mark comment as processed."""
        self.processed_comments.add(comment_id)
