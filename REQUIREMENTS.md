# EngageRunner - Project Requirements

## 1. Overview
**EngageRunner** is a local, AI-powered automation agent designed to manage your personal brand's engagement on social media. It acts as a "virtual employee," engaging with your audience using your **existing, pre-authenticated Chrome profile**.

**Core Philosophy:**
*   **"Bring Your Own Profile" (BYOP):** No complex login scripts or 2FA handling. We piggyback on your legitimate, logged-in session.
*   **Safety First:** Actions are rate-limited, randomized, and tracked to prevent spam detection.
*   **Local Execution:** Everything runs on your machine; your credentials never leave your local Chrome profile.

---

## 2. Current Scope: MVP (Iteration 1)
The initial release focuses on **YouTube Comment Maintenance**—ensuring every fan comment gets a reaction without you spending hours scrolling.

### ✅ Included Features
*   **Platform:** YouTube only.
*   **Identity:** Uses your local Chrome profile (e.g., `stealtechhq@gmail.com`).
*   **Discovery Methods:**
    *   **Recent Posts:** Check comments on the last $N$ videos.
    *   **Time-Based:** Check comments on videos posted in the last $N$ days.
*   **Engagement Actions:**
    *   **Heart (❤️):** Default. Channel owner's "thank you" badge on comments.
    *   **Like (👍):** Optional. Standard thumbs-up, available to anyone.
    *   Both actions are configurable per scenario. No text replies in MVP.
*   **Safety & Logic:**
    *   **Timestamp Parsing:** accurately identify "2 hours ago" vs "2 years ago".
    *   **Rate Limiting:** Enforced delays (randomized 2-5s) between actions.
    *   **State Tracking:** Remembers which comments were liked to avoid duplicates.
*   **Browser Setup:** User starts Chrome manually with remote debugging enabled.

### ❌ Excluded from MVP
*   Text replies (LLM-generated or template).
*   Instagram/TikTok/LinkedIn support.
*   "Global" discovery (finding comments on 3-year-old videos).
*   Web UI (CLI only).

---

## 3. Future Roadmap

### Phase 2: The Conversationalist
*   **LLM Replies:** Integration with OpenRouter/Llama for context-aware text replies.
*   **Approval Queue:** CLI dashboard to review generated replies before posting.
*   **Templates:** Spintax support (e.g., "{Great|Nice} video!").

### Phase 3: Multi-Platform Growth
*   **Instagram:** Like comments on posts, reply to DMs.
*   **TikTok:** Engage with trending niche content.
*   **Cross-Pollination:** Detect "superfans" active across multiple platforms.

---

## 4. Chrome Profile Setup

Chrome 136+ blocks remote debugging on the default data directory for security. Copy your profile to a separate location:

```bash
# One-time setup
mkdir -p ~/.engagerunner/chrome-profile
cp ~/.config/google-chrome/Local\ State ~/.engagerunner/chrome-profile/
cp -r ~/.config/google-chrome/<your-profile> ~/.engagerunner/chrome-profile/

# Start Chrome for EngageRunner
google-chrome --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.engagerunner/chrome-profile \
  --profile-directory=<your-profile>
```

---

## 5. Technical Architecture

**Stack:** `Python 3.13`, `uv` (package manager), `Playwright` (browser automation).

**MVP Approach:** Direct DOM automation via Playwright. No LLM required for simple like/heart actions.

### Configuration (`config.yaml`)
```yaml
profiles:
  main_identity:
    platform: youtube
    chrome_profile: "Default" # or specific profile folder name
    channel_url: "https://www.youtube.com/@MyChannel"

scenarios:
  daily_maintenance:
    discovery:
      method: recent_posts
      limit: 10 # Check last 10 videos
    actions:
      - type: like
      - type: heart
    filters:
      ignore_keywords: ["spam", "promo"]

settings:
  rate_limit:
    enabled: true
    min_delay: 2.0
    max_delay: 10.0
  state_file: "~/.engagerunner/state.json"
```

---

## 6. LLM Configuration

**When Used:** Complex scenarios only (text replies, content analysis). MVP actions (like/heart) use direct Playwright.

**Provider:** OpenRouter. Free models by default.

**Retry/Fallback Logic:**
- On failure (timeout, rate limit, error), retry with next model in list
- Cycle through configured free models before failing
- Configurable retry count and model priority

**Example Config:**
```yaml
llm:
  provider: openrouter
  models:
    - google/gemini-2.0-flash-exp:free  # primary
    - meta-llama/llama-3.2-3b-instruct:free  # fallback 1
    - qwen/qwen3-4b:free  # fallback 2
  max_retries: 3
  timeout: 45
```

---

## 7. Success Criteria for MVP
1.  **Reliable Connection:** Connects to user-started Chrome with remote debugging enabled.
2.  **Accurate Discovery:** Correctly ignores videos/comments older than the configured limit.
3.  **No Embarrassing Duplicates:** Never likes the same comment twice, even if the script is restarted.
4.  **Stealth:** Completes a "daily maintenance" run on 10 videos without triggering YouTube's "Action Unavailable" warning.