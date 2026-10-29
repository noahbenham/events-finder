#!/usr/bin/env bash
# Full local run using the personal Claude Pro login (kept separate from the work login).
set -euo pipefail
cd "$(dirname "$0")"
export CLAUDE_CONFIG_DIR="$PWD/.claude-personal"
export INSTAGRAM_USER="${INSTAGRAM_USER:?set INSTAGRAM_USER}"
source .venv/bin/activate
python scripts/fetch.py
python scripts/extract.py
python scripts/build.py
