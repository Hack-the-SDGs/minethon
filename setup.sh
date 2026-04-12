#!/usr/bin/env bash
# setup.sh -- one-shot install for minethon.
#
# Installs:
#   1. Python dependencies via `uv sync` (includes JSPyBridge).
#   2. Pinned npm packages into JSPyBridge's bundled node_modules so
#      `require()` at runtime never triggers a surprise lazy install.
#
# Requires:
#   - uv (https://docs.astral.sh/uv/)
#   - Node.js >= 22  (mineflayer 4.37 requires engines.node >=22)

set -euo pipefail

cd "$(dirname "$0")"

# --- Node.js version check ------------------------------------------------

if ! command -v node >/dev/null 2>&1; then
  echo "error: 'node' not found. Install Node.js 22+ before running setup.sh." >&2
  exit 1
fi

NODE_MAJOR=$(node -p "process.versions.node.split('.')[0]")
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "error: Node.js 22+ required; found $(node -v)." >&2
  exit 1
fi

# --- uv check --------------------------------------------------------------

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found. Install from https://docs.astral.sh/uv/" >&2
  exit 1
fi

# --- 1/2: Python dependencies ---------------------------------------------

echo "[1/2] syncing Python dependencies via uv..."
uv sync --quiet

# --- 2/2: pre-install pinned npm packages ---------------------------------
# JSPyBridge's require() uses aliased package names like
# `mineflayer--<hex(version)>` (see javascript/js/deps.js:63) so that multiple
# pinned versions can coexist. A plain `npm install mineflayer@4.37.0` WON'T
# register that alias, so the very next require() triggers a fresh install.
#
# The only reliable prime-the-cache is to call JSPyBridge's own install
# pipeline via require() from Python — it writes the aliased entry into
# js/package.json and runs npm with the right args.

echo "[2/2] priming JSPyBridge module cache with pinned versions..."
uv run --quiet python -c "
from javascript import require
# Versions must match the constants in src/minethon/_bridge.py.
require('mineflayer', '4.37.0')
require('vec3', '0.1.10')
require('mineflayer-pathfinder', '2.4.5')
"

cat <<'EOF'

Setup complete.

Next steps:
  cp examples/demos/drasl_auth/.env.example examples/demos/drasl_auth/.env
  # edit .env with your credentials
  uv run --env-file examples/demos/drasl_auth/.env examples/demos/drasl_auth/main.py
EOF
