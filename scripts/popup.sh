#!/usr/bin/env bash
# popup.sh — launched inside the tmux popup
# Runs picker.py piped through fzf, then calls open.sh with the selection.

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

selected=$(python3 "$PLUGIN_DIR/scripts/picker.py" \
  | fzf \
      --ansi \
      --delimiter='\t' \
      --with-nth=1 \
      --nth=1 \
      --no-sort \
      --layout=reverse \
      --border=rounded \
      --border-label=" 󱜚 Claude Sessions " \
      --border-label-pos=2 \
      --color="border:#0ABDC6,label:#0ABDC6,header:#D300C4" \
      --color="bg+:#111133,fg+:#ffffff,hl+:#D300C4,hl:#0ABDC6" \
      --color="pointer:#D300C4,marker:#0ABDC6,spinner:#0ABDC6" \
      --prompt="  " \
      --pointer="▶" \
      --header="  enter: open   esc: cancel   J/K: scroll preview   g/G: top/bottom   ctrl-d/u: half page" \
      --preview="python3 $PLUGIN_DIR/scripts/preview.py {2} {3}" \
      --preview-window="right:45%:wrap" \
      --bind="ctrl-j:down,ctrl-k:up" \
      --bind="J:preview-down,K:preview-up" \
      --bind="ctrl-d:preview-half-page-down,ctrl-u:preview-half-page-up" \
      --bind="ctrl-f:preview-page-down,ctrl-b:preview-page-up" \
      --bind="g:preview-top,G:preview-bottom" \
      --bind="/:toggle-preview" \
      2>/dev/null \
  | awk -F'\t' '{print $2"\t"$3}')  # extract path<TAB>session_id

# Exit on cancel or header-line selection (headers produce empty tab fields)
[ -z "$selected" ] && exit 0
dir=$(printf '%s' "$selected" | cut -f1)
[ -z "$dir" ] && exit 0

bash "$PLUGIN_DIR/scripts/open.sh" "$selected"
