#!/bin/bash
set -euo pipefail

echo "Checking database connection..."
if [ "${ENVIRONMENT}" = "production" ] || [ "${ENVIRONMENT}" = "staging" ]; then
  # For production/staging, test actual database connection
  echo "Testing Neon DB connection..."
  python3 -c "
import os
import asyncio
import asyncpg
import sys

async def test_db():
    try:
        db_url = os.getenv('DATABASE_URL_ASYNC', os.getenv('DATABASE_URL'))
        if not db_url:
            print('ERROR: No database URL found')
            return False
        
        # Convert to asyncpg format if needed
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        conn = await asyncpg.connect(db_url)
        await conn.execute('SELECT 1')
        await conn.close()
        print('Database connection: SUCCESS')
        return True
    except Exception as e:
        print(f'Database connection: FAILED - {e}')
        return False

success = asyncio.run(test_db())
sys.exit(0 if success else 1)
" || {
    echo "Database connection failed, but continuing startup..."
  }
else
  # For development, use pg_isready for local database
  echo "Waiting for local database to be ready..."
  until pg_isready -h ${DATABASE_HOST:-db} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-postgres}; do
    echo "Database is unavailable - sleeping"
    sleep 2
  done
fi

echo "Checking Redis connection..."
if [ "${ENVIRONMENT}" = "production" ] || [ "${ENVIRONMENT}" = "staging" ]; then
  # For production/staging, test actual Redis connection
  echo "Testing Redis connection..."
  python3 -c "
import os
import redis
import sys

try:
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print('WARNING: No Redis URL found, skipping Redis check')
        sys.exit(0)
    
    r = redis.from_url(redis_url)
    r.ping()
    print('Redis connection: SUCCESS')
except Exception as e:
    print(f'Redis connection: FAILED - {e}')
    sys.exit(1)
" || {
    echo "Redis connection failed, but continuing startup..."
  }
else
  # For development, assume Redis is available locally
  echo "Assuming Redis is available locally..."
fi

if [ "${INIT_DB:-false}" = "true" ]; then
  echo "Initializing database..."
  /usr/local/bin/init-db.sh
fi

echo "Running database migrations..."
python3 scripts/migrate.py --env production || {
  echo "Migration failed, but continuing startup..."
}

echo "Starting application on port ${PORT:-8080}..."
PORT="${PORT:-8080}"
echo "Starting application on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
