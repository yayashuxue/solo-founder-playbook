#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$HERE/skills"
DEST="$HOME/.codex/skills"
mkdir -p "$DEST"

# Shared knowledge folder (used by all solo-* skills except solo-failures, which ships its own)
mkdir -p "$DEST/knowledge"
cp -f "$HERE/knowledge/patterns.json" "$DEST/knowledge/patterns.json"
cp -f "$HERE/knowledge/insights.md" "$DEST/knowledge/insights.md"

# Install each shared-knowledge skill
for s in solo-analyze solo-growth solo-patterns solo-playbook solo-roast; do
  cp -R "$SKILLS_SRC/$s" "$DEST/$s"
  rm -f "$DEST/$s/knowledge"
  ln -sfn ../knowledge "$DEST/$s/knowledge"
  echo "installed: $DEST/$s"
done

# solo-failures has its own self-contained knowledge bundle
cp -R "$SKILLS_SRC/solo-failures" "$DEST/solo-failures"
echo "installed: $DEST/solo-failures"

echo
echo "Done. Restart Codex to pick up all 6 skills."
