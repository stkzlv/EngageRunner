# EngageRunner - Requirements

## Overview

AI-powered agent for social media engagement automation using the browser-use library. The agent opens social media platforms with specific browser profiles, reads comments, and responds to them.

## Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13 |
| Package Manager | uv |
| Browser Automation | browser-use (Playwright-based) |
| LLM | Claude / GPT (configurable) |

## Core Functionality

### 1. Profile Management
- Load specific Chrome profiles with pre-saved credentials (cookies/sessions)
- Support multiple named profiles for different accounts
- Configurable profile paths via settings

### 2. Platform Navigation
- Navigate to TikTok, Instagram, YouTube creator dashboards/comment sections
- Handle dynamic page loading (infinite scroll, lazy load)
- Wait for page elements to be interactive

### 3. Comment Reading
- Extract comments from posts/videos with metadata:
  - Author username
  - Timestamp
  - Comment text
  - Reply count (if available)
- Support pagination/scroll-based loading
- Return structured data (Pydantic models)

### 4. Comment Response
- Post replies to specific comments
- Support template-based responses
- Support LLM-generated contextual responses
- Verify successful submission

### 5. Session Persistence
- Save browser state (cookies, localStorage) between runs
- Restore sessions to avoid re-authentication

## Platform-Specific Details

| Platform | Login Method | Comment Location | Known Challenges |
|----------|--------------|------------------|------------------|
| YouTube | Google SSO (profile) | Video page → Comments section | Dynamic loading, nested replies |
| Instagram | Session cookies | Post page → Comments | Aggressive bot detection |
| TikTok | Session cookies | Video page → Comments | Frequent UI changes |

## First Iteration Scope

### In Scope
1. **Single platform focus** - YouTube only (most stable structure)
2. **Read-only validation** - Comment extraction before enabling responses
3. **Manual login** - Use pre-authenticated browser profile (no automated login)
4. **Simple responses** - Template-based or LLM-generated single replies
5. **CLI interface** - Command-line operation

### Out of Scope
- Multi-account management
- Automated login / 2FA handling
- Sentiment analysis / filtering
- Response scheduling / queuing
- Rate limit handling / backoff
- Instagram and TikTok support
- Web UI / dashboard

## Configuration

```yaml
# Example config structure
profiles:
  youtube-main:
    platform: youtube
    chrome_profile_path: ~/.config/google-chrome/Profile1

llm:
  provider: anthropic
  model: claude-sonnet-4-20250514

settings:
  headless: false
  timeout: 30
```

## Data Models

### Comment
```python
class Comment:
    id: str
    author: str
    text: str
    timestamp: datetime
    reply_count: int
    platform: Literal["youtube", "instagram", "tiktok"]
```

### EngagementTask
```python
class EngagementTask:
    platform: str
    video_url: str
    action: Literal["read", "respond"]
    response_template: str | None
```

## Success Criteria

1. Successfully load a Chrome profile with saved YouTube login
2. Navigate to a specified video URL
3. Extract at least 10 comments with accurate metadata
4. Post a reply to a specific comment (manual trigger)
5. Persist session for reuse

## Dependencies

```toml
[project]
dependencies = [
    "browser-use>=1.0.0",
    "pydantic>=2.0",
    "python-dotenv",
]
```

## References

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [browser-use Documentation](https://docs.browser-use.com)
