"""Shared test fixtures."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.profiles = {
        "test-profile": MagicMock(
            channel_url="https://youtube.com/channel/123",
            chrome_profile_path="/tmp/profile"
        )
    }
    config.scenarios = {
        "test-scenario": MagicMock(
            discovery=MagicMock(method="recent_posts", limit=5),
            actions=[MagicMock(type="like")],
            max_comments_per_video=2
        )
    }
    config.settings.headless = True
    config.settings.timeout = 10
    config.llm = MagicMock()
    return config
