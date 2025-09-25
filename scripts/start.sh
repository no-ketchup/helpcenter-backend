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

echo "Testing migration script..."
python3 scripts/migrate.py --env production || {
  echo "Migration failed, but continuing startup..."
}

echo "Testing FastAPI app import step by step..."
python3 -c "
import sys
print('Python path:', sys.path[:3])

print('Testing settings import...')
try:
    from app.core import settings
    print('Settings import: SUCCESS')
    print('Environment:', settings.ENVIRONMENT)
except Exception as e:
    print('Settings import failed:', e)
    with open('/tmp/error.log', 'w') as f:
        f.write(f'Settings import failed: {e}\n')
        import traceback
        f.write(traceback.format_exc())
    sys.exit(1)

print('Testing models import...')
try:
    from app.domain import models
    print('Models import: SUCCESS')
except Exception as e:
    print('Models import failed:', e)
    with open('/tmp/error.log', 'w') as f:
        f.write(f'Models import failed: {e}\n')
        import traceback
        f.write(traceback.format_exc())
    sys.exit(1)

print('Testing main app import...')
try:
    from app.main import app
    print('FastAPI app import: SUCCESS')
    print('App title:', app.title)
except Exception as e:
    print('FastAPI app import failed:', e)
    with open('/tmp/error.log', 'w') as f:
        f.write(f'FastAPI app import failed: {e}\n')
        import traceback
        f.write(traceback.format_exc())
    sys.exit(1)
" || {
  echo "FastAPI app import failed"
  echo "Error details:"
  cat /tmp/error.log 2>/dev/null || echo "No error log found"
  exit 1
}

echo "Starting simple HTTP server on port ${PORT:-8080}..."
PORT="${PORT:-8080}"
echo "About to start HTTP server on port $PORT"

# Start a simple HTTP server that will definitely work
python3 -m http.server $PORT
