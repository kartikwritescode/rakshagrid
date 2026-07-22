#!/usr/bin/env bash
# scripts/build.sh - Production build verification

echo "=================================================="
echo "Building Raksha Grid Production Artifacts..."
echo "=================================================="

# Check Python environment
python -c "import fastapi, torch, sklearn, pandas; print('✓ Python dependencies verified')"

# Build Next.js
cd frontend/nextjs && npm run build
echo "✓ Next.js build complete"
