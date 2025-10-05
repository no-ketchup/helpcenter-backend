#!/bin/bash
set -euo pipefail

echo "=== DEBUGGING STARTUP ==="
echo "Environment: ${ENVIRONMENT:-not_set}"
echo "Port: ${PORT:-8080}"
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo "========================="

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

echo "Skipping migration script for now..."

echo "Testing FastAPI app import..."
python3 -c "
import sys
sys.path.append('graphql-api')
from main import app
print('FastAPI app import: SUCCESS')
print('App title:', app.title)
" || {
  echo "FastAPI app import failed"
  exit 1
}

echo "Starting FastAPI app on port ${PORT:-8080}..."
cd graphql_api
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
