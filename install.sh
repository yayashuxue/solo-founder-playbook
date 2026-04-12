#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
for s in analyze-idea growth-strategy roast-my-plan startup-patterns startup-playbook; do
  ln -sfn "$HERE/$s" "$DEST/$s"
  echo "linked: $DEST/$s"
done
echo
echo "Done. Restart Claude Code, then try: /analyze-idea, /startup-playbook, /growth-strategy, /startup-patterns, /roast-my-plan"
