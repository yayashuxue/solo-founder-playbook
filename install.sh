#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
for s in solo-analyze solo-growth solo-patterns solo-playbook solo-roast; do
  ln -sfn "$HERE/$s" "$DEST/$s"
  echo "linked: $DEST/$s"
done
echo
echo "Done. Restart Claude Code, then type /solo to see all 5 skills."
