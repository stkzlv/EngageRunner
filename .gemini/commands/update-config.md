# Update Configuration Playbook

Review and optimize project configuration for consistency and maintainability.

## Process
1. Discover configuration files and Pydantic models.
2. Look for magic numbers and hardcoded values in code.
3. Move hardcoded values to appropriate config files.
4. Remove unused settings and duplicated logic.
5. Add descriptive comments to config options.

## Discover Configuration
```bash
ls config.yaml              # Runtime configuration
ls src/engagerunner/config.py # Pydantic models for validation
```

## Configuration Structure
- `config.yaml` - User-provided scenario configuration.
- `src/engagerunner/config.py` - Pydantic models for validation and defaults.

## Guidelines
- Use Pydantic models for type-safe validation.
- Keep secrets in environment variables (never in config files).
- Group related settings logically.
- Use descriptive names (avoid abbreviations).
- Document non-obvious settings with comments.

## Review Checklist
- [ ] No magic numbers in code (move to config).
- [ ] No duplicated settings across files.
- [ ] Unused settings removed.
- [ ] All settings have clear names.
- [ ] Complex settings have comments.
- [ ] Secrets use environment variables.
- [ ] Pydantic models validate all config options.