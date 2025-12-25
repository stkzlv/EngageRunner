# EngageRunner - Requirements

## Overview

AI-powered social media engagement automation. Read and respond to comments across platforms using browser automation and LLM intelligence.

**Tech Stack**: Python 3.13, uv, browser-use, OpenRouter (free models)

## What It Does

**Read Comments**
- Navigate to videos/posts using saved browser profiles
- Extract comments with author, text, timestamp, reply count
- Support YouTube (MVP), Instagram, TikTok (future)

**Respond to Comments**
- Post replies using templates or AI-generated responses
- Verify successful submission

**Manage Profiles**
- Use Chrome profiles with saved logins (cookies/sessions)
- Support multiple accounts per platform

**Persist Sessions**
- Maintain browser state between runs
- No repeated logins required

**Browser Session Management**
- **CRITICAL**: Only close Chrome sessions created by the tool
- Never close pre-existing Chrome sessions
- User may have Chrome already running with same profile

## MVP Scope (Iteration 1)

**Included**:
- YouTube comment reading and responding
- CLI interface
- Pre-authenticated browser profiles
- Template-based or LLM responses

**Excluded**:
- Automated login/2FA
- Multi-platform support
- Sentiment analysis
- Rate limiting
- Web UI

## Success Criteria

✅ Load Chrome profile with YouTube login
✅ Navigate to video URL
✅ Extract 10+ comments with metadata
✅ Post reply to specific comment
✅ Persist session for reuse

## Configuration

Config hierarchy: **CLI args → env vars → YAML → defaults**

### LLM Provider

**Default**: OpenRouter with free models (no cost, unified API for 400+ models)

**Supported providers**:
- `openrouter` (default) - Access free models via OpenRouter API
- `anthropic` - Direct Anthropic API (requires paid API key)
- `openai` - Direct OpenAI API (requires paid API key)

**Free models available** (via OpenRouter):
- `meta-llama/llama-4-maverick:free` (default) - 400B MoE, 256K context
- `meta-llama/llama-4-scout:free` - 109B MoE, 512K context
- `mistralai/mistral-small-3.1-24b-instruct:free` - 24B, 96K context
- `deepseek/deepseek-chat-v3-0324:free` - High-quality reasoning

```yaml
# config.yaml
profiles:
  youtube-main:
    chrome_profile_path: ~/.config/google-chrome/Profile1

llm:
  provider: openrouter  # default
  model: meta-llama/llama-4-maverick:free  # default free model

settings:
  headless: false
  timeout: 30
```

```bash
# .env (secrets only, gitignored)
# OpenRouter (free models, recommended)
OPENROUTER_API_KEY=sk-or-v1-...

# Alternative providers (optional)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### Why OpenRouter?

- **Free models**: No API costs for experimentation
- **Unified API**: Access 400+ models with one key
- **OpenAI-compatible**: Drop-in replacement for OpenAI SDK
- **Fallback support**: Switch providers without code changes
- **Privacy options**: Control whether requests are logged
