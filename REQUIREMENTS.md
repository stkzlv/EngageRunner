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
    *   **Reactions:** Like (👍) and Heart (❤️).
    *   *Note: No text replies in MVP to minimize risk.*
*   **Safety & Logic:**
    *   **Timestamp Parsing:** accurately identify "2 hours ago" vs "2 years ago".
    *   **Rate Limiting:** Enforced delays (randomized 2-5s) between actions.
    *   **State Tracking:** Remembers which comments were liked to avoid duplicates.
    *   **Session Safety:** Connects to existing Chrome debugging port if open, or launches new instance if closed.

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

## 4. Technical Architecture

**Stack:** `Python 3.13`, `uv` (package manager), `browser-use` (agent control).

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

## 5. Success Criteria for MVP
1.  **Reliable Connection:** Script detects if Chrome is running. If yes, attaches to it. If no, launches it.
2.  **Accurate Discovery:** Correctly ignores videos/comments older than the configured limit (requires robust "relative time" parsing).
3.  **No Embarrassing Duplicates:** Never likes the same comment twice, even if the script is restarted.
4.  **Stealth:** Completes a "daily maintenance" run on 10 videos without triggering YouTube's "Action Unavailable" warning.