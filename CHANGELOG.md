# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Heart action for channel owners (default engagement action)
- YouTube Shorts support with automatic fallback to watch URL
- Direct Playwright automation (no LLM required for MVP actions)
- Chrome profile setup documentation for Chrome 136+
- Dry-run mode for previewing actions
- Rate limiting with randomized delays
- State tracking to avoid duplicate processing
- CLI commands: `engage`, `list-videos`, `read`
- Unit and integration tests (29 tests, 66% coverage)
- CI/CD workflows (CI, Security, Release)

### Changed
- Refactored from browser-use to direct Playwright automation
- Default action changed from like to heart
- Browser connection via CDP instead of launching new instance

### Removed
- LLM dependency for MVP actions (like/heart)
- `auto-engage` command (replaced by `engage` with scenarios)

[Unreleased]: https://github.com/stkzlv/EngageRunner/compare/main...HEAD
