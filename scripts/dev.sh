#!/usr/bin/env bash
# scripts/dev.sh - Launch local development servers for FastAPI backend & Next.js frontend

echo "=================================================="
echo "Starting Raksha Grid Production Monorepo Dev Servers..."
echo "=================================================="

export PYTHONPATH=$(pwd)

# Start FastAPI backend in background
python -m uvicorn backend.fastapi.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✓ FastAPI Backend started (PID: $BACKEND_PID) on http://localhost:8000"

# Start Next.js frontend
cd frontend/nextjs && npm run dev
