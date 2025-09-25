#!/bin/bash
set -euo pipefail

echo "Waiting for database to be ready..."
until pg_isready -h ${DATABASE_HOST:-db} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-postgres}; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

if [ "${INIT_DB:-false}" = "true" ]; then
  echo "Initializing database..."
  /usr/local/bin/init-db.sh
fi

echo "Running database migrations..."
python3 scripts/migrate.py --env production || {
  echo "Migration failed, but continuing startup..."
}

echo "Starting application on port ${PORT:-8000}..."
PORT=${PORT:-8000}
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
