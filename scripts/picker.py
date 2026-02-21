#!/usr/bin/env python3
"""
picker.py — lists all Claude AI sessions for fzf consumption.

Reads CLAUDE_SESSIONS_DIR (env) or ~/.claude/projects/, decodes the
hyphen-encoded directory names back to real filesystem paths, and emits
one tab-delimited line per session:

    <display-text>\t<real-path>\t<session-id>

fzf is invoked with --with-nth=1 so only the display text is shown;
columns 2 and 3 are passed to preview.py and open.sh as hidden payload.
"""

import json
import os
import sys
import time
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────

_dir = os.environ.get("CLAUDE_SESSIONS_DIR", "")
CLAUDE_PROJECTS = Path(_dir).expanduser() if _dir else Path.home() / ".claude" / "projects"

# ── decode encoded project dir → real path ───────────────────────────────────

def decode_project_dir(encoded: str) -> Path | None:
    """
    Claude CLI encodes project paths by replacing '/' with '-' and '.' with '--'.
    We reverse this by doing a greedy filesystem walk to reconstruct the real path.
    """
    raw = encoded.lstrip("-").replace("--", "-\x00")
    parts = []
    for token in raw.split("-"):
        if token.startswith("\x00"):
            parts.append("." + token[1:])
        elif token:
            parts.append(token)

    def match(base: Path, tokens: list) -> Path | None:
        if not tokens:
            return base
        for width in range(1, len(tokens) + 1):
            component = "-".join(tokens[:width])
            candidate = base / component
            if candidate.exists():
                result = match(candidate, tokens[width:])
                if result is not None:
                    return result
        return None

    return match(Path("/"), parts)

# ── extract first real user message ──────────────────────────────────────────

def first_message(jsonl: Path) -> str:
    try:
        with open(jsonl) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "user":
                    continue
                content = d.get("message", {}).get("content", [])
                texts = []
                if isinstance(content, str):
                    texts = [content]
                elif isinstance(content, list):
                    texts = [c["text"] for c in content
                             if isinstance(c, dict) and c.get("type") == "text"]
                for text in texts:
                    t = text.strip()
                    if t and not t.startswith("<"):
                        return " ".join(t.split())  # collapse whitespace
    except Exception:
        pass
    return ""

# ── human-readable age ────────────────────────────────────────────────────────

def age(mtime: float) -> str:
    s = int(time.time() - mtime)
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"

# ── ANSI colors ───────────────────────────────────────────────────────────────

CYAN    = "\033[38;5;45m"
MAGENTA = "\033[38;5;201m"
GRAY    = "\033[38;5;242m"
WHITE   = "\033[38;5;252m"
RESET   = "\033[0m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"

# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not CLAUDE_PROJECTS.exists():
        print("No claude projects directory found.", file=sys.stderr)
        sys.exit(1)

    home = Path.home()
    groups = []

    for p in sorted(CLAUDE_PROJECTS.iterdir()):
        if not p.is_dir():
            continue
        convs = []
        for f in p.glob("*.jsonl"):
            if f.stem.startswith("agent-"):
                continue
            convs.append((f.stat().st_mtime, f))
        if not convs:
            continue
        convs.sort(reverse=True)
        real = decode_project_dir(p.name)
        groups.append((convs[0][0], real, convs))

    groups.sort(reverse=True)

    for _, real, convs in groups:
        short = str(real).replace(str(home), "~") if real else "(unknown)"
        real = real or Path.home()  # fallback dir for open.sh

        # Directory header — no tab payload so fzf selection is silently ignored
        count = len(convs)
        print(f"  {col(short, CYAN)}  {col(f'({count})', GRAY)}")

        for mtime, f in convs:
            sid   = f.stem
            msg   = first_message(f)
            a     = age(mtime)
            label = (msg[:58] + "…") if len(msg) > 58 else (msg or col("(empty)", GRAY))
            age_s = col(f"[{a:>3}]", MAGENTA)

            # Format: <display>\t<path>\t<session-id>
            # fzf --with-nth=1 shows only display; {2},{3} are hidden payload
            print(f"    {age_s}  {col(label, WHITE)}\t{real}\t{sid}")


if __name__ == "__main__":
    main()
