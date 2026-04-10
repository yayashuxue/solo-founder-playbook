#!/bin/bash
# Setup script for solo-founder-playbook
# Creates symlinks so Claude Code can discover the skills as slash commands.

SKILL_DIR="$HOME/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Error: $SKILL_DIR does not exist. Is Claude Code installed?"
  exit 1
fi

count=0
for skill in "$REPO_DIR"/skills/*/; do
  name=$(basename "$skill")
  ln -sfn "$skill" "$SKILL_DIR/$name"
  echo "  Linked /$(basename "$skill")"
  count=$((count + 1))
done

echo "Done — $count skills linked. Restart Claude Code to use them."
