#!/usr/bin/env bash
# Legacy installer for Claude Code (clone-and-symlink flavor).
# Recommended path: install as a Claude plugin instead —
#   /plugin marketplace add yayashuxue/solo-founder-playbook
#   /plugin install solo-founder-playbook
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$HERE/skills"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
for s in solo-analyze solo-distribution solo-failures solo-growth solo-patterns solo-playbook solo-roast; do
  ln -sfn "$SKILLS_SRC/$s" "$DEST/$s"
  echo "linked: $DEST/$s"
done
echo
echo "Done. Restart Claude Code, then type /solo to see all 7 skills."
