#!/usr/bin/env bash
# demo.sh — run the full demo: install, seed, start, and open
set -euo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  LinkChest — Personal Bookmarks Manager"
echo "============================================"
echo ""

# Install and seed
bash install.sh

echo ""
echo "==> Starting the server…"
echo "    Open http://localhost:${PORT:-8000} in your browser."
echo ""

python3 app.py
