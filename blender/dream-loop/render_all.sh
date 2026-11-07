#!/usr/bin/env bash
# Render all 10 episodes to PNG frame folders. Needs `bpy` (pip install bpy) or Blender's python.
# Usage: PY=python3 ./render_all.sh <frames_dir> [res] [samples] [episodes...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-python3}"
OUT="${1:-$HERE/frames}"; RES="${2:-960x540}"; SAMPLES="${3:-10}"; shift 3 2>/dev/null || true
EPS="${*:-1 2 3 4 5 6 7 8 9 10}"
for e in $EPS; do
  d="$OUT/ep$(printf %02d "$e")"
  echo "== episode $e -> $d"
  "$PY" "$HERE/episodes.py" --ep "$e" --out "$d" --res "$RES" --samples "$SAMPLES" | grep -E "Saved|Error" | tail -1
done
