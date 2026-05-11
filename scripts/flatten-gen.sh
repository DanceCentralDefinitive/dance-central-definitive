#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"

DRY_RUN=0
FORCE=0

usage() {
  cat <<'EOF'
Usage: scripts/flatten-gen.sh [--dry-run] [--force]

Moves all items from src/**/gen/ to their parent directories and removes
any now-empty gen directories.

Options:
  --dry-run  Show what would be moved/removed without making changes.
  --force    Overwrite destination paths when collisions occur.
  -h, --help Show this help.
EOF
}

while (($#)); do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      ;;
    --force)
      FORCE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Missing src directory: $SRC_DIR" >&2
  exit 1
fi

mapfile -d '' GEN_DIRS < <(find "$SRC_DIR" -type d -name gen -print0)

if ((${#GEN_DIRS[@]} == 0)); then
  echo "No gen directories found under src/."
  exit 0
fi

MOVED=0
SKIPPED=0
REMOVED_GEN=0

for GEN_DIR in "${GEN_DIRS[@]}"; do
  PARENT_DIR="$(dirname "$GEN_DIR")"

  mapfile -d '' ITEMS < <(find "$GEN_DIR" -mindepth 1 -maxdepth 1 -print0)

  if ((${#ITEMS[@]} == 0)); then
    if ((DRY_RUN)); then
      echo "DRY-RUN remove empty dir: $GEN_DIR"
    else
      rmdir "$GEN_DIR" && ((REMOVED_GEN+=1)) || true
    fi
    continue
  fi

  for ITEM in "${ITEMS[@]}"; do
    BASENAME="$(basename "$ITEM")"
    DEST="$PARENT_DIR/$BASENAME"

    if [[ -e "$DEST" && $FORCE -ne 1 ]]; then
      echo "Skip (destination exists): $ITEM -> $DEST"
      ((SKIPPED+=1))
      continue
    fi

    if ((DRY_RUN)); then
      echo "DRY-RUN move: $ITEM -> $DEST"
      ((MOVED+=1))
    else
      if ((FORCE)); then
        mv -f "$ITEM" "$DEST"
      else
        mv "$ITEM" "$DEST"
      fi
      ((MOVED+=1))
    fi
  done

  if ((DRY_RUN)); then
    if [[ -z "$(find "$GEN_DIR" -mindepth 1 -print -quit)" ]]; then
      echo "DRY-RUN remove empty dir: $GEN_DIR"
    else
      echo "Keep non-empty dir: $GEN_DIR"
    fi
  else
    if [[ -z "$(find "$GEN_DIR" -mindepth 1 -print -quit)" ]]; then
      rmdir "$GEN_DIR" && ((REMOVED_GEN+=1)) || true
    fi
  fi
done

echo "Moved: $MOVED"
echo "Skipped: $SKIPPED"
echo "Removed empty gen dirs: $REMOVED_GEN"
