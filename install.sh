#!/usr/bin/env bash
# Install Solo Founder Playbook skills into ~/.claude/skills/
# Each skill is copied as a direct child of ~/.claude/skills/ so Claude Code
# discovers it (personal skills are not loaded recursively).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
SKILLS=(analyze-idea growth-strategy roast-my-plan startup-patterns startup-playbook)

mkdir -p "$SKILLS_DIR"

for skill in "${SKILLS[@]}"; do
  src="$SCRIPT_DIR/$skill"
  dst="$SKILLS_DIR/$skill"
  if [[ ! -d "$src" ]]; then
    echo "skip: $skill (not found in $SCRIPT_DIR)"
    continue
  fi
  rm -rf "$dst"
  cp -r "$src" "$dst"
  echo "installed: $dst"
done

echo
echo "Done. Restart Claude Code, then try: /analyze-idea, /startup-playbook, /growth-strategy, /startup-patterns, /roast-my-plan"
