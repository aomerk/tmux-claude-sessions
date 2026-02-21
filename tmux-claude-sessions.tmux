#!/usr/bin/env bash
# tmux-claude-sessions.tmux — TPM-compatible plugin entry point
#
# Binds a key (default: prefix+g) to open an fzf popup listing all
# Claude AI conversations from ~/.claude/projects/.

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"

# Read user-configurable options (with defaults)
KEY=$(tmux show-option -gv @claude_sessions_key    2>/dev/null); KEY=${KEY:-g}
WIDTH=$(tmux show-option -gv @claude_sessions_popup_width  2>/dev/null); WIDTH=${WIDTH:-80%}
HEIGHT=$(tmux show-option -gv @claude_sessions_popup_height 2>/dev/null); HEIGHT=${HEIGHT:-75%}
DIR=$(tmux show-option -gv @claude_sessions_dir    2>/dev/null); DIR=${DIR:-~/.claude/projects}

tmux bind-key "$KEY" display-popup \
  -w "$WIDTH" \
  -h "$HEIGHT" \
  -d "#{pane_current_path}" \
  -e "CLAUDE_SESSIONS_DIR=$DIR" \
  -E "bash $PLUGIN_DIR/scripts/popup.sh"
