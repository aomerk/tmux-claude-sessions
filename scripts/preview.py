#!/usr/bin/env python3
"""
preview.py — fzf preview pane for tmux-claude-sessions.

Called by fzf as:  preview.py <path> <session-id>

Renders the conversation from the selected .jsonl file with colored
role badges and wrapped text, fitting within the 45% preview panel.
"""

import json
import os
import sys
import textwrap
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────

_dir = os.environ.get("CLAUDE_SESSIONS_DIR", "")
CLAUDE_PROJECTS = Path(_dir).expanduser() if _dir else Path.home() / ".claude" / "projects"

# ── ANSI colors ───────────────────────────────────────────────────────────────

CYAN    = "\033[38;5;45m"
MAGENTA = "\033[38;5;201m"
GRAY    = "\033[38;5;242m"
GREEN   = "\033[38;5;84m"
WHITE   = "\033[38;5;252m"
RESET   = "\033[0m"
BOLD    = "\033[1m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"

# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 3:
        print("No session selected.")
        return

    dir_path = Path(sys.argv[1].strip())
    sid      = sys.argv[2].strip()
    home     = Path.home()

    # Locate the .jsonl file — first try encoding the path, then brute-force
    try:
        rel = dir_path.relative_to("/")
        encoded = "-" + str(rel).replace("/", "-").replace(".", "-")
    except Exception:
        encoded = ""

    jsonl = None
    for p in CLAUDE_PROJECTS.iterdir():
        if encoded and (p.name == encoded or p.name.startswith(encoded)):
            candidate = p / f"{sid}.jsonl"
            if candidate.exists():
                jsonl = candidate
                break

    if not jsonl:
        for p in CLAUDE_PROJECTS.iterdir():
            candidate = p / f"{sid}.jsonl"
            if candidate.exists():
                jsonl = candidate
                break

    if not jsonl:
        print(col(f"Session file not found: {sid}", MAGENTA))
        return

    short_dir = str(dir_path).replace(str(home), "~")
    print(col(f" {short_dir}", CYAN))
    print(col(f" {sid[:8]}…", GRAY))
    print()

    try:
        with open(jsonl) as f:
            lines = [json.loads(l) for l in f if l.strip()]
    except Exception as e:
        print(f"Error reading session: {e}")
        return

    for d in lines:
        role = d.get("type")
        if role not in ("user", "assistant"):
            continue

        content = d.get("message", {}).get("content", [])
        texts: list[str] = []
        if isinstance(content, str):
            texts = [content]
        elif isinstance(content, list):
            texts = [c["text"] for c in content
                     if isinstance(c, dict) and c.get("type") == "text"]

        for text in texts:
            text = text.strip()
            if not text or text.startswith("<"):
                continue

            if role == "user":
                badge = col("  you  ", f"\033[48;5;18m{CYAN}")
            else:
                badge = col(" claude ", f"\033[48;5;22m{GREEN}")

            wrapped = textwrap.fill(text, width=42,
                                    subsequent_indent="         ")
            print(f"{badge} {WHITE}{wrapped}{RESET}")
            print()


if __name__ == "__main__":
    main()
