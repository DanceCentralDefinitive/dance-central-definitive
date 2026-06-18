#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Default build is deluxe non-debug. Extra flags are forwarded.
python3 tools/build.py src bin "$@"