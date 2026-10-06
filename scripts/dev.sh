#!/usr/bin/env bash
# scripts/dev.sh - Launch local development servers for FastAPI backend & Next.js frontend
set -e

# Resolve repository root directory reliably from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================="
echo "Starting Raksha Grid Production Monorepo Dev Servers..."
echo "=================================================="

# Check and activate virtual environment if present
if [ -d "$ROOT_DIR/.venv" ]; then
    if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
        source "$ROOT_DIR/.venv/bin/activate"
    elif [ -f "$ROOT_DIR/.venv/Scripts/activate" ]; then
        source "$ROOT_DIR/.venv/Scripts/activate"
    fi
fi

# Ensure uvicorn is available
if ! command -v uvicorn &> /dev/null && ! python -c "import uvicorn" &> /dev/null; then
    echo "[INFO] uvicorn not found. Installing requirements..."
    pip install -r "$ROOT_DIR/requirements.txt"
fi

# Start FastAPI backend in background
python -m uvicorn apps.api.src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✓ FastAPI Backend started (PID: $BACKEND_PID) on http://localhost:8000"

# Check node_modules
if [ ! -d "$ROOT_DIR/apps/web/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    (cd "$ROOT_DIR/apps/web" && npm install)
fi

# Start Next.js frontend
cd "$ROOT_DIR/apps/web" && npm run dev

