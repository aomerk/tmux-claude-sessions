# Changelog

All notable changes to `tmux-claude-sessions` will be documented here.

## [1.0.0] — 2026-02-21

### Added
- `tmux-claude-sessions.tmux` — TPM-compatible plugin entry point
- `scripts/popup.sh` — fzf popup launcher with vaporwave color scheme
- `scripts/picker.py` — decodes Claude's hyphen-encoded project directories,
  groups sessions by project, shows age and first user message
- `scripts/preview.py` — live conversation preview with colored role badges
- `scripts/open.sh` — opens `claude -r <id>` in a new window; switches to
  existing window if session is already open
- Configuration via tmux options:
  - `@claude_sessions_key` (default: `g`)
  - `@claude_sessions_popup_width` (default: `80%`)
  - `@claude_sessions_popup_height` (default: `75%`)
  - `@claude_sessions_dir` (default: `~/.claude/projects`)
- GitHub Actions CI: shellcheck + Python syntax validation
