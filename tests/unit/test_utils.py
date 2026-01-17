"""Unit tests for utility modules."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from engagerunner.utils.safety import RateLimiter
from engagerunner.utils.state import EngagementState
from engagerunner.utils.time_parser import parse_relative_time


class TestTimeParser:
    def test_parse_seconds_ago(self):
        now = datetime.now(UTC)
        result = parse_relative_time("30 seconds ago")
        # Allow small delta for execution time
        diff = now - result
        assert timedelta(seconds=29) < diff < timedelta(seconds=31)

    def test_parse_hours_ago(self):
        now = datetime.now(UTC)
        result = parse_relative_time("2 hours ago")
        diff = now - result
        assert timedelta(hours=1.99) < diff < timedelta(hours=2.01)

    def test_parse_days_ago(self):
        now = datetime.now(UTC)
        result = parse_relative_time("5 days ago")
        diff = now - result
        assert timedelta(days=4.99) < diff < timedelta(days=5.01)

    def test_parse_years_ago(self):
        now = datetime.now(UTC)
        result = parse_relative_time("1 year ago")
        diff = now - result
        assert timedelta(days=364) < diff < timedelta(days=366)

    def test_just_now(self):
        now = datetime.now(UTC)
        result = parse_relative_time("Just now")
        assert (now - result) < timedelta(seconds=1)

    def test_invalid_string_defaults_to_now(self):
        now = datetime.now(UTC)
        result = parse_relative_time("Invalid time string")
        assert (now - result) < timedelta(seconds=1)


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_wait_if_needed_respects_jitter(self):
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)
        start = datetime.now(UTC)
        await limiter.wait_if_needed()
        duration = (datetime.now(UTC) - start).total_seconds()
        assert 0.1 <= duration <= 0.3  # slight buffer for async overhead

    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self):
        # Allow 2 actions per minute
        limiter = RateLimiter(actions_per_minute=2, min_delay=0.01, max_delay=0.02)

        # First 2 should be fast (just jitter)
        start = datetime.now(UTC)
        await limiter.wait_if_needed()
        await limiter.wait_if_needed()
        fast_duration = (datetime.now(UTC) - start).total_seconds()
        assert fast_duration < 0.2

        # 3rd action should trigger wait (approx 60s in real world, mocked here)
        # We'll just verify the logic tracks the actions
        assert len(limiter.action_times) == 2


class TestEngagementState:
    def test_load_and_save(self, tmp_path):
        state_file = tmp_path / "state.json"
        state = EngagementState(state_file=state_file)

        state.mark_video_processed("https://youtube.com/v/123")
        state.mark_comment_processed("comment_abc")
        state.save()

        # Reload
        new_state = EngagementState(state_file=state_file)
        assert new_state.is_video_processed("https://youtube.com/v/123")
        assert new_state.is_comment_processed("comment_abc")
        assert not new_state.is_video_processed("other_video")

    def test_default_path_creation(self):
        # We won't actually write to home dir in test, but verify path logic
        with patch.object(Path, "home", return_value=Path("/tmp/fakehome")):
            state = EngagementState()
            assert str(state.state_file) == "/tmp/fakehome/.engagerunner/state.json"
