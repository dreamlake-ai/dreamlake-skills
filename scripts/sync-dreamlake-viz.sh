#!/usr/bin/env bash
# dreamlake-viz is GENERATED — never hand-edit it here. It is built from the
# viz docs by `pnpm gen:llms` in the viz-workspace repo (docs ARE the skill).
# This script re-syncs the copy in this repo, preferring a local checkout and
# falling back to the published zip.
set -euo pipefail
cd "$(dirname "$0")/.."
LOCAL=${VIZ_WORKSPACE:-$HOME/Code/vuer-ai/dreamlake-workspace/dreamlake-ai/packages/viz-workspace}
if [ -d "$LOCAL/skills/dreamlake-viz" ]; then
  rm -rf dreamlake-viz
  cp -R "$LOCAL/skills/dreamlake-viz" .
  echo "synced from $LOCAL"
else
  TMP=$(mktemp -d)
  curl -fsSL https://viz.dreamlake.ai/skills/dreamlake-viz.zip -o "$TMP/skill.zip"
  rm -rf dreamlake-viz && mkdir dreamlake-viz
  unzip -q "$TMP/skill.zip" -d dreamlake-viz
  rm -rf "$TMP"
  echo "synced from viz.dreamlake.ai"
fi
