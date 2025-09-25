#!/bin/bash
set -euo pipefail

echo "=== STARTUP DEBUG ==="
echo "Environment: ${ENVIRONMENT}"
echo "Port: ${PORT:-8080}"
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo "Files in /app: $(ls -la /app)"
echo "====================="

echo "Skipping all health checks - starting application directly..."

if [ "${INIT_DB:-false}" = "true" ]; then
  echo "Initializing database..."
  /usr/local/bin/init-db.sh
fi

echo "Running database migrations..."
python3 scripts/migrate.py --env production || {
  echo "Migration failed, but continuing startup..."
  echo "Migration error details: $?"
}

echo "Starting application on port ${PORT:-8080}..."
PORT="${PORT:-8080}"
echo "Starting application on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
