#!/bin/bash
set -euo pipefail

echo "=== MINIMAL STARTUP TEST ==="
echo "Environment: ${ENVIRONMENT:-not_set}"
echo "Port: ${PORT:-8080}"
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo "Files in /app: $(ls -la /app | head -10)"
echo "============================="

echo "Testing basic Python import..."
python3 -c "import sys; print('Python path:', sys.path[:3])" || {
  echo "Python import failed"
  exit 1
}

echo "Testing FastAPI import..."
python3 -c "from fastapi import FastAPI; print('FastAPI import: SUCCESS')" || {
  echo "FastAPI import failed"
  exit 1
}

echo "Starting minimal HTTP server on port ${PORT:-8080}..."
PORT="${PORT:-8080}"
echo "About to start server on port $PORT"

# Start a simple HTTP server instead of the full app
python3 -m http.server $PORT
