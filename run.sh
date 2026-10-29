#!/usr/bin/env bash
# Daily run: fetch posts, extract events, build the site, push to GitHub Pages.
# Uses the personal Claude login in .claude-personal and the personal GitHub account.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export CLAUDE_CONFIG_DIR="$PWD/.claude-personal"
export PYTHONWARNINGS=ignore
source .venv/bin/activate

python scripts/fetch.py
python scripts/extract.py
python scripts/build.py

git add docs data/events.json data/accounts.json data/accounts.txt
if ! git diff --cached --quiet; then
  git commit -q -m "Update events $(date +%F)"
  GH_TOKEN=$(gh auth token --user noahbenham) git push -q
fi
echo "done $(date)"
