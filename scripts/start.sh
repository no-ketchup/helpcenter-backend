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

echo "Running database migrations..."
python3 scripts/migrate.py --env production || {
  echo "Migration failed, but continuing startup..."
}

echo "Testing FastAPI app import..."
python3 -c "
from app.main import app
print('FastAPI app import: SUCCESS')
print('App title:', app.title)
" || {
  echo "FastAPI app import failed"
  exit 1
}

echo "Starting FastAPI application on port ${PORT:-8080}..."
PORT="${PORT:-8080}"
echo "About to start FastAPI on port $PORT"

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
