#!/usr/bin/env bash
# LinkChest — setup script
# Installs dependencies, initialises the database, seeds demo data, then EXITS.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Installing Python dependencies…"
pip install -r requirements.txt

echo "==> Seeding database…"
python3 seed.py

echo ""
echo "Setup complete. Start the server with:"
echo "  python3 app.py"
echo ""
echo "The app will be available at http://0.0.0.0:\${PORT:-8000}"
