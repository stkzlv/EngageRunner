# Versioning Strategy

EngageRunner follows [Semantic Versioning (SemVer) 2.0.0](https://semver.org/) principles with a clear pre-production strategy, adhering to [PEP 440](https://peps.python.org/pep-0440/) for Python package versioning.

## Version Format

**`MAJOR.MINOR.PATCH`**

- **MAJOR**: Breaking changes that require user intervention or incompatible API changes
- **MINOR**: New features, backward-compatible functionality additions
- **PATCH**: Bug fixes, performance improvements, documentation updates

### Version Sequencing

**Version numbers must be sequential** - skipping versions is not allowed, even when a release contains multiple significant features. Each version increment represents a single release, regardless of the number or magnitude of changes included.

**Examples:**
- ✅ Correct: 0.1.0 → 0.2.0 → 0.3.0 (sequential)
- ❌ Incorrect: 0.1.0 → 0.5.0 (skips 0.2.0, 0.3.0, 0.4.0)

This ensures version consistency, predictability, and adherence to semantic versioning principles.

## Pre-Production Phase (0.x.y)

**Current Status**: EngageRunner is in early development toward a stable 1.0.0 release.

### 0.x.y Development Roadmap

- **0.1.0**: Initial release with YouTube comment reading (read-only)
- **0.2.0**: YouTube comment response capability
- **0.3.0**: Instagram platform support
- **0.4.0**: TikTok platform support
- **0.5.0**: Multi-account management
- **0.6.0**: Advanced filtering and sentiment analysis
- **0.7.0**: Response templates and scheduling
- **0.8.0**: Rate limiting and safety features
- **0.9.0**: Release candidates, stability focus, production testing
- **1.0.0**: First stable production release

### Breaking Changes in 0.x

⚠️ **Important**: During the 0.x phase, breaking changes may occur in minor versions.

We will:
- Document all breaking changes in the CHANGELOG
- Provide migration guides for significant changes
- Announce breaking changes in advance when possible
- Maintain backward compatibility when feasible
- Use deprecation warnings before removing features

### Pre-1.0.0 API Stability

- Public APIs may change without major version bump
- Configuration format may evolve
- Data models may be restructured
- Platform-specific implementations may be refactored

## Release Process

### Release Schedule

- **Patch releases**: As needed for bug fixes (weekly/bi-weekly)
- **Minor releases**: Bi-weekly to monthly for new features
- **Major releases**: When significant breaking changes are necessary (post-1.0.0)

### Release Workflow

1. **Development**: Feature branches with development work
2. **Testing**: Automated CI/CD pipeline validates all changes
3. **Version Bump**: Update version in `pyproject.toml` and `__init__.py`
4. **Changelog**: Update CHANGELOG.md with release notes
5. **Pull Request**: Feature branch merged to `main` via Pull Request
6. **Tagging**: Git tag created from `main` after merge (`v0.1.0`, `v0.2.0`, etc.)
7. **GitHub Release**: Automated release notes generation
8. **PyPI**: Package published to PyPI (optional, when public-ready)
9. **Communication**: Community notification of new releases

### Version Bumping

Use semantic versioning to determine version increment:

```bash
# Patch version (0.1.0 -> 0.1.1)
# For: Bug fixes, typos, documentation
git tag v0.1.1

# Minor version (0.1.0 -> 0.2.0)
# For: New features, platform additions
git tag v0.2.0

# Major version (1.0.0 -> 2.0.0) - post-1.0.0 only
# For: Breaking API changes
git tag v2.0.0
```

## Path to 1.0.0

### Stability Criteria

EngageRunner will reach 1.0.0 when:

- ✅ **Platform Coverage**: YouTube, Instagram, and TikTok fully supported
- ✅ **Core Features**: Comment reading and responding stable across all platforms
- ✅ **API Stability**: Public APIs finalized with backward compatibility commitment
- ✅ **Documentation**: Complete user and developer documentation
- ✅ **Test Coverage**: >80% code coverage with comprehensive integration tests
- ✅ **Error Handling**: Robust error handling and recovery mechanisms
- ✅ **Rate Limiting**: Production-ready rate limiting to prevent platform bans
- ✅ **Security**: Security audit completed, no known vulnerabilities
- ✅ **Production Use**: Successfully deployed in production environments by beta users
- ✅ **Community**: Active contributor base and issue resolution process

### Post-1.0.0 Promise

After 1.0.0 release:
- **Semantic Versioning**: Strict SemVer 2.0.0 compliance
- **Backward Compatibility**: Breaking changes only in major versions
- **Deprecation Policy**: 6-month deprecation period before removal
- **Migration Guides**: Comprehensive upgrade documentation for major versions
- **LTS Support**: Long-term support for major versions (if applicable)

## Version Support Policy

### Current Support (Pre-1.0.0)

- **Latest Version**: Full support with new features and bug fixes
- **Previous Minor**: Critical bug fixes for 1 month after new minor release
- **Pre-1.0.0**: Best-effort support, focus on latest version

### Post-1.0.0 Support Policy

- **Current Major**: Full feature development and bug fixes
- **Previous Major**: Security patches and critical bug fixes for 12 months
- **Older Majors**: Community support only, no official patches

## Release Notes Format

Each release follows the [Keep a Changelog](https://keepachangelog.com/) format:

### Changelog Categories

- **Added**: New features and capabilities
- **Changed**: Modifications to existing functionality
- **Deprecated**: Features being phased out (with timeline)
- **Removed**: Discontinued features (major versions only)
- **Fixed**: Bug fixes and performance improvements
- **Security**: Security-related changes and patches

### Example Release Notes

```markdown
## [0.2.0] - 2025-01-15

### Added
- YouTube comment response capability
- LLM integration for contextual replies
- Template-based response system

### Changed
- Improved comment extraction performance by 40%
- Enhanced browser profile management

### Fixed
- Fixed handling of nested YouTube comment threads
- Resolved session persistence issues

### Security
- Updated playwright dependency to patch CVE-2025-XXXX
```

## Python Package Versioning

### PEP 440 Compliance

EngageRunner adheres to [PEP 440](https://peps.python.org/pep-0440/) for version identification:

- **Final releases**: `0.1.0`, `1.0.0`, `2.1.3`
- **Pre-releases** (if used): `0.1.0a1`, `0.1.0b2`, `0.1.0rc1`
- **Development releases** (if used): `0.1.0.dev1`

### Version in Code

Version is defined in multiple locations for consistency:

```python
# pyproject.toml
[project]
version = "0.1.0"

# src/engagerunner/__init__.py
__version__ = "0.1.0"
```

## Contributing to Releases

### Feature Requests

- Submit feature requests via [GitHub Issues](https://github.com/YOUR-USERNAME/EngageRunner/issues)
- Use the "enhancement" label
- Provide use cases and expected behavior
- Community voting helps prioritize features

### Bug Reports

- Report bugs via [GitHub Issues](https://github.com/YOUR-USERNAME/EngageRunner/issues)
- Include reproduction steps and environment details
- Critical bugs may trigger patch releases
- Use appropriate severity labels (critical, high, medium, low)

### Release Testing

- Beta versions available for testing (tagged with `-beta` suffix)
- Community feedback incorporated before final release
- Release candidates published for major versions (post-1.0.0)

## Automation

### Automated Version Management

Consider using [Python Semantic Release](https://python-semantic-release.readthedocs.io/) for automated version bumping based on commit messages:

```bash
# Install (when ready)
uv add --dev python-semantic-release

# Auto-bump version based on commits
semantic-release version

# Create release with changelog
semantic-release publish
```

## Resources

- [Semantic Versioning 2.0.0](https://semver.org/)
- [PEP 440 – Version Identification](https://peps.python.org/pep-0440/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Questions?** Open an issue or discussion on GitHub for version-related questions.
